"""
MCP tools implementation for eggcalc.

Maps MCP tool names to their corresponding synthesis functions
and handles input validation and error wrapping.
"""

from __future__ import annotations

import json
import multiprocessing
import re
from typing import Any

from .. import EvaluationError, evaluate_raw
from ..evaluator import evaluate_with_timeout
from ..exact import (
    check_brackets as _check_brackets,
)
from ..exact import (
    glob_match as _glob_match,
)
from ..exact import (
    prompt_input_inspect as _prompt_input_inspect,
)
from ..exact import (
    identifier_inspect as _identifier_inspect,
)
from ..exact import (
    identifier_table_inspect as _identifier_table_inspect,
)
from ..exact import (
    json_compare as _json_compare,
)
from ..exact import (
    json_extract as _json_extract,
)
from ..exact import (
    json_shape as _json_shape,
)
from ..exact import (
    list_dedupe as _list_dedupe,
)
from ..exact import (
    list_sort as _list_sort,
)
from ..exact import (
    regex_finditer as _regex_finditer,
)
from ..exact import (
    regex_safety_check as _regex_safety_check,
)
from ..exact import (
    regex_test as _regex_test,
)
from ..exact import (
    text_position as _text_position,
)
from ..exact import (
    toml_shape as _toml_shape,
)
from ..exact import (
    validate_json as _validate_json,
)
from ..exact import (
    validate_schema_light as _validate_schema_light,
)
from ..exact import (
    validate_toml_text as _validate_toml_text,
)
from ..exact import (
    version_compare as _version_compare,
)
from ..exact.config import (
    dotenv_validate as _dotenv_validate,
)
from ..exact.config import (
    ini_validate as _ini_validate,
)
from ..exact.identifier import (
    identifier_analyze as _identifier_analyze,
)
from ..exact.markdown import (
    code_fence_extract as _code_fence_extract,
)
from ..exact.markdown import (
    markdown_structure as _markdown_structure,
)
from ..exact.path_tools import (
    path_analyze as _path_analyze,
)
from ..exact.path_tools import (
    path_compare as _path_compare,
)
from ..exact.path_tools import (
    path_normalize as _path_normalize,
)
from ..exact.path_tools import (
    path_scope_check as _path_scope_check,
)
from ..exact.primitives import (
    count_graphemes as _count_graphemes,
)
from ..exact.primitives import (
    truncate_to_grapheme as _truncate_to_grapheme,
)
from ..exact.shell import (
    argv_compare as _argv_compare,
)
from ..exact.shell import (
    shell_quote_join as _shell_quote_join,
)
from ..exact.shell import (
    shell_split as _shell_split,
)
from ..exact.synthesis import (
    count_chars as _count_chars,
)
from ..exact.synthesis import (
    explain_diff as _explain_diff,
)
from ..exact.synthesis import (
    inspect_text as _inspect_text,
)
from ..exact.synthesis import (
    line_range_compare as _line_range_compare,
)
from ..exact.synthesis import (
    line_range_extract as _line_range_extract,
)
from ..exact.synthesis import (
    list_compare as _list_compare,
)
from ..exact.synthesis import (
    measure_text as _measure_text,
)
from ..exact.synthesis import (
    text_equal as _text_equal,
)
from ..exact.synthesis import (
    text_replace_check as _text_replace_check,
)
from ..exact.synthesis import (
    text_window as _text_window,
)
from ..exact.transform import (
    escape_text as _escape_text,
)
from ..exact.transform import (
    text_fingerprint as _text_fingerprint,
)
from ..exact.transform import (
    text_hash as _text_hash,
)
from ..exact.transform import (
    text_transform as _text_transform,
)
from ..exact.transform import (
    unescape_text as _unescape_text,
)
from ..exact.unicode_policy import (
    canonicalize_text as _canonicalize_text,
)
from ..exact.unicode_policy import (
    unicode_policy_check as _unicode_policy_check,
)
from ..exact.cargo import (
    cargo_toml_inspect as _cargo_toml_inspect,
)
from ..exact.version import (
    check_version_constraint as _check_version_constraint,
)
from ..exact.validate import (
    json_canonicalize as _json_canonicalize,
)
from ..exact.validate import (
    json_query as _json_query,
)
from .schemas import TOOL_SCHEMAS, ErrorEnvelope

MAX_TEXT_LENGTH = 100_000
MAX_EXPRESSION_LENGTH = 10_000
MAX_LIST_ITEMS = 10_000
MAX_REGEX_SAMPLES = 100
REGEX_TIMEOUT_SECONDS = 5
MAX_CONCURRENT_SPAWNED = 4

# Module-level semaphore that caps how many worker processes can be in flight
# at once. multiprocessing.spawn is ~150-300 ms per call, and unbounded
# concurrent spawns can exhaust file descriptors and CPU. Acquire before any
# Process() is created in validate_regex and math_eval (via evaluate_with_timeout).
_SPAWN_SEMAPHORE = multiprocessing.BoundedSemaphore(MAX_CONCURRENT_SPAWNED)

def _build_physical_constants() -> dict[str, dict[str, Any]]:
    """Build PHYSICAL_CONSTANTS from Evaluator.CONSTANTS to prevent drift.

    Values are sourced from the evaluator's canonical definitions. Metadata
    (symbol, display name) is added here for MCP tool responses.
    """
    from ..evaluator import Evaluator

    _CONSTANT_META: dict[str, tuple[str, str]] = {
        # (symbol, display_name)
        "na": ("N_A", "Avogadro constant"),
        "avogadro": ("N_A", "Avogadro constant"),
        "avogadros": ("N_A", "Avogadro constant"),
        "r": ("R", "Gas constant"),
        "gasconstant": ("R", "Gas constant"),
        "idealgasconstant": ("R", "Gas constant"),
        "h": ("h", "Planck constant"),
        "planck": ("h", "Planck constant"),
        "planckconstant": ("h", "Planck constant"),
        "k": ("k_B", "Boltzmann constant"),
        "boltzmann": ("k_B", "Boltzmann constant"),
        "boltzmannconstant": ("k_B", "Boltzmann constant"),
        "c": ("c", "Speed of light in vacuum"),
        "c0": ("c", "Speed of light in vacuum"),
        "speedoflight": ("c", "Speed of light in vacuum"),
        "speedoflightvacuum": ("c", "Speed of light in vacuum"),
        "elementarycharge": ("e", "Elementary charge"),
        "echarge": ("e", "Elementary charge"),
        "f": ("F", "Faraday constant"),
        "faraday": ("F", "Faraday constant"),
        "faradayconstant": ("F", "Faraday constant"),
        "u": ("u", "Atomic mass unit"),
        "amu": ("u", "Atomic mass unit"),
        "atomicmassunit": ("u", "Atomic mass unit"),
        "epsilon0": ("ε₀", "Vacuum permittivity"),
        "vacuumpermittivity": ("ε₀", "Vacuum permittivity"),
        "mu0": ("μ₀", "Vacuum permeability"),
        "vacuumpermeability": ("μ₀", "Vacuum permeability"),
        "g": ("gₙ", "Standard gravity"),
        "standardgravity": ("gₙ", "Standard gravity"),
        "G": ("G", "Gravitational constant"),
        "gravitationalconstant": ("G", "Gravitational constant"),
        "rydberg": ("R∞", "Rydberg constant"),
        "rydbergconstant": ("R∞", "Rydberg constant"),
        "stefan": ("σ", "Stefan-Boltzmann constant"),
        "stefanboltzmann": ("σ", "Stefan-Boltzmann constant"),
        "planckbar": ("ℏ", "Reduced Planck constant"),
        "hbar": ("ℏ", "Reduced Planck constant"),
        "reducedplanck": ("ℏ", "Reduced Planck constant"),
        "me": ("mₑ", "Electron mass"),
        "electronmass": ("mₑ", "Electron mass"),
        "mp": ("mₚ", "Proton mass"),
        "protonmass": ("mₚ", "Proton mass"),
        "mn": ("mₙ", "Neutron mass"),
        "neutronmass": ("mₙ", "Neutron mass"),
        "re": ("rₑ", "Classical electron radius"),
        "electronradius": ("rₑ", "Classical electron radius"),
        "alpha": ("α", "Fine-structure constant"),
        "finestructure": ("α", "Fine-structure constant"),
        "wien": ("b", "Wien displacement constant"),
        "wienconstant": ("b", "Wien displacement constant"),
    }

    result: dict[str, dict[str, Any]] = {}
    for key, (symbol, display_name) in _CONSTANT_META.items():
        if key in Evaluator.CONSTANTS:
            result[key] = {
                "value": Evaluator.CONSTANTS[key],
                "symbol": symbol,
                "name": display_name,
            }
    return result


PHYSICAL_CONSTANTS = _build_physical_constants()


def _regex_test_worker(
    pattern: str,
    samples: list[str],
    flags: list[str] | None,
    ignore_case: bool,
    multiline: bool,
    dotall: bool,
    ascii: bool,
    result_queue: multiprocessing.Queue,
) -> None:
    """Run regex test in a child process. Must be top-level for pickling."""
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024, 256 * 1024 * 1024))
    except (ImportError, ValueError, OSError):
        # RLIMIT_AS may not be supported or enforced on all platforms (e.g., macOS).
        # On failure, we rely solely on the time-based timeout for protection.
        pass
    try:
        result = _regex_test(pattern, samples, flags, ignore_case, multiline, dotall, ascii)
        result_queue.put(("ok", result))
    except Exception as exc:
        result_queue.put(("error", f"{type(exc).__name__}: {exc}"))


def _sanitize_error(message: str) -> str:
    """Sanitize error messages by removing non-ASCII, file paths, and Python internals.

    Patterns are anchored to traceback-like contexts so unrelated prose
    containing the substrings "line 5" or "File" is preserved. Input is
    also capped at 8192 bytes to bound the cost of regex substitution on
    very large error messages.
    """
    text = message[:8192]
    text = text.encode("ascii", "replace").decode("ascii")
    text = re.sub(r'File\s+["\'][^"\']*["\'],\s*line\s+\d+', 'File "<redacted>", line <redacted>', text)
    text = re.sub(r'(?:in\s+)<[^>]+>', 'in <module>', text)
    text = re.sub(r'[A-Za-z_][\w.]*\s*=\s*["\'][^"\']*["\']', '<var>=<redacted>', text)
    return text


def _get_tool_tier(name: str) -> int:
    """Get the tier for a tool (1, 2, or 3)."""
    return TOOL_SCHEMAS.get(name, {}).get("tier", 3)


def _require_str(value: Any, name: str, tool: str) -> dict | None:
    """Validate that ``value`` is a non-overlong string.

    Returns a standard error envelope on failure, or None if valid.
    Used at the top of every public tool that takes a string to convert
    a TypeError from ``len()`` into a clean ``invalid_arguments`` response.
    """
    if not isinstance(value, str):
        return _error_response(
            "invalid_arguments",
            f"{name} must be a string, got {type(value).__name__}",
            tool=tool,
        )
    if len(value) > MAX_TEXT_LENGTH:
        return _error_response(
            "input_too_large",
            f"{name} length {len(value)} exceeds {MAX_TEXT_LENGTH}",
            tool=tool,
        )
    return None


def _error_response(
    error_type: str,
    error: str,
    hints: list[str] | None = None,
    tool: str | None = None,
) -> dict:
    """Create a standardized error envelope."""
    return ErrorEnvelope(
        ok=False,
        tool=tool,
        error_type=error_type,
        error=_sanitize_error(error),
        hints=[_sanitize_error(h) for h in (hints or [])],
        warnings=[],
    )


def _success_response(
    result: Any,
    tool: str | None = None,
    warnings: list[str] | None = None,
    limits_applied: list[str] | None = None,
    findings: list[dict] | None = None,
    machine_code: str | None = None,
    recommended_next_tool: str | list[str] | None = None,
) -> dict:
    """Create a standardized success envelope.

    The ``warnings`` and ``limits_applied`` keys are omitted when empty
    to keep successful responses compact. Callers that explicitly pass
    a list (even empty) get the key; ``None`` or omitted args omit it.
    """
    envelope: dict[str, Any] = {
        "ok": True,
        "tool": tool,
        "result": result,
    }
    if warnings is not None:
        envelope["warnings"] = warnings
    if limits_applied is not None:
        envelope["limits_applied"] = limits_applied
    if findings:
        envelope["findings"] = findings
    if machine_code is not None:
        envelope["machine_code"] = machine_code
    if recommended_next_tool is not None:
        envelope["recommended_next_tool"] = recommended_next_tool
    return envelope


def math_eval(expression: str) -> dict:
    """Evaluate a math expression.

    Args:
        expression: Math expression (e.g., "5 + 3", "30m + 100ft", "five plus three").

    Returns:
        Success response with result, or error envelope.
    """
    if not isinstance(expression, str):
        return _error_response("invalid_arguments", f"expression must be a string, got {type(expression).__name__}", tool="math_eval")
    if len(expression) > MAX_EXPRESSION_LENGTH:
        return _error_response("input_too_large", f"Expression exceeds maximum length of {MAX_EXPRESSION_LENGTH}", tool="math_eval")
    _SPAWN_SEMAPHORE.acquire()
    try:
        result = evaluate_with_timeout(expression, timeout=5.0)
        if hasattr(result, 'value') and hasattr(result, 'unit'):
            response_data: dict[str, Any] = {
                "value": str(result.value),
                "type": type(result.value).__name__,
            }
            if result.unit:
                response_data["unit"] = result.unit
                response_data["display"] = str(result)
        else:
            response_data = {"value": str(result), "type": type(result).__name__}
        return _success_response(response_data, tool="math_eval")
    except TimeoutError:
        return _error_response("timeout", "Expression evaluation timed out", ["Try a simpler expression"], tool="math_eval")
    except EvaluationError as e:
        return _error_response("evaluation_error", str(e), ["Check expression syntax"], tool="math_eval")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="math_eval")
    finally:
        _SPAWN_SEMAPHORE.release()


