"""Data extraction: locate elements and pull content via CSS selectors.

Field spec: "selector" -> text, "selector@attr" -> attribute, "@attr" -> attr of item itself.
"""
from urllib.parse import urljoin

def _extract_field(item, spec: str, base_url: str):
    sel, _, attr = spec.partition("@")
    el = item.select_one(sel) if sel.strip() else item
    if el is None:
        return None
    if attr:
        val = el.get(attr)
        if val and attr in ("href", "src"):
            val = urljoin(base_url, val)
        return val
    return el.get_text(" ", strip=True)

def extract(soup, cfg, page_url: str) -> list[dict]:
    return [{name: _extract_field(item, spec, page_url) for name, spec in cfg.fields.items()}
            for item in soup.select(cfg.item_selector)]
