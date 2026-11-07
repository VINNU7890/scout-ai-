from __future__ import annotations

from typing import Any, Dict

DEMO_RUN_DATA: Dict[str, Any] = {
    "run_id": "demo-bitdelta-run-001",
    "query": "Compare BitDelta India with CoinDCX, CoinSwitch, ZebPay and Mudrex. Focus on trust, compliance, product, fees and go-to-market gaps.",
    "title": "Competitive Brief: BitDelta India vs CoinDCX, CoinSwitch, ZebPay & Mudrex",
    "status": "completed",
    "plan": {
        "entities": ["BitDelta India", "CoinDCX", "CoinSwitch", "ZebPay", "Mudrex"],
        "aspects": [
            "product",
            "pricing/fees",
            "trust & security",
            "compliance",
            "marketing/gtm",
            "target users",
        ],
        "sub_questions": {
            "BitDelta India": [
                "BitDelta India platform features trading pairs derivatives",
                "BitDelta maker taker fee structure India",
                "BitDelta FIU-IND registration compliance licensing",
                "BitDelta marketing campaigns sponsorships influencer GTM",
            ],
            "CoinDCX": [
                "CoinDCX spot futures Earn product ecosystem",
                "CoinDCX 1% TDS zero fee promotions trading charges",
                "CoinDCX FIU compliance ISO 27001 proof of reserves",
                "CoinDCX Namaste Web3 campaign user acquisition",
            ],
            "CoinSwitch": [
                "CoinSwitch PRO multi-exchange trading SIP product",
                "CoinSwitch deposit withdrawal fees crypto spreads",
                "CoinSwitch FIU registration AML PMLA guidelines",
                "CoinSwitch IPL advertising referral program",
            ],
            "ZebPay": [
                "ZebPay lightning network OTC crypto SIP lending",
                "ZebPay monthly membership fees trading commissions",
                "ZebPay regulatory standing FIU registration Australia compliance",
                "ZebPay diaspora retention institutional onboarding",
            ],
            "Mudrex": [
                "Mudrex crypto baskets Coin Sets automated investing",
                "Mudrex management fee transaction charges",
                "Mudrex FIU registration EU VASP compliance safety",
                "Mudrex 1-on-1 advisor strategy performance marketing",
            ],
        },
        "assumptions": [
            "Focus is on Indian retail and pro-retail crypto trading landscape post-1% TDS mandate.",
            "Compliance evaluation prioritizes FIU-IND registration and PMLA adherence.",
        ],
    },
    "sources": [
        {
            "id": 1,
            "title": "BitDelta Global & India Platform Overview",
            "url": "https://bitdelta.com/en/about-us",
            "domain": "bitdelta.com",
            "source_type": "web",
            "retrieved_at": "2026-11-05T10:00:00Z",
            "supported_claims": [
                "BitDelta offers spot, derivatives, and copy-trading modules on a unified engine [1].",
                "BitDelta features military-grade multi-sig cold storage custody partnerships [1].",
            ],
        },
        {
            "id": 2,
            "title": "Financial Intelligence Unit India - Registered Reporting Entities",
            "url": "https://fiuindia.gov.in/vda-compliance-registry",
            "domain": "fiuindia.gov.in",
            "source_type": "web",
            "retrieved_at": "2026-11-05T10:05:00Z",
            "supported_claims": [
                "CoinDCX, CoinSwitch, ZebPay, and Mudrex are registered reporting entities with FIU-IND [2].",
                "BitDelta completed preliminary FIU-IND local compliance filing in 2024 [2].",
            ],
        },
        {
            "id": 3,
            "title": "CoinDCX Fee Schedule & Proof of Reserves Audit",
            "url": "https://coindcx.com/fees-and-charges",
            "domain": "coindcx.com",
            "source_type": "web",
            "retrieved_at": "2026-11-05T10:10:00Z",
            "supported_claims": [
                "CoinDCX charges 0.2% maker / 0.5% taker for spot with quarterly Proof-of-Reserves publication [3]."
            ],
        },
        {
            "id": 4,
            "title": "CoinSwitch PRO Launch & Institutional Order Routing",
            "url": "https://coinswitch.co/pro-trading-deep-dive",
            "domain": "coinswitch.co",
            "source_type": "web",
            "retrieved_at": "2026-11-05T10:15:00Z",
            "supported_claims": [
                "CoinSwitch PRO aggregates liquidity across CoinDCX, WazirX, and global order books [4]."
            ],
        },
        {
            "id": 5,
            "title": "Mudrex Managed Crypto Baskets & European VASP License",
            "url": "https://mudrex.com/regulatory-status-and-investing",
            "domain": "mudrex.com",
            "source_type": "web",
            "retrieved_at": "2026-11-05T10:20:00Z",
            "supported_claims": [
                "Mudrex holds an EU VASP registration in Italy and Lithuania while operating compliant INR on-ramps [5]."
            ],
        },
        {
            "id": 6,
            "title": "ZebPay Institutional OTC and Quick Trade Structure",
            "url": "https://zebpay.com/in/pricing",
            "domain": "zebpay.com",
            "source_type": "web",
            "retrieved_at": "2026-11-05T10:25:00Z",
            "supported_claims": [
                "ZebPay charges an active monthly membership fee of 0.0001 BTC if accounts remain inactive [6]."
            ],
        },
    ],
    "findings": [
        {
            "entity": "BitDelta India",
            "aspect": "product",
            "claim": "BitDelta provides multi-asset trading including 400+ spot crypto pairs, derivatives, and integrated copy-trading.",
            "evidence_quote": "multi-asset trading with 400+ spot crypto pairs, derivatives, and integrated copy-trading",
            "source_url": "https://bitdelta.com/en/about-us",
            "source_type": "web",
            "retrieved_at": "2026-11-05T10:00:00Z",
            "confidence": "high",
        },
        {
            "entity": "BitDelta India",
            "aspect": "trust & security",
            "claim": "BitDelta secures customer deposits through cold storage and strategic multi-signature security protocols.",
            "evidence_quote": "cold storage and strategic multi-signature security protocols safeguarding client assets",
            "source_url": "https://bitdelta.com/en/about-us",
            "source_type": "web",
            "retrieved_at": "2026-11-05T10:00:00Z",
            "confidence": "high",
        },
        {
            "entity": "CoinDCX",
            "aspect": "compliance",
            "claim": "CoinDCX is registered with FIU-IND and maintains ISO 27001 security compliance along with published Proof-of-Reserves.",
            "evidence_quote": "registered with FIU-IND and maintains ISO 27001 compliance and quarterly Proof-of-Reserves",
            "source_url": "https://fiuindia.gov.in/vda-compliance-registry",
            "source_type": "web",
            "retrieved_at": "2026-11-05T10:05:00Z",
            "confidence": "high",
        },
        {
            "entity": "CoinSwitch",
            "aspect": "product",
            "claim": "CoinSwitch PRO aggregates multiple domestic exchange order books to deliver optimal liquidity and unified INR fiat gateway.",
            "evidence_quote": "aggregates multiple domestic exchange order books to deliver optimal liquidity and unified INR",
            "source_url": "https://coinswitch.co/pro-trading-deep-dive",
            "source_type": "web",
            "retrieved_at": "2026-11-05T10:15:00Z",
            "confidence": "high",
        },
        {
            "entity": "Mudrex",
            "aspect": "product",
            "claim": "Mudrex focuses on thematic crypto baskets ('Coin Sets') and automated SIP investments rather than raw spot day trading.",
            "evidence_quote": "thematic crypto baskets ('Coin Sets') and automated SIP investments for long term holders",
            "source_url": "https://mudrex.com/regulatory-status-and-investing",
            "source_type": "web",
            "retrieved_at": "2026-11-05T10:20:00Z",
            "confidence": "high",
        },
        {
            "entity": "ZebPay",
            "aspect": "pricing/fees",
            "claim": "ZebPay applies a monthly active membership fee for dormant accounts alongside traditional spot transaction commissions.",
            "evidence_quote": "active monthly membership fee for dormant accounts alongside traditional spot transaction commissions",
            "source_url": "https://zebpay.com/in/pricing",
            "source_type": "web",
            "retrieved_at": "2026-11-05T10:25:00Z",
            "confidence": "high",
        },
    ],
    "profiles": [
        {
            "entity": "BitDelta India",
            "strengths": [
                "Extensive token breadth with 400+ pairs [1]",
                "High-performance copy trading and derivatives engine [1]",
                "Modern multi-asset trading UX [1]",
            ],
            "weaknesses": [
                "Later entry into Indian domestic market compared to first-wave exchanges [2]",
                "Brand recall among mass-market retail still scaling [1]",
            ],
            "positioning": "Global multi-asset crypto and derivatives trading exchange tailored for active pro-retail traders [1].",
            "pricing_notes": "Competitive 0.1% spot fee tiers with volume discounts and zero deposit surcharges [1].",
            "trust_signals": [
                "Multi-signature cold custody architecture [1]",
                "Compliant local corporate registration process [2]",
            ],
            "gtm_tactics": [
                "High-impact global sports sponsorships [1]",
                "Affiliate rebate structures and trading competitions [1]",
            ],
            "aspect_scores": {
                "product": 4,
                "pricing/fees": 4,
                "trust & security": 4,
                "compliance": 3,
                "marketing/gtm": 4,
                "target users": 4,
            },
            "aspect_rationales": {
                "product": "Robust derivatives, 400+ pairs and copy-trading capability [1].",
                "pricing/fees": "Low baseline taker fees competitive with Tier-1 venues [1].",
                "trust & security": "Institutional grade multi-sig cold custody setup [1].",
                "compliance": "Local compliance filings initiated in 2024 [2].",
                "marketing/gtm": "Aggressive sports and influencer sponsorship strategy [1].",
                "target users": "Tailored for sophisticated pro-retail traders [1].",
            },
        },
        {
            "entity": "CoinDCX",
            "strengths": [
                "First Indian crypto unicorn with deep regulatory footprint [2]",
                "Transparent Proof-of-Reserves published regularly [3]",
                "Extensive educational arm (DCX Learn) [3]",
            ],
            "weaknesses": [
                "Strict withdrawal restrictions due to local compliance mandates [3]",
                "Higher effective taker fees for retail spot [3]",
            ],
            "positioning": "India's flagship compliant crypto exchange for institutional and retail investors [2].",
            "pricing_notes": "0.2% maker / 0.5% taker for spot; competitive VIP tiers [3].",
            "trust_signals": [
                "FIU-IND registered [2]",
                "ISO 27001 certified [3]",
                "Proof-of-Reserves audited [3]",
            ],
            "gtm_tactics": [
                "Mainstream Bollywood celebrity marketing [3]",
                "Extensive collegiate hackathons [3]",
            ],
            "aspect_scores": {
                "product": 5,
                "pricing/fees": 3,
                "trust & security": 5,
                "compliance": 5,
                "marketing/gtm": 5,
                "target users": 4,
            },
            "aspect_rationales": {
                "product": "Full suite including Earn, futures, and enterprise custody [3].",
                "pricing/fees": "Higher retail fee structure offset by liquidity depth [3].",
                "trust & security": "Rigorous security audits and verifiable reserves [3].",
                "compliance": "Gold standard adherence to FIU-IND reporting [2].",
                "marketing/gtm": "High-budget mainstream awareness campaigns [3].",
                "target users": "Caters from complete novice to HNI institutions [3].",
            },
        },
        {
            "entity": "CoinSwitch",
            "strengths": [
                "20M+ registered Indian user base [4]",
                "CoinSwitch PRO multi-exchange order routing [4]",
                "Seamless UPI and INR fiat on-ramps [4]",
            ],
            "weaknesses": [
                "Spread-based pricing in legacy app criticized by advanced traders [4]",
                "Crypto deposit/withdrawal constraints [4]",
            ],
            "positioning": "The Robinhood of India: accessible wealth-tech ecosystem spanning crypto and mutual funds [4].",
            "pricing_notes": "Zero fee marketing on app; PRO charges 0.1% - 0.15% [4].",
            "trust_signals": [
                "FIU-IND compliant entity [2]",
                "Routine transparency disclosures [4]",
            ],
            "gtm_tactics": [
                "IPL prime-time cricket sponsorships [4]",
                "Gamified referral incentives [4]",
            ],
            "aspect_scores": {
                "product": 4,
                "pricing/fees": 3,
                "trust & security": 4,
                "compliance": 5,
                "marketing/gtm": 5,
                "target users": 5,
            },
            "aspect_rationales": {
                "product": "PRO desktop engine combined with simple retail mobile app [4].",
                "pricing/fees": "Wide spreads on basic app, improved on PRO [4].",
                "trust & security": "Strong domestic credibility and KYC infrastructure [4].",
                "compliance": "Active participation in BACC and FIU guidelines [2].",
                "marketing/gtm": "Highest domestic brand recall in consumer fintech [4].",
                "target users": "Unrivaled reach across Tier-2 and Tier-3 Indian cities [4].",
            },
        },
        {
            "entity": "ZebPay",
            "strengths": [
                "Pioneer legacy brand operating since 2014 [6]",
                "Lightning Network integration for instant BTC transactions [6]",
                "Dedicated institutional OTC desk [6]",
            ],
            "weaknesses": [
                "Unpopular monthly membership fee for inactive users [6]",
                "Slower feature velocity compared to younger competitors [6]",
            ],
            "positioning": "Veteran, security-first crypto broker for steadfast long-term bitcoiners [6].",
            "pricing_notes": "Monthly activity fee, 0.15% - 0.25% trading fees [6].",
            "trust_signals": [
                "One of India's earliest FIU registrants [2]",
                "Global presence in Australia and Singapore [6]",
            ],
            "gtm_tactics": [
                "Targeted HNI direct outreach [6]",
                "Bitcoin-centric educational webinars [6]",
            ],
            "aspect_scores": {
                "product": 3,
                "pricing/fees": 2,
                "trust & security": 4,
                "compliance": 4,
                "marketing/gtm": 3,
                "target users": 3,
            },
            "aspect_rationales": {
                "product": "Solid core trading engine with Lightning support, lacks copy-trade [6].",
                "pricing/fees": "Inactivity fees hurt passive retail balances [6].",
                "trust & security": "Decade-long spotless security and cold storage track record [6].",
                "compliance": "Complies across multi-jurisdictional frameworks [2].",
                "marketing/gtm": "Conservative organic community marketing [6].",
                "target users": "Loyal core of legacy crypto investors and HNI traders [6].",
            },
        },
        {
            "entity": "Mudrex",
            "aspect_scores": {
                "product": 4,
                "pricing/fees": 4,
                "trust & security": 4,
                "compliance": 5,
                "marketing/gtm": 4,
                "target users": 4,
            },
            "aspect_rationales": {
                "product": "Pioneered thematic crypto baskets and automated recurring investments [5].",
                "pricing/fees": "Transparent fund management and zero hidden spreads [5].",
                "trust & security": "Y Combinator backed with dual European VASP registrations [5].",
                "compliance": "Full FIU-IND compliance alongside Italian and Lithuanian licenses [2, 5].",
                "marketing/gtm": "Content-driven performance marketing and 1-on-1 portfolio consultation [5].",
                "target users": "Tailored for retail SIP investors and disciplined wealth builders [5].",
            },
            "strengths": [
                "Simplified thematic indices (Coin Sets) eliminating stock picking [5]",
                "Dual EU and FIU regulatory status [2, 5]",
                "Personalized investor relationship advisory [5]",
            ],
            "weaknesses": [
                "Not built for high-frequency day or futures traders [5]",
                "Smaller overall AUM compared to pure exchange unicorns [5]",
            ],
            "positioning": "Passive, systematic crypto asset management platform for retail wealth accumulation [5].",
            "pricing_notes": "Zero commission on direct purchases; small AUM management fee on select automated products [5].",
            "trust_signals": ["Y-Combinator alumnus [5]", "Dual European VASP registrations [5]"],
            "gtm_tactics": [
                "Personalized WhatsApp advisory [5]",
                "Fintech influencer podcasts and educational newsletters [5]",
            ],
        },
    ],
    "comparison_table": {
        "Product Suite": {
            "BitDelta India": "Spot, Derivatives, 400+ pairs, Copy-Trading [1]",
            "CoinDCX": "Spot, Futures, Earn, Web3 Wallet [3]",
            "CoinSwitch": "PRO Desktop, Simple Retail App, SIPs [4]",
            "ZebPay": "Spot, OTC Desk, Lightning Network [6]",
            "Mudrex": "Thematic Coin Sets, Systematic SIPs [5]",
        },
        "Pricing & Fees": {
            "BitDelta India": "0.10% baseline maker/taker, volume discounts [1]",
            "CoinDCX": "0.20% maker / 0.50% taker [3]",
            "CoinSwitch": "Spread-based on app, 0.10% on PRO [4]",
            "ZebPay": "Monthly membership fee + 0.15% fee [6]",
            "Mudrex": "Zero transaction fee, small basket fee [5]",
        },
        "Regulatory & Compliance": {
            "BitDelta India": "FIU-IND registration process active [2]",
            "CoinDCX": "Registered FIU-IND, ISO 27001 [2, 3]",
            "CoinSwitch": "Registered FIU-IND, PMLA compliant [2, 4]",
            "ZebPay": "Registered FIU-IND, AUSTRAC registered [2, 6]",
            "Mudrex": "Registered FIU-IND, EU VASP licensed [2, 5]",
        },
        "Trust & Reserves": {
            "BitDelta India": "Multi-sig cold storage architecture [1]",
            "CoinDCX": "Quarterly audited Proof-of-Reserves [3]",
            "CoinSwitch": "Public reserve transparency dashboard [4]",
            "ZebPay": "10-year track record without security loss [6]",
            "Mudrex": "YC-backed, regulated custodian partners [5]",
        },
        "Target Audience": {
            "BitDelta India": "Active pro-retail & derivatives traders [1]",
            "CoinDCX": "Universal (Novice to Institutions) [3]",
            "CoinSwitch": "Mass market retail & beginners [4]",
            "ZebPay": "HNI & Long-term Bitcoiners [6]",
            "Mudrex": "Passive SIP wealth accumulators [5]",
        },
    },
    "swot": {
        "strengths": [
            "Advanced multi-asset derivatives engine with copy-trading functionality [1].",
            "High token variety (400+ pairs) surpassing most domestic Indian exchanges [1].",
            "Ultra-competitive fee structure with aggressive VIP maker/taker rebates [1].",
        ],
        "weaknesses": [
            "Brand familiarity lags incumbents who spent hundreds of crores during bull runs [3, 4].",
            "FIU-IND full registration pending final listing completion compared to first-wave peers [2].",
        ],
        "opportunities": [
            "Attract high-volume derivatives traders disaffected by domestic TDS friction and lack of leverage on pure spot apps [1].",
            "Partner with regional Indian trading academies and quantitative finance communities [1].",
            "Introduce seamless zero-slippage copy-trading to win younger demographic [1].",
        ],
        "threats": [
            "Aggressive counter-measures by CoinDCX and CoinSwitch to launch competitive derivatives engines [3, 4].",
            "Dynamic Indian regulatory headwinds surrounding offshore liquidity and derivatives taxation [2].",
        ],
    },
    "gaps_and_opportunities": [
        "Pro-retail derivatives deficit: CoinSwitch and ZebPay focus almost entirely on spot; BitDelta can capture active traders seeking leverage and copy-trading [1, 4].",
        "Transparent fee differentiation: Educating Indian traders on hidden spreads charged by retail brokers offers a strong conversion wedge [3, 4].",
        "Copy-trading whitespace: No domestic Indian exchange offers a robust, regulatory-aligned copy-trading ecosystem for retail [1].",
    ],
    "recommended_gtm_actions": [
        {
            "priority": "High",
            "title": "Establish Regulatory Transparency Hub",
            "action": "Accelerate and prominently showcase FIU-IND compliance milestones and publish real-time wallet proof-of-reserves.",
            "rationale_and_evidence": "Indian crypto traders rank trust and regulatory certainty as their #1 barrier to platform switching [2, 3].",
        },
        {
            "priority": "High",
            "title": "Launch Copy-Trading Masterclass Campaign",
            "action": "Partner with top Indian quantitative influencers on YouTube and Telegram to showcase verified master traders on BitDelta copy-trade.",
            "rationale_and_evidence": "BitDelta's copy-trading feature is a clear functional differentiator absent on CoinDCX and CoinSwitch [1, 4].",
        },
        {
            "priority": "Medium",
            "title": "Institutional & Pro-Trader VIP Fee Match",
            "action": "Offer a 90-day fee-match incentive for high-volume traders migrating from CoinDCX or Binance.",
            "rationale_and_evidence": "Incumbent taker fees reach up to 0.5%, giving BitDelta a dramatic price advantage [1, 3].",
        },
    ],
    "methodology_and_limitations": "Findings gathered from live public filings, exchange fee schedules, FIU registries, and product audits conducted in November 2026. Private institutional OTC rates and undisclosed VIP tiers were excluded [2, 3].",
    "verification": {
        "passed": True,
        "issues": [],
        "summary": "All 18 factual statements cross-referenced against official disclosures and verified quotes.",
    },
}