def unit_convert(value: float, from_unit: str, to_unit: str) -> dict:
    """Convert a value from one unit to another.

    Args:
        value: Numeric value to convert.
        from_unit: Source unit.
        to_unit: Target unit.

    Returns:
        Success response with conversion result.
    """
    import math
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return _error_response(
            "invalid_arguments",
            f"value must be a finite number, got {type(value).__name__}",
            tool="unit_convert",
        )
    value = float(value)
    if not math.isfinite(value):
        return _error_response(
            "invalid_arguments",
            f"Value must be a finite number, got {value}",
            tool="unit_convert",
        )
    try:
        from ..units import (
            convert_temperature,
            get_conversion_factor,
            get_unit_category,
            is_unit,
        )

        if not is_unit(from_unit):
            return _error_response("invalid_arguments", f"Unknown unit: {from_unit}", tool="unit_convert")
        if not is_unit(to_unit):
            return _error_response("invalid_arguments", f"Unknown unit: {to_unit}", tool="unit_convert")

        if get_unit_category(from_unit) == "temperature" and get_unit_category(to_unit) == "temperature":
            result = convert_temperature(value, from_unit, to_unit)
            return _success_response({
                "value": result,
                "from_unit": from_unit,
                "to_unit": to_unit,
                "factor": None,
            }, tool="unit_convert")

        from_cat = get_unit_category(from_unit)
        to_cat = get_unit_category(to_unit)
        if from_cat is not None and to_cat is not None and from_cat != to_cat:
            return _error_response(
                "conversion_error",
                f"Cannot convert between incompatible categories: {from_cat} ({from_unit}) -> {to_cat} ({to_unit})",
                tool="unit_convert",
            )

        factor = get_conversion_factor(from_unit, to_unit)
        result = value * factor

        return _success_response({
            "value": result,
            "from_unit": from_unit,
            "to_unit": to_unit,
            "factor": factor,
        }, tool="unit_convert")
    except ValueError as e:
        return _error_response("conversion_error", str(e), tool="unit_convert")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="unit_convert")


def unit_info(unit: str) -> dict:
    """Get information about a unit.

    Args:
        unit: Unit name or alias.

    Returns:
        Success response with unit information.
    """
    try:
        from ..units import UNIT_ALIASES, UNIT_BASE, UNIT_CATEGORIES

        if unit not in UNIT_ALIASES:
            return _error_response("invalid_arguments", f"Unknown unit: {unit}", tool="unit_info")

        canonical = UNIT_ALIASES[unit]
        category = None
        for cat, units in UNIT_CATEGORIES.items():
            if canonical in units:
                category = cat
                break

        if category is None:
            for base_unit, units_dict in UNIT_BASE.items():
                if canonical in units_dict:
                    category = base_unit
                    break

        return _success_response({
            "unit": unit,
            "canonical": canonical,
            "category": category,
            "is_valid": True,
        }, tool="unit_info")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="unit_info")


def constant_lookup(name: str) -> dict:
    """Look up a physical constant.

    Args:
        name: Constant name (e.g., "avogadro", "planck", "c").

    Returns:
        Success response with constant value and symbol.
    """
    try:
        if (err := _require_str(name, "name", "constant_lookup")) is not None:
            return err

        key = name.lower()
        if key not in PHYSICAL_CONSTANTS:
            return _error_response("invalid_arguments", f"Unknown constant: {name}", tool="constant_lookup")

        return _success_response({
            "name": name,
            "value": PHYSICAL_CONSTANTS[key]["value"],
            "symbol": PHYSICAL_CONSTANTS[key]["symbol"],
            "display_name": PHYSICAL_CONSTANTS[key]["name"],
        }, tool="constant_lookup")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="constant_lookup")


def text_measure(text: str, detail: str = "normal") -> dict:
    """Measure text properties.

    Args:
        text: Input string.
        detail: Detail level ("summary", "normal", "full").

    Returns:
        Success envelope with metrics, or error envelope.
    """
    if (err := _require_str(text, "text", "text_measure")) is not None:
        return err

    valid_details = {"summary", "normal", "full"}
    if detail not in valid_details:
        return _error_response(
            "invalid_arguments",
            f"Unsupported detail level: {detail}",
            [f"Use one of: {', '.join(valid_details)}"],
            tool="text_measure",
        )

    try:
        result = _measure_text(text)
        if detail == "summary":
            summary_result = {
                "codepoints": result["codepoints"],
                "graphemes": result["graphemes"],
                "words": result["words"],
                "bytes_utf8": result["bytes_utf8"],
                "ascii": result["ascii"],
                "non_ascii": result["non_ascii"],
                "warnings": result.get("warnings", []),
            }
        elif detail == "full":
            summary_result = dict(result)
        else:
            summary_result = dict(result)
        return _success_response(summary_result, tool="text_measure")
    except ValueError as e:
        return _error_response("invalid_arguments", str(e), tool="text_measure")


def text_equal(
    a: str,
    b: str,
    normalization: str = "raw",
    casefold: bool = False,
    trim: bool = False,
    ignore_newline_style: bool = False,
    ignore_trailing_whitespace: bool = False,
    ignore_final_newline: bool = False,
) -> dict:
    """Compare two strings for equality.

    Args:
        a: First string.
        b: Second string.
        normalization: "raw", "NFC", "NFD", "NFKC", or "NFKD".
        casefold: Use casefolded comparison.
        trim: Trim whitespace.
        ignore_newline_style: Normalize different newline styles before comparison.
        ignore_trailing_whitespace: Ignore trailing whitespace on each line.
        ignore_final_newline: Ignore trailing newline at end of strings.

    Returns:
        Success envelope with comparison result, or error envelope.
    """
    valid_normalizations = {"raw", "NFC", "NFD", "NFKC", "NFKD"}
    if normalization not in valid_normalizations:
        return _error_response(
            "invalid_arguments",
            f"Unsupported normalization form: {normalization}",
            [f"Use one of: {', '.join(valid_normalizations)}"],
            tool="text_equal",
        )

    if (err := _require_str(a, "a", "text_equal")) is not None:
        return err
    if (err := _require_str(b, "b", "text_equal")) is not None:
        return err

    try:
        result = _text_equal(a, b, normalization, casefold, trim,
                            ignore_newline_style, ignore_trailing_whitespace, ignore_final_newline)
        return _success_response(result, tool="text_equal")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="text_equal")


def text_diff_explain(
    a: str,
    b: str,
    max_diffs: int = 20,
    include_codepoints: bool = True,
    include_context: bool = True,
    detail: str = "normal",
) -> dict:
    """Explain differences between two strings.

    Args:
        a: First string.
        b: Second string.
        max_diffs: Maximum diff spans to return.
        include_codepoints: Include codepoint details.
        include_context: Include context notes.
        detail: "summary", "normal", or "full".

    Returns:
        Success envelope with diff explanation, or error envelope.
    """
    if (err := _require_str(a, "a", "text_diff_explain")) is not None:
        return err
    if (err := _require_str(b, "b", "text_diff_explain")) is not None:
        return err

    MAX_DIFFS = 10_000
    if max_diffs < 0:
        return _error_response(
            "invalid_arguments",
            f"max_diffs must be non-negative, got {max_diffs}",
            tool="text_diff_explain",
        )
    if max_diffs > MAX_DIFFS:
        return _error_response(
            "invalid_arguments",
            f"max_diffs {max_diffs} exceeds {MAX_DIFFS}",
            tool="text_diff_explain",
        )

    valid_details = {"summary", "normal", "full"}
    if detail not in valid_details:
        return _error_response(
            "invalid_arguments",
            f"Unsupported detail level: {detail}",
            [f"Use one of: {', '.join(valid_details)}"],
            tool="text_diff_explain",
        )

    try:
        result = _explain_diff(a, b, max_diffs, include_codepoints, include_context, detail)
        return _success_response(result, tool="text_diff_explain")
    except ValueError as e:
        return _error_response("invalid_arguments", str(e), tool="text_diff_explain")


def text_inspect(
    text: str,
    include_codepoints: bool = True,
    include_confusables: bool = True,
    detail: str = "normal",
    normalize: str = "none",
    compare_normalized: bool = False,
) -> dict:
    """Inspect text for Unicode signals and hidden characters.

    Args::
        text: Input string.
        include_codepoints: Include codepoint details in invisibles.
        include_confusables: Check for confusables.
        detail: "summary", "normal", or "full".
        normalize: Normalization form ("none", "NFC", "NFD", "NFKC", "NFKD").
        compare_normalized: Report both original and normalized analysis.

    Returns:
        Success envelope with inspection result, or error envelope.
    """
    if (err := _require_str(text, "text", "text_inspect")) is not None:
        return err

    valid_details = {"summary", "normal", "full"}
    if detail not in valid_details:
        return _error_response(
            "invalid_arguments",
            f"Unsupported detail level: {detail}",
            [f"Use one of: {', '.join(valid_details)}"],
            tool="text_inspect",
        )

    valid_normalizations = {"none", "NFC", "NFD", "NFKC", "NFKD"}
    if normalize not in valid_normalizations:
        return _error_response(
            "invalid_arguments",
            f"Unsupported normalization form: {normalize}",
            [f"Use one of: {', '.join(valid_normalizations)}"],
            tool="text_inspect",
        )

    try:
        result = _inspect_text(text, include_codepoints, include_confusables, detail, normalize, compare_normalized)

        findings: list[dict] = []
        for inv in result.get("invisibles", []):
            findings.append({
                "code": "INVISIBLE_CHAR",
                "severity": "warn",
                "message": f"Invisible character: {inv.get('name', 'unknown')} at index {inv.get('index', '?')}",
                "span": {"char_start": inv.get("index", 0), "char_end": inv.get("index", 0) + 1},
                "details": {"codepoint": inv.get("codepoint"), "category": inv.get("category")},
            })
        for conf in result.get("confusables", []):
            findings.append({
                "code": "CONFUSABLE_CHAR",
                "severity": "warn",
                "message": f"Confusable character at index {conf.get('index', '?')}",
                "span": {"char_start": conf.get("index", 0), "char_end": conf.get("index", 0) + 1},
                "details": {"original": conf.get("original"), "confusable": conf.get("confusable")},
            })
        for bidi in result.get("bidi_controls", []):
            findings.append({
                "code": "BIDI_CONTROL",
                "severity": "warn",
                "message": f"Bidirectional control character: {bidi.get('name', 'unknown')} at index {bidi.get('index', '?')}",
                "span": {"char_start": bidi.get("index", 0), "char_end": bidi.get("index", 0) + 1},
                "details": {"codepoint": bidi.get("codepoint")},
            })

        machine_code: str | None = None
        if findings:
            codes = {f["code"] for f in findings}
            if "CONFUSABLE_CHAR" in codes:
                machine_code = "CONFUSABLES_DETECTED"
            elif "BIDI_CONTROL" in codes:
                machine_code = "BIDI_DETECTED"
            elif "INVISIBLE_CHAR" in codes:
                machine_code = "INVISIBLES_DETECTED"

        return _success_response(result, tool="text_inspect", findings=findings or None, machine_code=machine_code)
    except ValueError as e:
        return _error_response("invalid_arguments", str(e), tool="text_inspect")


def text_count(
    text: str,
    target: str | None = None,
    normalization: str = "raw",
    count_mode: str = "codepoint",
) -> dict:
    """Count character occurrences or return frequency table.

    Args:
        text: Input string.
        target: Single character to count (None for frequency table).
        normalization: "raw", "NFC", or "NFKC".
        count_mode: "codepoint", "grapheme", "byte", or "substring".

    Returns:
        Success envelope with count result, or error envelope.
    """
    if (err := _require_str(text, "text", "text_count")) is not None:
        return err

    MAX_TARGET_LENGTH = 1000
    if target is not None:
        if not isinstance(target, str):
            return _error_response(
                "invalid_arguments",
                f"target must be a string, got {type(target).__name__}",
                tool="text_count",
            )
        if len(target) > MAX_TARGET_LENGTH:
            return _error_response(
                "input_too_large",
                f"target length {len(target)} exceeds {MAX_TARGET_LENGTH}",
                tool="text_count",
            )
        if count_mode != "substring":
            if count_mode == "byte" and len(target.encode("utf-8")) != 1:
                return _error_response(
                    "invalid_arguments",
                    "target must be a single byte for count_mode='byte'",
                    ["Provide a single-byte target"],
                    tool="text_count",
                )
            elif count_mode == "grapheme" and _count_graphemes(target) != 1:
                return _error_response(
                    "invalid_arguments",
                    "target must be a single grapheme for count_mode='grapheme'",
                    ["Provide a single-grapheme target"],
                    tool="text_count",
                )
            elif count_mode == "codepoint" and len(target) != 1:
                return _error_response(
                    "invalid_arguments",
                    "target must be a single codepoint for count_mode='codepoint'",
                    ["Provide a single-codepoint target"],
                    tool="text_count",
                )

    valid_normalizations = {"raw", "NFC", "NFKC"}
    if normalization not in valid_normalizations:
        return _error_response(
            "invalid_arguments",
            f"Unsupported normalization form: {normalization}",
            [f"Use one of: {', '.join(valid_normalizations)}"],
            tool="text_count",
        )

    valid_modes = {"codepoint", "grapheme", "byte", "substring"}
    if count_mode not in valid_modes:
        return _error_response(
            "invalid_arguments",
            f"Unsupported count_mode: {count_mode}",
            [f"Use one of: {', '.join(valid_modes)}"],
            tool="text_count",
        )

    try:
        result = _count_chars(text, target, normalization, count_mode)
        return _success_response(result, tool="text_count")
    except ValueError as e:
        return _error_response("invalid_arguments", str(e), tool="text_count")


def validate_brackets(text: str, pairs: dict[str, str] | None = None) -> dict:
    """Check bracket balance.

    Args:
        text: Input string.
        pairs: Bracket pair mapping (default: () [] {} <>).

    Returns:
        Success envelope with bracket check result, or error envelope.
    """
    if (err := _require_str(text, "text", "validate_brackets")) is not None:
        return err

    if pairs is not None and not isinstance(pairs, dict):
        return _error_response(
            "invalid_arguments",
            f"pairs must be a dict or None, got {type(pairs).__name__}",
            tool="validate_brackets",
        )

    try:
        result = _check_brackets(text, pairs)
        return _success_response(result, tool="validate_brackets")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="validate_brackets")


def validate_json(text: str) -> dict:
    """Validate JSON string.

    Args:
        text: Input string.

    Returns:
        Success envelope with validation result, or error envelope.
    """
    if (err := _require_str(text, "text", "validate_json")) is not None:
        return err

    try:
        result = _validate_json(text)

        findings: list[dict] = []
        if not result.get("valid", True):
            span: dict = {}
            if result.get("line") is not None:
                span["line"] = result["line"]
            if result.get("column") is not None:
                span["column"] = result["column"]
            findings.append({
                "code": "JSON_PARSE_ERROR",
                "severity": "error",
                "message": result.get("error", "Invalid JSON"),
                "span": span or None,
                "details": {"position": result.get("position")},
            })

        machine_code: str | None = None
        if not result.get("valid", True):
            machine_code = "JSON_INVALID"

        return _success_response(result, tool="validate_json", findings=findings or None, machine_code=machine_code)
    except Exception as e:
        return _error_response("internal_error", str(e), tool="validate_json")


