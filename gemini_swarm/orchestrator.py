import subprocess
import os

# This is a stub.  We'll flesh this out with the Router Agent logic.
def orchestrate_mission(user_request):
    print(f"Received user request: {user_request}")

    # 1. Route the request using the Router Agent
    # (This part will use the llm and agent_orchestrator.md persona)
    # For now, we'll just hardcode the routing for testing purposes
    sub_agent_persona = "gemini_swarm/personas/agent_engineer.md" # Example: Route to the engineer agent

    # 2. Spawn the sub-agent using agent_runner.py
    print(f"Spawning sub-agent with persona: {sub_agent_persona}")
    subprocess.run([
        "python3",
        "gemini_swarm/agent_runner.py",
        user_request,
        "--persona",
        sub_agent_persona
    ])

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        user_request = sys.argv[1]
        orchestrate_mission(user_request)
    else:
        print("Usage: python orchestrator.py <user_request>")
