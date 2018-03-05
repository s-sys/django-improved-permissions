""" permissions models """
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models

from improved_permissions.exceptions import RoleNotFound
from improved_permissions.roles import ALL_MODELS, ALLOW_MODE
from improved_permissions.utils import (get_permissions_list, get_roleclass,
                                        permission_to_string)


class UserRole(models.Model):
    """
    UserRole

    This model represents the relationship between
    a user instance of the project with any other
    Django model, according to the rules defined
    in the Role class.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='roles',
        verbose_name='Usuário'
    )

    permissions = models.ManyToManyField(
        Permission,
        through='RolePermission',
        related_name='roles',
        verbose_name='Permissões'
    )

    role_class = models.CharField(max_length=256)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    obj = GenericForeignKey()

    class Meta:
        verbose_name = 'Role Instance'
        verbose_name_plural = 'Role Instances'
        unique_together = ('user', 'role_class', 'content_type', 'object_id')

    def __str__(self):
        role = get_roleclass(self.role_class)
        output = '{user} is {role}'.format(user=self.user, role=role.get_verbose_name())
        if self.obj:
            output += ' of {obj}'.format(obj=self.obj)
        return output

    @property
    def role(self):
        return get_roleclass(self.role_class)

    def get_verbose_name(self):
        return self.role.get_verbose_name()

    def clean(self):
        try:
            get_roleclass(self.role_class)
        except RoleNotFound:
            raise ValidationError(
                {'role_class': 'This string representation does not exist as a Role class.'}
            )

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ,unused-argument
        self.clean()
        super().save()

        # non-object roles does not have specific
        # permissions auto created.
        if self.role.models == ALL_MODELS:
            return

        all_perms = get_permissions_list(self.role.get_models())

        # Filtering the permissions based
        # on "allow" or "deny".
        role_instances = list()
        for perm in all_perms:
            access = None
            perm_s = permission_to_string(perm)
            if self.role.get_mode() == ALLOW_MODE:
                # [Allow Mode]
                # Put the access as "True" only for
                # the permissions in allow list.
                access = True if perm_s in self.role.allow else False
            else:
                # [Deny Mode]
                # Put the acces as "False" only for
                # the permissions in deny list.
                access = False if perm_s in self.role.deny else True
            role_instances.append(RolePermission(role=self, permission=perm, access=access))

        RolePermission.objects.bulk_create(role_instances)


class RolePermission(models.Model):
    """
    RolePermission

    This model has the function of performing
    the m2m relation between the Permission
    and the UserRole instances. It is possible
    that different instances of the same UserRole
    may have access to different permissions.
    """
    PERMISSION_CHOICES = (
        (True, 'Allow'),
        (False, 'Deny')
    )

    access = models.BooleanField(choices=PERMISSION_CHOICES, default=True)

    role = models.ForeignKey(
        UserRole,
        on_delete=models.CASCADE,
        related_name='accesses'
    )

    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='accesses'
    )

    class Meta:
        unique_together = ('role', 'permission')