def validate_toml(text: str, detail: str = "normal") -> dict:
    """Validate TOML string.

    Args:
        text: Input string.
        detail: Detail level ("summary", "normal", "full").

    Returns:
        Success envelope with validation result, or error envelope.
    """
    if (err := _require_str(text, "text", "validate_toml")) is not None:
        return err

    valid_details = {"summary", "normal", "full"}
    if detail not in valid_details:
        return _error_response(
            "invalid_arguments",
            f"Unsupported detail level: {detail}",
            [f"Use one of: {', '.join(valid_details)}"],
            tool="validate_toml",
        )

    try:
        result = _validate_toml_text(text)

        if detail == "summary":
            result = {
                "valid": result["valid"],
                "error": result["error"],
            }
        elif detail == "full":
            pass

        return _success_response(result, tool="validate_toml")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="validate_toml")


def json_compare(
    a: str,
    b: str,
    ignore_object_order: bool = True,
    ignore_array_order: bool = False,
    numeric_string_equivalence: bool = False,
    casefold_keys: bool = False,
    treat_missing_null_as_equal: bool = False,
    max_diffs: int = 50,
    detail: str = "normal",
) -> dict:
    """Compare two JSON documents semantically.

    Args:
        a: First JSON document.
        b: Second JSON document.
        ignore_object_order: Sort object keys for comparison.
        ignore_array_order: Sort arrays if all items are serializable.
        numeric_string_equivalence: Treat numeric strings as numbers.
        casefold_keys: Casefold object keys before comparison.
        treat_missing_null_as_equal: Treat missing and null as equal.
        max_diffs: Maximum number of differences to report.
        detail: Detail level ("summary", "normal", "full").

    Returns:
        Success envelope with comparison result, or error envelope.
    """
    if (err := _require_str(a, "a", "json_compare")) is not None:
        return err
    if (err := _require_str(b, "b", "json_compare")) is not None:
        return err

    MAX_DIFFS = 10_000
    if max_diffs < 0:
        return _error_response(
            "invalid_arguments",
            f"max_diffs must be non-negative, got {max_diffs}",
            tool="json_compare",
        )
    if max_diffs > MAX_DIFFS:
        return _error_response(
            "invalid_arguments",
            f"max_diffs {max_diffs} exceeds {MAX_DIFFS}",
            tool="json_compare",
        )

    valid_details = {"summary", "normal", "full"}
    if detail not in valid_details:
        return _error_response(
            "invalid_arguments",
            f"Unsupported detail level: {detail}",
            [f"Use one of: {', '.join(valid_details)}"],
            tool="json_compare",
        )

    try:
        result = _json_compare(a, b, ignore_object_order, ignore_array_order,
                              numeric_string_equivalence, casefold_keys,
                              treat_missing_null_as_equal, max_diffs)

        if detail == "summary":
            result = {
                "equal": result["equal"],
                "valid_json_a": result["valid_json_a"],
                "valid_json_b": result["valid_json_b"],
                "diff_count": result["diff_count"],
                "summary": result["summary"],
            }

        return _success_response(result, tool="json_compare")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="json_compare")


_VALID_TRANSFORM_OPERATIONS = {
    "normalize_nfc",
    "normalize_nfd",
    "normalize_nfkc",
    "normalize_nfkd",
    "casefold",
    "trim",
    "trim_trailing_whitespace",
    "normalize_newlines_lf",
    "ensure_final_newline",
    "strip_final_newline",
    "remove_zero_width",
    "remove_bidi_controls",
    "visible_repr",
}


def validate_regex(
    pattern: str,
    samples: list[str],
    flags: list[str] | None = None,
    ignore_case: bool = False,
    multiline: bool = False,
    dotall: bool = False,
    ascii: bool = False,
) -> dict:
    """Test regex pattern against samples.

    Args:
        pattern: Regular expression pattern.
        samples: List of strings to test.
        flags: List of flag names (IGNORECASE, MULTILINE, etc.).
        ignore_case: Use IGNORECASE flag.
        multiline: Use MULTILINE flag.
        dotall: Use DOTALL flag.
        ascii: Use ASCII flag.

    Returns:
        Success envelope with regex test results, or error envelope.
    """
    if not isinstance(pattern, str):
        return _error_response(
            "invalid_arguments",
            f"pattern must be a string, got {type(pattern).__name__}",
            tool="validate_regex",
        )
    if not isinstance(samples, list):
        return _error_response(
            "invalid_arguments",
            f"samples must be a list, got {type(samples).__name__}",
            tool="validate_regex",
        )

    if len(samples) > MAX_REGEX_SAMPLES:
        return _error_response(
            "input_too_large",
            f"Number of samples {len(samples)} exceeds MAX_REGEX_SAMPLES {MAX_REGEX_SAMPLES}",
            [f"Maximum {MAX_REGEX_SAMPLES} samples allowed"],
            tool="validate_regex",
        )

    safety = _regex_safety_check(pattern)
    if safety.get("risk") in ("high", "medium"):
        return _error_response(
            "unsafe_pattern",
            f"Pattern has {safety.get('risk', 'unknown')} risk of catastrophic backtracking",
            [
                "Try a simpler pattern or break it into smaller parts",
                "Use the regex_safety_check tool for detailed analysis and suggestions",
            ],
            tool="validate_regex",
        )

    ctx = multiprocessing.get_context("spawn")
    queue: multiprocessing.Queue = ctx.Queue()
    proc: multiprocessing.Process | None = None
    released = False
    try:
        _SPAWN_SEMAPHORE.acquire()
        try:
            proc = ctx.Process(
                target=_regex_test_worker,
                args=(pattern, samples, flags, ignore_case, multiline, dotall, ascii, queue),
            )
            proc.start()
        except BaseException:
            released = True
            _SPAWN_SEMAPHORE.release()
            raise

        try:
            status, value = queue.get(timeout=REGEX_TIMEOUT_SECONDS)
        except Exception:
            return _error_response(
                "timeout",
                f"Regex evaluation timed out after {REGEX_TIMEOUT_SECONDS} seconds",
                ["Try a simpler pattern or fewer samples"],
                tool="validate_regex",
            )
        finally:
            try:
                queue.close()
            except Exception:
                pass
            try:
                queue.join_thread()
            except Exception:
                pass
            if proc is not None:
                if proc.is_alive():
                    proc.terminate()
                    proc.join(timeout=2)
                if proc.is_alive():
                    proc.kill()
                    proc.join(timeout=1)
                try:
                    proc.close()
                except Exception:
                    pass

        if status == "error":
            return _error_response("internal_error", value, tool="validate_regex")
        return _success_response(value, tool="validate_regex")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="validate_regex")
    finally:
        if not released:
            _SPAWN_SEMAPHORE.release()


def json_extract(
    text: str,
    pointer: str = "",
    detail: str = "normal",
    max_output_chars: int = 4000,
) -> dict:
    """Extract a value from JSON using RFC 6901 JSON Pointer.

    Args:
        text: JSON document string.
        pointer: JSON Pointer path (e.g., "/foo/bar/0").
        detail: Detail level ("summary", "normal", "full").
        max_output_chars: Maximum output characters.

    Returns:
        Success envelope with extraction result, or error envelope.
    """
    if (err := _require_str(text, "text", "json_extract")) is not None:
        return err

    if not isinstance(max_output_chars, int) or isinstance(max_output_chars, bool):
        return _error_response(
            "invalid_arguments",
            f"max_output_chars must be a non-negative integer, got {type(max_output_chars).__name__}",
            tool="json_extract",
        )
    if max_output_chars < 0:
        return _error_response(
            "invalid_arguments",
            f"max_output_chars must be non-negative, got {max_output_chars}",
            tool="json_extract",
        )
    if max_output_chars > MAX_TEXT_LENGTH:
        return _error_response(
            "invalid_arguments",
            f"max_output_chars {max_output_chars} exceeds {MAX_TEXT_LENGTH}",
            tool="json_extract",
        )

    valid_details = {"summary", "normal", "full"}
    if detail not in valid_details:
        return _error_response(
            "invalid_arguments",
            f"Unsupported detail level: {detail}",
            [f"Use one of: {', '.join(valid_details)}"],
            tool="json_extract",
        )

    try:
        result = _json_extract(text, pointer, max_output_chars)

        if detail == "summary":
            return _success_response({
                "valid_json": result["valid_json"],
                "found": result["found"],
                "summary": result["summary"],
            }, tool="json_extract")
        elif detail == "normal":
            return _success_response(result, tool="json_extract")
        else:
            return _success_response(result, tool="json_extract")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="json_extract")


def json_shape(text: str, max_depth: int = 4, max_keys: int = 100, max_array_items: int = 5) -> dict:
    """Analyze the structure of a JSON document.

    Args:
        text: JSON document string.
        max_depth: Maximum depth for nested structure (default 4).
        max_keys: Maximum keys to show per object (default 100).
        max_array_items: Maximum array item previews (default 5).

    Returns:
        Success envelope with shape result, or error envelope.
    """
    if (err := _require_str(text, "text", "json_shape")) is not None:
        return err

    if max_depth < 1:
        return _error_response(
            "invalid_arguments",
            f"max_depth must be at least 1, got {max_depth}",
            ["Set max_depth to 1 or higher"],
            tool="json_shape",
        )

    if max_keys < 1:
        return _error_response(
            "invalid_arguments",
            f"max_keys must be at least 1, got {max_keys}",
            ["Set max_keys to 1 or higher"],
            tool="json_shape",
        )

    if max_array_items < 1:
        return _error_response(
            "invalid_arguments",
            f"max_array_items must be at least 1, got {max_array_items}",
            ["Set max_array_items to 1 or higher"],
            tool="json_shape",
        )

    MAX_SHAPE_DEPTH = 32
    MAX_SHAPE_KEYS = 10_000
    MAX_SHAPE_ARRAY_ITEMS = 10_000
    if max_depth > MAX_SHAPE_DEPTH:
        return _error_response(
            "invalid_arguments",
            f"max_depth {max_depth} exceeds {MAX_SHAPE_DEPTH}",
            tool="json_shape",
        )
    if max_keys > MAX_SHAPE_KEYS:
        return _error_response(
            "invalid_arguments",
            f"max_keys {max_keys} exceeds {MAX_SHAPE_KEYS}",
            tool="json_shape",
        )
    if max_array_items > MAX_SHAPE_ARRAY_ITEMS:
        return _error_response(
            "invalid_arguments",
            f"max_array_items {max_array_items} exceeds {MAX_SHAPE_ARRAY_ITEMS}",
            tool="json_shape",
        )

    try:
        result = _json_shape(text, max_depth, max_keys, max_array_items)
        return _success_response(result, tool="json_shape")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="json_shape")


MAX_TEXT_LENGTH_REGEX = 100_000
MAX_PATTERN_LENGTH_REGEX = 1000
MAX_MATCHES_REGEX = 100


def regex_finditer(
    pattern: str,
    text: str,
    flags: list[str] | None = None,
    max_matches: int = MAX_MATCHES_REGEX,
    include_line_column: bool = True,
    include_groups: bool = True,
) -> dict:
    """Find all regex matches in text with positions.

    Args:
        pattern: Regular expression pattern.
        text: Input string to search.
        flags: List of flag names (IGNORECASE, MULTILINE, DOTALL, etc.).
        max_matches: Maximum number of matches to return (default 100).
        include_line_column: Include line and column info (default True).
        include_groups: Include capture groups (default True).

    Returns:
        Success envelope with matches result, or error envelope.
    """
    if not isinstance(text, str):
        return _error_response(
            "invalid_arguments",
            f"text must be a string, got {type(text).__name__}",
            tool="regex_finditer",
        )
    if not isinstance(pattern, str):
        return _error_response(
            "invalid_arguments",
            f"pattern must be a string, got {type(pattern).__name__}",
            tool="regex_finditer",
        )

    if len(text) > MAX_TEXT_LENGTH_REGEX:
        return _error_response(
            "input_too_large",
            f"Text length {len(text)} exceeds MAX_TEXT_LENGTH_REGEX {MAX_TEXT_LENGTH_REGEX}",
            [f"Maximum input length is {MAX_TEXT_LENGTH_REGEX} characters"],
            tool="regex_finditer",
        )

    if len(pattern) > MAX_PATTERN_LENGTH_REGEX:
        return _error_response(
            "input_too_large",
            f"Pattern length {len(pattern)} exceeds MAX_PATTERN_LENGTH_REGEX {MAX_PATTERN_LENGTH_REGEX}",
            [f"Maximum pattern length is {MAX_PATTERN_LENGTH_REGEX} characters"],
            tool="regex_finditer",
        )

    if max_matches < 1:
        return _error_response(
            "invalid_arguments",
            f"max_matches must be at least 1, got {max_matches}",
            ["Set max_matches to 1 or higher"],
            tool="regex_finditer",
        )

    safety = _regex_safety_check(pattern)
    if safety.get("risk") in ("high", "medium"):
        return _error_response(
            "unsafe_pattern",
            f"Pattern has {safety.get('risk', 'unknown')} risk of catastrophic backtracking",
            [
                "Try a simpler pattern or break it into smaller parts",
                "Use the regex_safety_check tool for detailed analysis and suggestions",
            ],
            tool="regex_finditer",
        )

    try:
        result = _regex_finditer(pattern, text, flags, max_matches, include_line_column, include_groups)
        return _success_response(result, tool="regex_finditer")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="regex_finditer")


