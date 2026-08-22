import re


def normalize_whitespace(text: str) -> str:
    text = text.replace("\t", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()

def strip_boilerplate(text: str) -> str:
    lines = text.splitlines()

    cleaned_lines = [
        line
        for line in lines
        if line.strip()
        and not re.fullmatch(r"[-_=*]{3,}", line.strip())
    ]

    return "\n".join(cleaned_lines).strip()

def clean(text: str) -> str:
    text = normalize_whitespace(text)
    text = strip_boilerplate(text)
    return text