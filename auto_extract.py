"""Automatic extraction: no selectors needed. Pulls common data from any page."""
from urllib.parse import urljoin

def extract_auto(soup, page_url: str, kinds: set) -> list[dict]:
    rows = []
    if "headings" in kinds:
        for h in soup.find_all(["h1", "h2", "h3"]):
            t = h.get_text(" ", strip=True)
            if t: rows.append({"type": "heading", "level": h.name, "text": t, "link": "", "page": page_url})
    if "paragraphs" in kinds:
        for p in soup.find_all("p"):
            t = p.get_text(" ", strip=True)
            if len(t) > 30: rows.append({"type": "paragraph", "level": "", "text": t, "link": "", "page": page_url})
    if "links" in kinds:
        for a in soup.find_all("a", href=True):
            href = urljoin(page_url, a["href"])
            if href.startswith("http"):
                rows.append({"type": "link", "level": "", "text": a.get_text(" ", strip=True), "link": href, "page": page_url})
    if "images" in kinds:
        for img in soup.find_all("img", src=True):
            rows.append({"type": "image", "level": "", "text": img.get("alt", ""), "link": urljoin(page_url, img["src"]), "page": page_url})
    if "emails" in kinds:
        import re
        for e in sorted(set(re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", soup.get_text(" ")))):
            rows.append({"type": "email", "level": "", "text": e, "link": "", "page": page_url})
    if "tables" in kinds:
        for ti, table in enumerate(soup.find_all("table"), 1):
            for tr in table.find_all("tr"):
                cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
                if any(cells):
                    rows.append({"type": f"table{ti}", "level": "", "text": " | ".join(cells), "link": "", "page": page_url})
    return rows

def find_next_page(soup, page_url: str):
    """Guess a 'next page' link."""
    a = soup.find("a", rel="next") or soup.select_one("li.next a, a.next, .pagination .next a")
    if not a:
        for cand in soup.find_all("a", href=True):
            if cand.get_text(strip=True).lower() in ("next", "next »", "next ›", "»", "›", "next page", "next →"):
                a = cand; break
    return urljoin(page_url, a["href"]) if a and a.get("href") else None