def regex_safety_check(pattern: str) -> dict:
    """Check regex pattern for potential catastrophic backtracking risks.

    Args:
        pattern: Regular expression pattern to check.

    Returns:
        Success envelope with safety check result, or error envelope.
    """
    if len(pattern) > MAX_PATTERN_LENGTH_REGEX:
        return _error_response(
            "input_too_large",
            f"Pattern length {len(pattern)} exceeds MAX_PATTERN_LENGTH_REGEX {MAX_PATTERN_LENGTH_REGEX}",
            [f"Maximum pattern length is {MAX_PATTERN_LENGTH_REGEX} characters"],
            tool="regex_safety_check",
        )

    try:
        result = _regex_safety_check(pattern)

        findings: list[dict] = []
        for risk in result.get("findings", []):
            findings.append({
                "code": risk.get("kind", "UNKNOWN_RISK").upper(),
                "severity": risk.get("severity", "warn"),
                "message": risk.get("message", risk.get("kind", "Unknown risk")),
                "details": {"pattern_length": result.get("pattern_length", len(pattern))},
            })

        machine_code: str | None = None
        if result.get("risk") in ("medium", "high"):
            machine_code = "REGEX_UNSAFE"

        return _success_response(result, tool="regex_safety_check", findings=findings or None, machine_code=machine_code)
    except Exception as e:
        return _error_response("internal_error", str(e), tool="regex_safety_check")


def validate_schema_light(text: str, schema: dict, detail: str = "normal") -> dict:
    """Validate JSON against a simple schema format.

    Args:
        text: JSON document string to validate.
        schema: Schema to validate against.
        detail: Detail level ("summary", "normal", "full").

    Returns:
        Success envelope with validation result, or error envelope.
    """
    if (err := _require_str(text, "text", "validate_schema_light")) is not None:
        return err

    MAX_SCHEMA_LENGTH = 100_000
    if not isinstance(schema, dict):
        return _error_response(
            "invalid_arguments",
            f"schema must be a dict, got {type(schema).__name__}",
            tool="validate_schema_light",
        )
    try:
        schema_size = len(json.dumps(schema))
    except (TypeError, ValueError) as e:
        return _error_response(
            "invalid_arguments",
            f"schema is not JSON-serializable: {e}",
            tool="validate_schema_light",
        )
    if schema_size > MAX_SCHEMA_LENGTH:
        return _error_response(
            "input_too_large",
            f"schema length {schema_size} exceeds {MAX_SCHEMA_LENGTH}",
            tool="validate_schema_light",
        )

    valid_details = {"summary", "normal", "full"}
    if detail not in valid_details:
        return _error_response(
            "invalid_arguments",
            f"Unsupported detail level: {detail}",
            [f"Use one of: {', '.join(valid_details)}"],
            tool="validate_schema_light",
        )

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        return _error_response(
            "invalid_arguments",
            f"Invalid JSON: {e.msg}",
            ["Provide valid JSON"],
            tool="validate_schema_light",
        )

    try:
        result = _validate_schema_light(parsed, schema)

        if detail == "summary":
            return _success_response({
                "valid": result["valid"],
                "summary": result["summary"],
            }, tool="validate_schema_light")
        else:
            return _success_response(result, tool="validate_schema_light")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="validate_schema_light")


def list_compare(
    a: list[str],
    b: list[str],
    mode: str = "set",
    casefold: bool = False,
    normalization: str = "NFC",
    trim: bool = False,
    include_near_matches: bool = False,
    near_match_threshold: int = 2,
    ignore_order: bool | None = None,
    treat_as_multiset: bool | None = None,
) -> dict:
    """Compare two lists.

    Args:
        a: First list.
        b: Second list.
        mode: Comparison mode - "ordered", "set", or "multiset".
        casefold: Casefold elements before comparison.
        normalization: Unicode normalization form.
        trim: Trim whitespace from each element.
        include_near_matches: Include near matches (fuzzy).
        near_match_threshold: Maximum edit distance for near matches.
        ignore_order: Legacy, use mode="set" or mode="multiset" instead.
        treat_as_multiset: Legacy, use mode="multiset" instead.

    Returns:
        Success envelope with comparison result, or error envelope.
    """
    if not isinstance(a, list) or not isinstance(b, list):
        return _error_response(
            "invalid_arguments",
            f"a and b must be lists, got {type(a).__name__} and {type(b).__name__}",
            tool="list_compare",
        )

    if len(a) > MAX_LIST_ITEMS or len(b) > MAX_LIST_ITEMS:
        return _error_response(
            "input_too_large",
            f"List length exceeds MAX_LIST_ITEMS {MAX_LIST_ITEMS}",
            [f"Maximum {MAX_LIST_ITEMS} items per list"],
            tool="list_compare",
        )

    total_chars = sum(len(s) for s in a) + sum(len(s) for s in b)
    if total_chars > MAX_TEXT_LENGTH * 2:
        return _error_response(
            "input_too_large",
            f"Total string length {total_chars} exceeds maximum",
            [f"Maximum combined string length is {MAX_TEXT_LENGTH * 2} characters"],
            tool="list_compare",
        )

    valid_modes = {"ordered", "set", "multiset"}
    if mode not in valid_modes:
        return _error_response(
            "invalid_arguments",
            f"Unsupported mode: {mode}",
            [f"Use one of: {', '.join(valid_modes)}"],
            tool="list_compare",
        )

    valid_normalizations = {"raw", "NFC", "NFD", "NFKC", "NFKD"}
    if normalization not in valid_normalizations:
        return _error_response(
            "invalid_arguments",
            f"Unsupported normalization form: {normalization}",
            [f"Use one of: {', '.join(valid_normalizations)}"],
            tool="list_compare",
        )

    if near_match_threshold < 0:
        return _error_response(
            "invalid_arguments",
            f"near_match_threshold must be non-negative, got {near_match_threshold}",
            ["Set near_match_threshold to 0 or higher"],
            tool="list_compare",
        )

    treat_as_multiset_val = treat_as_multiset if treat_as_multiset is not None else (mode == "multiset")
    ignore_order_val = ignore_order if ignore_order is not None else (mode != "ordered")

    try:
        raw_result = _list_compare(
            a, b, ignore_order_val, casefold, normalization, trim,
            treat_as_multiset_val, include_near_matches, near_match_threshold
        )
        if mode == "ordered":
            equal = raw_result["same_ordered"]
        elif mode == "set":
            equal = raw_result["same_unordered"] and raw_result["only_in_a"] == [] and raw_result["only_in_b"] == []
        else:
            equal = raw_result["same_unordered"]

        if mode == "ordered":
            aligned = []
            max_len = max(len(a), len(b))
            for i in range(max_len):
                if i >= len(a):
                    aligned.append({"op": "insert", "b_index": i, "b": b[i]})
                elif i >= len(b):
                    aligned.append({"op": "delete", "a_index": i, "a": a[i]})
                elif a[i] != b[i]:
                    aligned.append({"op": "replace", "a_index": i, "a": a[i], "b_index": i, "b": b[i]})
                else:
                    aligned.append({"op": "equal", "a_index": i, "a": a[i], "b_index": i, "b": b[i]})

            first_diff = None
            for i, al in enumerate(aligned):
                if al["op"] != "equal":
                    first_diff = i
                    break

            equal_prefix_len = first_diff if first_diff is not None else len(a)

            result = {
                "equal": equal,
                "first_diff_index": first_diff,
                "equal_prefix_length": equal_prefix_len,
                "aligned": aligned,
                "only_in_a": raw_result["only_in_a"],
                "only_in_b": raw_result["only_in_b"],
                "missing_in_a": raw_result["only_in_b"],
                "missing_in_b": raw_result["only_in_a"],
                "duplicates_in_a": raw_result["duplicates_a"],
                "duplicates_in_b": raw_result["duplicates_b"],
                "near_matches": raw_result["near_matches"],
            }
        elif mode == "set":
            result = {
                "equal": equal,
                "only_in_a": raw_result["only_in_a"],
                "only_in_b": raw_result["only_in_b"],
                "missing_in_a": raw_result["only_in_b"],
                "missing_in_b": raw_result["only_in_a"],
                "near_matches": raw_result["near_matches"],
            }
        else:
            from collections import Counter
            a_transformed = a
            b_transformed = b
            def transform(s: str) -> str:
                result = s
                if trim:
                    result = result.strip()
                if normalization != "raw":
                    import unicodedata
                    result = unicodedata.normalize(normalization, result)
                if casefold:
                    result = result.casefold()
                return result

            a_counts = Counter(transform(x) for x in a)
            b_counts = Counter(transform(x) for x in b)
            count_deltas = {}
            all_keys = set(a_counts.keys()) | set(b_counts.keys())
            for k in all_keys:
                delta = a_counts.get(k, 0) - b_counts.get(k, 0)
                if delta != 0:
                    count_deltas[k] = delta

            result = {
                "equal": equal,
                "count_deltas": count_deltas,
                "missing_in_a": raw_result["only_in_b"],
                "missing_in_b": raw_result["only_in_a"],
                "duplicates_in_a": raw_result["duplicates_a"],
                "duplicates_in_b": raw_result["duplicates_b"],
                "only_in_a": raw_result["only_in_a"],
                "only_in_b": raw_result["only_in_b"],
                "near_matches": raw_result["near_matches"],
            }
        return _success_response(result, tool="list_compare")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="list_compare")


def text_truncate(text: str, max_graphemes: int) -> dict:
    """Truncate a string to a specified number of grapheme clusters.

    Args:
        text: Input string to truncate.
        max_graphemes: Maximum number of grapheme clusters to return.

    Returns:
        Success envelope with truncation result, or error envelope.
    """
    if (err := _require_str(text, "text", "text_truncate")) is not None:
        return err

    if max_graphemes < 0:
        return _error_response(
            "invalid_arguments",
            f"max_graphemes must be non-negative, got {max_graphemes}",
            ["Set max_graphemes to 0 or higher"],
            tool="text_truncate",
        )

    try:
        original_graphemes = _count_graphemes(text)
        if original_graphemes <= max_graphemes:
            return _success_response({
                "original_graphemes": original_graphemes,
                "truncated_graphemes": original_graphemes,
                "truncated": False,
                "text": text,
            }, tool="text_truncate")

        truncated_text = _truncate_to_grapheme(text, max_graphemes)
        return _success_response({
            "original_graphemes": original_graphemes,
            "truncated_graphemes": max_graphemes,
            "truncated": True,
            "text": truncated_text,
        }, tool="text_truncate")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="text_truncate")


def text_transform(text: str, operations: list[str], detail: str = "normal") -> dict:
    """Apply deterministic text transformations.

    Args:
        text: Input string to transform.
        operations: List of operations to apply.
        detail: Detail level ("summary", "normal", "full").

    Returns:
        Success envelope with transformation result, or error envelope.
    """
    if (err := _require_str(text, "text", "text_transform")) is not None:
        return err

    if not isinstance(operations, list):
        return _error_response(
            "invalid_arguments",
            f"operations must be a list, got {type(operations).__name__}",
            tool="text_transform",
        )

    valid_details = {"summary", "normal", "full"}
    if detail not in valid_details:
        return _error_response(
            "invalid_arguments",
            f"Unsupported detail level: {detail}",
            [f"Use one of: {', '.join(valid_details)}"],
            tool="text_transform",
        )

    unknown_ops = [op for op in operations if op.lower() not in _VALID_TRANSFORM_OPERATIONS]
    if unknown_ops:
        return _error_response(
            "invalid_arguments",
            f"Unknown operation(s): {', '.join(unknown_ops)}",
            [f"Valid operations: {', '.join(sorted(_VALID_TRANSFORM_OPERATIONS))}"],
            tool="text_transform",
        )

    try:
        result = _text_transform(text, operations, detail)
        return _success_response(result, tool="text_transform")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="text_transform")


def text_position(
    text: str,
    byte_offset: int | None = None,
    codepoint_index: int | None = None,
    line: int | None = None,
    column: int | None = None,
    utf16_offset: int | None = None,
    line_base: int = 1,
    column_base: int = 1,
    detail: str = "normal",
) -> dict:
    """Convert between byte offsets, codepoint indices, line/column positions, and UTF-16 offsets.

    Args:
        text: Input string.
        byte_offset: UTF-8 byte offset (0-based).
        codepoint_index: Python string index (Unicode scalar index).
        line: 1-based line number (with line_base).
        column: 1-based column number (with column_base).
        utf16_offset: UTF-16 code unit offset for LSP-style positions.
        line_base: Base for line numbers (1 for 1-based, 0 for 0-based).
        column_base: Base for column numbers (1 for 1-based, 0 for 0-based).
        detail: Detail level ("summary", "normal", "full").

    Returns:
        Success envelope with position result, or error envelope.
    """
    if (err := _require_str(text, "text", "text_position")) is not None:
        return err

    if line_base not in (0, 1):
        return _error_response(
            "invalid_arguments",
            f"line_base must be 0 or 1, got {line_base}",
            tool="text_position",
        )
    if column_base not in (0, 1):
        return _error_response(
            "invalid_arguments",
            f"column_base must be 0 or 1, got {column_base}",
            tool="text_position",
        )

    valid_details = {"summary", "normal", "full"}
    if detail not in valid_details:
        return _error_response(
            "invalid_arguments",
            f"Unsupported detail level: {detail}",
            [f"Use one of: {', '.join(valid_details)}"],
            tool="text_position",
        )

    try:
        result = _text_position(
            text,
            byte_offset=byte_offset,
            codepoint_index=codepoint_index,
            line=line,
            column=column,
            utf16_offset=utf16_offset,
            line_base=line_base,
            column_base=column_base,
        )

        if not result["valid"]:
            return _error_response(
                "invalid_arguments",
                result["error"] or "Invalid position",
                tool="text_position",
            )

        if detail == "summary":
            summary_result = {
                "summary": result["summary"],
            }
        elif detail == "full":
            summary_result = dict(result)
        else:
            summary_result = dict(result)

        return _success_response(summary_result, tool="text_position")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="text_position")


def escape_text(text: str, mode: str, detail: str = "normal") -> dict:
    """Escape text for various output formats.

    Args:
        text: Input string to escape.
        mode: Escape mode (json_string, python_string, rust_string,
              posix_shell_single, regex_literal, markdown_inline_code,
              markdown_code_block, html_text, url_component).
        detail: Detail level ("summary", "normal", "full").

    Returns:
        Success envelope with escape result, or error envelope.
    """
    if (err := _require_str(text, "text", "escape_text")) is not None:
        return err

    valid_details = {"summary", "normal", "full"}
    if detail not in valid_details:
        return _error_response(
            "invalid_arguments",
            f"Unsupported detail level: {detail}",
            [f"Use one of: {', '.join(valid_details)}"],
            tool="escape_text",
        )

    valid_modes = {
        "json_string",
        "python_string",
        "rust_string",
        "posix_shell_single",
        "regex_literal",
        "markdown_inline_code",
        "markdown_code_block",
        "html_text",
        "url_component",
    }
    if mode not in valid_modes:
        return _error_response(
            "invalid_arguments",
            f"Unsupported escape mode: {mode}",
            [f"Valid modes: {', '.join(sorted(valid_modes))}"],
            tool="escape_text",
        )

    try:
        result = _escape_text(text, mode)

        if detail == "summary":
            return _success_response({
                "mode": result["mode"],
                "changed": result["changed"],
                "summary": result["summary"],
            }, tool="escape_text")
        else:
            return _success_response(result, tool="escape_text")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="escape_text")


