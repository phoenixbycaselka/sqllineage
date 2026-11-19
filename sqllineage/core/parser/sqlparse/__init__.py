import re

from sqlparse import tokens
from sqlparse.keywords import KEYWORDS, PROCESS_AS_KEYWORD, SQL_REGEX


def _patch_adding_builtin_type() -> None:
    KEYWORDS["STRING"] = tokens.Name.Builtin
    KEYWORDS["DATETIME"] = tokens.Name.Builtin


def _patch_updating_lateral_view_lexeme() -> None:
    for i, (regex, lexeme) in enumerate(SQL_REGEX):
        rgx = re.compile(regex, re.IGNORECASE | re.UNICODE).match
        if rgx("LATERAL VIEW EXPLODE(col)"):
            new_regex = r"(LATERAL\s+VIEW\s+)(OUTER\s+)?(EXPLODE|INLINE|PARSE_URL_TUPLE|POSEXPLODE|STACK|JSON_TUPLE)\b"
            SQL_REGEX[i] = (new_regex, lexeme)
            break


def _patch_keyword_before_parenthesis() -> None:
    # sqlparse lexes any word directly followed by "(" as a function name, so in
    # EXISTS(SELECT ...), SELECT(SELECT ...) or LATERAL(SELECT ...) the keyword
    # becomes a function and the subquery is lost. Keep these keywords keywords.
    for i, (regex, _) in enumerate(SQL_REGEX):
        if regex == r"[A-ZÀ-Ü]\w*(?=\()":
            SQL_REGEX.insert(i, (r"(EXISTS|SELECT|LATERAL)(?=\()", PROCESS_AS_KEYWORD))
            break


def _monkey_patch() -> None:
    _patch_adding_builtin_type()
    _patch_updating_lateral_view_lexeme()
    _patch_keyword_before_parenthesis()


_monkey_patch()
