"""Non-destructive checks for image upload type and content validation."""

from __future__ import annotations

from io import BytesIO

from fastapi import HTTPException, UploadFile

try:
    from .app import upload_image
except ImportError:
    from app import upload_image


def expect_rejected(filename: str, content: bytes) -> None:
    upload = UploadFile(filename=filename, file=BytesIO(content))
    try:
        upload_image(upload)
    except HTTPException as error:
        if error.status_code != 400:
            raise AssertionError(f"expected 400, got {error.status_code}") from error
        return
    raise AssertionError(f"unsafe upload was accepted: {filename}")


def main() -> None:
    expect_rejected("script.svg", b'<svg onload="alert(1)"/>')
    expect_rejected("fake.jpg", b"this is not an image")
    print("Upload validation checks passed.")


if __name__ == "__main__":
    main()