def unescape_text(text: str, mode: str, detail: str = "normal") -> dict:
    """Unescape text from various formats.

    Args:
        text: Input string to unescape.
        mode: Unescape mode (json_string, python_string,
              unicode_escape, url_component).
        detail: Detail level ("summary", "normal", "full").

    Returns:
        Success envelope with unescape result, or error envelope.
    """
    if (err := _require_str(text, "text", "unescape_text")) is not None:
        return err

    valid_details = {"summary", "normal", "full"}
    if detail not in valid_details:
        return _error_response(
            "invalid_arguments",
            f"Unsupported detail level: {detail}",
            [f"Use one of: {', '.join(valid_details)}"],
            tool="unescape_text",
        )

    valid_modes = {
        "json_string",
        "python_string",
        "unicode_escape",
        "url_component",
    }
    if mode not in valid_modes:
        return _error_response(
            "invalid_arguments",
            f"Unsupported unescape mode: {mode}",
            [f"Valid modes: {', '.join(sorted(valid_modes))}"],
            tool="unescape_text",
        )

    try:
        result = _unescape_text(text, mode)

        if detail == "summary":
            return _success_response({
                "mode": result["mode"],
                "changed": result["changed"],
                "error": result["error"],
                "summary": result["summary"],
            }, tool="unescape_text")
        else:
            return _success_response(result, tool="unescape_text")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="unescape_text")


def text_hash(
    text: str,
    algorithms: list[str] | None = None,
    encoding: str = "utf-8",
    detail: str = "normal",
) -> dict:
    """Compute cryptographic hashes of text for identity checking.

    Args:
        text: Input string to hash.
        algorithms: List of hash algorithms (sha256, sha1, md5, crc32).
        encoding: Text encoding for byte conversion.
        detail: Detail level ("summary", "normal", "full").

    Returns:
        Success envelope with hash result, or error envelope.
    """
    if (err := _require_str(text, "text", "text_hash")) is not None:
        return err

    valid_details = {"summary", "normal", "full"}
    if detail not in valid_details:
        return _error_response(
            "invalid_arguments",
            f"Unsupported detail level: {detail}",
            [f"Use one of: {', '.join(valid_details)}"],
            tool="text_hash",
        )

    if algorithms is not None and not isinstance(algorithms, list):
        return _error_response(
            "invalid_arguments",
            f"algorithms must be a list, got {type(algorithms).__name__}",
            tool="text_hash",
        )

    if algorithms is None:
        algorithms = ["sha256"]

    try:
        result = _text_hash(text, algorithms, encoding)
    except (LookupError, UnicodeDecodeError):
        return _error_response(
            "invalid_arguments",
            f"Invalid encoding: {encoding}",
            ["Use a valid Python encoding name like 'utf-8', 'ascii', 'latin-1'"],
            tool="text_hash",
        )
    except Exception as e:
        return _error_response("internal_error", str(e), tool="text_hash")

    if detail == "summary":
        return _success_response({
            "summary": result["summary"],
        }, tool="text_hash")
    else:
        return _success_response(result, tool="text_hash")


def path_analyze_mcp(path: str, style: str = "auto", detail: str = "normal") -> dict:
    """Analyze path components, extensions, hidden status, and traversal.

    Args:
        path: Path string to analyze.
        style: "auto", "posix", or "windows".
        detail: Detail level ("summary", "normal", "full").

    Returns:
        Success envelope with path analysis result, or error envelope.
    """
    if (err := _require_str(path, "path", "path_analyze")) is not None:
        return err

    valid_styles = {"auto", "posix", "windows"}
    if style not in valid_styles:
        return _error_response(
            "invalid_arguments",
            f"Unsupported style: {style}",
            [f"Use one of: {', '.join(valid_styles)}"],
            tool="path_analyze",
        )

    valid_details = {"summary", "normal", "full"}
    if detail not in valid_details:
        return _error_response(
            "invalid_arguments",
            f"Unsupported detail level: {detail}",
            [f"Use one of: {', '.join(valid_details)}"],
            tool="path_analyze",
        )

    try:
        result = _path_analyze(path, style)

        findings: list[dict] = []
        if result.get("has_traversal"):
            findings.append({
                "code": "PATH_TRAVERSAL",
                "severity": "warn",
                "message": "Path contains parent directory traversal (..)",
                "details": {"normalized_lexical": result.get("normalized_lexical")},
            })
        if result.get("hidden"):
            findings.append({
                "code": "PATH_HIDDEN",
                "severity": "info",
                "message": "Path starts with a dot (hidden file/directory)",
            })

        machine_code: str | None = None
        if result.get("has_traversal"):
            machine_code = "PATH_HAS_TRAVERSAL"
        elif result.get("hidden"):
            machine_code = "PATH_IS_HIDDEN"

        if detail == "summary":
            summary_result = {
                "summary": result["summary"],
                "style": result["style"],
                "absolute": result["absolute"],
                "hidden": result["hidden"],
                "has_traversal": result["has_traversal"],
                "warnings": result["warnings"],
            }
        else:
            summary_result = dict(result)

        return _success_response(summary_result, tool="path_analyze", findings=findings or None, machine_code=machine_code)
    except Exception as e:
        return _error_response("internal_error", str(e), tool="path_analyze")


def path_normalize(
    path: str,
    platform: str = "posix",
    collapse_dot_segments: bool = True,
    preserve_trailing_separator: bool = False,
) -> dict:
    """Normalize a path using posixpath or ntpath semantics.

    Args:
        path: Path string to normalize.
        platform: "posix" or "windows".
        collapse_dot_segments: If True, collapse . and .. segments.
        preserve_trailing_separator: If True, keep trailing separator.

    Returns:
        Success envelope with path normalization result, or error envelope.
    """
    if (err := _require_str(path, "path", "path_normalize")) is not None:
        return err

    valid_platforms = {"posix", "windows"}
    if platform not in valid_platforms:
        return _error_response(
            "invalid_arguments",
            f"Unsupported platform: {platform}",
            [f"Use one of: {', '.join(valid_platforms)}"],
            tool="path_normalize",
        )

    try:
        result = _path_normalize(path, platform, collapse_dot_segments, preserve_trailing_separator)
        return _success_response(result, tool="path_normalize")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="path_normalize")


def path_compare_mcp(
    left: str,
    right: str,
    platform: str = "posix",
    case_sensitive: bool = True,
    normalize_separators: bool = True,
    collapse_dot_segments: bool = True,
) -> dict:
    """Compare two paths under explicit normalization rules.

    Args:
        left: First path string.
        right: Second path string.
        platform: "posix" or "windows".
        case_sensitive: Whether comparison is case-sensitive.
        normalize_separators: Whether to normalize path separators.
        collapse_dot_segments: Whether to collapse . and .. segments.

    Returns:
        Success envelope with comparison result, or error envelope.
    """
    if (err := _require_str(left, "left", "path_compare")) is not None:
        return err
    if (err := _require_str(right, "right", "path_compare")) is not None:
        return err

    valid_platforms = {"posix", "windows"}
    if platform not in valid_platforms:
        return _error_response(
            "invalid_arguments",
            f"Unsupported platform: {platform}",
            [f"Use one of: {', '.join(valid_platforms)}"],
            tool="path_compare",
        )

    try:
        result = _path_compare(left, right, platform, case_sensitive, normalize_separators, collapse_dot_segments)
        return _success_response(result, tool="path_compare")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="path_compare")


def path_scope_check_mcp(
    root: str,
    target: str,
    platform: str = "posix",
    case_sensitive: bool = True,
) -> dict:
    """Determine whether a target path remains lexically inside a declared root.

    This is lexical only. Does NOT resolve symlinks.

    Args:
        root: Root directory path.
        target: Target path to check.
        platform: "posix" or "windows".
        case_sensitive: Whether comparison is case-sensitive.

    Returns:
        Success envelope with scope check result, or error envelope.
    """
    if (err := _require_str(root, "root", "path_scope_check")) is not None:
        return err
    if (err := _require_str(target, "target", "path_scope_check")) is not None:
        return err

    valid_platforms = {"posix", "windows"}
    if platform not in valid_platforms:
        return _error_response(
            "invalid_arguments",
            f"Unsupported platform: {platform}",
            [f"Use one of: {', '.join(valid_platforms)}"],
            tool="path_scope_check",
        )

    try:
        result = _path_scope_check(root, target, platform, case_sensitive)
        return _success_response(result, tool="path_scope_check")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="path_scope_check")


def identifier_analyze(
    text: str,
    languages: list[str] | None = None,
    detail: str = "normal",
) -> dict:
    """Classify and validate identifier naming conventions across languages.

    Args:
        text: Identifier to analyze.
        languages: Languages to check (python, rust, javascript, env).
        detail: Detail level ("summary", "normal", "full").

    Returns:
        Success envelope with analysis result, or error envelope.
    """
    if (err := _require_str(text, "text", "identifier_analyze")) is not None:
        return err

    valid_details = {"summary", "normal", "full"}
    if detail not in valid_details:
        return _error_response(
            "invalid_arguments",
            f"Unsupported detail level: {detail}",
            [f"Use one of: {', '.join(valid_details)}"],
            tool="identifier_analyze",
        )

    if languages is None:
        languages = ["python", "rust", "javascript", "env"]

    valid_languages = {"python", "rust", "javascript", "env"}
    invalid_langs = [l for l in languages if l not in valid_languages]
    if invalid_langs:
        return _error_response(
            "invalid_arguments",
            f"Unsupported language(s): {', '.join(invalid_langs)}",
            [f"Valid languages: {', '.join(sorted(valid_languages))}"],
            tool="identifier_analyze",
        )

    try:
        result = _identifier_analyze(text, languages)

        if detail == "summary":
            summary_result = {
                "text": result["text"],
                "classification": result["classification"],
                "python_valid": result["python_valid"],
                "python_keyword": result["python_keyword"],
                "env_valid": result["env_valid"],
                "summary": result["summary"],
            }
        else:
            summary_result = dict(result)

        return _success_response(summary_result, tool="identifier_analyze")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="identifier_analyze")


def text_window(
    text: str,
    position: dict,
    context_lines: int = 2,
    include_visible_repr: bool = True,
) -> dict:
    """Get a window around a position in text with context lines.

    Args:
        text: Input string.
        position: Dict with kind (byte_offset/codepoint_index/grapheme_index/line_column)
                  and value (numeric) or line/column for line_column kind.
        context_lines: Number of lines before and after to return.
        include_visible_repr: Include visible representation of the line.

    Returns:
        Success envelope with text_window result, or error envelope.
    """
    if (err := _require_str(text, "text", "text_window")) is not None:
        return err

    if not isinstance(position, dict):
        return _error_response(
            "invalid_arguments",
            f"position must be a dict, got {type(position).__name__}",
            tool="text_window",
        )

    if context_lines < 0:
        return _error_response(
            "invalid_arguments",
            f"context_lines must be non-negative, got {context_lines}",
            ["Set context_lines to 0 or higher"],
            tool="text_window",
        )

    MAX_CONTEXT_LINES = 10_000
    if context_lines > MAX_CONTEXT_LINES:
        return _error_response(
            "invalid_arguments",
            f"context_lines {context_lines} exceeds {MAX_CONTEXT_LINES}",
            tool="text_window",
        )

    valid_kinds = {"byte_offset", "codepoint_index", "grapheme_index", "line_column"}
    kind = position.get("kind", "codepoint_index")
    if kind not in valid_kinds:
        return _error_response(
            "invalid_arguments",
            f"Unknown position kind: {kind}",
            [f"Use one of: {', '.join(valid_kinds)}"],
            tool="text_window",
        )

    try:
        result = _text_window(text, position, context_lines, include_visible_repr)
        return _success_response(result, tool="text_window")
    except ValueError as e:
        return _error_response("invalid_arguments", str(e), tool="text_window")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="text_window")


def json_canonicalize(
    text: str,
    sort_keys: bool = True,
    indent: int | None = None,
    ensure_ascii: bool = False,
    detect_duplicate_keys: bool = True,
    trailing_newline: bool = False,
) -> dict:
    """Canonicalize JSON with deterministic formatting.

    Args:
        text: Input JSON string.
        sort_keys: Sort object keys alphabetically.
        indent: Indentation spaces (None for minified).
        ensure_ascii: Use ASCII escaping for non-ASCII characters.
        detect_duplicate_keys: Report duplicate keys in the input.
        trailing_newline: Add a trailing newline to the canonical form.

    Returns:
        Success envelope with canonicalization result, or error envelope.
    """
    if (err := _require_str(text, "text", "json_canonicalize")) is not None:
        return err

    if indent is not None and (indent < 0 or indent > 100):
        return _error_response(
            "invalid_arguments",
            f"indent must be 0-100 or None, got {indent}",
            ["Use a value between 0-100 or None for minified"],
            tool="json_canonicalize",
        )

    try:
        result = _json_canonicalize(
            text,
            sort_keys=sort_keys,
            indent=indent,
            ensure_ascii=ensure_ascii,
            detect_duplicate_keys=detect_duplicate_keys,
            trailing_newline=trailing_newline,
        )
        return _success_response(result, tool="json_canonicalize")
    except ValueError as e:
        return _error_response("invalid_arguments", str(e), tool="json_canonicalize")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="json_canonicalize")


def json_query(text: str, pointer: str = "") -> dict:
    """Query JSON using RFC 6901 JSON Pointer.

    Args:
        text: JSON document string.
        pointer: RFC 6901 JSON Pointer path (e.g., "/foo/bar/0").

    Returns:
        Success envelope with query result, or error envelope.
    """
    if (err := _require_str(text, "text", "json_query")) is not None:
        return err

    try:
        result = _json_query(text, pointer)
        return _success_response(
            result,
            tool="json_query",
            warnings=["json_query is deprecated; use json_extract instead"],
            recommended_next_tool="json_extract",
        )
    except Exception as e:
        return _error_response("internal_error", str(e), tool="json_query")


