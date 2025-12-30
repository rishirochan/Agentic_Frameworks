import asyncio
import gradio as gr
from agents import Runner

from .models import BullCase, BearCase, FinalDecision
from .agents import optimist_agent, skeptic_agent, investment_committee
from .orchestrator import format_verdict, format_bull_case, format_bear_case


# Store results globally for button access
analysis_results = {}


async def analyze_startup(startup_name: str, progress=gr.Progress()):
    """Run the VC debate and stream updates."""
    global analysis_results
    
    if not startup_name.strip():
        yield "Please enter a startup name.", "", "", "none"
        return
    
    progress(0, desc="Starting analysis...")
    yield f"🎯 Starting AI-VC analysis for: {startup_name}", "", "", "none"
    
    progress(0.2, desc="Running parallel research...")
    yield f"🐂 Optimist researching bull case...\n🐻 Skeptic researching bear case...", "", "", "none"
    
    # Run bull and bear in parallel with higher turn limit
    bull_task = Runner.run(
        optimist_agent, 
        f"Analyze startup: {startup_name}. Build the strongest bull case for investment.",
        max_turns=30
    )
    bear_task = Runner.run(
        skeptic_agent, 
        f"Analyze startup: {startup_name}. Build the most thorough bear case with all risks.",
        max_turns=30
    )
    
    bull_result, bear_result = await asyncio.gather(bull_task, bear_task)
    bull_case: BullCase = bull_result.final_output
    bear_case: BearCase = bear_result.final_output
    
    progress(0.6, desc="Bull & Bear cases complete...")
    yield (
        f"✅ Bull Case Complete (Confidence: {bull_case.confidence_score}/10)\n"
        f"✅ Bear Case Complete (Risk Score: {bear_case.risk_severity_score}/10)\n\n"
        f"⚖️ Investment Committee deliberating...",
        "", "", "none"
    )
    
    # Investment Committee
    progress(0.8, desc="Investment Committee deliberating...")
    committee_input = f"""# Startup: {startup_name}

## BULL CASE (from The Optimist)
{bull_case.model_dump_json(indent=2)}

## BEAR CASE (from The Skeptic)
{bear_case.model_dump_json(indent=2)}

Based on both cases, make your final investment decision.
Remember: You CANNOT recommend INVEST if there are unresolved_risks.
"""
    
    committee_result = await Runner.run(investment_committee, committee_input)
    final_decision: FinalDecision = committee_result.final_output
    
    # Store results for buttons
    verdict = format_verdict(final_decision)
    analysis_results["bull_case"] = bull_case
    analysis_results["bear_case"] = bear_case
    analysis_results["final_decision"] = final_decision
    analysis_results["verdict"] = verdict  # Store formatted verdict
    
    progress(1.0, desc="Analysis complete!")
    yield "✅ Analysis Complete!", verdict, "", "none"


def toggle_bull_case(current_view: str):
    """Toggle bull case display - also restores verdict."""
    if "bull_case" not in analysis_results:
        return "", "Run an analysis first!", "none"
    
    verdict = analysis_results.get("verdict", "")
    
    if current_view == "bull":
        return verdict, "", "none"
    else:
        return verdict, format_bull_case(analysis_results["bull_case"]), "bull"


def toggle_bear_case(current_view: str):
    """Toggle bear case display - also restores verdict."""
    if "bear_case" not in analysis_results:
        return "", "Run an analysis first!", "none"
    
    verdict = analysis_results.get("verdict", "")
    
    if current_view == "bear":
        return verdict, "", "none"
    else:
        return verdict, format_bear_case(analysis_results["bear_case"]), "bear"


def create_app() -> gr.Blocks:
    """Create and return the Gradio app."""
    with gr.Blocks(title="AI-VC: Multi-Agent Startup Analyzer", theme=gr.themes.Soft()) as demo:
        current_view = gr.State("none")
        
        gr.Markdown("# 🎯 AI-VC: Multi-Agent Startup Analyzer")
        gr.Markdown("Enter a startup name to run a full bull vs bear debate analysis.")
        
        with gr.Row():
            startup_input = gr.Textbox(
                label="Startup Name",
                placeholder="e.g., Anthropic, OpenAI, Stripe...",
                scale=3
            )
            analyze_btn = gr.Button("🚀 Analyze", variant="primary", scale=1)
        
        status_output = gr.Textbox(label="Status", interactive=False)
        
        # Verdict stays visible in its own section
        verdict_output = gr.Markdown(label="Final Verdict")
        
        with gr.Row():
            bull_btn = gr.Button("🐂 View Bull Case", variant="secondary")
            bear_btn = gr.Button("🐻 View Bear Case", variant="secondary")
        
        # Case details appear below buttons
        case_output = gr.Markdown(label="Case Details")
        
        # Event handlers - verdict_output is NOT cleared by toggle buttons
        analyze_btn.click(
            fn=analyze_startup,
            inputs=[startup_input],
            outputs=[status_output, verdict_output, case_output, current_view]
        )
        
        # Toggle buttons restore verdict and show/hide case
        bull_btn.click(
            fn=toggle_bull_case, 
            inputs=[current_view], 
            outputs=[verdict_output, case_output, current_view]
        )
        bear_btn.click(
            fn=toggle_bear_case, 
            inputs=[current_view], 
            outputs=[verdict_output, case_output, current_view]
        )
    
    return demo


if __name__ == "__main__":
    app = create_app()
    app.launch()

