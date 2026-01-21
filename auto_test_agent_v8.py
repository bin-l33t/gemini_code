import sys
import argparse
from gemini_swarm import core

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Gemini Auto-Test Agent v8")
    parser.add_argument("prompt_input", nargs="?", help="Path to mission file OR direct mission text string")
    parser.add_argument("--model", default="gemini-2.0-flash", help="Model ID")
    parser.add_argument("--persona", default="hydrated_personas/agent_engineer.md", help="Persona path")
    args = parser.parse_args()

    core.run_mission(args.prompt_input, args.model, args.persona)
