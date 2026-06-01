from abc import ABC, abstractmethod
from typing import List, Optional

from .models import User

class UserRepository(ABC):
    """Interface defining persistence operations for User aggregate."""

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a User by its ID."""
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """Retrieve a User by username."""
        pass

    @abstractmethod
    def list_active(self) -> List[User]:
        """Return all active users."""
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        """Persist a User (create or update)."""
        pass
