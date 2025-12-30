import asyncio
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_vc_debate import run_vc_debate, format_verdict, create_app


def main():
    load_dotenv(override=True)
    
    parser = argparse.ArgumentParser(description="AI-VC: Multi-Agent Startup Analyzer")
    parser.add_argument("--startup", "-s", type=str, help="Startup name to analyze")
    parser.add_argument("--ui", action="store_true", help="Launch Gradio UI")
    parser.add_argument("--share", action="store_true", help="Create public Gradio link")
    args = parser.parse_args()
    
    if args.ui or not args.startup:
        app = create_app()
        app.launch(share=args.share)
    else:
        async def run():
            final_decision, bull_case, bear_case = await run_vc_debate(args.startup)
            print("\n" + "="*60)
            print(format_verdict(final_decision))
        
        asyncio.run(run())


if __name__ == "__main__":
    main()
