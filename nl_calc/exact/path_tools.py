"""
Path lexical analysis tools.

Provides deterministic path parsing without filesystem access.
Analyzes path components, extensions, hidden status, and traversal.
"""

from __future__ import annotations

import re
from typing import TypedDict

from .unicode_tools import detect_confusables


class PathAnalyzeResult(TypedDict):
    input: str
    style: str
    absolute: bool
    has_traversal: bool
    components: list[str]
    parent: str | None
    name: str | None
    stem: str | None
    suffix: str | None
    suffixes: list[str]
    hidden: bool
    normalized_lexical: str
    warnings: list[str]
    summary: str


class PathNormalizeResult(TypedDict):
    normalized: str
    is_absolute: bool
    components: list[str]
    warnings: list[str]


def _detect_windows_path(path: str) -> bool:
    """Detect if path uses Windows syntax."""
    if len(path) < 2:
        return False
    if path[1] == ":":
        return True
    if path[:2] == "\\\\":
        return True
    if "\\" in path:
        return True
    return False


def _split_posix_components(path: str) -> tuple[list[str], str | None]:
    """Split POSIX path into components and root.

    Returns (components, root) where root is "/" for absolute paths, None for relative.
    """
    if path == "":
        return [], None

    if path.startswith("/"):
        root = "/"
        rest = path[1:]
        if rest:
            parts = rest.split("/")
            components = [p for p in parts if p]
        else:
            components = []
    else:
        root = None
        parts = path.split("/")
        components = [p for p in parts if p]

    return components, root


def _split_windows_components(path: str) -> tuple[list[str], str | None]:
    """Split Windows path into components and root.

    Returns (components, root) where root is like "C:" or "\\\\server\\share", None for relative.
    """
    if path == "":
        return [], None

    if len(path) >= 2 and path[1] == ":":
        root = path[:2]
        rest = path[2:]
        if rest:
            parts = re.split(r"[/\\]", rest)
            components = [p for p in parts if p]
        else:
            components = []
        return components, root

    if path.startswith("\\\\"):
        parts = re.split(r"[/\\]", path)
        if len(parts) >= 4:
            root = "\\\\" + parts[1] + "\\" + parts[2]
            components = [p for p in parts[3:] if p]
        else:
            root = path
            components = []
        return components, root

    if "\\" in path:
        parts = re.split(r"[/\\]", path)
        components = [p for p in parts if p]
        root = None
        return components, root

    parts = path.split("/")
    components = [p for p in parts if p]
    root = None
    return components, root


def _get_suffixes(name: str) -> list[str]:
    """Extract all suffixes from a filename.

    For ".tar.gz" returns [".tar.gz", ".gz"]
    For ".txt" returns [".txt"]
    """
    if not name or name == ".":
        return []

    parts = name.split(".")
    if len(parts) <= 1:
        return []

    suffixes = []
    for i in range(1, len(parts)):
        suffix = "." + ".".join(parts[i:])
        suffixes.append(suffix)

    return suffixes


def path_analyze(path: str, style: str = "auto") -> PathAnalyzeResult:
    """Analyze path components, extensions, hidden status, and traversal.

    This is lexical analysis only. Does NOT call Path.exists, resolve,
    or any filesystem API.

    Args:
        path: Path string to analyze.
        style: "auto", "posix", or "windows". Default "auto" detects from path syntax.

    Returns:
        PathAnalyzeResult with detailed path information.
    """
    warnings: list[str] = []
    input_path = path

    if style == "auto":
        detected = _detect_windows_path(path)
        style = "windows" if detected else "posix"

    if style == "windows":
        raw_components, root = _split_windows_components(path)
        sep = "\\"
    else:
        raw_components, root = _split_posix_components(path)
        sep = "/"

    components = []
    normalized_parts = []

    for i, comp in enumerate(raw_components):
        if comp == ".":
            warnings.append(f"Redundant current directory segment at position {i}")
            components.append(comp)
            normalized_parts.append(comp)
        elif comp == "..":
            warnings.append(f"Parent traversal segment at position {i}")
            components.append(comp)
            normalized_parts.append(comp)
        else:
            components.append(comp)
            normalized_parts.append(comp)

    has_traversal = ".." in raw_components
    absolute = root is not None

    name = components[-1] if components else None

    if name:
        suffixes = _get_suffixes(name)
        suffix = suffixes[-1] if suffixes else None
        if suffixes:
            full_suffix = suffixes[0]
            stem = name[:-len(full_suffix)] if len(full_suffix) > 0 else name
        else:
            stem = name
    else:
        suffixes = []
        suffix = None
        stem = None

    if components:
        parent_parts = components[:-1]
        if parent_parts:
            if root:
                if style == "posix":
                    parent = sep + sep.join(parent_parts)
                else:
                    parent = root + sep + sep.join(parent_parts)
            else:
                parent = sep.join(parent_parts)
        else:
            parent = None
    else:
        parent = None

    hidden = False
    if name and name != "." and name != "..":
        hidden = name.startswith(".")

    normalized = sep.join(normalized_parts) if normalized_parts else ""
    if root and style == "posix":
        normalized = sep + normalized

    confusables = detect_confusables(path)
    if confusables:
        warnings.append(f"Path contains {len(confusables)} confusable character(s)")

    summary_parts = []
    if style != "auto":
        summary_parts.append(f"{style.upper()}")
    if absolute:
        summary_parts.append("absolute")
    else:
        summary_parts.append("relative")
    if hidden:
        summary_parts.append("hidden")
    if has_traversal:
        summary_parts.append("with traversal")
    if len(components) == 1:
        summary_parts.append(f"single component '{components[0]}'")
    elif components:
        summary_parts.append(f"{len(components)} components")
    if suffix:
        if len(suffixes) > 1:
            summary_parts.append(f"suffixes {suffixes}")
        else:
            summary_parts.append(f"suffix '{suffix}'")

    summary = ", ".join(summary_parts) if summary_parts else "empty path"

    return PathAnalyzeResult(
        input=input_path,
        style=style,
        absolute=absolute,
        has_traversal=has_traversal,
        components=components,
        parent=parent,
        name=name,
        stem=stem,
        suffix=suffix,
        suffixes=suffixes,
        hidden=hidden,
        normalized_lexical=normalized,
        warnings=warnings,
        summary=summary,
    )


