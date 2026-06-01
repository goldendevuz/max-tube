from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class User:
    """Core User aggregate root.
    This is a pure domain object, independent of any persistence framework.
    """
    id: int
    username: str
    email: str
    is_active: bool = True
    full_name: Optional[str] = None