def glob_match_mcp(
    pattern: str,
    path: str,
    platform: str = "posix",
    case_sensitive: bool = True,
) -> dict:
    """Match a glob pattern against a path.

    Args:
        pattern: Glob pattern to match.
        path: Path string to match against.
        platform: "posix" or "windows".
        case_sensitive: Whether to match case-sensitively.

    Returns:
        Success envelope with match result, or error envelope.
    """
    valid_platforms = {"posix", "windows"}
    if platform not in valid_platforms:
        return _error_response(
            "invalid_arguments",
            f"Unsupported platform: {platform}",
            [f"Use one of: {', '.join(valid_platforms)}"],
            tool="glob_match",
        )

    if (err := _require_str(pattern, "pattern", "glob_match")) is not None:
        return err
    if (err := _require_str(path, "path", "glob_match")) is not None:
        return err

    try:
        result = _glob_match(pattern, path, platform, case_sensitive)
        return _success_response(result, tool="glob_match")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="glob_match")


def text_fingerprint_mcp(
    text: str,
    unicode: str = "raw",
    newline: str = "raw",
    trim_final_newline: bool = False,
    casefold: bool = False,
) -> dict:
    """Compute a deterministic fingerprint of text.

    Args:
        text: Input string to fingerprint.
        unicode: Unicode normalization ("raw", "NFC", "NFD", "NFKC", "NFKD").
        newline: Newline normalization ("raw", "LF").
        trim_final_newline: Remove trailing newline before hashing.
        casefold: Apply casefolding before hashing.

    Returns:
        Success envelope with fingerprint result, or error envelope.
    """
    if (err := _require_str(text, "text", "text_fingerprint")) is not None:
        return err

    valid_unicode = {"raw", "NFC", "NFD", "NFKC", "NFKD"}
    if unicode not in valid_unicode:
        return _error_response(
            "invalid_arguments",
            f"Unsupported unicode normalization: {unicode}",
            [f"Use one of: {', '.join(valid_unicode)}"],
            tool="text_fingerprint",
        )

    valid_newline = {"raw", "LF"}
    if newline not in valid_newline:
        return _error_response(
            "invalid_arguments",
            f"Unsupported newline normalization: {newline}",
            [f"Use one of: {', '.join(valid_newline)}"],
            tool="text_fingerprint",
        )

    try:
        result = _text_fingerprint(text, unicode, newline, trim_final_newline, casefold)
        return _success_response(result, tool="text_fingerprint")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="text_fingerprint")


def identifier_inspect_mcp(
    identifiers: list[str],
    language: str = "generic",
    normalization: str = "NFC",
    casefold: bool = False,
    check_confusables: bool = True,
) -> dict:
    """Inspect identifiers for validity and collisions.

    Args:
        identifiers: List of identifier strings to inspect.
        language: Language for validation ("generic", "python", "rust",
                  "javascript", "typescript", "json_key").
        normalization: Unicode normalization form ("NFC", "NFD", etc).
        casefold: Apply casefolding for collision detection.
        check_confusables: Check for confusable characters.

    Returns:
        Success envelope with inspection result, or error envelope.
    """
    if not isinstance(identifiers, list):
        return _error_response(
            "invalid_arguments",
            f"identifiers must be a list, got {type(identifiers).__name__}",
            tool="identifier_inspect",
        )

    if len(identifiers) > MAX_LIST_ITEMS:
        return _error_response(
            "input_too_large",
            f"Number of identifiers {len(identifiers)} exceeds MAX_LIST_ITEMS {MAX_LIST_ITEMS}",
            [f"Maximum {MAX_LIST_ITEMS} identifiers allowed"],
            tool="identifier_inspect",
        )

    for ident in identifiers:
        if len(ident) > MAX_TEXT_LENGTH:
            return _error_response(
                "input_too_large",
                f"Identifier length {len(ident)} exceeds MAX_TEXT_LENGTH {MAX_TEXT_LENGTH}",
                [f"Maximum identifier length is {MAX_TEXT_LENGTH}"],
                tool="identifier_inspect",
            )

    valid_languages = {"generic", "python", "rust", "javascript", "typescript", "json_key"}
    if language not in valid_languages:
        return _error_response(
            "invalid_arguments",
            f"Unsupported language: {language}",
            [f"Use one of: {', '.join(valid_languages)}"],
            tool="identifier_inspect",
        )

    valid_normalizations = {"raw", "NFC", "NFD", "NFKC", "NFKD"}
    if normalization not in valid_normalizations:
        return _error_response(
            "invalid_arguments",
            f"Unsupported normalization form: {normalization}",
            [f"Use one of: {', '.join(valid_normalizations)}"],
            tool="identifier_inspect",
        )

    try:
        result = _identifier_inspect(identifiers, language, normalization, casefold, check_confusables)

        findings: list[dict] = []
        for ident_info in result.get("identifiers", []):
            for issue in ident_info.get("issues", []):
                findings.append({
                    "code": issue.get("code", "IDENT_ISSUE"),
                    "severity": issue.get("severity", "warn"),
                    "message": issue.get("message", "Identifier issue"),
                    "details": {"identifier": ident_info.get("raw", "")},
                })
        for collision in result.get("collisions", []):
            findings.append({
                "code": "IDENT_COLLISION",
                "severity": "warn",
                "message": collision.get("message", "Identifier collision detected"),
                "details": collision,
            })

        machine_code: str | None = None
        if result.get("collisions"):
            machine_code = "IDENT_COLLISIONS"
        elif any(f.get("severity") == "error" for f in findings):
            machine_code = "IDENT_INVALID"

        return _success_response(result, tool="identifier_inspect", findings=findings or None, machine_code=machine_code)
    except Exception as e:
        return _error_response("internal_error", str(e), tool="identifier_inspect")


def markdown_structure_mcp(
    text: str,
    include_sections: bool = True,
    include_links: bool = True,
    include_code_fences: bool = True,
    include_html_comments: bool = True,
) -> dict:
    """Parse Markdown structure using a deterministic line scanner.

    Args:
        text: Markdown text to analyze.
        include_sections: Include heading detection (default true).
        include_links: Include link detection (default true).
        include_code_fences: Include code fence detection (default true).
        include_html_comments: Include HTML comment detection (default true).

    Returns:
        Success envelope with Markdown structure, or error envelope.
    """
    if (err := _require_str(text, "text", "markdown_structure")) is not None:
        return err

    try:
        result = _markdown_structure(
            text,
            include_sections=include_sections,
            include_links=include_links,
            include_code_fences=include_code_fences,
            include_html_comments=include_html_comments,
        )
        return _success_response(result, tool="markdown_structure")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="markdown_structure")


def code_fence_extract_mcp(
    text: str,
    language: str | None = None,
    include_content: bool = True,
) -> dict:
    """Extract fenced code blocks with exact line ranges and fingerprints.

    Args:
        text: Markdown text to scan.
        language: Optional language filter (case-insensitive).
        include_content: Include block content in output (default true).

    Returns:
        Success envelope with extracted code blocks, or error envelope.
    """
    if (err := _require_str(text, "text", "code_fence_extract")) is not None:
        return err

    try:
        result = _code_fence_extract(
            text,
            language=language,
            include_content=include_content,
        )
        return _success_response(result, tool="code_fence_extract")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="code_fence_extract")


def version_compare_mcp(
    a: str,
    b: str,
    scheme: str = "semver",
) -> dict:
    """Compare two version strings with explicit scheme.

    Args:
        a: First version string.
        b: Second version string.
        scheme: Version scheme ("semver", "pep440", or "loose").

    Returns:
        Success envelope with comparison result, or error envelope.
    """
    valid_schemes = {"semver", "pep440", "loose"}
    if scheme not in valid_schemes:
        return _error_response(
            "invalid_arguments",
            f"Unsupported scheme: {scheme}",
            [f"Use one of: {', '.join(valid_schemes)}"],
            tool="version_compare",
        )

    if (err := _require_str(a, "a", "version_compare")) is not None:
        return err
    if (err := _require_str(b, "b", "version_compare")) is not None:
        return err

    try:
        result = _version_compare(a, b, scheme)
        return _success_response(result, tool="version_compare")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="version_compare")


def toml_shape_mcp(
    text: str,
    max_tables: int = 100,
    detail: str = "normal",
) -> dict:
    """Analyze the structure of a TOML document.

    Args:
        text: TOML document string.
        max_tables: Maximum tables to return (default 100).
        detail: Detail level ("summary", "normal", "full").

    Returns:
        Success envelope with shape result, or error envelope.
    """
    if (err := _require_str(text, "text", "toml_shape")) is not None:
        return err

    valid_details = {"summary", "normal", "full"}
    if detail not in valid_details:
        return _error_response(
            "invalid_arguments",
            f"Unsupported detail level: {detail}",
            [f"Use one of: {', '.join(valid_details)}"],
            tool="toml_shape",
        )

    try:
        result = _toml_shape(text, max_tables)

        if detail == "summary":
            summary_result = {
                "valid": result["valid"],
                "summary": result["summary"],
                "truncated": result["truncated"],
            }
        else:
            summary_result = dict(result)

        return _success_response(summary_result, tool="toml_shape")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="toml_shape")


def list_dedupe_mcp(
    items: list[str],
    normalization: str = "NFC",
    casefold: bool = False,
    stable: bool = True,
) -> dict:
    """Remove duplicates from list while preserving order.

    Args:
        items: List of strings to dedupe.
        normalization: Unicode normalization form ("raw", "NFC", "NFD", "NFKC", "NFKD").
        casefold: Apply casefolding before comparison.
        stable: If True, preserve first occurrence order.

    Returns:
        Success envelope with deduped list, or error envelope.
    """
    if not isinstance(items, list):
        return _error_response(
            "invalid_arguments",
            f"items must be a list, got {type(items).__name__}",
            tool="list_dedupe",
        )

    if len(items) > MAX_LIST_ITEMS:
        return _error_response(
            "input_too_large",
            f"List length {len(items)} exceeds MAX_LIST_ITEMS {MAX_LIST_ITEMS}",
            [f"Maximum {MAX_LIST_ITEMS} items allowed"],
            tool="list_dedupe",
        )

    valid_normalizations = {"raw", "NFC", "NFD", "NFKC", "NFKD"}
    if normalization not in valid_normalizations:
        return _error_response(
            "invalid_arguments",
            f"Unsupported normalization form: {normalization}",
            [f"Use one of: {', '.join(valid_normalizations)}"],
            tool="list_dedupe",
        )

    try:
        result = _list_dedupe(items, normalization, casefold, stable)
        return _success_response({
            "items": result,
            "original_count": len(items),
            "deduped_count": len(result),
            "duplicates_removed": len(items) - len(result),
        }, tool="list_dedupe")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="list_dedupe")


def list_sort_mcp(
    items: list[str],
    normalization: str = "NFC",
    casefold: bool = False,
    reverse: bool = False,
    stable: bool = True,
) -> dict:
    """Sort list of strings with normalization support.

    Args:
        items: List of strings to sort.
        normalization: Unicode normalization form ("raw", "NFC", "NFD", "NFKC", "NFKD").
        casefold: Apply casefolding for sorting.
        reverse: Sort in descending order.
        stable: If True, preserve original order for equal elements.

    Returns:
        Success envelope with sorted list, or error envelope.
    """
    if not isinstance(items, list):
        return _error_response(
            "invalid_arguments",
            f"items must be a list, got {type(items).__name__}",
            tool="list_sort",
        )

    if len(items) > MAX_LIST_ITEMS:
        return _error_response(
            "input_too_large",
            f"List length {len(items)} exceeds MAX_LIST_ITEMS {MAX_LIST_ITEMS}",
            [f"Maximum {MAX_LIST_ITEMS} items allowed"],
            tool="list_sort",
        )

    valid_normalizations = {"raw", "NFC", "NFD", "NFKC", "NFKD"}
    if normalization not in valid_normalizations:
        return _error_response(
            "invalid_arguments",
            f"Unsupported normalization form: {normalization}",
            [f"Use one of: {', '.join(valid_normalizations)}"],
            tool="list_sort",
        )

    try:
        result = _list_sort(items, normalization, casefold, reverse, stable)
        return _success_response({
            "items": result,
            "original_count": len(items),
            "sorted_count": len(result),
        }, tool="list_sort")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="list_sort")


def text_replace_check(
    text: str,
    old: str,
    new: str,
    mode: str = "exact",
    expected_count: int | None = None,
    allow_multiple: bool = False,
    newline_policy: str = "preserve",
    return_preview: bool = False,
    max_preview_chars: int = 2000,
) -> dict:
    """Check whether a replacement would apply cleanly before editing.

    Args:
        text: Source text.
        old: Text to find.
        new: Replacement text.
        mode: Matching mode (exact, nfc, nfkc, casefold, whitespace_collapse).
        expected_count: Expected number of matches.
        allow_multiple: If False and more than one match, add a finding.
        newline_policy: How to handle newlines.
        return_preview: If True, include before/after previews.
        max_preview_chars: Maximum characters in preview output.

    Returns:
        Success envelope with replace check result, or error envelope.
    """
    if (err := _require_str(text, "text", "text_replace_check")) is not None:
        return err

    valid_modes = {"exact", "nfc", "nfkc", "casefold", "whitespace_collapse"}
    if mode not in valid_modes:
        return _error_response(
            "invalid_arguments",
            f"Unsupported mode: {mode}",
            [f"Use one of: {', '.join(valid_modes)}"],
            tool="text_replace_check",
        )

    valid_newline = {"preserve", "normalize_lf", "normalize_crlf"}
    if newline_policy not in valid_newline:
        return _error_response(
            "invalid_arguments",
            f"Unsupported newline_policy: {newline_policy}",
            [f"Use one of: {', '.join(valid_newline)}"],
            tool="text_replace_check",
        )

    if max_preview_chars < 0:
        return _error_response(
            "invalid_arguments",
            f"max_preview_chars must be non-negative, got {max_preview_chars}",
            tool="text_replace_check",
        )

    MAX_PREVIEW_CHARS = 100_000
    if max_preview_chars > MAX_PREVIEW_CHARS:
        return _error_response(
            "invalid_arguments",
            f"max_preview_chars {max_preview_chars} exceeds {MAX_PREVIEW_CHARS}",
            tool="text_replace_check",
        )

    try:
        result = _text_replace_check(
            text, old, new, mode, expected_count, allow_multiple,
            newline_policy, return_preview, max_preview_chars,
        )
        return _success_response(result, tool="text_replace_check")
    except ValueError as e:
        return _error_response("invalid_arguments", str(e), tool="text_replace_check")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="text_replace_check")


