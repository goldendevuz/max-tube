from typing import Optional
from backend.domain.user.models import User
from backend.domain.user.repositories import UserRepository

class UserService:
    """Application services for User domain."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their ID."""
        return self.user_repository.get_by_id(user_id)

    def create_user(self, username: str, email: str, full_name: Optional[str] = None) -> User:
        """Create and persist a new user."""
        user = User(
            id=0,  # placeholder before persistence
            username=username,
            email=email,
            is_active=True,
            full_name=full_name
        )
        return self.user_repository.save(user)
