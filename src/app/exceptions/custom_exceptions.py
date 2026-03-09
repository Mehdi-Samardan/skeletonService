class SkeletonServiceError(Exception):
    """Base exception for all Skeleton Service errors."""

class LayoutNotFoundError(SkeletonServiceError):
    """Raised when a requested saved layout YAML does not exist."""

    def __init__(self, layout_name: str) -> None:
        super().__init__(f"Layout not found: '{layout_name}'")
        self.layout_name = layout_name

class TemplateNotFoundError(SkeletonServiceError):
    """Raised when a PPTX template file referenced by a layout does not exist."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)

class InvalidLayoutError(SkeletonServiceError):
    """Raised when a layout YAML is malformed or contains no slides."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)

class MissingEnvironmentVariableError(SkeletonServiceError):
    """Raised when a required environment variable is not set."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)

class PptxMergeError(SkeletonServiceError):
    """Raised when the GroupDocs merge or upload/download operation fails."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
