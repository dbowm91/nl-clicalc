"""
Natural language to math expression normalizer.

Converts mathematical expressions written in natural language
(e.g., "sixteen plus five hundred twenty two") into executable
mathematical expressions.

Usage:
    python -m nl_calc "five plus two"
    python -m nl_calc "30m + 100ft"
    python -m nl_calc --help
"""

from __future__ import annotations

import argparse
import re
import sys
import traceback
from functools import lru_cache
from typing import Any, Mapping, Pattern

from .evaluator import EvaluationError, evaluate
from .units import UnitValue, UNIT_ALIASES, is_unit, UNIT_CATEGORIES
from .exact import inspect_text, count_chars, regex_test

__all__ = [
    "evaluate",
    "EvaluationError",
    "UnitValue",
    "run",
    "normalize",
    "normalize_expression",
    "main",
    "print_help",
    "NORMALIZE",
    "PATTERNS",
    "MAX_INPUT_LENGTH",
    "MAX_NESTING_DEPTH",
]

MAX_INPUT_LENGTH = 10000
MAX_NESTING_DEPTH = 100

# Pre-computed sorted units list for performance (avoid re-sorting each call)
_UNITS_BY_LENGTH: list[str] = sorted(UNIT_ALIASES.keys(), key=len, reverse=True)

# Common unit prefixes for faster lookup (most frequently used units first)
_COMMON_UNITS: list[str] = [
    "m",
    "km",
    "cm",
    "mm",
    "s",
    "ms",
    "us",
    "ns",
    "min",
    "h",
    "d",
    "g",
    "kg",
    "mg",
    "lb",
    "oz",
    "L",
    "mL",
    "gal",
    "J",
    "kJ",
    "W",
    "kW",
    "Pa",
    "atm",
    "N",
    "V",
    "A",
    "Hz",
    "B",
    "KB",
    "MB",
    "GB",
    "in",
    "ft",
    "yd",
    "mi",
    "yr",
    "K",
    "C",
    "F",
]

# Build a prefix set for O(1) lookup of common unit starts
_UNIT_PREFIXES: set[str] = set()
for unit in _COMMON_UNITS:
    for i in range(1, len(unit) + 1):
        _UNIT_PREFIXES.add(unit[:i])


# Operator conversions: operator -> list of word representations
OPERATOR_CONVERSIONS: dict[str, list[str]] = {
    "+": ["plus", "positive"],
    "-": ["minus", "negative"],
    "*": ["times", "multiplied by", "of"],  # "of" for "30% of 200"
    "/": ["divided by", "over", "per", "divide"],
    "**": ["^", "raised to", "raised to the power", "to the power of"],
    ".": ["point"],
    ",": [],
    "&": ["AND", "and", "bitand", "bit and"],
    "|": ["OR", "or", "bitor", "bit or"],
    "^": ["XOR", "xor", "bitxor", "bit xor"],
    "<<": ["left shift", "shift left", "lshift"],
    ">>": ["right shift", "shift right", "rshift"],
    "~": ["NOT", "not", "bitnot", "bit not"],
    "%": ["mod", "modulo", "percent", "remainder"],
    # Unit conversion words - these get split out as tokens
    "IN": ["in", "into"],
    "TO": ["to", "as"],
}

# Function name mappings (for function name normalization)
# Maps common names/aliases to canonical function names
FUNCTION_MAPPINGS: dict[str, str] = {
    "square root": "sqrt",
    "sqrt": "sqrt",
    "sine": "sin",
    "sin": "sin",
    "cosine": "cos",
    "cos": "cos",
    "tangent": "tan",
    "tan": "tan",
    "arcsine": "asin",
    "asin": "asin",
    "inverse sine": "asin",
    "arccos": "acos",
    "acos": "acos",
    "inverse cosine": "acos",
    "arctan": "atan",
    "atan": "atan",
    "inverse tangent": "atan",
    "absolute": "abs",
    "abs": "abs",
    "magnitude": "abs",
    "ln": "log",
    "log": "log",
    "log10": "log10",
    "log2": "log2",
    "exp": "exp",
    "temp": "temp",
    "bin": "bin",
    "hex": "hex",
    "oct": "oct",
    "mean": "mean",
    "average": "mean",
    "median": "median",
    "mode": "mode",
    "std": "std",
    "stdev": "std",
    "variance": "variance",
    "var": "var",
    "sum": "sum",
    "max": "max",
    "min": "min",
    "gcd": "gcd",
    "lcm": "lcm",
    "perm": "perm",
    "comb": "comb",
    "nPr": "nPr",
    "nCr": "nCr",
    "factorial": "factorial",
    "fact": "factorial",
    "real": "real",
    "imag": "imag",
    "conj": "conj",
    "conjugate": "conj",
    "phase": "phase",
    "polar": "polar",
    "rect": "rect",
    "bitand": "bitand",
    "bitor": "bitor",
    "bitxor": "bitxor",
    "bitnot": "bitnot",
    "isprime": "isprime",
    "primefactors": "primefactors",
    "prime_factors": "primefactors",
    "nextprime": "nextprime",
    "prevprime": "prevprime",
    "random": "random",
    "randint": "randint",
    "randn": "randn",
    "gauss": "gauss",
    "seed": "seed",
    "percentof": "percentof",
    "percent_of": "percentof",
    "aspercent": "aspercent",
    "as_percent": "aspercent",
    "clamp": "clamp",
    "hypot": "hypot",
    "round": "round",
    "sign": "sign",
    "cbrt": "cbrt",
    "cube root": "cbrt",
    "ceil": "ceil",
    "ceiling": "ceil",
    "floor": "floor",
    "store": "store",
    "recall": "recall",
    "Mplus": "Mplus",
    "Mminus": "Mminus",
    "MC": "MC",
    "MR": "MR",
    "setvar": "setvar",
    "getvar": "getvar",
    "delvar": "delvar",
    "listvars": "listvars",
    "clearvars": "clearvars",
}

