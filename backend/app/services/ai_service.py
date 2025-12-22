import sys
import os

# Add the root directory to sys.path to import from 'ai'
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if root_path not in sys.path:
    sys.path.append(root_path)

from ai.agent_manager import AgentManager

agent_manager = AgentManager()

def process_user_request(content: str):
    """
    Processes the user request through the AI pipeline.
    Returns the result from AgentManager.
    """
    return agent_manager.process_ticket(content)
