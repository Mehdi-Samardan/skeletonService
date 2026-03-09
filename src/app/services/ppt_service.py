"""PPTX skeleton generation via GroupDocs Merger Cloud API."""

import os
import random
import shutil
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime as dt
from pathlib import Path

import groupdocs_conversion_cloud
import groupdocs_merger_cloud

from app.exceptions.custom_exceptions import MissingEnvironmentVariableError, PptxMergeError
from app.utils.logger import logger

TEMPLATE_DIR = Path("storage/templates")
SKELETONS_DIR = Path("generated")
SKELETONS_DIR.mkdir(parents=True, exist_ok=True)


def _init_groupdocs_api() -> tuple[
    groupdocs_conversion_cloud.FileApi, groupdocs_merger_cloud.DocumentApi
]:
    """Initialize GroupDocs API clients with credentials."""
    app_sid = os.getenv("GROUPDOCS_CLIENT_ID")
    app_key = os.getenv("GROUPDOCS_CLIENT_SECRET")
    if not app_sid or not app_key:
        raise MissingEnvironmentVariableError(
            "GROUPDOCS_CLIENT_ID and GROUPDOCS_CLIENT_SECRET environment variables must be set"
        )

    return (
        groupdocs_conversion_cloud.FileApi.from_keys(app_sid, app_key),
        groupdocs_merger_cloud.DocumentApi.from_keys(app_sid, app_key),
    )


def _upload_to_groupdocs(
    file_api: groupdocs_conversion_cloud.FileApi,
    local_path: str,
) -> str:
    """Upload a single file to GroupDocs cloud storage."""
    time.sleep(random.random() * 3)
    normalized_path = os.path.normpath(local_path)
    path_parts = normalized_path.split(os.sep)
    cloud_path = os.path.join(*path_parts[-3:])

    upload_request = groupdocs_conversion_cloud.UploadFileRequest(
        cloud_path, local_path, None
    )
    file_api.upload_file(upload_request, _request_timeout=180)

    return cloud_path


def _upload_templates_for_merging(
    file_api: groupdocs_conversion_cloud.FileApi,
    templates: list[str],
) -> list[groupdocs_merger_cloud.JoinItem]:
    """Upload all template files in parallel and build JoinItem list."""
    join_items = []

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [
            executor.submit(_upload_to_groupdocs, file_api, template)
            for template in templates
        ]

        for i, future in enumerate(futures):
            template_path = templates[i]
            try:
                cloud_path = future.result()
            except Exception as e:
                logger.error(f"[ppt_service] Failed to upload {template_path}: {e}")
                raise PptxMergeError(
                    f"Uploading {template_path} to GroupDocs failed: {e}"
                )

            join_item = groupdocs_merger_cloud.JoinItem()
            join_item.file_info = groupdocs_merger_cloud.FileInfo(
                cloud_path, storage_name=None
            )
            join_items.append(join_item)
            logger.debug(f"[ppt_service] Uploaded: {template_path} → {cloud_path}")

    return join_items


def _execute_merge_operation(
    document_api: groupdocs_merger_cloud.DocumentApi,
    join_items: list[groupdocs_merger_cloud.JoinItem],
) -> str:
    """Execute the server-side merge on GroupDocs."""
    options = groupdocs_merger_cloud.JoinOptions()
    options.join_items = join_items
    options.output_path = f"Output/{dt.now().strftime('%Y%m%d_%H%M%S')}.pptx"

    try:
        result = document_api.join(
            groupdocs_merger_cloud.JoinRequest(options), _request_timeout=600
        )
        return str(result.path)
    except groupdocs_merger_cloud.ApiException as e:
        raise PptxMergeError(
            f"Merging the powerpoints on GroupDocs failed: {e.message}"
        )


def _download_merged_presentation(
    file_api: groupdocs_conversion_cloud.FileApi,
    cloud_path: str,
    local_path: str,
) -> None:
    """Download the merged presentation from GroupDocs and save it locally."""
    try:
        download_request = groupdocs_merger_cloud.DownloadFileRequest(cloud_path, None)
        download_path = file_api.download_file(download_request, _request_timeout=180)
    except groupdocs_merger_cloud.ApiException as e:
        raise PptxMergeError(
            f"Downloading the merged presentation from GroupDocs failed: {e.message}"
        )

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    with open(local_path, "wb") as f:
        if not isinstance(download_path, str) or not os.path.exists(download_path):
            raise PptxMergeError(
                "The downloaded path from GroupDocs is not valid, or nothing was downloaded"
            )
        with open(download_path, "rb") as temp_f:
            shutil.copyfileobj(temp_f, f)


def generate_ppt(slide_names: list[str]) -> str:
    """Merge single-slide PPTX templates into one skeleton presentation."""
    if not slide_names:
        raise ValueError("slide_names must not be empty.")

    template_paths: list[str] = []
    for name in slide_names:
        path = TEMPLATE_DIR / f"{name}.pptx"
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {path}")
        template_paths.append(str(path))

    temp_path = str(SKELETONS_DIR / f"{uuid.uuid4()}.pptx")

    if len(template_paths) == 1:
        shutil.copy(template_paths[0], temp_path)
        logger.info(f"[ppt_service] Single template copied to temp: {temp_path}")
        return temp_path

    logger.info(f"[ppt_service] Merging {len(template_paths)} templates via GroupDocs")

    try:
        file_api, document_api = _init_groupdocs_api()
        join_items = _upload_templates_for_merging(file_api, template_paths)
        cloud_result_path = _execute_merge_operation(document_api, join_items)
        _download_merged_presentation(file_api, cloud_result_path, temp_path)
    except groupdocs_merger_cloud.ApiException as e:
        raise PptxMergeError(f"API request failed: {e.message}") from e

    logger.info(f"[ppt_service] Merged skeleton saved to temp: {temp_path}")
    return temp_path
