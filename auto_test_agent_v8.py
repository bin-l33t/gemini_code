import sys
import argparse
from gemini_swarm import core, tools

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Gemini Auto-Test Agent v8 (Tool-Enabled)")
    parser.add_argument("prompt_input", nargs="?", help="Path to mission file OR direct mission text string")
    parser.add_argument("--model", default="gemini-2.0-flash", help="Model ID")
    parser.add_argument("--persona", default="hydrated_personas/agent_engineer.md", help="Persona path")
    args = parser.parse_args()

    # Define the toolset required for the agent to build the workspace and execute tests.
    # This includes filesystem access (Edit/SmartRead) and shell execution (Bash).
    agent_tools = [
        tools.Bash,
        tools.Edit,
        tools.InspectPort,
        tools.KillProcess,
        tools.SmartRead,
        tools.SpawnSubAgent
    ]

    # Execute the mission with the full toolset enabled.
    # For optimization, ensure the agent follows an iterative approach when 
    # setting up the supervisor feedback loop.
    core.run_mission(
        prompt_input=args.prompt_input, 
        model_id=args.model, 
        persona_path=args.persona,
        tools=agent_tools
    )
