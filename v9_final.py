import json
import time
import uuid
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, Field

from gemini_swarm.tools import Bash, Edit, SmartRead, InspectPort, KillProcess


class StatusUpdate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    name: str
    status: str
    operation: Optional[str] = None
    details: Optional[str] = None
    created_at: float = Field(default_factory=time.time)


class Thought(BaseModel):
    thought: str
    verification: str


class Step(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tool: str
    tool_args: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[str] = None
    start_time: float = Field(default_factory=time.time)
    finish_time: Optional[float] = None


class Record(BaseModel):
    steps: List[Step] = Field(default_factory=list)
    success: Optional[bool] = None
    failure_reason: Optional[str] = None


class AgentState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    mission: str
    status: str = "idle"
    created_at: float = Field(default_factory=time.time)
    record: Record = Field(default_factory=Record)
    current_step: Optional[Step] = None
    last_thought: Optional[Thought] = None


class AgentThoughts:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    def record(self, thought: str, verification: str) -> None:
        """Records the agent's thoughts and verifications persistently."""
        # Persist the thought and verification using a tool or external storage
        # For now, we'll just print them
        print(f"Agent {{self.agent_id}} Thought: {{thought}}")
        print(f"Agent {{self.agent_id}} Verification: {{verification}}")


class MainAgent:
    def __init__(self, mission: str, name: str = "Default_Agent"):
        self.state = AgentState(mission=mission, name=name)
        self.thoughts = AgentThoughts(agent_id=self.state.id)

    def run(self, task: Dict) -> Dict:
        print("running task: ", task)
        step = Step(tool=task["tool"], tool_args=task["tool_args"])
        self.state.current_step = step
        step.start_time = time.time()

        # Before executing any tool, record the thought and verification
        self.thoughts.record(thought=task["thought"], verification=task["verification"])

        max_iterations = 10
        iteration_count = 0
        result = None

        while iteration_count < max_iterations:
            try:
                if task["tool"] == "Bash":
                    result = Bash(**task["tool_args"])
                elif task["tool"] == "Edit":
                    result = Edit(**task["tool_args"])
                elif task["tool"] == "SmartRead":
                    result = SmartRead(**task["tool_args"])
                elif task["tool"] == "InspectPort":
                    result = InspectPort(port=task["tool_args"]["port"])
                elif task["tool"] == "KillProcess":
                    result = KillProcess(pid=task["tool_args"]["pid"])
                else:
                    result = {"stdout": "Unknown tool"}

                step.result = str(result)
                step.finish_time = time.time()
                self.state.record.steps.append(step)
                break # Exit loop on success

            except Exception as e:
                step.result = str(e)
                step.finish_time = time.time()
                self.state.record.steps.append(step)
                result = {"stdout": str(e)}
                break # Exit loop on exception

            iteration_count += 1

        if 'verification' not in task:
            raise TimeoutError("Verification field missing from task.")

        if result is None:
            raise TimeoutError("Max iterations reached without result.")

        return result