# Number words
NUMBER_WORDS: dict[str, list[str]] = {
    "0": ["zero"],
    "1": ["one"],
    "2": ["two"],
    "3": ["three"],
    "4": ["four"],
    "5": ["five"],
    "6": ["six"],
    "7": ["seven"],
    "8": ["eight"],
    "9": ["nine"],
    "10": ["teen", "ten"],
    "11": ["eleven"],
    "12": ["twelve"],
    "13": ["thirteen"],
    "14": ["fourteen"],
    "15": ["fifteen"],
    "16": ["sixteen"],
    "17": ["seventeen"],
    "18": ["eighteen"],
    "19": ["nineteen"],
    "20": ["twenty"],
    "30": ["thirty"],
    "40": ["forty"],
    "50": ["fifty"],
    "60": ["sixty"],
    "70": ["seventy"],
    "80": ["eighty"],
    "90": ["ninety"],
    "100": ["hundred"],
    "1000": ["thousand"],
    "1000000": ["million"],
    "1000000000": ["billion"],
    "1000000000000": ["trillion"],
    "1000000000000000": ["quadrillion"],
    "1000000000000000000": ["quintillion"],
    "0.5": ["half"],
    "0.25": ["quarter"],
    "0.001": ["thousandth"],
    "0.000001": ["millionth"],
    "0.000000001": ["billionth"],
}

# Phrases to strip from input
STRIPPED_PHRASES: list[str] = [
    "what's",
    "what is",
    "a ",
    r"\bof\b",
    "?",
    "calculate",
    "compute",
    "convert",
    "tell me",
    "give me",
    "the ",
]

# Physical constants word mappings
CONSTANT_WORDS: dict[str, list[str]] = {
    "na": ["avogadro", "avogadros", "avogadro number"],
    "r": ["gas constant", "ideal gas constant", "molar gas constant"],
    "h": ["planck", "planck constant"],
    "k": ["boltzmann", "boltzmann constant"],
    "c": ["speed of light", "speed of light in vacuum", "c zero"],
    "elementarycharge": ["elementary charge", "e charge"],
    "f": ["faraday", "faraday constant"],
    "u": ["atomic mass", "atomic mass unit", "amu"],
    "epsilon0": ["vacuum permittivity", "permittivity of free space"],
    "mu0": ["vacuum permeability", "permeability of free space", "magnetic constant"],
    "g": ["gravity", "standard gravity", "earth gravity"],
    "G": ["gravitational constant", "newton constant", "big g"],
    "me": ["electron mass"],
    "mp": ["proton mass"],
    "mn": ["neutron mass"],
    "re": ["electron radius", "classical electron radius"],
    "alpha": ["fine structure constant", "sommerfeld"],
    "rydberg": ["rydberg constant"],
    "stefan": ["stefan boltzmann", "stefan-boltzmann constant"],
    "wien": ["wien constant", "wien displacement"],
}


