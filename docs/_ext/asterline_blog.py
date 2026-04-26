"""Sphinx extension for rendering community blog pages from frontmatter."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from sphinx.application import Sphinx


class BlogEntry(BaseModel):
    """Validated metadata for one community blog item."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9_.-]*$")
    title: str = Field(min_length=1)
    summary: str = Field(min_length=1, max_length=260)
    author: str = Field(min_length=1)
    published_at: date
    category: str = "社区文章"
    tags: list[str] = Field(default_factory=list)
    url: str | None = None
    doc: str | None = None
    featured: bool = False

    @field_validator("url")
    @classmethod
    def _validate_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        parsed = urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("url must be absolute http(s)")
        return value

    @field_validator("tags", mode="before")
    @classmethod
    def _normalize_tags(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        if not isinstance(value, list):
            raise TypeError("tags must be a list")
        return [str(item).strip() for item in value if str(item).strip()]


class AsterlineBlogDirective(Directive):
    """Render the full blog landing page or a compact card list."""

    has_content = False
    option_spec = {
        "title": directives.unchanged,
        "layout": directives.unchanged,
        "limit": directives.nonnegative_int,
    }

    def run(self) -> list[nodes.Node]:
        env = self.state.document.settings.env
        app = env.app
        entries = load_blog_entries(app.srcdir, list(app.config.asterline_blog_registry_paths))
        limit = self.options.get("limit")
        if limit is not None:
            entries = entries[: int(limit)]
        title = self.options.get("title", "Asterline Blog")
        layout = str(self.options.get("layout", "index")).strip().lower()
        if layout == "cards":
            html = _render_cards_section(entries, title=title, app=app, current_doc=env.docname)
        else:
            html = _render_blog_index(entries, title=title, app=app, current_doc=env.docname)
        return [nodes.raw("", html, format="html")]


def setup(app: Sphinx) -> dict[str, Any]:
    """Register blog directives and assets."""

    app.add_config_value(
        "asterline_blog_registry_paths",
        ["community/blog/posts"],
        "env",
        types=frozenset({list, tuple}),
    )
    app.add_directive("asterline-blog", AsterlineBlogDirective)
    app.add_css_file("asterline-blog.css")
    app.connect("source-read", _strip_frontmatter_on_source_read)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def load_blog_entries(source_dir: str | Path, registry_paths: list[str] | tuple[str, ...]) -> list[BlogEntry]:
    """Load community blog entries from RST or Markdown files with YAML frontmatter."""

    root = Path(source_dir).resolve()
    entries: list[BlogEntry] = []
    for raw_path in registry_paths:
        path = (root / raw_path).resolve()
        files: list[Path]
        if path.is_dir():
            files = sorted([*path.glob("*.rst"), *path.glob("*.md")])
        elif path.is_file():
            files = [path]
        else:
            continue
        for file_path in files:
            try:
                frontmatter, _ = parse_frontmatter(file_path.read_text(encoding="utf-8"))
                if not frontmatter:
                    raise ValueError("missing YAML frontmatter")
                payload = dict(frontmatter)
                payload.setdefault("id", file_path.stem.replace("_", "-"))
                payload.setdefault("doc", _doc_href(root, file_path))
                entries.append(BlogEntry.model_validate(payload))
            except (OSError, ValidationError, ValueError) as exc:
                raise ValueError(f"invalid Asterline blog entry {file_path}: {exc}") from exc
    return sorted(entries, key=lambda entry: entry.published_at, reverse=True)


def parse_frontmatter(source: str) -> tuple[dict[str, Any], str]:
    """Parse a small YAML-frontmatter subset from one article source."""

    lines = source.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, source
    try:
        end_index = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError("unterminated frontmatter") from exc
    payload = _parse_yaml_subset(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    return payload, body


def _parse_yaml_subset(lines: list[str]) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"invalid frontmatter line: {line!r}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        if not raw_value:
            items: list[str] = []
            while index < len(lines) and lines[index].lstrip().startswith("- "):
                items.append(_unquote(lines[index].split("- ", 1)[1].strip()))
                index += 1
            payload[key] = items
            continue
        if raw_value.startswith("[") and raw_value.endswith("]"):
            inner = raw_value[1:-1].strip()
            payload[key] = [_unquote(item.strip()) for item in inner.split(",") if item.strip()]
        elif raw_value.lower() in {"true", "false"}:
            payload[key] = raw_value.lower() == "true"
        else:
            payload[key] = _unquote(raw_value)
    return payload


def _strip_frontmatter_on_source_read(app: Sphinx, docname: str, source: list[str]) -> None:
    registry_paths = [str(path).rstrip("/") for path in app.config.asterline_blog_registry_paths]
    if not any(docname.startswith(path) for path in registry_paths):
        return
    _, body = parse_frontmatter(source[0])
    source[0] = body


def _render_blog_index(entries: list[BlogEntry], *, title: str, app: Sphinx, current_doc: str) -> str:
    if not entries:
        return _render_cards_section(entries, title=title, app=app, current_doc=current_doc)
    latest = entries[0]
    latest_three = entries[:3]
    html = [
        '<section class="asterline-blog asterline-blog--index">',
        '<div class="asterline-blog-hero">',
        '<div>',
        '<span class="asterline-blog-hero__eyebrow">最新消息</span>',
        f"<h2>{_escape_html(latest.title)}</h2>",
        f"<p>{_escape_html(latest.summary)}</p>",
        '<div class="asterline-blog-card__meta">',
        f"<span>{_escape_html(latest.category)}</span>",
        f"<time>{latest.published_at.isoformat()}</time>",
        f"<span>{_escape_html(latest.author)}</span>",
        "</div>",
        "</div>",
        f'<a class="asterline-blog-hero__link" href="{_escape_attr(_href(latest, app, current_doc))}">阅读最新文章</a>',
        "</div>",
        _render_cards_section(latest_three, title="最新三篇", app=app, current_doc=current_doc),
        '<section class="asterline-blog-list">',
        f"<h2>{_escape_html(title)}</h2>",
        "<p>所有文章按发布时间倒序排列。</p>",
        '<div class="asterline-blog-list__items">',
    ]
    for entry in entries:
        html.append(_render_list_item(entry, app, current_doc))
    html.extend(["</div>", "</section>", "</section>"])
    return "\n".join(html)


def _render_cards_section(entries: list[BlogEntry], *, title: str, app: Sphinx, current_doc: str) -> str:
    html = [
        '<section class="asterline-blog">',
        '<div class="asterline-blog__header">',
        f"<h2>{_escape_html(title)}</h2>",
        "<p>来自维护者和社区的设计笔记、发布记录、接入经验与案例复盘。</p>",
        "</div>",
    ]
    if not entries:
        html.append('<p class="asterline-blog__empty">暂无文章。</p>')
    else:
        html.append('<div class="asterline-blog__grid">')
        for entry in entries:
            html.append(_render_card(entry, app, current_doc))
        html.append("</div>")
    html.append("</section>")
    return "\n".join(html)


def _render_card(entry: BlogEntry, app: Sphinx, current_doc: str) -> str:
    tags = "".join(f"<span>#{_escape_html(tag)}</span>" for tag in entry.tags)
    featured = '<span class="asterline-blog-card__featured">精选</span>' if entry.featured else ""
    return (
        '<article class="asterline-blog-card">'
        '<div class="asterline-blog-card__meta">'
        f"<span>{_escape_html(entry.category)}</span>"
        f"<time>{entry.published_at.isoformat()}</time>"
        f"{featured}"
        "</div>"
        f'<h3><a href="{_escape_attr(_href(entry, app, current_doc))}">{_escape_html(entry.title)}</a></h3>'
        f"<p>{_escape_html(entry.summary)}</p>"
        f'<div class="asterline-blog-card__footer"><span>{_escape_html(entry.author)}</span>'
        f"<div>{tags}</div></div>"
        "</article>"
    )


def _render_list_item(entry: BlogEntry, app: Sphinx, current_doc: str) -> str:
    tags = " ".join(f"<span>#{_escape_html(tag)}</span>" for tag in entry.tags)
    return (
        '<article class="asterline-blog-list__item">'
        f"<time>{entry.published_at.isoformat()}</time>"
        "<div>"
        f'<h3><a href="{_escape_attr(_href(entry, app, current_doc))}">{_escape_html(entry.title)}</a></h3>'
        f"<p>{_escape_html(entry.summary)}</p>"
        f'<div class="asterline-blog-list__meta"><span>{_escape_html(entry.category)}</span>'
        f"<span>{_escape_html(entry.author)}</span>{tags}</div>"
        "</div>"
        "</article>"
    )


def _doc_href(root: Path, file_path: Path) -> str:
    return file_path.relative_to(root).with_suffix(".html").as_posix()


def _href(entry: BlogEntry, app: Sphinx, current_doc: str) -> str:
    if entry.url:
        return entry.url
    if not entry.doc:
        return "#"
    target_doc = entry.doc.removesuffix(".html")
    return app.builder.get_relative_uri(current_doc, target_doc)


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _escape_attr(value: str) -> str:
    return _escape_html(value).replace("'", "&#x27;")
