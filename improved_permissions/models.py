""" permissions models """
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class RolePermission(models.Model):
    """
    Role

    This model rocks.

    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='roles',
        verbose_name='Usuário'
    )

    role_class = models.CharField(max_length=256)

    _role_object_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    _role_object_id = models.PositiveIntegerField()
    obj = GenericForeignKey(ct_field='_role_object_type', fk_field='_role_object_id')

    class Meta:
        unique_together = ('user', '_role_object_type', '_role_object_id')