def _build_config() -> tuple[dict, dict]:
    """Build normalization configuration."""
    # Sort numbers by key descending for matching
    sorted_numbers = {k: NUMBER_WORDS[k] for k in sorted(NUMBER_WORDS.keys(), reverse=True)}

    # Build symbols list
    symbols = ["(", ")"] + list(OPERATOR_CONVERSIONS.keys())

    # Build word to operator mapping
    word_to_operator: dict[str, str] = {}
    for operator, words in OPERATOR_CONVERSIONS.items():
        for word in words:
            word_to_operator[word] = operator

    # Build word to number mapping (sorted by length for correct replacement)
    word_to_number: dict[str, str] = {}
    for num_val, words in NUMBER_WORDS.items():
        for word in words:
            word_to_number[word] = num_val
    sorted_word_to_number = dict(
        sorted(word_to_number.items(), key=lambda x: len(x[0]), reverse=True)
    )

    # Build word to constant mapping
    word_to_constant: dict[str, str] = {}
    for const_key, words in CONSTANT_WORDS.items():
        for word in words:
            word_to_constant[word] = const_key
    sorted_word_to_constant = dict(
        sorted(word_to_constant.items(), key=lambda x: len(x[0]), reverse=True)
    )

    # Build combined word replacement regex for performance (constants + operators)
    all_words = {}
    all_words.update(sorted_word_to_constant)
    all_words.update(sorted_word_to_number)
    all_words.update(word_to_operator)

    # Sort by length descending for correct matching
    sorted_all_words = dict(sorted(all_words.items(), key=lambda x: len(x[0]), reverse=True))

    # Build normalize config
    normalize_config = {
        "symbols": symbols,
        "convert": OPERATOR_CONVERSIONS,
        "word_to_operator": word_to_operator,
        "word_to_number": sorted_word_to_number,
        "word_to_constant": sorted_word_to_constant,
        "word_to_all": sorted_all_words,
        "numbers": sorted_numbers,
        "functions": FUNCTION_MAPPINGS,
    }

    # Compile regex patterns
    compiled_patterns: dict[str, re.Pattern[str]] = {
        "space": re.compile(r"\s+"),
        "point": re.compile(r"\."),
        "negative": re.compile(r"\-"),
        "thousands_separator": re.compile(r","),
        "inline_negative": re.compile(r"^[a-zA-Z]+-[a-zA-Z]+$"),
        "parenthesis": re.compile(r"\(|\)"),
        "operators": re.compile(f"^({'|'.join([re.escape(s) for s in symbols])}){{1}}$"),
        # Handle stripped_chars: literals get escaped, but regex patterns like \bof\b are preserved
        "stripped_chars": re.compile(f"({'|'.join([re.escape(p) if not (p.startswith(r'\\b') or r'\\b' in p) else p for p in STRIPPED_PHRASES])})"),
        "int": re.compile(r"^[-|+]?[0-9]\d*$"),
        "float": re.compile(r"^[-|+]?[0-9]\d*\.\d+?$"),
        "int_number_combine": re.compile(r"^[-|+|*]?[0-9]\d*$"),
        "valid_operations": re.compile(
            f"^({'|'.join([re.escape(s) for s in symbols] + [re.escape(f) for f in FUNCTION_MAPPINGS.values()] + [re.escape(c) for c in CONSTANT_WORDS.keys()])}){{1}}$"
        ),
    }

    return normalize_config, compiled_patterns


# Module-level config (computed once)
NORMALIZE, PATTERNS = _build_config()


def _rebuild_config() -> None:
    """Rebuild NORMALIZE and PATTERNS after adding custom words."""
    global NORMALIZE, PATTERNS
    NORMALIZE, PATTERNS = _build_config()


@lru_cache(maxsize=1024)
def check_if_number(token: str) -> dict:
    """Check if a token represents a number.

    Returns a dict with:
        bool: whether the token is a number
        converted: the parsed number or original string
        type: the original input type
    """
    patterns = PATTERNS
    if len(token) == 0:
        return {"bool": False, "converted": token, "type": type(token)}

    # Remove thousands separator
    cleaned = patterns["thousands_separator"].sub("", token)

    # Check for percentage (e.g., "50%")
    if cleaned.endswith("%"):
        num_part = cleaned[:-1]
        try:
            val = float(num_part) / 100
            return {"bool": True, "converted": val, "type": type(token)}
        except ValueError:
            pass

    # Check for complex number suffix (e.g., "3i", "4j")
    if cleaned.endswith(("i", "j")) and len(cleaned) > 1:
        num_part = cleaned[:-1]
        if num_part in ("+", "-"):
            # Just "+i" or "-i"
            return {
                "bool": True,
                "converted": complex(0, 1 if num_part == "+" else -1),
                "type": type(token),
            }
        try:
            val = float(num_part)
            return {"bool": True, "converted": complex(0, val), "type": type(token)}
        except ValueError:
            pass

    # Check for hex prefix (0x)
    if cleaned.lower().startswith("0x"):
        try:
            val = int(cleaned, 16)
            return {"bool": True, "converted": val, "type": type(token)}
        except ValueError:
            pass

    # Check for binary prefix (0b)
    if cleaned.lower().startswith("0b"):
        try:
            val = int(cleaned, 2)
            return {"bool": True, "converted": val, "type": type(token)}
        except ValueError:
            pass

    # Check for octal prefix (0o)
    if cleaned.lower().startswith("0o"):
        try:
            val = int(cleaned, 8)
            return {"bool": True, "converted": val, "type": type(token)}
        except ValueError:
            pass

    # Check if it's a plain number
    if patterns["int"].match(cleaned):
        return {"bool": True, "converted": int(cleaned), "type": type(token)}
    if patterns["float"].match(cleaned):
        return {"bool": True, "converted": float(cleaned), "type": type(token)}
    if patterns["int_number_combine"].match(cleaned):
        return {"bool": True, "converted": cleaned, "type": type(token)}

    # Check if it's a number with unit (use pre-computed sorted list)
    for unit in _UNITS_BY_LENGTH:
        if cleaned.endswith(unit):
            num_part = cleaned[: -len(unit)]
            if num_part:
                try:
                    val = float(num_part)
                    return {"bool": True, "converted": val, "type": type(token)}
                except ValueError:
                    pass

    return {"bool": False, "converted": token, "type": type(token)}


def validate_for_eval(tokens: list, patterns: Mapping[str, Pattern[str]]) -> bool:
    """Validate that all tokens are either numbers, valid operations, units, or known constants."""
    from .evaluator import _default_evaluator

    known_constants = set(_default_evaluator.CONSTANTS.keys())

    for token in tokens:
        # Skip tokens that look like function calls (contain parentheses)
        if "(" in token or ")" in token:
            continue
        if not check_if_number(token)["bool"]:
            if not patterns["valid_operations"].match(token):
                if not is_unit(token):
                    if token not in known_constants:
                        raise ValueError(f"Invalid token: {token}")
    return True