def line_range_extract(
    text: str,
    start_line: int,
    end_line: int,
    line_base: int = 1,
    include_line_numbers: bool = False,
    include_fingerprint: bool = True,
) -> dict:
    """Extract exact line ranges and return stable offsets/fingerprints.

    Args:
        text: Input string.
        start_line: First line to extract.
        end_line: Last line to extract (inclusive).
        line_base: Base for line numbers (1 for 1-based, 0 for 0-based).
        include_line_numbers: If True, include line number in each line dict.
        include_fingerprint: If True, compute SHA-256 fingerprint.

    Returns:
        Success envelope with line range extract result, or error envelope.
    """
    if (err := _require_str(text, "text", "line_range_extract")) is not None:
        return err

    if not isinstance(start_line, int) or isinstance(start_line, bool):
        return _error_response(
            "invalid_arguments",
            f"start_line must be an int, got {type(start_line).__name__}",
            tool="line_range_extract",
        )
    if not isinstance(end_line, int) or isinstance(end_line, bool):
        return _error_response(
            "invalid_arguments",
            f"end_line must be an int, got {type(end_line).__name__}",
            tool="line_range_extract",
        )
    if start_line < 0:
        return _error_response(
            "invalid_arguments",
            f"start_line must be non-negative, got {start_line}",
            tool="line_range_extract",
        )
    if end_line < 0:
        return _error_response(
            "invalid_arguments",
            f"end_line must be non-negative, got {end_line}",
            tool="line_range_extract",
        )
    if start_line > end_line:
        return _error_response(
            "invalid_arguments",
            f"start_line ({start_line}) must be <= end_line ({end_line})",
            tool="line_range_extract",
        )

    try:
        result = _line_range_extract(
            text, start_line, end_line, line_base,
            include_line_numbers, include_fingerprint,
        )
        return _success_response(result, tool="line_range_extract")
    except ValueError as e:
        return _error_response("invalid_arguments", str(e), tool="line_range_extract")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="line_range_extract")


def line_range_compare(
    left_text: str,
    right_text: str,
    start_line: int,
    end_line: int,
    line_base: int = 1,
    comparison_mode: str = "exact",
) -> dict:
    """Compare a line range from two text inputs.

    Args:
        left_text: First text input.
        right_text: Second text input.
        start_line: First line to compare.
        end_line: Last line to compare (inclusive).
        line_base: Base for line numbers.
        comparison_mode: "exact", "ignore_trailing_whitespace", or "normalize_newlines".

    Returns:
        Success envelope with line range compare result, or error envelope.
    """
    if not isinstance(left_text, str) or not isinstance(right_text, str):
        return _error_response(
            "invalid_arguments",
            f"left_text and right_text must be strings, got {type(left_text).__name__} and {type(right_text).__name__}",
            tool="line_range_compare",
        )

    for label, t in [("left_text", left_text), ("right_text", right_text)]:
        if len(t) > MAX_TEXT_LENGTH:
            return _error_response(
                "input_too_large",
                f"{label} length {len(t)} exceeds MAX_TEXT_LENGTH {MAX_TEXT_LENGTH}",
                [f"Maximum input length is {MAX_TEXT_LENGTH} characters"],
                tool="line_range_compare",
            )

    valid_modes = {"exact", "ignore_trailing_whitespace", "normalize_newlines"}
    if comparison_mode not in valid_modes:
        return _error_response(
            "invalid_arguments",
            f"Unsupported comparison_mode: {comparison_mode}",
            [f"Use one of: {', '.join(valid_modes)}"],
            tool="line_range_compare",
        )

    try:
        result = _line_range_compare(
            left_text, right_text, start_line, end_line,
            line_base, comparison_mode,
        )
        return _success_response(result, tool="line_range_compare")
    except ValueError as e:
        return _error_response("invalid_arguments", str(e), tool="line_range_compare")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="line_range_compare")


def shell_split(
    command: str,
    shell: str = "posix",
    detect_risky_features: bool = True,
) -> dict:
    """Parse a shell-like command string into argv and report risky features.

    This performs lexical POSIX-like parsing only, not full shell evaluation.

    Args:
        command: The command string to parse.
        shell: Shell dialect (only "posix" is supported).
        detect_risky_features: Whether to detect risky lexical features.

    Returns:
        Success envelope with parsed argv and features, or error envelope.
    """
    if (err := _require_str(command, "command", "shell_split")) is not None:
        return err

    valid_shells = {"posix"}
    if shell not in valid_shells:
        return _error_response(
            "invalid_arguments",
            f"Unsupported shell: {shell}",
            [f"Use one of: {', '.join(valid_shells)}"],
            tool="shell_split",
        )

    try:
        result = _shell_split(command, shell=shell, detect_risky_features=detect_risky_features)
        return _success_response(result, tool="shell_split")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="shell_split")


def shell_quote_join(
    argv: list[str],
    shell: str = "posix",
) -> dict:
    """Safely quote a list of argv tokens into a POSIX-like shell string.

    Args:
        argv: List of argument strings to join.
        shell: Shell dialect (only "posix" is supported).

    Returns:
        Success envelope with quoted command and roundtrip status, or error envelope.
    """
    if not isinstance(argv, list):
        return _error_response(
            "invalid_arguments",
            f"argv must be a list, got {type(argv).__name__}",
            tool="shell_quote_join",
        )

    if len(argv) > MAX_LIST_ITEMS:
        return _error_response(
            "input_too_large",
            f"argv length {len(argv)} exceeds MAX_LIST_ITEMS {MAX_LIST_ITEMS}",
            [f"Maximum {MAX_LIST_ITEMS} items allowed"],
            tool="shell_quote_join",
        )

    valid_shells = {"posix"}
    if shell not in valid_shells:
        return _error_response(
            "invalid_arguments",
            f"Unsupported shell: {shell}",
            [f"Use one of: {', '.join(valid_shells)}"],
            tool="shell_quote_join",
        )

    try:
        result = _shell_quote_join(argv, shell=shell)
        return _success_response(result, tool="shell_quote_join")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="shell_quote_join")


def shell_argv_compare(
    left_command: str | None = None,
    right_command: str | None = None,
    left_argv: list[str] | None = None,
    right_argv: list[str] | None = None,
    shell: str = "posix",
) -> dict:
    """Compare two command strings or argv lists by parsed argv.

    Args:
        left_command: Left command string to parse and compare.
        right_command: Right command string to parse and compare.
        left_argv: Left pre-parsed argv list.
        right_argv: Right pre-parsed argv list.
        shell: Shell dialect (only "posix" is supported).

    Returns:
        Success envelope with comparison results, or error envelope.
    """
    valid_shells = {"posix"}
    if shell not in valid_shells:
        return _error_response(
            "invalid_arguments",
            f"Unsupported shell: {shell}",
            [f"Use one of: {', '.join(valid_shells)}"],
            tool="argv_compare",
        )

    # XOR validation: each side must be either a *_command OR an *_argv,
    # not both (and not neither).
    if (left_command is not None) == (left_argv is not None):
        return _error_response(
            "invalid_arguments",
            "Provide exactly one of left_command or left_argv, not both",
            tool="argv_compare",
        )
    if (right_command is not None) == (right_argv is not None):
        return _error_response(
            "invalid_arguments",
            "Provide exactly one of right_command or right_argv, not both",
            tool="argv_compare",
        )

    if left_argv is not None and not isinstance(left_argv, list):
        return _error_response(
            "invalid_arguments",
            f"left_argv must be a list, got {type(left_argv).__name__}",
            tool="argv_compare",
        )
    if right_argv is not None and not isinstance(right_argv, list):
        return _error_response(
            "invalid_arguments",
            f"right_argv must be a list, got {type(right_argv).__name__}",
            tool="argv_compare",
        )

    if left_command is not None and len(left_command) > MAX_TEXT_LENGTH:
        return _error_response(
            "input_too_large",
            f"Left command length {len(left_command)} exceeds MAX_TEXT_LENGTH {MAX_TEXT_LENGTH}",
            [f"Maximum input length is {MAX_TEXT_LENGTH} characters"],
            tool="argv_compare",
        )

    if right_command is not None and len(right_command) > MAX_TEXT_LENGTH:
        return _error_response(
            "input_too_large",
            f"Right command length {len(right_command)} exceeds MAX_TEXT_LENGTH {MAX_TEXT_LENGTH}",
            [f"Maximum input length is {MAX_TEXT_LENGTH} characters"],
            tool="argv_compare",
        )

    if left_argv is not None and len(left_argv) > MAX_LIST_ITEMS:
        return _error_response(
            "input_too_large",
            f"left_argv length {len(left_argv)} exceeds MAX_LIST_ITEMS {MAX_LIST_ITEMS}",
            [f"Maximum {MAX_LIST_ITEMS} items allowed"],
            tool="argv_compare",
        )

    if right_argv is not None and len(right_argv) > MAX_LIST_ITEMS:
        return _error_response(
            "input_too_large",
            f"right_argv length {len(right_argv)} exceeds MAX_LIST_ITEMS {MAX_LIST_ITEMS}",
            [f"Maximum {MAX_LIST_ITEMS} items allowed"],
            tool="argv_compare",
        )

    try:
        result = _argv_compare(
            left_command=left_command,
            right_command=right_command,
            left_argv=left_argv,
            right_argv=right_argv,
            shell=shell,
        )
        return _success_response(result, tool="argv_compare")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="argv_compare")


def dotenv_validate_mcp(
    text: str,
    allow_export: bool = True,
    key_pattern: str = r"^[A-Za-z_][A-Za-z0-9_]*$",
    duplicate_policy: str = "warn",
) -> dict:
    """Validate .env-style key=value text.

    Args:
        text: Input text to validate.
        allow_export: If True, allow ``export KEY=VALUE`` syntax (default true).
        key_pattern: Regex pattern keys must match (default POSIX-ish identifier).
        duplicate_policy: ``warn``, ``error``, or ``allow`` (default ``warn``).

    Returns:
        Success envelope with validation result, or error envelope.
    """
    if (err := _require_str(text, "text", "dotenv_validate")) is not None:
        return err

    valid_policies = {"warn", "error", "allow"}
    if duplicate_policy not in valid_policies:
        return _error_response(
            "invalid_arguments",
            f"Unsupported duplicate_policy: {duplicate_policy}",
            [f"Use one of: {', '.join(sorted(valid_policies))}"],
            tool="dotenv_validate",
        )

    if len(key_pattern) > 1000:
        return _error_response(
            "input_too_large",
            f"key_pattern length {len(key_pattern)} exceeds 1000",
            tool="dotenv_validate",
        )

    try:
        pattern_safety = _regex_safety_check(key_pattern)
    except re.error as e:
        return _error_response(
            "invalid_arguments",
            f"key_pattern is not a valid regular expression: {e}",
            ["Fix the regex syntax in key_pattern"],
            tool="dotenv_validate",
        )
    except ValueError as e:
        return _error_response(
            "invalid_arguments",
            f"key_pattern safety check failed: {e}",
            tool="dotenv_validate",
        )
    # Other exception types (TypeError, AttributeError, etc.) propagate as
    # internal errors so they are not silently swallowed.
    if not pattern_safety.get("valid_pattern", True):
        return _error_response(
            "invalid_arguments",
            f"key_pattern is not a valid regular expression: {pattern_safety.get('error', 'unknown')}",
            ["Fix the regex syntax in key_pattern"],
            tool="dotenv_validate",
        )
    if pattern_safety.get("risk") in ("high", "medium"):
        return _error_response(
            "unsafe_pattern",
            f"key_pattern has {pattern_safety.get('risk', 'unknown')} risk of catastrophic backtracking",
            ["Use a simpler regex pattern for key_pattern"],
            tool="dotenv_validate",
        )

    try:
        result = _dotenv_validate(text, allow_export, key_pattern, duplicate_policy)
        return _success_response(result, tool="dotenv_validate")
    except re.error:
        return _error_response(
            "invalid_arguments",
            f"Invalid key_pattern regex: {key_pattern}",
            ["Provide a valid regular expression for key_pattern"],
            tool="dotenv_validate",
        )
    except Exception as e:
        return _error_response("internal_error", str(e), tool="dotenv_validate")


def ini_validate_mcp(
    text: str,
    duplicate_policy: str = "warn",
) -> dict:
    """Validate simple INI-style configuration.

    Args:
        text: Input text to validate.
        duplicate_policy: ``warn``, ``error``, or ``allow`` (default ``warn``).

    Returns:
        Success envelope with validation result, or error envelope.
    """
    if (err := _require_str(text, "text", "ini_validate")) is not None:
        return err

    valid_policies = {"warn", "error", "allow"}
    if duplicate_policy not in valid_policies:
        return _error_response(
            "invalid_arguments",
            f"Unsupported duplicate_policy: {duplicate_policy}",
            [f"Use one of: {', '.join(sorted(valid_policies))}"],
            tool="ini_validate",
        )

    try:
        result = _ini_validate(text, duplicate_policy)
        return _success_response(result, tool="ini_validate")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="ini_validate")


def patch_apply_check_mcp(
    original_text: str,
    patch_text: str,
    strict: bool = True,
    return_result_fingerprint: bool = True,
    return_result_text: bool = False,
) -> dict:
    """Check whether a unified diff applies cleanly to original text.

    Args:
        original_text: The original source text.
        patch_text: The unified diff patch.
        strict: If True, context lines must match exactly.
        return_result_fingerprint: If True, compute SHA-256 of result.
        return_result_text: If True, include the resulting text (bounded).

    Returns:
        Success envelope with patch apply check result, or error envelope.
    """
    from ..exact.patch import (
        MAX_ORIGINAL_LENGTH,
        MAX_PATCH_LENGTH,
    )
    from ..exact.patch import (
        patch_apply_check as _patch_apply_check,
    )

    if not isinstance(original_text, str):
        return _error_response(
            "invalid_arguments",
            f"original_text must be a string, got {type(original_text).__name__}",
            tool="patch_apply_check",
        )
    if not isinstance(patch_text, str):
        return _error_response(
            "invalid_arguments",
            f"patch_text must be a string, got {type(patch_text).__name__}",
            tool="patch_apply_check",
        )

    if len(original_text) > MAX_ORIGINAL_LENGTH:
        return _error_response(
            "input_too_large",
            f"Original text length {len(original_text)} exceeds maximum of {MAX_ORIGINAL_LENGTH}",
            [f"Maximum original text length is {MAX_ORIGINAL_LENGTH}"],
            tool="patch_apply_check",
        )

    if len(patch_text) > MAX_PATCH_LENGTH:
        return _error_response(
            "input_too_large",
            f"Patch text length {len(patch_text)} exceeds maximum of {MAX_PATCH_LENGTH}",
            [f"Maximum patch text length is {MAX_PATCH_LENGTH}"],
            tool="patch_apply_check",
        )

    try:
        result = _patch_apply_check(
            original_text,
            patch_text,
            strict=strict,
            return_result_fingerprint=return_result_fingerprint,
            return_result_text=return_result_text,
        )
        return _success_response(result, tool="patch_apply_check")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="patch_apply_check")


