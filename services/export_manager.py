class ExportManager:
    def __init__(self):
        pass
    def export_json(self, data, filename="output.json"):
        import json
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        return filename
    def export_txt(self, data, filename="output.txt"):
        with open(filename, "w") as f:
            f.write(str(data))
        return filename
    def export_csv(self, data, filename="output.csv"):
        import csv
        if isinstance(data, list) and len(data) > 0:
            keys = data[0].keys()
            with open(filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
        return filename
    def export_all(self, data, prefix):
        return {"json": self.export_json(data, f"{prefix}.json"), "txt": self.export_txt(data, f"{prefix}.txt")}
    def export_html(self, data, prefix):
        path = f"{prefix}.html"
        with open(path, "w") as f:
            f.write(str(data))
        return path