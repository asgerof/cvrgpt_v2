import re

CVR_RE = re.compile(r"^\d{8}$")


def assert_cvr(value: str) -> str:
    if not CVR_RE.match(value):
        raise ValueError("CVR must be exactly 8 digits")
    return value
