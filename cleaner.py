"""Data cleaning: normalize values, validate records, remove duplicates."""
import re, unicodedata

def normalize(value):
    if value is None: return None
    if isinstance(value, str):
        value = unicodedata.normalize("NFKC", value)
        value = re.sub(r"\s+", " ", value).strip()
        return value or None
    return value

def clean(records: list[dict], required: list[str] | None = None) -> list[dict]:
    seen, out = set(), []
    for r in records:
        r = {k: normalize(v) for k, v in r.items()}
        if all(v is None for v in r.values()): continue
        if required and any(r.get(k) is None for k in required): continue
        key = tuple(sorted(r.items(), key=lambda kv: kv[0]))
        if key in seen: continue
        seen.add(key); out.append(r)
    return out
