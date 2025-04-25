# clean_markdown.py
import re
from collections import OrderedDict


def normalize_quotes(text: str) -> str:
    return (
        text
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
        .replace(" ", " ")  # Also normalize non-breaking spaces
    )


def replace_all_dashes(text: str) -> str:
    dash_like = [
        '\u2014',  # em dash
        '\u2013',  # en dash
        '\u2010',  # hyphen
        '\u2011',  # non-breaking hyphen
        '\u2012',  # figure dash
        '\u2015',  # horizontal bar
        '\ufe58',  # small em dash
        '\uff0d',  # fullwidth hyphen-minus
    ]
    for dash in dash_like:
        text = re.sub(rf'\s*{re.escape(dash)}\s*', '--', text)
    return text


def extract_and_remove_links(text: str) -> tuple[str, list[str]]:
    link_pattern = re.compile(r'\[([^]]+)]\((https?:[^)#\s]+)(?:#:~:[^)]+)?\)')
    links: OrderedDict[tuple[str, str], None] = OrderedDict()

    def replace_link(match: re.Match) -> str:
        name, url = match.groups()
        key = (name.strip(), url.strip())
        if key not in links:
            links[key] = None
        return ''

    # Preserve code and inline code blocks before substitution
    code_block_pattern = re.compile(r'```.*?```', re.DOTALL)
    inline_code_pattern = re.compile(r'`[^`]*`')

    code_blocks: list[str] = []
    inline_blocks: list[str] = []

    def hide_code_block(match: re.Match) -> str:
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks) - 1}__"

    def hide_inline_code(match: re.Match) -> str:
        inline_blocks.append(match.group(0))
        return f"__INLINE_CODE_{len(inline_blocks) - 1}__"

    text = code_block_pattern.sub(hide_code_block, text)
    text = inline_code_pattern.sub(hide_inline_code, text)

    cleaned_text = link_pattern.sub(replace_link, text)

    # Remove any residual empty parentheses only outside protected blocks
    cleaned_text = re.sub(r'(?<!\w)\(\s*\)', '', cleaned_text)

    # Restore inline and code blocks
    for i, block in enumerate(inline_blocks):
        cleaned_text = cleaned_text.replace(f"__INLINE_CODE_{i}__", block)
    for i, block in enumerate(code_blocks):
        cleaned_text = cleaned_text.replace(f"__CODE_BLOCK_{i}__", block)

    sources = [f"{i + 1}. [{name}]({url})" for i, (name, url) in enumerate(links.keys())]
    return cleaned_text, sources


def wrap_sentences(text: str) -> str:
    code_block_pattern = re.compile(r'```.*?```', re.DOTALL)
    placeholder = "__CODE_BLOCK__"
    code_blocks = []

    def extract_code_block(match: re.Match) -> str:
        code_blocks.append(match.group(0))
        return placeholder

    text = code_block_pattern.sub(extract_code_block, text)

    def wrap_paragraph(paragraph: str) -> str:
        if not paragraph.strip():
            return paragraph
        return re.sub(r'(?<=[.!?]) +', '\n', paragraph.strip())

    paragraphs = text.split("\n\n")
    wrapped_paragraphs = [wrap_paragraph(p) for p in paragraphs]
    wrapped_text = "\n\n".join(wrapped_paragraphs)

    for cb in code_blocks:
        wrapped_text = wrapped_text.replace(placeholder, cb, 1)

    return wrapped_text


def remove_emphasis(text: str) -> str:
    """
    Removes Markdown bold (** **) and italics (_ _ or * *) from the input string,
    preserving content inside fenced code blocks (```), and inline code fragments (`code`).
    Handles multiline emphasis spans.
    """
    # Pattern to split out fenced code blocks and inline code
    code_pattern = re.compile(r'(```[\s\S]*?```|`[^`]*`)')

    parts = code_pattern.split(text)
    result_parts: list[str] = []

    # Regex to remove strong (bold) and italic markers
    strong_re = re.compile(r'(?:\*\*|__)(.+?)(?:\*\*|__)', re.S)
    italic_re = re.compile(r'(?:\*|_)(.+?)(?:\*|_)', re.S)

    for part in parts:
        # If this part is a code block or inline code, leave it unchanged
        if code_pattern.fullmatch(part):
            result_parts.append(part)
        else:
            # Remove emphasis markers in non-code text
            new_part = part
            prev_part = None
            while prev_part != new_part:
                prev_part = new_part
                new_part = strong_re.sub(r'\1', new_part)
                new_part = italic_re.sub(r'\1', new_part)
            result_parts.append(new_part)

    return ''.join(result_parts)


def clean_markdown(markdown: str) -> str:
    """
    Clean a Markdown string by:
    1. Replacing curly quotes and apostrophes with straight versions.
    2. Replacing all dash-like characters with '--'.
    3. Removing inline URLs and collecting them into a numbered '## References' section.
    4. Structurally wrapping sentences (but not inside code blocks).

    Args:
        markdown: A string containing Markdown-formatted text.

    Returns:
        A cleaned Markdown string with formatted sentences and a references section.
    """
    markdown = normalize_quotes(markdown)
    markdown = replace_all_dashes(markdown)
    markdown, sources = extract_and_remove_links(markdown)
    markdown = wrap_sentences(markdown)
    markdown = remove_emphasis(markdown)

    if sources:
        markdown = markdown.rstrip() + "\n\n## References\n" + "\n".join(sources) + "\n"

    return markdown