def path_normalize(
    path: str,
    platform: str = "posix",
    collapse_dot_segments: bool = True,
    preserve_trailing_separator: bool = False,
) -> PathNormalizeResult:
    """Normalize a path by collapsing dot segments and resolving parent traversal.

    This is lexical normalization only. Does NOT call filesystem APIs.

    Args:
        path: Path string to normalize.
        platform: "posix" or "windows".
        collapse_dot_segments: If True, collapse . and .. segments.
        preserve_trailing_separator: If True, keep trailing separator.

    Returns:
        PathNormalizeResult with normalized path and metadata.
    """
    warnings: list[str] = []
    has_dot_dot = False
    has_dot = False
    had_trailing_separator = path.endswith("/") or path.endswith("\\")

    if platform not in ("posix", "windows"):
        platform = "posix"

    sep = "/" if platform == "posix" else "\\"

    components = []
    is_unc_track = platform == "windows" and (path.startswith("\\\\") or path.startswith("//"))
    for part in path.split(sep):
        if part == "":
            continue
        if part == ".":
            has_dot = True
            if collapse_dot_segments:
                warnings.append("Collapsing dot segment")
                continue
            else:
                components.append(part)
                continue
        elif part == "..":
            has_dot_dot = True
            if collapse_dot_segments:
                warnings.append("Collapsing dot-dot segment")
                if is_unc_track:
                    if components and components[-1] not in ("", ".."):
                        if components[-1] != "server" or len(components) == 1:
                            components.pop()
                        else:
                            components.append("..")
                    else:
                        components.append("..")
                elif components and components[-1] != "..":
                    components.pop()
                else:
                    components.append("..")
            else:
                components.append(part)
            continue
        elif is_unc_track and part in ("server", "share"):
            if len(components) >= 2:
                is_unc_track = False
            components.append(part)
        elif part not in ("", ".", ".."):
            components.append(part)

    if preserve_trailing_separator and had_trailing_separator and components:
        components.append("")

    normalized = sep.join(components) if components else ""

    if platform == "posix" and path.startswith("/") and not normalized.startswith("/"):
        normalized = "/" + normalized
    elif platform == "windows":
        if is_unc_track:
            normalized = "\\\\" + normalized
        elif len(path) >= 2 and path[1] == ":":
            normalized = path[:2] + normalized

    if not normalized:
        if platform == "posix" and path.startswith("/"):
            normalized = "/"
        elif platform == "windows" and is_unc_track:
            normalized = "\\\\"

    is_absolute = (
        (platform == "posix" and path.startswith("/")) or
        (platform == "windows" and (
            (len(path) >= 2 and path[1] == ":") or
            is_unc_track
        ))
    )

    if has_dot and not collapse_dot_segments:
        warnings.append("Path contains dot segments")
    if has_dot_dot and not collapse_dot_segments:
        warnings.append("Path contains parent traversal segments")

    return PathNormalizeResult(
        normalized=normalized,
        is_absolute=is_absolute,
        components=components,
        warnings=warnings,
    )