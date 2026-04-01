import io
import os
from datetime import datetime

from PIL import Image, ExifTags
from PyPDF2 import PdfReader
from docx import Document


class MetadataExtractor:
    ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "pdf", "docx"}
    max_file_size = 50 * 1024 * 1024

    def extract(self, file_data_or_path, filename=None):
        """
        Supports both:
        - extract(file_bytes, filename) for uploaded files
        - extract(file_path) for legacy callers
        """
        file_data, resolved_name = self._normalize_input(file_data_or_path, filename)
        ext = self._get_extension(resolved_name)

        if ext not in self.ALLOWED_EXTENSIONS:
            return {
                "success": False,
                "error": "Unsupported file type. Allowed: JPG, PNG, PDF, DOCX",
            }

        if len(file_data) > self.max_file_size:
            return {
                "success": False,
                "error": "File too large. Maximum size: 50MB",
            }

        try:
            metadata = {}
            if ext in {"jpg", "jpeg", "png"}:
                metadata = self._extract_image_metadata(file_data)
            elif ext == "pdf":
                metadata = self._extract_pdf_metadata(file_data)
            elif ext == "docx":
                metadata = self._extract_docx_metadata(file_data)
        except Exception as exc:
            return {
                "success": False,
                "error": f"Could not parse metadata: {str(exc)}",
            }

        categorized = self._categorize_metadata(metadata)
        security_flags = self._build_security_flags(metadata, categorized["gps_data"])

        return {
            "success": True,
            "file_name": resolved_name,
            "file_type": ext.upper(),
            "file_size": len(file_data),
            "file_size_formatted": self._format_size(len(file_data)),
            "metadata": metadata,
            "security_flags": security_flags,
            "gps_data": categorized["gps_data"],
            "camera_info": categorized["camera_info"],
            "author_info": categorized["author_info"],
            "datetime_info": categorized["datetime_info"],
            "software_info": categorized["software_info"],
            "document_info": categorized["document_info"],
            "image_info": categorized["image_info"],
            "extracted_at": datetime.utcnow().isoformat() + "Z",
        }

    def _normalize_input(self, file_data_or_path, filename):
        if isinstance(file_data_or_path, (bytes, bytearray)):
            return bytes(file_data_or_path), filename or "uploaded_file"

        if isinstance(file_data_or_path, str):
            with open(file_data_or_path, "rb") as f:
                file_data = f.read()
            return file_data, filename or os.path.basename(file_data_or_path)

        raise TypeError("Expected bytes or file path string for extraction input")

    def _get_extension(self, filename):
        return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    def _extract_image_metadata(self, file_data):
        metadata = {}
        image = Image.open(io.BytesIO(file_data))
        metadata["format"] = image.format
        metadata["mode"] = image.mode
        metadata["width"] = image.width
        metadata["height"] = image.height

        exif = image.getexif()
        if exif:
            for tag_id, value in exif.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                metadata[tag_name] = self._safe_value(value)

            gps_info = exif.get_ifd(34853) if hasattr(exif, "get_ifd") else None
            gps_data = self._parse_gps(gps_info) if gps_info else None
            if gps_data:
                metadata["gps_latitude"] = gps_data["latitude"]
                metadata["gps_longitude"] = gps_data["longitude"]

        return metadata

    def _extract_pdf_metadata(self, file_data):
        metadata = {}
        reader = PdfReader(io.BytesIO(file_data))
        metadata["pages"] = len(reader.pages)
        raw = reader.metadata or {}
        for key, value in raw.items():
            clean_key = str(key).lstrip("/")
            metadata[clean_key] = self._safe_value(value)
        return metadata

    def _extract_docx_metadata(self, file_data):
        metadata = {}
        doc = Document(io.BytesIO(file_data))
        props = doc.core_properties
        property_map = {
            "author": props.author,
            "title": props.title,
            "subject": props.subject,
            "category": props.category,
            "comments": props.comments,
            "content_status": props.content_status,
            "created": props.created,
            "identifier": props.identifier,
            "keywords": props.keywords,
            "language": props.language,
            "last_modified_by": props.last_modified_by,
            "last_printed": props.last_printed,
            "modified": props.modified,
            "revision": props.revision,
            "version": props.version,
        }
        for key, value in property_map.items():
            if value not in (None, ""):
                metadata[key] = self._safe_value(value)
        metadata["paragraphs"] = len(doc.paragraphs)
        return metadata

    def _categorize_metadata(self, metadata):
        lowered = {str(k).lower(): v for k, v in metadata.items()}

        camera_keys = ("make", "model", "lens", "fnumber", "iso", "exposure", "focal", "flash")
        author_keys = ("author", "creator", "artist", "owner", "last_modified_by")
        datetime_keys = ("date", "time", "created", "modified", "last_printed")
        software_keys = ("software", "producer", "application", "creator tool")
        document_keys = ("title", "subject", "category", "keywords", "pages", "revision", "language")
        image_keys = ("format", "mode", "width", "height", "resolution", "dpi")

        camera_info = self._pick_contains(lowered, camera_keys)
        author_info = self._pick_contains(lowered, author_keys)
        datetime_info = self._pick_contains(lowered, datetime_keys)
        software_info = self._pick_contains(lowered, software_keys)
        document_info = self._pick_contains(lowered, document_keys)
        image_info = self._pick_contains(lowered, image_keys)
        gps_data = self._build_gps_data(metadata)

        return {
            "camera_info": camera_info,
            "author_info": author_info,
            "datetime_info": datetime_info,
            "software_info": software_info,
            "document_info": document_info,
            "image_info": image_info,
            "gps_data": gps_data,
        }

    def _pick_contains(self, lowered_metadata, key_parts):
        result = {}
        for key, value in lowered_metadata.items():
            if any(part in key for part in key_parts):
                result[key] = self._safe_value(value)
        return result

    def _build_gps_data(self, metadata):
        lat = metadata.get("gps_latitude")
        lon = metadata.get("gps_longitude")
        if lat is None or lon is None:
            return None
        return {
            "latitude": float(lat),
            "longitude": float(lon),
            "formatted": f"{float(lat):.6f}, {float(lon):.6f}",
            "maps_url": f"https://maps.google.com/?q={float(lat):.6f},{float(lon):.6f}",
            "osm_url": f"https://www.openstreetmap.org/?mlat={float(lat):.6f}&mlon={float(lon):.6f}",
        }

    def _build_security_flags(self, metadata, gps_data):
        flags = []
        lowered = {str(k).lower(): str(v).lower() for k, v in metadata.items()}

        if gps_data:
            flags.append("gps_location_exposed")
        if any("author" in k or "creator" in k for k in lowered):
            flags.append("author_identity_exposed")
        if any("software" in k or "producer" in k for k in lowered):
            flags.append("software_fingerprint_exposed")
        if any("date" in k or "time" in k or "created" in k or "modified" in k for k in lowered):
            flags.append("timeline_metadata_exposed")
        if any("last_modified_by" in k for k in lowered):
            flags.append("editor_identity_exposed")

        # Keep stable order and unique values.
        unique_flags = []
        for flag in flags:
            if flag not in unique_flags:
                unique_flags.append(flag)
        return unique_flags

    def _safe_value(self, value):
        if isinstance(value, bytes):
            try:
                return value.decode("utf-8", errors="replace")
            except Exception:
                return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    def _format_size(self, bytes_count):
        units = ["B", "KB", "MB", "GB"]
        size = float(bytes_count)
        idx = 0
        while size >= 1024 and idx < len(units) - 1:
            size /= 1024.0
            idx += 1
        return f"{size:.2f} {units[idx]}"

    def _parse_gps(self, gps_ifd):
        if not gps_ifd:
            return None

        try:
            lat_ref = gps_ifd.get(1)
            lat = gps_ifd.get(2)
            lon_ref = gps_ifd.get(3)
            lon = gps_ifd.get(4)
            if not (lat_ref and lat and lon_ref and lon):
                return None

            latitude = self._dms_to_decimal(lat, lat_ref)
            longitude = self._dms_to_decimal(lon, lon_ref)
            return {"latitude": latitude, "longitude": longitude}
        except Exception:
            return None

    def _dms_to_decimal(self, dms, ref):
        def _to_float(v):
            if isinstance(v, tuple) and len(v) == 2 and v[1]:
                return float(v[0]) / float(v[1])
            if hasattr(v, "numerator") and hasattr(v, "denominator") and v.denominator:
                return float(v.numerator) / float(v.denominator)
            return float(v)

        degrees = _to_float(dms[0])
        minutes = _to_float(dms[1])
        seconds = _to_float(dms[2])
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        ref_str = ref.decode() if isinstance(ref, bytes) else str(ref)
        if ref_str in ("S", "W"):
            decimal = -decimal
        return decimal

    def _check_dependencies(self):
        return ["Pillow", "PyPDF2", "python-docx"]

    def get_available_features(self):
        return [
            "Image EXIF metadata extraction",
            "PDF document metadata extraction",
            "DOCX core properties extraction",
            "GPS coordinate parsing for images",
            "Security flags and categorized metadata views",
        ]
