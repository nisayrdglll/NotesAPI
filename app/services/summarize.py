def simple_summarize(text: str) -> str:
    if "." in text and len(text.split(".")) > 1:
        first = text.split(".")[0].strip()
        if 20 <= len(first) <= 240:
            return first
    return (text[:240] + "…") if len(text) > 240 else text
