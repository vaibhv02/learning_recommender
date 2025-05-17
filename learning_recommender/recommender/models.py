from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Topic:
    name: str
    prerequisites: List[str] = field(default_factory=list)

@dataclass
class User:
    user_id: str
    name: str

@dataclass
class UserProgress:
    user_id: str
    mastery: Dict[str, float] = field(default_factory=dict)  # topic_name -> mastery score 