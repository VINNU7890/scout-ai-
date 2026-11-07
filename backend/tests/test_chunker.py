from backend.app.tools.rag import DocumentParser


def test_chunk_text_basic():
    text = "Hello world. " * 100
    chunks = DocumentParser.chunk_text(text, chunk_size=200, overlap=50)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 250


def test_chunk_text_empty():
    assert DocumentParser.chunk_text("") == []
    assert DocumentParser.chunk_text("   \n\n  ") == []


def test_chunk_text_small():
    text = "Small brief text."
    chunks = DocumentParser.chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) == 1
    assert chunks[0] == text