def combine_number_parts(
    number_parts: list, patterns: Mapping[str, Pattern[str]], split_tokens: list
) -> list:
    """Combine number parts into a single mathematical expression."""
    result = []
    for i, part in enumerate(number_parts):
        if i == 0:
            if i != len(number_parts) - 1 and part < 10 and number_parts[i + 1] == 10:
                result.append(f"{part + number_parts[i + 1]}")
            elif part != 10:
                result.append(str(part))
        else:
            if i != len(number_parts) - 1 and part < 10 and number_parts[i + 1] == 10:
                result.append(f"{part + number_parts[i + 1]}")
            elif part == 10 and number_parts[i - 1] < 10:
                pass
            elif part < 10:
                result.append(f"+{part}")
            elif number_parts[i - 1] < 10 and part < 100:
                result.append(f"+{part}")
            elif number_parts[i - 1] < 100:
                result.append(f"*{part}")
            else:
                result.append(f"+{part}")

    if patterns["negative"].match(split_tokens[0]):
        result.insert(0, "-")

    return result


def convert_numbers(number_info: list, patterns: Mapping[str, Pattern[str]]) -> str:
    """Convert a token that may contain number words to a numeric expression."""
    if number_info[1]["bool"]:
        return number_info[0]

    split_tokens = number_info[0].split("@")
    number_parts = []

    for token in split_tokens:
        check_result = check_if_number(token)
        if check_result["bool"]:
            number_parts.append(check_result["converted"])

    combined = combine_number_parts(number_parts, patterns, split_tokens)

    if validate_for_eval(combined, patterns):
        joined = "".join(combined)
        if joined:
            try:
                result = evaluate(joined)
                if isinstance(result, UnitValue):
                    return str(result.value)
                return str(result)
            except EvaluationError:
                return number_info[0]
        return number_info[0]

    return ""


def apply_math_functions(
    tokens: list, operators: dict, patterns: Mapping[str, Pattern[str]]
) -> list:
    """Convert function names to math function calls.

    Rules:
    - sin40 + 2 -> math.sin(40) + 2 (no paren means only first number is args)
    - sin(40+2) -> math.sin(40+2) (user's parens preserved)
    - sin of 40 -> math.sin(40)
    """
    output_tokens = []
    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token in operators["functions"]:
            output_tokens.append(operators["functions"][token])
            next_token = tokens[i + 1] if i + 1 < len(tokens) else None

            if next_token is not None and next_token == "(":
                pass
            else:
                output_tokens.append("(")

                while i + 1 < len(tokens):
                    next_token = tokens[i + 1]
                    is_operator = patterns["operators"].match(next_token) is not None

                    if is_operator and next_token != ".":
                        break
                    if next_token == ")":
                        break

                    output_tokens.append(next_token)
                    i += 1

                    if next_token == ".":
                        continue

                output_tokens.append(")")
        else:
            output_tokens.append(token)

        i += 1

    return output_tokens


def error_message(original: str, exception: BaseException, verbose: bool = False) -> None:
    """Print an error message based on the exception type."""
    exc_type = type(exception)
    if exc_type is ValueError:
        print(f"Unrecognized command: '{original}'", file=sys.stderr)
    elif exc_type is ZeroDivisionError:
        print(f"Can't divide by 0: '{original}'", file=sys.stderr)
    elif exc_type is EvaluationError:
        print(f"Evaluation error: {exception}", file=sys.stderr)
    else:
        if verbose:
            traceback.print_exc()
        else:
            print(f"Error: {exception}", file=sys.stderr)


def convert_from_human_handler(
    tokens: list,
    operators: dict,
    patterns: Mapping[str, Pattern[str]],
    original: str,
) -> tuple[list, bool]:
    """Convert human-readable number words to numeric values."""
    is_valid = False

    for i in range(len(tokens)):
        is_number = check_if_number(tokens[i])

        if not is_number["bool"]:
            replaced = tokens[i]
            word_to_number = operators.get("word_to_number", {})
            for word, num_val in word_to_number.items():
                replaced = replaced.replace(word, f"@{num_val}")
            tokens[i] = {0: replaced, 1: is_number}
        else:
            tokens[i] = {0: tokens[i], 1: is_number}

        try:
            tokens[i] = convert_numbers(tokens[i], patterns)
            is_valid = True
        except ValueError:
            tokens[i] = tokens[i][0] if isinstance(tokens[i], dict) else tokens[i]
            error_message(original, ValueError())
            break

    return tokens, is_valid


def _handle_negative_token(
    tokens: list,
    index: int,
    patterns: Mapping[str, Pattern[str]],
) -> tuple[list, list]:
    """Handle negative token patterns like 'five-six' or '5.-2'."""
    temp = tokens[index].split("-")
    tokens[index - 2] = f"{tokens[index - 2]}.{temp[0]}"
    tokens[index - 1] = ""
    tokens[index] = f"-{temp[1]}"
    return tokens, [index - 1]


