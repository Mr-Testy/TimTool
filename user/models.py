from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.template.defaultfilters import slugify
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from rest_framework.authtoken.models import Token
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings

ROLES = (("admin", "admin"), ("member", "member"), )
USERNAME_REGEX = '^[a-zA-Z0-9.@+-]*$'


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError(_('A user must have an email address.'))

        user = self.model(
            username=username,
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username,
            email,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(
        max_length=255,
        validators=[
            RegexValidator(
                regex=USERNAME_REGEX,
                message=_("The user cannot contain other special characters than : '. @ + -'"),
                code='invalid_username'
            )],
        unique=True
    )
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True, auto_now=False)

    tunes_favoris = models.ManyToManyField('tune.TuneFavori_user')
    groupe_roles = models.ManyToManyField('user.UserGroupRole')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        ordering = ["-date_creation"]

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    def has_tune_favori(self, tune_favori):
        if self.tunes_favoris.filter(slug=tune_favori.slug).exists():
            return True
        else:
            return False

    def is_admin_of_this_group(self, request, group):
        if request.user.groupe_roles.filter(of_group=group).exists():
            if request.user.groupe_roles.filter(of_group=group).first().role == "admin":
                return True
        messages.error(request, _('Only administrators of the group can use this functionnality'))
        return False


class GroupExtendManager(models.Manager):
    def create_groupextend(self, name, description, created_by):
        groupextend = self.create(name=name, description=description, slug=slugify(name), created_by=created_by)
        groupextend.save()
        return groupextend


class GroupExtend(models.Model):
    name = models.CharField(max_length=155)
    tunes_favoris = models.ManyToManyField('tune.TuneFavori_group')
    description = models.TextField(null=False)
    nb_vues = models.IntegerField(default=0)
    slug = models.SlugField(max_length=120, unique=True)
    user_roles = models.ManyToManyField('user.UserGroupRole')
    date_creation = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(User, related_name="created_group")

    objects = GroupExtendManager()

    def __str__(self):
        return _('Group : "%(groupname)s"') % {'groupname': self.name}

    class Meta:
        ordering = ["-date_creation"]


class UserGroupRole(models.Model):
    date_creation = models.DateTimeField(auto_now_add=True, auto_now=False)
    of_group = models.ForeignKey(GroupExtend)
    of_user = models.ForeignKey(User)
    role = models.CharField(max_length=15, null=False, blank=False)

    class Meta:
        ordering = ["-date_creation"]


# This receiver handles token creation immediately a new user is created.
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)