def patch_summary_mcp(
    patch_text: str,
) -> dict:
    """Summarize a unified diff without applying it.

    Args:
        patch_text: The unified diff text.

    Returns:
        Success envelope with patch summary result, or error envelope.
    """
    from ..exact.patch import (
        MAX_PATCH_LENGTH,
    )
    from ..exact.patch import (
        patch_summary as _patch_summary,
    )

    if not isinstance(patch_text, str):
        return _error_response(
            "invalid_arguments",
            f"patch_text must be a string, got {type(patch_text).__name__}",
            tool="patch_summary",
        )

    if len(patch_text) > MAX_PATCH_LENGTH:
        return _error_response(
            "input_too_large",
            f"Patch text length {len(patch_text)} exceeds maximum of {MAX_PATCH_LENGTH}",
            [f"Maximum patch text length is {MAX_PATCH_LENGTH}"],
            tool="patch_summary",
        )

    try:
        result = _patch_summary(patch_text)
        return _success_response(result, tool="patch_summary")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="patch_summary")


def unicode_policy_check_mcp(
    text: str,
    policy: str,
    normalization: str | None = None,
) -> dict:
    """Apply a named Unicode safety policy to text.

    Args:
        text: Input text to check.
        policy: One of identifier_strict, filename_safe, source_code,
                human_text, json_key, domain_like.
        normalization: Optional normalization form (defaults to policy-specific).

    Returns:
        Success envelope with policy check result, or error envelope.
    """
    if (err := _require_str(text, "text", "unicode_policy_check")) is not None:
        return err

    valid_policies = {
        "identifier_strict", "filename_safe", "source_code",
        "human_text", "json_key", "domain_like",
    }
    if policy not in valid_policies:
        return _error_response(
            "invalid_arguments",
            f"Unsupported policy: {policy}",
            [f"Use one of: {', '.join(sorted(valid_policies))}"],
            tool="unicode_policy_check",
        )

    if normalization is not None:
        valid_normalizations = {"raw", "NFC", "NFD", "NFKC", "NFKD"}
        if normalization not in valid_normalizations:
            return _error_response(
                "invalid_arguments",
                f"Unsupported normalization form: {normalization}",
                [f"Use one of: {', '.join(valid_normalizations)}"],
                tool="unicode_policy_check",
            )

    try:
        result = _unicode_policy_check(text, policy, normalization)
        return _success_response(result, tool="unicode_policy_check")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="unicode_policy_check")


def canonicalize_text_mcp(
    text: str,
    profile: str,
    return_mapping: bool = False,
) -> dict:
    """Apply a named text canonicalization profile.

    Args:
        text: Input text to canonicalize.
        profile: One of source_file_identity, identifier_compare,
                 human_label_compare, json_key_compare, path_segment_compare.
        return_mapping: If True, include a character mapping.

    Returns:
        Success envelope with canonicalization result, or error envelope.
    """
    if (err := _require_str(text, "text", "canonicalize_text")) is not None:
        return err

    valid_profiles = {
        "source_file_identity", "identifier_compare", "human_label_compare",
        "json_key_compare", "path_segment_compare",
    }
    if profile not in valid_profiles:
        return _error_response(
            "invalid_arguments",
            f"Unsupported profile: {profile}",
            [f"Use one of: {', '.join(sorted(valid_profiles))}"],
            tool="canonicalize_text",
        )

    try:
        result = _canonicalize_text(text, profile, return_mapping)
        return _success_response(result, tool="canonicalize_text")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="canonicalize_text")


def identifier_table_inspect_mcp(
    identifiers: list[dict],
    language: str = "python",
    checks: list[str] | None = None,
) -> dict:
    """Inspect a table of identifiers for collisions, reserved keywords, and mixed styles.

    Args:
        identifiers: List of dicts with required 'name' (str), optional 'kind' (str),
                     'file' (str), 'line' (int).
        language: Target language for keyword checking.
        checks: Subset of checks to run.

    Returns:
        Success envelope with inspection result, or error envelope.
    """
    if not isinstance(identifiers, list):
        return _error_response(
            "invalid_arguments",
            f"identifiers must be a list, got {type(identifiers).__name__}",
            tool="identifier_table_inspect",
        )

    if len(identifiers) > MAX_LIST_ITEMS:
        return _error_response(
            "input_too_large",
            f"Number of identifiers {len(identifiers)} exceeds MAX_LIST_ITEMS {MAX_LIST_ITEMS}",
            [f"Maximum {MAX_LIST_ITEMS} identifiers allowed"],
            tool="identifier_table_inspect",
        )

    valid_languages = {"generic", "python", "rust", "javascript", "typescript", "json_key"}
    if language not in valid_languages:
        return _error_response(
            "invalid_arguments",
            f"Unsupported language: {language}",
            [f"Use one of: {', '.join(valid_languages)}"],
            tool="identifier_table_inspect",
        )

    valid_checks = {"casefold", "normalization", "confusable", "style", "reserved", "mixed_style"}
    if checks is not None:
        invalid = [c for c in checks if c not in valid_checks]
        if invalid:
            return _error_response(
                "invalid_arguments",
                f"Unknown check(s): {', '.join(invalid)}",
                [f"Valid checks: {', '.join(sorted(valid_checks))}"],
                tool="identifier_table_inspect",
            )

    try:
        result = _identifier_table_inspect(identifiers, language, checks)

        findings: list[dict] = []
        for collision in result.get("collisions", []):
            findings.append({
                "code": f"COLLISION_{collision['kind'].upper()}",
                "severity": "warn",
                "message": collision.get("detail", "Collision detected"),
                "details": {"names": collision.get("names", [])},
            })
        for hit in result.get("reserved_keyword_hits", []):
            findings.append({
                "code": "RESERVED_KEYWORD",
                "severity": "warn",
                "message": f"'{hit['name']}' is a reserved keyword in {hit['language']}",
                "details": {"file": hit.get("file"), "line": hit.get("line")},
            })
        for group in result.get("mixed_style_groups", []):
            findings.append({
                "code": "MIXED_STYLE",
                "severity": "info",
                "message": f"Mixed styles for '{group['stripped']}': {', '.join(group['styles'])}",
                "details": {"names": group.get("names", [])},
            })

        machine_code: str | None = None
        if result.get("reserved_keyword_hits"):
            machine_code = "RESERVED_KEYWORDS"
        elif result.get("collisions"):
            machine_code = "IDENT_COLLISIONS"

        return _success_response(result, tool="identifier_table_inspect", findings=findings or None, machine_code=machine_code)
    except Exception as e:
        return _error_response("internal_error", str(e), tool="identifier_table_inspect")


def version_constraint_check_mcp(
    version: str,
    constraint: str,
    scheme: str = "semver",
) -> dict:
    """Check whether a version satisfies a constraint under a given versioning scheme.

    Args:
        version: Version string to check (e.g., '1.2.3', '0.5.0-beta.1').
        constraint: Version constraint (e.g., '>=1.0,<2.0', '^1.2.3', '~0.5', '1.*').
        scheme: Versioning scheme ('semver' or 'cargo').

    Returns:
        Success envelope with constraint check result, or error envelope.
    """
    if not isinstance(version, str):
        return _error_response(
            "invalid_arguments",
            f"version must be a string, got {type(version).__name__}",
            tool="version_constraint_check",
        )
    if not isinstance(constraint, str):
        return _error_response(
            "invalid_arguments",
            f"constraint must be a string, got {type(constraint).__name__}",
            tool="version_constraint_check",
        )

    valid_schemes = {"semver", "cargo"}
    if scheme not in valid_schemes:
        return _error_response(
            "invalid_arguments",
            f"Unsupported scheme: {scheme}",
            [f"Use one of: {', '.join(valid_schemes)}"],
            tool="version_constraint_check",
        )

    if not version.strip():
        return _error_response(
            "invalid_arguments",
            "Version string is empty",
            ["Provide a valid version string like '1.2.3'"],
            tool="version_constraint_check",
        )

    if not constraint.strip():
        return _error_response(
            "invalid_arguments",
            "Constraint string is empty",
            ["Provide a valid constraint like '>=1.0' or '^1.2.3'"],
            tool="version_constraint_check",
        )

    if len(version) > MAX_TEXT_LENGTH:
        return _error_response(
            "input_too_large",
            f"Input exceeds maximum length of {MAX_TEXT_LENGTH}",
            tool="version_constraint_check",
        )

    if len(constraint) > MAX_TEXT_LENGTH:
        return _error_response(
            "input_too_large",
            f"Input exceeds maximum length of {MAX_TEXT_LENGTH}",
            tool="version_constraint_check",
        )

    try:
        result = _check_version_constraint(version, constraint, scheme)

        findings: list[dict] = []
        for msg in result.get("findings", []):
            findings.append({
                "code": "CONSTRAINT_NOTE",
                "severity": "info",
                "message": msg,
            })

        machine_code: str | None = None
        if not result.get("satisfies"):
            machine_code = "CONSTRAINT_NOT_SATISFIED"
        elif findings:
            machine_code = "CONSTRAINT_NOTE"

        return _success_response(
            result,
            tool="version_constraint_check",
            findings=findings or None,
            machine_code=machine_code,
        )
    except Exception as e:
        return _error_response("internal_error", str(e), tool="version_constraint_check")


def cargo_toml_inspect_mcp(
    text: str,
    check_workspace: bool = True,
    check_dependencies: bool = True,
) -> dict:
    """Inspect Cargo.toml text without network or filesystem access.

    Args:
        text: The Cargo.toml content.
        check_workspace: Whether to analyze workspace section.
        check_dependencies: Whether to analyze dependencies sections.

    Returns:
        Success envelope with Cargo.toml inspection result, or error envelope.
    """
    if (err := _require_str(text, "text", "cargo_toml_inspect")) is not None:
        return err

    try:
        result = _cargo_toml_inspect(text, check_workspace, check_dependencies)

        findings: list[dict] = []
        for msg in result.get("findings", []):
            if "parse error" in msg.lower() or "not a table" in msg.lower():
                severity = "error"
                code = "CARGO_PARSE_ERROR"
            elif "missing" in msg.lower():
                severity = "warn"
                code = "CARGO_MISSING_FIELD"
            elif "confusable" in msg.lower():
                severity = "warn"
                code = "CARGO_CONFUSABLE_NAMES"
            elif "suspicious" in msg.lower():
                severity = "warn"
                code = "CARGO_SUSPICIOUS_NAME"
            elif "unrecognized" in msg.lower():
                severity = "warn"
                code = "CARGO_UNRECOGNIZED_VALUE"
            else:
                severity = "info"
                code = "CARGO_NOTE"
            findings.append({
                "code": code,
                "severity": severity,
                "message": msg,
            })

        machine_code: str | None = None
        if not result.get("parse_ok"):
            machine_code = "CARGO_PARSE_FAILED"
        elif result.get("findings"):
            machine_code = "CARGO_HAS_FINDINGS"

        return _success_response(
            result,
            tool="cargo_toml_inspect",
            findings=findings or None,
            machine_code=machine_code,
        )
    except Exception as e:
        return _error_response("internal_error", str(e), tool="cargo_toml_inspect")


def prompt_input_inspect_mcp(
    text: str,
    checks: list[str] | None = None,
    phrase_patterns: list[str] | None = None,
) -> dict:
    """Inspect text for deterministic red flags.

    Surfaces observable features that may influence agents or humans
    unexpectedly. Does NOT infer intent or detect prompt injection
    semantically.

    Args:
        text: The text to inspect.
        checks: Subset of check names to run.
        phrase_patterns: Optional literal strings or safe regexes to detect.

    Returns:
        Success envelope with inspection result, or error envelope.
    """
    if (err := _require_str(text, "text", "prompt_input_inspect")) is not None:
        return err

    if phrase_patterns is not None and not isinstance(phrase_patterns, list):
        return _error_response(
            "invalid_arguments",
            f"phrase_patterns must be a list, got {type(phrase_patterns).__name__}",
            tool="prompt_input_inspect",
        )

    if phrase_patterns is not None:
        phrase_patterns = [str(p) for p in phrase_patterns]

    valid_checks = {
        "unicode_hidden", "bidi", "html_comments", "markdown_links",
        "ansi_escapes", "terminal_controls", "base64_like_blobs",
        "instruction_phrases", "long_minified_lines",
    }
    if checks is not None:
        invalid = [c for c in checks if c not in valid_checks]
        if invalid:
            return _error_response(
                "invalid_arguments",
                f"Unknown check(s): {', '.join(invalid)}",
                [f"Valid checks: {', '.join(sorted(valid_checks))}"],
                tool="prompt_input_inspect",
            )

    try:
        result = _prompt_input_inspect(text, checks, phrase_patterns)

        findings: list[dict] = []
        for f in result.get("findings", []):
            findings.append({
                "code": f.get("code", "UNKNOWN"),
                "severity": f.get("severity", "info"),
                "message": f.get("message", ""),
                "span": f.get("span"),
                "details": f.get("details"),
            })

        machine_code: str | None = None
        if findings:
            codes = {f["code"] for f in findings}
            if any(c in codes for c in ("HIDDEN_CHAR", "BIDI_CONTROL", "ANSI_ESCAPE")):
                machine_code = "PROMPT_HIDDEN_CONTENT"
            elif codes:
                machine_code = "PROMPT_HAS_FLAGS"

        return _success_response(
            result,
            tool="prompt_input_inspect",
            findings=findings or None,
            machine_code=machine_code,
            recommended_next_tool=result.get("recommended_next_tool"),
        )
    except ValueError as e:
        return _error_response("invalid_arguments", str(e), tool="prompt_input_inspect")
    except Exception as e:
        return _error_response("internal_error", str(e), tool="prompt_input_inspect")
