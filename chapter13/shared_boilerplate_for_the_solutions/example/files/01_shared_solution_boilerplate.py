import time
from collections import deque
from enum import Enum

# --- Global Definitions and Custom Exceptions ---

class AgentStateViolationError(Exception):
    """Raised when an agent attempts an action in an invalid state."""
    pass

class AuthorizationFailure(Exception):
    """Raised when a secure, high-risk authorization fails."""
    pass

class AgentState(Enum):
    """States for Exercise 1: ConfigAgent"""
    PLANNING = 'Planning'
    GENERATING_PROPOSAL = 'Generating Proposal'
    AWAITING_APPROVAL = 'Awaiting Approval'
    EXECUTING = 'Executing'
    TERMINATED = 'Terminated'
    IDLE = 'Idle'
