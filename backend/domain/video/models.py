from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Video:
    """Core Video aggregate root.
    Pure domain object, independent of persistence.
    """
    id: int
    title: str
    description: Optional[str] = None
    url: str
    uploaded_by_user_id: int
    is_public: bool = True