def _should_split_number_minus(token: str) -> bool:
    """Check if token matches pattern: digit-sequence minus digit-sequence."""
    return bool(re.match(r"^\d+-\d+$", token))


def _should_handle_inline_negative(
    tokens: list, index: int, patterns: Mapping[str, Pattern[str]]
) -> bool:
    """Check if token should be handled as inline negative."""
    return bool(
        index >= 2
        and patterns["inline_negative"].match(tokens[index])
        and patterns["point"].match(tokens[index - 1])
        and not check_if_number(tokens[index - 2])["bool"]
    )


def _should_handle_decimal_negative(
    tokens: list, index: int, patterns: Mapping[str, Pattern[str]]
) -> bool:
    """Check if token should be handled as decimal negative."""
    return bool(
        index >= 2
        and patterns["negative"].search(tokens[index])
        and patterns["point"].match(tokens[index - 1])
        and check_if_number(tokens[index - 2])["bool"]
    )


def split_at_operators(
    expression: str, operators: dict, patterns: Mapping[str, Pattern[str]]
) -> list:
    """Split an expression string at operator boundaries."""
    # Escape operators for splitting
    for symbol in operators["symbols"]:
        if symbol != "-":
            expression = expression.replace(symbol, f"\\{symbol}\\")

    tokens = [t.strip() for t in expression.split("\\") if t.strip()]

    indices_to_remove = []

    for i in range(len(tokens)):
        is_num = check_if_number(tokens[i])["bool"]
        is_op = patterns["operators"].match(tokens[i]) is not None

        if not is_num and not is_op:
            if _should_handle_inline_negative(tokens, i, patterns):
                tokens, removed = _handle_negative_token(tokens, i, patterns)
                indices_to_remove.extend(removed)
            elif _should_handle_decimal_negative(tokens, i, patterns):
                tokens, removed = _handle_negative_token(tokens, i, patterns)
                indices_to_remove.extend(removed)
            elif _should_split_number_minus(tokens[i]):
                token = tokens[i]
                parts = token.split("-", 1)
                tokens[i] = parts[0]
                tokens.insert(i + 1, "-")
                tokens.insert(i + 2, parts[1])
            elif tokens[i][:1] != "-" and tokens[i - 1] != ".":
                tokens[i] = tokens[i].replace("-", "")
            elif patterns["negative"].match(tokens[i][:1]):
                tokens[i] = f"-{tokens[i][1:].replace('-', '')}"

    if indices_to_remove:
        for idx in reversed(indices_to_remove):
            tokens.pop(idx)

    return tokens


def normalize(expression: str, operators: dict, patterns: Mapping[str, Pattern[str]]) -> str:
    """Normalize an expression by removing filler words and applying conversions."""
    # Handle "N percent" -> "N/100" BEFORE word_to_all substitutions
    # This must come first so we get "0.2 of 150" then word_to_all converts "of" to "*"
    expression = re.sub(r"(\d+(?:\.\d+)?)\s+percent\b", lambda m: str(float(m.group(1)) / 100), expression, flags=re.IGNORECASE)

    # Use combined word replacement for efficiency (single pass)
    # Use word boundaries to avoid replacing parts of words
    word_to_all = operators.get("word_to_all", {})
    for word, replacement in sorted(word_to_all.items(), key=lambda x: len(x[0]), reverse=True):
        # Use regex with word boundaries to only match whole words
        expression = re.sub(r"\b" + re.escape(word) + r"\b", replacement, expression)

    # Strip phrases
    expression = patterns["stripped_chars"].sub("", expression)

    # Convert percentages (e.g., 50% -> 0.5)
    expression = re.sub(r"(\d+(?:\.\d+)?)%", lambda m: str(float(m.group(1)) / 100), expression)

    # Convert 'i' suffix to 'j' for complex numbers (e.g., 3+4i -> 3+4j)
    # Match: number followed by 'i' (not preceded by another letter)
    expression = re.sub(r"(\d)i\b", r"\1j", expression)
    # Handle standalone 'i' preceded by operators or at start
    expression = re.sub(r"(^|[+\-*/(])i\b", r"\g<1>1j", expression)

    # Replace whitespace outside parentheses with nothing
    # Preserve whitespace inside parentheses to separate function args
    result = []
    depth = 0
    for char in expression:
        if char == "(":
            depth += 1
            if depth > MAX_NESTING_DEPTH:
                raise ValueError(f"Expression nesting too deep (max {MAX_NESTING_DEPTH})")
            result.append(char)
        elif char == ")":
            depth -= 1
            result.append(char)
        elif char.isspace():
            if depth > 0:
                result.append(char)  # Keep space inside parentheses
            # Skip space outside parentheses
        else:
            result.append(char)

    expression = "".join(result)

    return expression


