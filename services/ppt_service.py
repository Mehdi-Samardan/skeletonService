"""PPTX skeleton generation via zip-level merge.

Each template is a single-slide PPTX. We merge them by:
  1. Copying the first template as the base (inherits theme, master, dimensions).
  2. Removing the base's own slide from the zip, presentation.xml, and Content_Types.
  3. For every template (including the first), extracting its slide XML + all
     embedded parts (charts, images, …) into the output zip with unique names.
  4. Registering each new slide in presentation.xml, presentation.xml.rels,
     and [Content_Types].xml.
"""
import copy
import shutil
import uuid
import warnings
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from utils.logger import logger

TEMPLATE_DIR  = Path("storage/templates")
SKELETONS_DIR = Path("generated")
SKELETONS_DIR.mkdir(parents=True, exist_ok=True)

_REL_NS  = "http://schemas.openxmlformats.org/package/2006/relationships"
_PML_NS  = "http://schemas.openxmlformats.org/presentationml/2006/main"
_CT_NS   = "http://schemas.openxmlformats.org/package/2006/content-types"
_SLIDE_REL_TYPE = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide"
)
_SLIDE_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.presentationml.slide+xml"
)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _rels_path_for(part_path: str) -> str:
    if "/" in part_path:
        d, f = part_path.rsplit("/", 1)
        return f"{d}/_rels/{f}.rels"
    return f"_rels/{part_path}.rels"


