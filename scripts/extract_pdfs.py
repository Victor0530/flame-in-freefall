"""Download and extract text from official NASA PDFs for the retrieval corpus."""

from __future__ import annotations

import re
import urllib.request
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CORPUS = ROOT / "data" / "corpus"

PDFS = {
    "researchers_guide_2015.pdf": "https://www.nasa.gov/wp-content/uploads/2016/05/np-2015-10-034-jsc_combustion_in_reduced_gravity-iss-mini-book-011116-508.pdf",
}

PAGES = {
    "combustion_science_page.html": "https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/",
}


def get(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    CORPUS.mkdir(parents=True, exist_ok=True)

    for name, url in PDFS.items():
        path = RAW / name
        if not path.exists():
            print(f"downloading {name} ...")
            path.write_bytes(get(url))
        reader = PdfReader(str(path))
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        out = CORPUS / (path.stem + ".txt")
        out.write_text(text, encoding="utf-8")
        print(f"{name}: {len(reader.pages)} pages, {len(text)} chars -> {out.name}")

    for name, url in PAGES.items():
        path = RAW / name
        if not path.exists():
            path.write_bytes(get(url))
        html = path.read_text(encoding="utf-8", errors="ignore")
        body = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
        text = re.sub(r"<[^>]+>", " ", body)
        text = re.sub(r"&[a-z]+;", " ", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n", text)
        out = CORPUS / (path.stem + ".txt")
        out.write_text(text, encoding="utf-8")
        print(f"{name}: {len(text)} chars -> {out.name}")


if __name__ == "__main__":
    main()
