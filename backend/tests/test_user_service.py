import pytest
from django.test import TestCase
from backend.domain.user.models import User
from backend.application.user.services import UserService
from backend.infrastructure.user.django_repository import DjangoUserRepository

class TestUserService(TestCase):
    def setUp(self):
        self.repo = DjangoUserRepository()
        self.service = UserService(self.repo)
        # create a sample user in the db via ORM model
        from backend.infrastructure.user.models import UserModel
        self.orm_user = UserModel.objects.create(username='alice', email='alice@example.com')

    def test_get_by_id(self):
        user = self.service.get_user_by_id(self.orm_user.id)
        assert isinstance(user, User)
        assert user.username == 'alice'

    def test_create_user(self):
        new_user = self.service.create_user(username='bob', email='bob@example.com')
        assert new_user.id is not None
        assert new_user.username == 'bob'
        # ensure persisted
        from backend.infrastructure.user.models import UserModel
        assert UserModel.objects.filter(username='bob').exists()