def _resolve(base: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    base_dir = base.rsplit("/", 1)[0] if "/" in base else ""
    return f"{base_dir}/{target}" if base_dir else target


def _next_rid(existing: set[str]) -> str:
    i = 1
    while f"rId{i}" in existing:
        i += 1
    return f"rId{i}"


def _read_xml(zf: zipfile.ZipFile, path: str) -> ET.Element:
    return ET.fromstring(zf.read(path))


def _read_rels(zf: zipfile.ZipFile, part_path: str) -> ET.Element:
    try:
        return _read_xml(zf, _rels_path_for(part_path))
    except KeyError:
        return ET.Element(f"{{{_REL_NS}}}Relationships")


def _collect_parts(
    zf: zipfile.ZipFile,
    part_path: str,
    out: dict[str, bytes],
    skip_rel_types: tuple[str, ...] = ("slideLayout", "slideMaster", "theme", "presProps"),
) -> None:
    """Recursively collect *part_path* + all embedded parts into *out*."""
    if part_path in out:
        return
    try:
        out[part_path] = zf.read(part_path)
    except KeyError:
        return

    rels_path = _rels_path_for(part_path)
    try:
        rels_bytes = zf.read(rels_path)
        out[rels_path] = rels_bytes
        rels_root = ET.fromstring(rels_bytes)
    except KeyError:
        return

    for rel in rels_root:
        if rel.get("TargetMode") == "External":
            continue
        if any(s in rel.get("Type", "") for s in skip_rel_types):
            continue
        _collect_parts(zf, _resolve(part_path, rel.get("Target", "")), out, skip_rel_types)


def _find_first_slide(zf: zipfile.ZipFile) -> tuple[str, str] | None:
    """Return (rId, slide_path) for the first slide, or None."""
    prs_root = _read_xml(zf, "ppt/presentation.xml")
    sldIdLst  = prs_root.find(f"{{{_PML_NS}}}sldIdLst")
    if sldIdLst is None or len(sldIdLst) == 0:
        return None
    first_rId = sldIdLst[0].get(
        "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    )
    prs_rels = _read_rels(zf, "ppt/presentation.xml")
    for rel in prs_rels:
        if rel.get("Id") == first_rId:
            return first_rId, _resolve("ppt/presentation.xml", rel.get("Target", ""))
    return None


def _rebuild_zip(src_path: Path, keep_names: set[str]) -> dict[str, bytes]:
    """Read all entries from *src_path*, skipping names not in *keep_names*."""
    kept: dict[str, bytes] = {}
    with zipfile.ZipFile(str(src_path), "r") as zf:
        for name in zf.namelist():
            if name in keep_names:
                kept[name] = zf.read(name)
    return kept


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_ppt(skeleton_hash: str, slide_names: list[str]) -> str:
    """Merge single-slide PPTX templates into one skeleton presentation.

    Args:
        skeleton_hash: SHA-256 hash — used as the output filename.
        slide_names:   Ordered list of template names (no .pptx extension).
                       Sub-folder names supported: e.g. "PPG/Front".

    Returns:
        Path to the generated skeleton PPTX (str).
    """
    if not slide_names:
        raise ValueError("slide_names must not be empty.")

    template_paths: list[Path] = []
    for name in slide_names:
        path = TEMPLATE_DIR / f"{name}.pptx"
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {path}")
        template_paths.append(path)

    final_path = SKELETONS_DIR / f"{skeleton_hash}.pptx"
    if final_path.exists():
        logger.info(f"[ppt_service] Already on disk: {final_path}")
        return str(final_path)

    logger.info(f"[ppt_service] Merging {len(template_paths)} templates → '{skeleton_hash[:10]}'")

    tmp_path = SKELETONS_DIR / f"{uuid.uuid4()}.pptx"
    shutil.copy(str(template_paths[0]), str(tmp_path))

    # -----------------------------------------------------------------------
    # Step 1 — open the base zip, read structural XMLs, strip the base slide
    # -----------------------------------------------------------------------
    with zipfile.ZipFile(str(tmp_path), "r") as base_zip:
        all_base_names = set(base_zip.namelist())

        prs_root      = _read_xml(base_zip, "ppt/presentation.xml")
        prs_rels_root = _read_rels(base_zip, "ppt/presentation.xml")
        ct_root       = _read_xml(base_zip, "[Content_Types].xml")

        base_slide_info = _find_first_slide(base_zip)

        # Names to drop (base slide file + its rels)
        drop_names: set[str] = set()
        if base_slide_info:
            _, base_slide_path = base_slide_info
            drop_names.add(base_slide_path)
            drop_names.add(_rels_path_for(base_slide_path))

        # Read everything except what we're dropping
        kept_entries: dict[str, bytes] = {}
        for name in all_base_names:
            if name not in drop_names and name not in (
                "ppt/presentation.xml",
                "ppt/_rels/presentation.xml.rels",
                "[Content_Types].xml",
            ):
                kept_entries[name] = base_zip.read(name)

    # Strip base slide from presentation.xml
    sldIdLst = prs_root.find(f"{{{_PML_NS}}}sldIdLst")
    if sldIdLst is None:
        sldIdLst = ET.SubElement(prs_root, f"{{{_PML_NS}}}sldIdLst")
    else:
        for el in list(sldIdLst):
            sldIdLst.remove(el)

    # Strip slide rels from presentation.xml.rels
    prs_rids: set[str] = {rel.get("Id", "") for rel in prs_rels_root}
    for rel in list(prs_rels_root):
        if rel.get("Type") == _SLIDE_REL_TYPE:
            prs_rels_root.remove(rel)
            prs_rids.discard(rel.get("Id", ""))

    # Strip slide Override entries from [Content_Types].xml
    for override in list(ct_root):
        part_name = override.get("PartName", "")
        if override.get("ContentType") == _SLIDE_CONTENT_TYPE:
            ct_root.remove(override)

    # -----------------------------------------------------------------------
    # Step 2 — for each template, collect its slide + parts and register them
    # -----------------------------------------------------------------------
    next_slide_id = 256
    new_parts: dict[str, bytes] = {}     # parts to add (slide XMLs, charts, images)
    new_rels:  dict[str, bytes] = {}     # rebuilt .rels for each new slide

    for idx, tpl_path in enumerate(template_paths):
        with zipfile.ZipFile(str(tpl_path), "r") as src:
            info = _find_first_slide(src)
            if info is None:
                logger.warning(f"[ppt_service] No slide in: {tpl_path.name}")
                continue
            _, slide_path = info

            parts: dict[str, bytes] = {}
            _collect_parts(src, slide_path, parts)

        prefix = f"sl{idx:04d}_"

        # Build path_map:  old_zip_path → new_zip_path  (skip .rels)
        path_map: dict[str, str] = {}
        for old in parts:
            if old.endswith(".rels"):
                continue
            d, f = (old.rsplit("/", 1) if "/" in old else ("", old))
            path_map[old] = f"{d}/{prefix}{f}" if d else f"{prefix}{f}"

        new_slide_path = path_map[slide_path]

        # Store new content parts
        for old, new in path_map.items():
            if new not in kept_entries and new not in new_parts:
                new_parts[new] = parts[old]

        # Rebuild slide's .rels
        old_rels_path = _rels_path_for(slide_path)
        old_rels = (
            ET.fromstring(parts[old_rels_path])
            if old_rels_path in parts
            else ET.Element(f"{{{_REL_NS}}}Relationships")
        )
        rebuilt_rels = ET.Element(f"{{{_REL_NS}}}Relationships")
        for rel in old_rels:
            rel_type    = rel.get("Type", "")
            target_mode = rel.get("TargetMode", "")
            old_target  = rel.get("Target", "")
            new_rel     = copy.deepcopy(rel)

            if target_mode == "External" or "slideLayout" in rel_type:
                rebuilt_rels.append(new_rel)
                continue

            resolved_old = _resolve(slide_path, old_target)
            resolved_new = path_map.get(resolved_old, resolved_old)

            # Make target relative to new slide's directory
            new_slide_dir = new_slide_path.rsplit("/", 1)[0] if "/" in new_slide_path else ""
            if new_slide_dir and resolved_new.startswith(new_slide_dir + "/"):
                new_target = resolved_new[len(new_slide_dir) + 1:]
            else:
                new_target = resolved_new

            new_rel.set("Target", new_target)
            rebuilt_rels.append(new_rel)

        new_rels_path = _rels_path_for(new_slide_path)
        new_rels[new_rels_path] = ET.tostring(rebuilt_rels, encoding="unicode").encode()

        # Register in presentation.xml.rels
        new_rid = _next_rid(prs_rids)
        prs_rids.add(new_rid)
        rel_el = ET.SubElement(prs_rels_root, f"{{{_REL_NS}}}Relationship")
        rel_el.set("Id", new_rid)
        rel_el.set("Type", _SLIDE_REL_TYPE)
        rel_target = new_slide_path[len("ppt/"):] if new_slide_path.startswith("ppt/") else new_slide_path
        rel_el.set("Target", rel_target)

        # Register in presentation.xml sldIdLst
        sld_el = ET.SubElement(sldIdLst, f"{{{_PML_NS}}}sldId")
        sld_el.set("id", str(next_slide_id))
        sld_el.set(
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id",
            new_rid,
        )
        next_slide_id += 1

        # Register slide in [Content_Types].xml
        override_el = ET.SubElement(ct_root, f"{{{_CT_NS}}}Override")
        override_el.set("PartName", f"/{new_slide_path}")
        override_el.set("ContentType", _SLIDE_CONTENT_TYPE)

    # -----------------------------------------------------------------------
    # Step 3 — write final zip from scratch (no duplicate names)
    # -----------------------------------------------------------------------
    with zipfile.ZipFile(str(tmp_path), "w", compression=zipfile.ZIP_DEFLATED) as out_zip:
        # Preserved base entries (theme, master, layouts, images, charts, …)
        for name, data in kept_entries.items():
            out_zip.writestr(name, data)

        # New slide parts
        for name, data in new_parts.items():
            out_zip.writestr(name, data)

        # New slide .rels
        for name, data in new_rels.items():
            out_zip.writestr(name, data)

        # Updated structural XMLs
        ET.register_namespace("", _CT_NS)
        out_zip.writestr(
            "[Content_Types].xml",
            ET.tostring(ct_root, encoding="unicode", xml_declaration=False).encode(),
        )
        out_zip.writestr(
            "ppt/presentation.xml",
            ET.tostring(prs_root, encoding="unicode").encode(),
        )
        out_zip.writestr(
            "ppt/_rels/presentation.xml.rels",
            ET.tostring(prs_rels_root, encoding="unicode").encode(),
        )

    tmp_path.rename(final_path)
    logger.info(f"[ppt_service] Skeleton saved: {final_path}")
    return str(final_path)
