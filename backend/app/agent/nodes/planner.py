from __future__ import annotations

import logging
import re
from backend.app.agent.events_manager import emit_event, is_run_cancelled
from backend.app.agent.prompts import PLANNER_SYSTEM_PROMPT, PLANNER_USER_TEMPLATE
from backend.app.agent.state import ResearchState
from backend.app.schemas import ResearchPlan
from backend.app.services.llm import call_structured_llm

logger = logging.getLogger("scoutai.agent.planner")


def extract_entities_fallback(query: str) -> list[str]:
    """Heuristic entity extraction when LLM planner is rate-limited or offline."""
    q = query.strip()
    # Pattern 1: between X and Y / btw X and Y
    m = re.search(r'(?:between|btw)\s+([a-zA-Z0-9_\s]+?)\s+(?:and|&)\s+([a-zA-Z0-9_\s]+)', q, re.I)
    if m:
        e1 = m.group(1).strip()
        e2 = re.sub(r'\s+(?:in|for|market|sales|pricing|quick commerce|metrics).*$', '', m.group(2).strip(), flags=re.I).strip()
        return [e1.title(), e2.title()]

    # Pattern 2: X vs Y / X versus Y / X against Y
    m = re.search(r'([a-zA-Z0-9_\s]+?)\s+(?:vs\.?|versus|against)\s+([a-zA-Z0-9_\s]+)', q, re.I)
    if m:
        e1 = re.sub(r'^(?:compare|analyze|research)\s+', '', m.group(1).strip(), flags=re.I).strip()
        e2 = re.sub(r'\s+(?:in|for|market|sales|pricing).*$', '', m.group(2).strip(), flags=re.I).strip()
        return [e1.title(), e2.title()]

    # Pattern 3: compare X and Y
    m = re.search(r'compare\s+([a-zA-Z0-9_\s]+?)\s+(?:and|&|with)\s+([a-zA-Z0-9_\s]+)', q, re.I)
    if m:
        e1 = m.group(1).strip()
        e2 = re.sub(r'\s+(?:in|for|market|sales|pricing).*$', '', m.group(2).strip(), flags=re.I).strip()
        return [e1.title(), e2.title()]

    # Single entity / general search
    cleaned = re.sub(r'^(?:research|analyze|overview of|details about|compare)\s+', '', q, flags=re.I).strip()
    return [cleaned.title()] if cleaned else ["Primary Entity"]


async def planner_node(state: ResearchState) -> dict:
    run_id = state["run_id"]
    if is_run_cancelled(run_id):
        await emit_event(run_id, "run_cancelled", "plan", "Research cancelled by user.")
        return {"errors": ["Run cancelled by user."]}

    await emit_event(
        run_id, "node_started", "plan", "Analyzing research prompt and creating plan..."
    )

    query = state["query"]
    options = state.get("options")
    focus_areas = (
        options.focus_areas if options else ["product", "pricing", "trust", "compliance", "gtm"]
    )
    depth = options.depth if options else "standard"

    user_prompt = PLANNER_USER_TEMPLATE.format(
        query=query,
        focus_areas=", ".join(focus_areas),
        depth=depth,
    )

    call_tracker = {"calls": state.get("llm_call_count", 0)}

    try:
        plan: ResearchPlan = await call_structured_llm(
            schema=ResearchPlan,
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            call_tracker=call_tracker,
        )

        # Enforce caps
        plan.entities = plan.entities[:6]
        plan.aspects = plan.aspects[:8]

        # Ensure every entity has sub-questions
        for entity in plan.entities:
            if entity not in plan.sub_questions or not plan.sub_questions[entity]:
                plan.sub_questions[entity] = [
                    f"{entity} core products and features",
                    f"{entity} pricing fees and business model",
                    f"{entity} compliance regulatory status trust security",
                    f"{entity} go to market growth traction and market share",
                ]

        summary_msg = f"Identified {len(plan.entities)} entities ({', '.join(plan.entities)}) and {len(plan.aspects)} aspects to investigate."
        await emit_event(run_id, "step", "plan", summary_msg, data={"plan": plan.model_dump()})
        await emit_event(run_id, "node_finished", "plan", "Research plan finalized.")

        return {
            "plan": plan,
            "llm_call_count": call_tracker["calls"],
        }
    except Exception as e:
        logger.warning(f"Planner LLM failed ({e}). Generating heuristic research plan from query...")
        entities = extract_entities_fallback(query)
        aspects = ["sales & revenue", "market share", "dark stores & delivery", "pricing & business model"]
        sub_questions = {}
        for ent in entities:
            sub_questions[ent] = [
                f"{ent} sales revenue order volume market share",
                f"{ent} quick commerce dark stores expansion cities",
                f"{ent} pricing delivery charges platform fees discounts",
            ]

        fallback_plan = ResearchPlan(
            entities=entities,
            aspects=aspects,
            sub_questions=sub_questions,
            query_angles=[f"Competitive metrics for {', '.join(entities)}", f"Market comparison: {query}"],
        )

        summary_msg = f"Extracted target entities ({', '.join(fallback_plan.entities)}) and {len(fallback_plan.aspects)} aspects for live web research."
        await emit_event(run_id, "step", "plan", summary_msg, data={"plan": fallback_plan.model_dump()})
        await emit_event(run_id, "node_finished", "plan", "Research plan finalized.")

        return {
            "plan": fallback_plan,
            "llm_call_count": call_tracker.get("calls", state.get("llm_call_count", 0)),
        }