def _preprocess_units(expression: str) -> str:
    """Preprocess expression to add multiplication before units."""
    result = []
    i = 0
    depth = 0
    units = _UNITS_BY_LENGTH  # Use pre-computed list
    prefixes = _UNIT_PREFIXES  # Use pre-computed prefix set

    while i < len(expression):
        char = expression[i]

        if char == "(":
            depth += 1
            result.append(char)
            i += 1
        elif char == ")":
            depth -= 1
            result.append(char)
            i += 1
        elif char.isdigit():
            # Look for number followed by optional whitespace and unit
            num_start = i
            while i < len(expression) and (expression[i].isdigit() or expression[i] == "."):
                i += 1
            num = expression[num_start:i]

            # Skip whitespace between number and unit
            while i < len(expression) and expression[i].isspace():
                i += 1

            if i < len(expression):
                # Quick check: does the remaining start with a potential unit prefix?
                remaining = expression[i:]
                if remaining and remaining[0] not in prefixes:
                    # No unit possible, skip unit search
                    result.append(num)
                else:
                    # Check for unit using pre-computed sorted list
                    found_unit = False
                    for unit in units:
                        if remaining.startswith(unit):
                            result.append(num)
                            result.append("*")
                            result.append(unit)
                            i += len(unit)
                            found_unit = True
                            break
                    if not found_unit:
                        result.append(num)
            else:
                result.append(num)
        else:
            result.append(char)
            i += 1

    return "".join(result)


def _handle_unit_conversion_from_tokens(tokens: list) -> list:
    """Handle unit conversion patterns from tokens like ['2meters', 'in', 'feet'].

    Detects patterns like: [number+unit, 'in'/'to'/'into'/'as', target_unit]
    Converts to: ['convert(number*unit,target_unit)']
    """
    if len(tokens) < 3:
        return tokens

    # Look for pattern: token with number+unit followed by conversion word followed by unit
    conversion_words = {"in", "to", "into", "as"}

    for i in range(len(tokens) - 2):
        # Check if tokens[i] ends with a unit (has number prefix)
        token = tokens[i]
        for unit in _UNITS_BY_LENGTH:
            if token.endswith(unit):
                num_part = token[: -len(unit)]
                if num_part and num_part[-1].isdigit():
                    # Found number+unit pattern
                    from_unit = unit
                    from_unit_normalized = UNIT_ALIASES.get(from_unit, from_unit)

                    # Check conversion word (uppercase from operator split)
                    conv_word = tokens[i + 1].upper()
                    if conv_word in {"IN", "TO"}:
                        # Check target unit
                        to_token = tokens[i + 2]
                        to_unit_normalized = None

                        for unit2 in _UNITS_BY_LENGTH:
                            if to_token == unit2 or to_token.endswith(unit2):
                                to_unit_normalized = UNIT_ALIASES.get(unit2, unit2)
                                break

                        if to_unit_normalized and from_unit_normalized in UNIT_ALIASES:
                            from .units import get_unit_category, are_units_compatible

                            cat1 = get_unit_category(from_unit_normalized)
                            cat2 = get_unit_category(to_unit_normalized)

                            if (
                                cat1
                                and cat2
                                and are_units_compatible(from_unit_normalized, to_unit_normalized)
                            ):
                                # Replace the three tokens with the convert function
                                new_tokens = (
                                    tokens[:i]
                                    + [
                                        f"convert({num_part}*{from_unit_normalized},{to_unit_normalized})"
                                    ]
                                    + tokens[i + 3 :]
                                )
                                return new_tokens

    return tokens


def normalize_expression(
    expression: str,
    operators: dict,
    patterns: Mapping[str, Pattern[str]],
    skip_validation: bool = False,
) -> tuple[str, int]:
    """Normalize an expression without evaluating it.

    This is useful when you want to use a custom evaluator.

    Args:
        expression: The raw expression to normalize
        operators: The operators configuration dict
        patterns: The compiled regex patterns dict
        skip_validation: If True, skip token validation (for custom evaluators)

    Returns:
        tuple: (normalized_expression, exit_code) - normalized_expression is the
               normalized string, exit_code is 0 on success, non-zero on error
    """
    if len(expression) > MAX_INPUT_LENGTH:
        return f"Error: Input too long (max {MAX_INPUT_LENGTH} characters)", 2

    expression = normalize(expression, operators, patterns)
    tokens = split_at_operators(expression, operators, patterns)
    tokens, is_valid = convert_from_human_handler(tokens, operators, patterns, expression)

    if not is_valid:
        return "", 1

    tokens = apply_math_functions(tokens, operators, patterns)

    # Handle unit conversion patterns from tokens (e.g., "2m in feet" -> tokens ['2m', 'in', 'feet'])
    tokens = _handle_unit_conversion_from_tokens(tokens)
    joined = "".join(tokens)

    joined = _preprocess_units(joined)

    if not skip_validation:
        try:
            validate_for_eval(tokens, patterns)
        except ValueError:
            return "", 1

    return joined, 0


def run(
    expression: str,
    operators: dict,
    patterns: Mapping[str, Pattern[str]],
    output_format: str = "plain",
    show_expression: bool = True,
) -> tuple[Any, int]:
    """Process a single expression: normalize, convert, evaluate, and print result.

    Returns:
        tuple: (result, exit_code) - result is the evaluated value or None on error
    """
    original = expression
    joined, exit_code = normalize_expression(expression, operators, patterns)

    if exit_code != 0:
        if exit_code == 2:
            print(joined, file=sys.stderr)
        return None, exit_code

    try:
        result = evaluate(joined)
        if output_format == "json":
            import json

            if show_expression:
                print(json.dumps({"expression": joined, "result": str(result)}))
            else:
                print(json.dumps({"result": str(result)}))
        else:
            if show_expression:
                print(f"{joined} -> {result}")
            else:
                print(result)
        return result, 0
    except ZeroDivisionError as e:
        error_message(original, e)
        return None, 1
    except EvaluationError as e:
        error_message(original, e)
        return None, 1


