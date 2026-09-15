import bleach
from markdown_it import MarkdownIt

_ALLOWED_TAGS = ["p", "br", "strong", "em", "a", "ul", "ol", "li", "blockquote", "code", "pre", "h1", "h2", "h3", "h4"]
_ALLOWED_ATTRIBUTES = {"a": ["href", "title", "rel"]}
_markdown = MarkdownIt("commonmark", {"html": False, "linkify": True})


def sanitize_markdown(value: str) -> str:
    return bleach.clean(value.strip(), tags=[], attributes={}, strip=True)


def render_markdown(value: str) -> str:
    rendered = _markdown.render(value)
    return bleach.clean(rendered, tags=_ALLOWED_TAGS, attributes=_ALLOWED_ATTRIBUTES, protocols=["http", "https", "mailto"], strip=True)


def sanitize_comment(value: str) -> str:
    return bleach.clean(value.strip(), tags=[], attributes={}, strip=True)
