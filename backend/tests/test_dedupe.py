from backend.app.agent.nodes.web_researcher import deduplicate_findings
from backend.app.schemas import Finding


def test_deduplicate_identical_claims():
    f1 = Finding(
        entity="BitDelta",
        aspect="product",
        claim="BitDelta supports 400+ crypto spot trading pairs and copy trading.",
        evidence_quote="supports 400+ crypto pairs",
        source_url="https://bitdelta.com/1",
        source_type="web",
    )
    f2 = Finding(
        entity="BitDelta",
        aspect="product",
        claim="BitDelta supports 400+ crypto spot trading pairs and copy trading.",
        evidence_quote="supports 400+ crypto pairs",
        source_url="https://bitdelta.com/2",
        source_type="web",
    )
    f3 = Finding(
        entity="CoinDCX",
        aspect="product",
        claim="CoinDCX offers spot and earn features.",
        evidence_quote="offers spot and earn",
        source_url="https://coindcx.com",
        source_type="web",
    )

    deduped = deduplicate_findings([f1, f2, f3])
    assert len(deduped) == 2
    assert deduped[0].entity == "BitDelta"
    assert deduped[1].entity == "CoinDCX"
