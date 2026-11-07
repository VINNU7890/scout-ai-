from backend.app.schemas import Finding, ResearchOptions, ResearchPlan


def test_research_options_defaults():
    opts = ResearchOptions()
    assert opts.depth == "standard"
    assert opts.max_sources_per_entity == 5
    assert opts.include_docs is True
    assert "product" in opts.focus_areas


def test_finding_schema():
    f = Finding(
        entity="CoinSwitch",
        aspect="product",
        claim="Aggregates liquidity across order books.",
        evidence_quote="aggregates liquidity across multiple books",
        source_url="https://coinswitch.co",
        source_type="web",
    )
    assert f.entity == "CoinSwitch"
    assert f.source_type == "web"
    assert f.confidence == "high"


def test_research_plan_schema():
    plan = ResearchPlan(
        entities=["BitDelta", "CoinDCX"],
        aspects=["product", "pricing"],
        sub_questions={"BitDelta": ["BitDelta trading fees"]},
    )
    assert len(plan.entities) == 2
    assert plan.assumptions == []
