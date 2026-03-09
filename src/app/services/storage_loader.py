from pathlib import Path

from app.utils.yaml_loader import load_all_yaml_from_directory, load_yaml_file


class StorageLoader:
    LAYOUTS_DIR = Path("storage/layouts/saved")
    TEMPLATES_DIR = Path("storage/templates")

    def get_all_layouts(self) -> list[dict]:
        """Return all saved layouts: [{"name": "...", "content": [...]}, ...]"""
        return load_all_yaml_from_directory(str(self.LAYOUTS_DIR), recursive=False)

    def get_all_templates(self) -> list[dict]:
        """Return all templates (recursive, includes subdirs like PPG/, APE/)."""
        return load_all_yaml_from_directory(str(self.TEMPLATES_DIR), recursive=True)

    def get_layout(self, layout_name: str) -> dict | None:
        """Return a single layout by name, or None if not found."""
        yaml_path = self.LAYOUTS_DIR / f"{layout_name}.yaml"
        if not yaml_path.exists():
            return None
        content = load_yaml_file(str(yaml_path))
        return {"name": layout_name, "content": content}

    def get_template(self, template_name: str) -> dict | None:
        """Return a single template YAML content by name, or None if not found."""
        yaml_path = self.TEMPLATES_DIR / f"{template_name}.yaml"
        if not yaml_path.exists():
            return None
        return load_yaml_file(str(yaml_path))
