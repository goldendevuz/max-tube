    from django.db import models
from utils.crypto import encrypt, decrypt


class EncryptedTextField(models.TextField):

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return decrypt(value)

    def to_python(self, value):
        if value is None:
            return value
        return decrypt(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return encrypt(value)


class EncryptedCharField(models.CharField):

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return decrypt(value)

    def to_python(self, value):
        if value is None:
            return value
        return decrypt(value)

    def get_prep_value(self, value):
        if value is None:
            return value
        return encrypt(value)
