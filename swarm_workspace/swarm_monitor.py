import time
from gemini_swarm import core, tools

# Define the Quality Assurance persona for the feedback loop
REVIEWER_PERSONA = (
    "You are a Quality Assurance lead. Compare the User's Mission with the Agent's Report. "
    "Respond ONLY with 'SUCCESS' if the goal is met, or a detailed list of 'REMAINING_TASKS' if not."
)

def run_supervised_mission(mission_text, retries=3):
    """
    Executes a mission with an automated feedback loop.
    If the mission fails, the reviewer's feedback is passed to the next attempt.
    """
    current_mission = mission_text
    # Toolset includes diagnostics from the swarm definitions
    swarm_tools = [tools.Bash, tools.Edit, tools.InspectPort, tools.KillProcess]
    
    for attempt in range(retries):
        print(f"\n--- [SUPERVISOR] ATTEMPT {attempt + 1} OF {retries} ---")
        
        # Step 1: Execute the mission using the Swarm Core
        agent_report = core.run_mission(
            prompt_input=current_mission,
            persona_path="personas/agent_engineer.md",
            tools=swarm_tools
        )

        # Step 2: Perform a Reviewer call to verify completion
        print("🔍 [SUPERVISOR] Reviewing agent performance...")
        review = core.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"MISSION: {mission_text}\n\nREPORT: {agent_report}\n\n{REVIEWER_PERSONA}"
        )

        if "SUCCESS" in review.text.upper():
            print("✅ [SUPERVISOR] Mission Accomplished.")
            return True
        else:
            print(f"⚠️ [SUPERVISOR] Goal not achieved. Feedback:\n{review.text}")
            # Update the mission with the reviewer's critique for the next respawn
            current_mission = (
                f"Original Mission: {mission_text}\n\n"
                f"Previous Attempt Failed. Feedback: {review.text}. Try again."
            )
            time.sleep(2) # Brief cooldown between attempts

    print("❌ [SUPERVISOR] Mission failed after maximum retries.")
    return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        run_supervised_mission(sys.argv[1])
    else:
        print("Usage: python3 swarm_monitor.py '<mission_text>'")