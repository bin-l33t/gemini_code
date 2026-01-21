import sys
import argparse
import os

# Import the core logic
from gemini_swarm import core
from gemini_swarm import tools # Import tool definitions

# Tool list must be explicitly passed to run_mission
TOOL_LIST = [tools.Bash, tools.Edit, tools.SmartRead, tools.InspectPort, tools.KillProcess, tools.SpawnSubAgent, tools.browser_evaluate, tools.click, tools.type, tools.scroll, tools.screenshot]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Gemini Sub-Agent")
    parser.add_argument("prompt_input", nargs="?", help="Path to mission file OR direct mission text string")
    parser.add_argument("--model", default="gemini-2.0-flash", help="Model ID")
    parser.add_argument("--persona", default="gemini_swarm/personas/agent_engineer.md", help="Persona path")
    args = parser.parse_args()

    core.run_mission(args.prompt_input, args.model, args.persona, tools=TOOL_LIST)