def _run_repl(show_expression: bool = True) -> int:
    """Run interactive REPL mode."""
    import sys

    print("nl-calc interactive mode. Type 'help' for available commands, 'quit' or 'exit' to exit.")
    print()

    history: list[tuple[str, Any]] = []

    while True:
        try:
            line = input(">>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        if line.lower() in ("quit", "exit", "exit()"):
            break

        if line.lower() == "help":
            print_help()
            continue

        if line.lower() == "history":
            for expr, result in history:
                print(f"{expr} -> {result}")
            continue

        if line.lower() == "clear":
            history.clear()
            continue

        _, exit_code = run(line, NORMALIZE, PATTERNS, "plain", show_expression)

        if exit_code == 0:
            history.append((line, _))

    return 0


def _get_units_by_category() -> dict[str, list[str]]:
    """Get units organized by category from UNIT_CATEGORIES."""
    categories: dict[str, set[str]] = {}
    for unit, category in UNIT_CATEGORIES.items():
        if category not in categories:
            categories[category] = set()
        categories[category].add(unit)
    # Sort units within each category
    result = {}
    for cat in sorted(categories.keys()):
        result[cat] = sorted(categories[cat])
    return result


def print_help() -> None:
    """Print available operators, functions, and units."""
    # Get units by category programmatically
    units_by_cat = _get_units_by_category()

    lines: list[str] = []

    lines.append("Usage:")
    lines.append("  calc <expression>          Evaluate math expression")
    lines.append("  calc inspect <text>       Check for hidden characters/confusables")
    lines.append("  calc count <text>         Count characters (or count <text> <char>)")
    lines.append("  calc regex <pat> <text>  Test regex pattern against text")
    lines.append("")
    lines.append("Operators:")
    lines.append("  Arithmetic: +  -  *  /  **")
    lines.append("  Words: plus, minus, times, divided by, over, raised to")
    lines.append("")
    lines.append("Functions:")
    lines.append("  Trigonometry: sin, cos, tan, asin, acos, atan, atan2")
    lines.append("  Hyperbolic: sinh, cosh, tanh, asinh, acosh, atanh")
    lines.append("  Logarithmic: log, log10, log2, log1p, exp, expm1")
    lines.append("  Rounding: abs, floor, ceil, trunc, round, sign")
    lines.append("  Other: sqrt, pow, factorial, gcd, lcm, mean, median")
    lines.append("")
    lines.append("Constants:")
    lines.append("  pi, e, tau, inf, nan")
    lines.append("  avogadro, gasconstant, planck, boltzmann")
    lines.append("  c (speed of light), elementarycharge, faraday, amu")
    lines.append("")
    lines.append("Units:")

    # Build unit lines by category
    for category, units in units_by_cat.items():
        # Truncate long lists with "..."
        if len(units) > 15:
            display_units = units[:12] + ["..."]
        else:
            display_units = units
        lines.append(f"  {category.capitalize()}: {', '.join(display_units)}")

    lines.append("")
    lines.append("Unit conversion examples:")
    lines.append("  calc 30m + 100ft")
    lines.append("  calc 1km in miles")
    lines.append("  calc 100F to C")
    lines.append("  calc 1kg in lb")
    lines.append("")
    lines.append("Text tools examples:")
    lines.append("  calc inspect \"hello\"")
    lines.append("  calc inspect \"p\u0430ypal\"  ( Cyrillic 'a' instead of Latin)")
    lines.append("  calc count \"hello world\"")
    lines.append("  calc count \"hello\" l")
    lines.append("  calc regex \"^\\d+$\" \"12345\"")

    for line in lines:
        print(line)


def _cli_text_command(expression: str) -> int:
    """Handle text commands (inspect, count, regex) before math evaluation.

    Returns:
        0 if command was handled, 1 if expression should continue to math eval
    """
    parts = expression.strip().split()
    if not parts:
        return 1

    cmd = parts[0].lower()

    if cmd == "inspect":
        if len(parts) < 2:
            print("Usage: calc inspect <text>", file=sys.stderr)
            return 1
        text = " ".join(parts[1:])
        try:
            result = inspect_text(text, include_codepoints=False, include_confusables=True)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        if result["warnings"]:
            for w in result["warnings"]:
                kind = w["kind"].upper()
                print(f"\u2717 {kind}: {w['message']}")
        else:
            print("\u2713 No hidden characters")

        if result["confusables"]:
            print(f"\nConfusables found: {len(result['confusables'])}")
            for c in result["confusables"][:5]:
                print(f"  '{c['char']}' (looks like '{c['confusable_with']}') at {c['index']}")
        return 0

    if cmd == "count":
        if len(parts) < 2:
            print("Usage: calc count <text> [char]", file=sys.stderr)
            return 1
        text = " ".join(parts[1:])

        # Check if last part is a single char to count
        if len(parts) >= 3 and len(parts[-1]) == 1:
            char = parts[-1]
            text = " ".join(parts[1:-1])
            try:
                result = count_chars(text, target=char)
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1
            print(f"'{char}' appears {result['count']} time(s) in \"{text}\"")
            return 0

        # Default: show frequency table for multi-word, simple count for single
        try:
            if " " in text:
                result = count_chars(text)
                if isinstance(result, dict):
                    print(f"\"{text}\":")
                    print(f"  {len(text)} characters")
                    sorted_chars = sorted(result.items(), key=lambda x: (-x[1], x[0]))
                    for char, count in sorted_chars[:10]:
                        display = repr(char) if char != " " else "(space)"
                        print(f"  {display}: {count}")
                    if len(result) > 10:
                        print(f"  ... and {len(result) - 10} more unique chars")
                return 0
            else:
                result = count_chars(text)
                print(f"\"{text}\": {len(text)} character(s)")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        return 0

    if cmd == "regex":
        if len(parts) < 3:
            print("Usage: calc regex <pattern> <text>", file=sys.stderr)
            return 1
        pattern = parts[1]
        text = " ".join(parts[2:])
        try:
            result = regex_test(pattern, [text])
        except Exception as e:
            print(f"Error: Invalid regex pattern: {e}", file=sys.stderr)
            return 1

        if not result["valid_pattern"]:
            print(f"\u2717 Invalid regex pattern: {pattern}", file=sys.stderr)
            return 1

        if result["results"]:
            r = result["results"][0]
            if r["matches"]:
                print(f"\u2713 Match: '{r['sample']}'")
                if r["groups"]:
                    print(f"  Groups: {r['groups']}")
                if r["groupdict"]:
                    print(f"  Named groups: {r['groupdict']}")
            else:
                print(f"\u2717 No match")
        else:
            print(f"\u2717 No match")
        return 0

    return 1  # Not a text command, continue to math eval


def main() -> int:
    """Main entry point for CLI."""
    import os
    from nl_calc import __version__

    parser = argparse.ArgumentParser(
        description="Natural language math expression calculator",
        add_help=False,
    )
    parser.add_argument(
        "expression", nargs="*", help="Expression to evaluate (e.g., 'five plus two')"
    )
    parser.add_argument(
        "-h", "--help", action="store_true", help="Show help and available operators"
    )
    parser.add_argument(
        "--usage", action="store_true", help="Show full usage information and examples"
    )
    parser.add_argument("-v", "--version", action="store_true", help="Show version information")
    parser.add_argument("-q", "--quiet", action="store_true", help="Suppress expression in output")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")
    parser.add_argument(
        "-e",
        "--expression",
        dest="single_expr",
        metavar="<expr>",
        help="Evaluate a single expression (useful for piping)",
    )
    parser.add_argument(
        "-i", "--interactive", action="store_true", help="Start interactive REPL mode"
    )
    parser.add_argument(
        "-s",
        "--show",
        action="store_true",
        help="Show expression in output (default for interactive)",
    )
    parser.add_argument(
        "--mcp", action="store_true", help="Run as MCP server for exact text tools"
    )

    args = parser.parse_args()

    if args.mcp:
        from nl_calc.mcp.server import mcp_main
        return mcp_main()

    if args.version:
        print(f"nl-calc {__version__}")
        return 0

    if args.usage:
        print_help()
        return 0

    if args.help or (not args.expression and not args.single_expr and not args.interactive):
        parser.print_help()
        return 0

    if args.interactive:
        return _run_repl(show_expression=args.show)

    if args.single_expr:
        expression = args.single_expr
        quiet_by_default = True
    else:
        expression = " ".join(args.expression)
        quiet_by_default = False

    # Detect shell glob expansion (e.g., "python nl_calc.py 30 * 3" expands "*" to files)
    if args.expression and len(args.expression) > 1:
        # Check if any argument is a file or directory that exists (likely from glob expansion)
        cwd = os.getcwd()
        glob_indicators = []
        for arg in args.expression:
            path = os.path.join(cwd, arg)
            if os.path.exists(path) and arg not in (".", ".."):
                glob_indicators.append(arg)

        if glob_indicators:
            print("Error: Possible shell glob expansion detected.", file=sys.stderr)
            print(
                f"The '*' character was expanded to file(s): {glob_indicators[:5]}{'...' if len(glob_indicators) > 5 else ''}",
                file=sys.stderr,
            )
            print("Please quote your expression:", file=sys.stderr)
            print(f'  calc "{" ".join(args.expression)}"', file=sys.stderr)
            print("Or use -e flag:", file=sys.stderr)
            print(f'  calc -e "{" ".join(args.expression)}"', file=sys.stderr)
            return 1

    # Try text commands first (inspect, count, regex)
    cmd_result = _cli_text_command(expression)
    if cmd_result == 0:
        return 0  # Command was handled

    output_format = "json" if args.json else "plain"
    if args.quiet:
        show_expression = False
    elif args.show:
        show_expression = True
    elif quiet_by_default:
        show_expression = False
    else:
        show_expression = False

    _, exit_code = run(expression, NORMALIZE, PATTERNS, output_format, show_expression)
    return exit_code


if __name__ == "__main__":
    main()
