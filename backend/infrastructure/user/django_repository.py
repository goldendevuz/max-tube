from typing import List, Optional
from backend.domain.user.models import User
from backend.domain.user.repositories import UserRepository
from .models import UserModel

class DjangoUserRepository(UserRepository):
    """Django ORM implementation of the UserRepository interface."""

    def _to_domain(self, orm_user: UserModel) -> User:
        return User(
            id=orm_user.id,
            username=orm_user.username,
            email=orm_user.email,
            is_active=orm_user.is_active,
            full_name=orm_user.full_name,
        )

    def get_by_id(self, user_id: int) -> Optional[User]:
        try:
            orm_user = UserModel.objects.get(pk=user_id)
            return self._to_domain(orm_user)
        except UserModel.DoesNotExist:
            return None

    def get_by_username(self, username: str) -> Optional[User]:
        try:
            orm_user = UserModel.objects.get(username=username)
            return self._to_domain(orm_user)
        except UserModel.DoesNotExist:
            return None

    def list_active(self) -> List[User]:
        orm_users = UserModel.objects.filter(is_active=True)
        return [self._to_domain(u) for u in orm_users]

    def save(self, user: User) -> User:
        # Save or update ORM model
        orm_user, created = UserModel.objects.update_or_create(
            username=user.username,
            defaults={
                "email": user.email,
                "is_active": user.is_active,
                "full_name": user.full_name,
            }
        )
        return self._to_domain(orm_user)
