"""CSV, JSON and SQLite exports."""
import csv, json, os, sqlite3, re
from datetime import datetime

def export(records: list[dict], fmt: str, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    cols = list(dict.fromkeys(k for r in records for k in r))
    if fmt == "csv":
        path = os.path.join(out_dir, f"data_{stamp}.csv")
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(records)
    elif fmt == "json":
        path = os.path.join(out_dir, f"data_{stamp}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    elif fmt == "sqlite":
        path = os.path.join(out_dir, "data.db")
        safe = [re.sub(r"\W", "_", c) for c in cols]
        con = sqlite3.connect(path)
        with con:
            con.execute(f"CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, scraped_at TEXT, "
                        + ", ".join(f'"{c}" TEXT' for c in safe) + ")")
            existing = {row[1] for row in con.execute("PRAGMA table_info(records)")}
            for c in safe:
                if c not in existing: con.execute(f'ALTER TABLE records ADD COLUMN "{c}" TEXT')
            q = f'INSERT INTO records (scraped_at, {", ".join(chr(34)+c+chr(34) for c in safe)}) VALUES (?{", ?"*len(safe)})'
            con.executemany(q, [[stamp] + [r.get(c) for c in cols] for r in records])
        con.close()
    else:
        raise ValueError(fmt)
    return path
