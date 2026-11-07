from backend.app.schemas import Finding
from backend.app.utils.citations import build_source_catalog, extract_citation_indices


def test_extract_citation_indices():
    text = "BitDelta leads in derivatives [1]. CoinDCX has high compliance [2, 3] while ZebPay has monthly fee [4]."
    indices = extract_citation_indices(text)
    assert indices == [1, 2, 3, 4]


def test_build_source_catalog():
    findings = [
        Finding(
            entity="BitDelta",
            aspect="product",
            claim="Multi-asset platform with 400+ pairs.",
            evidence_quote="400+ pairs on platform",
            source_url="https://bitdelta.com",
            source_type="web",
        ),
        Finding(
            entity="BitDelta",
            aspect="trust",
            claim="Multi-sig security custody architecture.",
            evidence_quote="multi-sig cold storage custody",
            source_url="https://bitdelta.com",
            source_type="web",
        ),
        Finding(
            entity="CoinDCX",
            aspect="compliance",
            claim="Registered with FIU-IND.",
            evidence_quote="registered with FIU-IND reporting registry",
            doc_name="fiu_report.pdf",
            page=2,
            source_type="doc",
        ),
    ]

    sources, mapping = build_source_catalog(findings)
    assert len(sources) == 2
    assert sources[0].id == 1
    assert sources[0].domain == "bitdelta.com"
    assert len(sources[0].supported_claims) == 2

    assert sources[1].id == 2
    assert sources[1].doc_name == "fiu_report.pdf"
    assert sources[1].page == 2
