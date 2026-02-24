from pptx import Presentation
from pptx.util import Inches


def build_pptx_from_skeleton(hash_value: str, skeleton: dict) -> str:
    """
    Builds a PowerPoint file from skeleton structure.
    """

    prs = Presentation()

    for slide_data in skeleton["slides"]:
        slide_layout = prs.slide_layouts[1]  # Title + Content
        slide = prs.slides.add_slide(slide_layout)

        title = slide.shapes.title
        content = slide.placeholders[1]

        title.text = slide_data["slide_name"]
        content.text = f"Auto-generated slide #{slide_data['order']}"

    file_path = f"generated/{hash_value}.pptx"
    prs.save(file_path)

    return file_path
