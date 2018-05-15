from django.db import models
from user.models import User, GroupExtend
from django.template.defaultfilters import slugify
from django.db.models.signals import pre_save


class Tune(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False)
    key = models.CharField(max_length=6, null=False, blank=False)
    type = models.CharField(max_length=15, null=False, blank=False)
    slug = models.SlugField(max_length=160, unique=True, null=False, blank=False)  # concat name-key-type
    description = models.TextField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True, auto_now=False)
    added_by = models.ForeignKey(User, null=False, blank=False)
    nb_vues = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = self.name + "-" + self.key + "-" + self.type
        self.slug = (slugify(self.slug))
        super(Tune, self).save(*args, **kwargs)

    class Meta:
        ordering = ["-date_creation"]

    def has_audio(self):
        if Audio_clyp_user_favori.objects.filter(of_tune_favori_user__of_tune=self).count() > 0 or Audio_clyp_group_favori.objects.filter(of_tune_favori_group__of_tune=self).count() > 0:
            return True
        return False


class Title(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False)
    slug = models.SlugField(max_length=160, unique=True, null=False, blank=False)  # concat name-key-type
    date_creation = models.DateTimeField(auto_now_add=True, auto_now=False)
    belong_to_tune = models.ForeignKey(Tune, related_name='titles')

    class Meta:
        ordering = ["-date_creation"]


class Composer(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False, unique=True)
    slug = models.SlugField(max_length=160, unique=True, null=False, blank=False)  # concat name-key-type
    date_creation = models.DateTimeField(auto_now_add=True, auto_now=False)
    composed_tunes = models.ManyToManyField(Tune, related_name='composers')


class Source(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True, auto_now=False)
    of_tunes = models.ManyToManyField(Tune, related_name='sources')


class Discography(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True, auto_now=False)
    composed_tunes = models.ManyToManyField(Tune, related_name='discographies')


class ABCTune(models.Model):
    date_creation = models.DateTimeField(auto_now_add=True, auto_now=False)
    X = models.IntegerField()
    T = models.CharField(max_length=150, null=False, blank=False)
    R = models.CharField(max_length=30, null=False, blank=False)
    C = models.CharField(max_length=150)
    S = models.CharField(max_length=150)
    H = models.TextField()
    D = models.CharField(max_length=150)
    Z = models.CharField(max_length=150, null=True, blank=False)
    M = models.CharField(max_length=10, null=False, blank=False)
    L = models.CharField(max_length=10, null=False, blank=False)
    Q = models.CharField(max_length=10, null=False, blank=False)
    K = models.CharField(max_length=10, null=False, blank=False)
    W = models.TextField()
    N = models.TextField(null=True)
    Z = models.CharField(max_length=150, null=True, blank=False)
    content = models.TextField(null=False, blank=False)
    created_by = models.CharField(max_length=30)
    other_title = models.CharField(max_length=100, null=True)
    other_title2 = models.CharField(max_length=100, null=True)
    other_composer = models.CharField(max_length=150, null=True)
    other_composer2 = models.CharField(max_length=150, null=True)
    version = models.CharField(max_length=150, null=False, blank=False)
    tune = models.ForeignKey(Tune, null=False, blank=False, related_name='abcs')
    from_user = models.ForeignKey(User, null=True, related_name='posted_abcs')
    version_is_from_tunebook = models.BooleanField(default=False, null=False, blank=False) 
    # Si le Tune ne provient pas d'un Tunebook, il faut que "from_user" soit valorisé

    
class TuneFavori(models.Model):
    personal_note = models.TextField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True, auto_now=False)
    of_tune = models.ForeignKey(Tune, null=False, blank=False)
    status = models.BooleanField(default=False, null=False, blank=False)
    slug = models.SlugField(max_length=120, unique=True, null=False, blank=False)  # concat tune.slug and user.username

    class Meta:
        ordering = ["-date_creation"]


class TuneFavori_group(TuneFavori):
    of_group = models.ForeignKey(GroupExtend, null=False, blank=False)

    def __str__(self):
        return "{}, {}, {}. Favori of group {}".format(
            self.of_tune.name,
            self.of_tune.type,
            self.of_tune.key,
            self.of_group.name
        )

    def has_audio(self):
        if self.audio_clyp_group_favori_set.count() > 0:
            return True
        return False


class TuneFavori_user(TuneFavori):
    of_user = models.ForeignKey(User, null=False, blank=False)

    def __str__(self):
        return "{}, {}, {}. Favori of user {}".format(
            self.of_tune.name,
            self.of_tune.type,
            self.of_tune.key,
            self.of_user.username
        )

    def has_audio(self):
        if self.audio_clyp_user_favori_set.count() > 0:
            return True
        return False


def create_tune_favori_slug_group(sender, instance, **kwargs):
    instance.slug = instance.of_tune.slug + "-" + instance.of_group.name + "-group"
    instance.slug = slugify(instance.slug)


pre_save.connect(create_tune_favori_slug_group, sender=TuneFavori_group)


def create_tune_favori_slug_user(sender, instance, **kwargs):
    instance.slug = instance.of_tune.slug + "-" + instance.of_user.username + "-user"
    instance.slug = slugify(instance.slug)


pre_save.connect(create_tune_favori_slug_user, sender=TuneFavori_user)


class Audio_clyp(models.Model):
    date_creation = models.DateTimeField(auto_now_add=True, auto_now=False)
    href = models.URLField(null=False, blank=False)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(max_length=120, unique=True, null=False, blank=False)
    name = models.CharField(max_length=50, null=False, blank=False)
    added_by = models.ForeignKey(User, null=False, blank=False)

    class Meta:
        ordering = ["-date_creation"]


class Audio_clyp_tune(Audio_clyp):
    of_tune = models.ForeignKey(Tune, null=False, blank=False)


class Audio_clyp_user_favori(Audio_clyp):
    of_tune_favori_user = models.ForeignKey(TuneFavori_user, null=False, blank=False)


class Audio_clyp_group_favori(Audio_clyp):
    of_tune_favori_group = models.ForeignKey(TuneFavori_group, null=False, blank=False)


def create_clyp_tune_slug(sender, instance, **kwargs):
    instance.slug = instance.href + "-" + instance.of_tune.name
    instance.slug = slugify(instance.slug)


pre_save.connect(create_clyp_tune_slug, sender=Audio_clyp_tune)


def create_clyp_user_favori_slug(sender, instance, **kwargs):
    instance.slug = instance.href + "-" + instance.of_tune_favori_user.of_user.username
    instance.slug = slugify(instance.slug)


pre_save.connect(create_clyp_user_favori_slug, sender=Audio_clyp_user_favori)


def create_clyp_group_favori_slug(sender, instance, **kwargs):
    instance.slug = instance.href + "-" + instance.of_tune_favori_group.of_group.name
    instance.slug = slugify(instance.slug)


pre_save.connect(create_clyp_group_favori_slug, sender=Audio_clyp_group_favori)
