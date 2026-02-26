# services/storage_loader.py

from pathlib import Path
import yaml


class StorageLoader:
    def __init__(self):
        self.templates_path = Path("storage/templates")

    def list_saved_layouts(self):
        """
        storage/templates altındaki
        .yaml dosyalarından layout listesini döner
        """

        layouts = []

        for file in self.templates_path.glob("*.yaml"):
            name = file.stem

            layouts.append(
                {
                    "name": name,
                    "yaml_path": str(file),
                    "pptx_path": str(self.templates_path / f"{name}.pptx"),
                }
            )

        return layouts

    def load_template_yaml(self, template_name: str):
        """
        Belirli template'in yaml içeriğini döner
        """
        yaml_path = self.templates_path / f"{template_name}.yaml"

        if not yaml_path.exists():
            raise FileNotFoundError(f"{template_name}.yaml not found")

        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
