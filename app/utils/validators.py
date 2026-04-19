# -*- coding: utf-8 -*-
from typing import Set

from app.core.exceptions import FileTooLargeError, InvalidFileExtensionError


def extract_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[-1].lower()


def validate_extension(filename: str, allowed: Set[str]) -> None:
    ext = extract_extension(filename)
    if ext not in allowed:
        raise InvalidFileExtensionError(ext, allowed)


def validate_size(size_bytes: int, max_bytes: int, max_mb: int) -> None:
    if size_bytes > max_bytes:
        raise FileTooLargeError(max_mb)
