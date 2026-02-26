import os
from pptx import Presentation


def generate_ppt(skeleton_hash: str, slide_titles: list[str]) -> str:

    prs = Presentation()

    for title in slide_titles:
        slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(slide_layout)
        slide.shapes.title.text = title

    os.makedirs("generated", exist_ok=True)

    file_path = f"generated/{skeleton_hash}.pptx"
    prs.save(file_path)

    return file_path
