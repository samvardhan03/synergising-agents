from fastapi import FastAPI
from uuid import uuid4
from app.agents.base_agent import BaseAgent
from app.models.data_models import AgentType
from app.config import settings  
from app.utils.logging import get_logger

app = FastAPI()

class DummyAgent(BaseAgent):
    def __init__(self, workflow_id=None):
        super().__init__(AgentType.SUMMARY, workflow_id)
        self.logger = get_logger("dummy_agent", "SUMMARY", self.workflow_id)

    def run(self):
        self.logger.info(f"Running DummyAgent for workflow {self.workflow_id}")
        return {"status": "success", "workflow_id": self.workflow_id}

@app.get("/")
def read_root():
    return {"message": "Welcome to Synergising Agents API!"}

@app.get("/run-agent")
def run_agent():
    agent = DummyAgent(workflow_id=str(uuid4()))
    result = agent.run()
    return {"result": result}