DEMO_RUN_DATA["executive_summary"] = (
    "The Indian digital asset ecosystem is entering a mature phase defined by stringent FIU-IND compliance, "
    "1% TDS mandates, and user demand for pro-grade tooling [2]. CoinDCX and CoinSwitch maintain dominance "
    "in mass-retail reach through early brand moats [3, 4], while Mudrex has carved out passive SIP investors [5]. "
    "BitDelta India represents a formidable high-velocity challenger, offering 400+ assets, low-latency derivatives, "
    "and copy-trading [1]. By locking down local regulatory milestones and targeting advanced retail traders tired "
    "of domestic fee spreads, BitDelta can capture decisive market share in the pro-retail segment [1, 3]."
)

DEMO_RUN_DATA["key_takeaways"] = [
    "BitDelta leads in product depth for active traders, featuring 400+ spot pairs, derivatives, and copy-trading [1].",
    "CoinDCX and CoinSwitch command dominant brand recall but charge higher retail spot fees and wider spreads [3, 4].",
    "FIU-IND registration and local compliance are the non-negotiable prerequisites for long-term trust in India [2].",
    "Mudrex successfully isolates the passive SIP niche, proving that product specialization beats generic spot trading [5].",
    "BitDelta's primary GTM opportunity lies in winning active derivatives traders through transparent pricing and copy-trade innovation [1].",
]
