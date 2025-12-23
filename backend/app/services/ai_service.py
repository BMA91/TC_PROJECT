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


def process_user_request_with_metadata(content: str, trace_id: str = None):
    """
    Processes the user request with additional metadata for logging.
    Returns the result from AgentManager with trace_id included.
    """
    result = agent_manager.process_ticket(content)
    if trace_id:
        result['trace_id'] = trace_id
    return result
