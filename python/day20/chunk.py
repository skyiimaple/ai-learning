"""固定窗口切块（字符级，够用版）。"""

from pathlib import Path


def chunk_text(text: str, *, chunk_size: int = 180, overlap: int = 40) -> list[str]:
    """将文本按字符级切块。"""
    chunks: list[str] = []
    text = " ".join(text.split())
    if not text:
        return chunks
    if overlap >= chunk_size:
        raise ValueError("overlap must be less than chunk_size")
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


def load_docs(docs_dir: Path) -> list[dict]:
    """返回[{id,source,text},...]."""
    rows: list[dict] = []
    docs = sorted(docs_dir.glob("*.md"))  # 按文件名排序
    for doc in docs:
        raw = doc.read_text(encoding="utf-8")
        file = enumerate(chunk_text(raw))
        for i, chunk in file:
            rows.append({"id": f"{doc.stem}-{i}", "source": doc.name, "text": chunk})
    return rows


if __name__ == "__main__":
    docs = load_docs(Path(__file__).with_name("docs"))
    print(f"chunks count: {len(docs)}")
    for d in docs[:3]:
        print(d["id"], d["source"], d["text"][:60], "...")
