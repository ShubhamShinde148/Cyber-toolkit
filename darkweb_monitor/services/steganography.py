"""
Steganography Tool - Hide and Extract Secret Messages in Images
Supports two LSB encoding formats:
  1. Native format (1 LSB per RGB channel, MSB-first, <<END>> delimiter)
  2. Stylesuxx-compatible format (1 LSB per RGB channel, MSB-first, null terminator)
     — compatible with https://stylesuxx.github.io/steganography/
"""

import io
from PIL import Image


class SteganographyTool:
    """Encode and decode hidden messages in PNG images using LSB steganography."""

    DELIMITER = "<<END>>"
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    # ------------------------------------------------------------------ #
    #  ENCODE                                                             #
    # ------------------------------------------------------------------ #

    def encode(self, image_data: bytes, message: str) -> bytes:
        """
        Hide a text message inside an image using LSB encoding.
        Uses stylesuxx-compatible format (1 LSB per RGB, MSB-first, null terminator).
        Returns the modified image as PNG bytes.
        """
        if not message:
            raise ValueError("Message cannot be empty.")

        img = Image.open(io.BytesIO(image_data)).convert("RGB")
        width, height = img.size
        pixels = list(img.getdata())

        # Build binary string: message chars as 8-bit MSB-first + null terminator
        binary_message = ''
        for ch in message:
            binary_message += format(ord(ch), '08b')
        binary_message += '00000000'  # null terminator

        max_bits = width * height * 3
        if len(binary_message) > max_bits:
            raise ValueError(
                f"Message too large for this image. "
                f"Max ~{max_bits // 8 - 1} characters, got {len(message)}."
            )

        new_pixels = []
        bit_idx = 0
        for pixel in pixels:
            new_channels = []
            for channel in pixel:
                if bit_idx < len(binary_message):
                    new_channels.append((channel & ~1) | int(binary_message[bit_idx]))
                    bit_idx += 1
                else:
                    new_channels.append(channel)
            new_pixels.append(tuple(new_channels))

        encoded_img = Image.new("RGB", (width, height))
        encoded_img.putdata(new_pixels)

        buf = io.BytesIO()
        encoded_img.save(buf, format="PNG")
        return buf.getvalue()

    # ------------------------------------------------------------------ #
    #  DECODE — reads 1 LSB per RGB channel, MSB-first                    #
    # ------------------------------------------------------------------ #

    def decode(self, image_data: bytes) -> dict:
        """
        Extract a hidden message from an LSB-encoded image.
        Uses 1 LSB per RGB channel, MSB-first bit ordering.
        Supports both null terminator (stylesuxx) and <<END>> delimiter (native).
        """
        try:
            img = Image.open(io.BytesIO(image_data)).convert("RGB")
            img_size = f"{img.size[0]}x{img.size[1]}"
            pixels = list(img.getdata())

            # Extract LSBs from RGB channels
            bits = []
            for pixel in pixels:
                for channel in pixel:
                    bits.append(channel & 1)

            # Decode 8-bit characters (MSB-first)
            chars = []
            full_text = []
            for i in range(0, len(bits) - 7, 8):
                val = 0
                for j in range(8):
                    val = (val << 1) | bits[i + j]

                # Null terminator — end of message (stylesuxx format)
                if val == 0:
                    if chars:
                        msg = ''.join(chars)
                        return {
                            "success": True,
                            "message": msg,
                            "characters": len(msg),
                            "image_size": img_size,
                        }
                    break

                chars.append(chr(val))
                full_text.append(chr(val))

                # Check for <<END>> delimiter (native format)
                current = ''.join(full_text)
                if current.endswith(self.DELIMITER):
                    hidden = current[:-len(self.DELIMITER)]
                    return {
                        "success": True,
                        "message": hidden,
                        "characters": len(hidden),
                        "image_size": img_size,
                    }

                # Safety limit
                if len(chars) > 100000:
                    break

        except Exception:
            pass

        return {
            "success": False,
            "message": None,
            "error": "No hidden message found in this image.",
            "image_size": f"{Image.open(io.BytesIO(image_data)).size[0]}x{Image.open(io.BytesIO(image_data)).size[1]}" if image_data else "unknown",
        }

    # ------------------------------------------------------------------ #
    #  CAPACITY                                                           #
    # ------------------------------------------------------------------ #

    def get_capacity(self, image_data: bytes) -> dict:
        """Return how many characters can be hidden in this image."""
        img = Image.open(io.BytesIO(image_data)).convert("RGB")
        w, h = img.size
        max_bits = w * h * 3
        # Each char needs 8 bits, plus 8 bits for null terminator
        usable_chars = (max_bits // 8) - 1
        return {
            "width": w,
            "height": h,
            "max_characters": max(usable_chars, 0),
        }
