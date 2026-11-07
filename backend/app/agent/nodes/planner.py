from __future__ import annotations

import logging

from backend.app.agent.events_manager import emit_event, is_run_cancelled
from backend.app.agent.prompts import PLANNER_SYSTEM_PROMPT, PLANNER_USER_TEMPLATE
from backend.app.agent.state import ResearchState
from backend.app.schemas import ResearchPlan
from backend.app.services.llm import call_structured_llm

logger = logging.getLogger("scoutai.agent.planner")


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
        logger.error(f"Planner error: {e}")
        err_msg = f"Planner node failed: {e}"
        await emit_event(run_id, "error", "plan", err_msg)
        return {
            "errors": [err_msg],
            "llm_call_count": call_tracker.get("calls", state.get("llm_call_count", 0)),
        }
