from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class Outcome:
    """What actually happens when I called the tool."""
    text: Optional[str]
    error: Optional[str]
    elapsed: float
    timed_out: bool

@dataclass
class AttackCase:
    """Attacks described as a data."""
    id: str
    category: str
    tool: str
    args: dict
    judge: Callable[[Outcome], tuple[str, str]]
    # above attributes describe the unique name (id), which mcp tool to call and what arguments to send
    timeout: float = 10.0 # limit for the attack 

@dataclass
class Finding:
    """Finds and generates report"""
    case_id: str
    category: str
    verdict: str
    evidence: str
    elapsed: float
