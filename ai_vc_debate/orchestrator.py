import asyncio
from agents import Runner

from .models import BullCase, BearCase, FinalDecision
from .agents import optimist_agent, skeptic_agent, investment_committee


async def run_vc_debate(startup_name: str) -> tuple[FinalDecision, BullCase, BearCase]:
    """
    Run the full multi-agent VC debate for a startup.
    
    1. Optimist builds Bull Case
    2. Skeptic builds Bear Case (in parallel)
    3. Investment Committee synthesizes and decides
    
    Returns:
        Tuple of (FinalDecision, BullCase, BearCase)
    """
    # Run Bull and Bear cases in parallel
    bull_task = Runner.run(
        optimist_agent, 
        f"Analyze startup: {startup_name}. Build the strongest bull case for investment.",
        max_turns=20
    )
    bear_task = Runner.run(
        skeptic_agent, 
        f"Analyze startup: {startup_name}. Build the most thorough bear case with all risks.",
        max_turns=20
    )
    
    bull_result, bear_result = await asyncio.gather(bull_task, bear_task)
    bull_case: BullCase = bull_result.final_output
    bear_case: BearCase = bear_result.final_output
    
    # Investment Committee decision
    committee_input = f"""# Startup: {startup_name}
    {bull_case.model_dump_json(indent=2)}
    {bear_case.model_dump_json(indent=2)}
    Based on both cases, make your final investment decision.
    Remember: You CANNOT recommend INVEST if there are unresolved_risks.
    """

    committee_result = await Runner.run(investment_committee, committee_input)
    final_decision: FinalDecision = committee_result.final_output
    
    return final_decision, bull_case, bear_case


def format_verdict(final_decision: FinalDecision) -> str:
    """Format the final decision as a readable string."""
    verdict = f"""## 📋 FINAL VERDICT: {final_decision.decision.value}

**Investment Thesis:**
{final_decision.investment_thesis}

**Weighting:** Bull {final_decision.bull_case_weight}% / Bear {final_decision.bear_case_weight}%
"""
    
    if final_decision.risk_mitigations:
        verdict += "\n**Risk Mitigations:**\n"
        for rm in final_decision.risk_mitigations:
            verdict += f"- {rm.risk}: {rm.mitigation}\n"
    
    if final_decision.unresolved_risks:
        verdict += "\n**Unresolved Risks:**\n"
        for risk in final_decision.unresolved_risks:
            verdict += f"- {risk}\n"
    
    if final_decision.recommended_check_size:
        verdict += f"\n**Recommended Check Size:** {final_decision.recommended_check_size}\n"
    
    if final_decision.key_due_diligence:
        verdict += "\n**Key Due Diligence:**\n"
        for item in final_decision.key_due_diligence:
            verdict += f"- {item}\n"
    
    if final_decision.follow_up_questions:
        verdict += "\n**Follow-up Questions:**\n"
        for q in final_decision.follow_up_questions:
            verdict += f"- {q}\n"
    
    return verdict


def format_bull_case(bull_case: BullCase) -> str:
    """Format the bull case as markdown."""
    return f"""## 🐂 BULL CASE: {bull_case.startup_name}

**{bull_case.one_liner}**

### Market Opportunity
{bull_case.market_opportunity}

### Competitive Moat
{bull_case.competitive_moat}

### Growth Catalysts
{chr(10).join(f'- {c}' for c in bull_case.growth_catalysts)}

### Traction
{chr(10).join(f'- {t}' for t in bull_case.traction_highlights)}

### Team Strengths
{chr(10).join(f'- {s}' for s in bull_case.team_strengths)}

### Comparable Exits
{chr(10).join(f'- {e}' for e in bull_case.comparable_exits)}

**Confidence Score: {bull_case.confidence_score}/10**

**Thesis:** {bull_case.investment_thesis_summary}
"""


def format_bear_case(bear_case: BearCase) -> str:
    """Format the bear case as markdown."""
    return f"""## 🐻 BEAR CASE: {bear_case.startup_name}

### Market Risks
{chr(10).join(f'- {r}' for r in bear_case.market_risks)}

### Execution Risks
{chr(10).join(f'- {r}' for r in bear_case.execution_risks)}

### Competitive Threats
{chr(10).join(f'- {t}' for t in bear_case.competitive_threats)}

### Financial Concerns
{chr(10).join(f'- {c}' for c in bear_case.financial_concerns)}

### Key Weaknesses
{chr(10).join(f'- {w}' for w in bear_case.key_weaknesses)}

### Kill Scenario
{bear_case.kill_scenario}

**Risk Severity Score: {bear_case.risk_severity_score}/10**"""