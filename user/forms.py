from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _

from .models import GroupExtend

User = get_user_model()

SUBJECTS = (("Demande d'évolution", _("Improvement request")), ("Suggestion", "Suggestion"), ("Anomalie", _("Bug")), ("Demande d'information", _("Information request")),
            ("Simple message", "Simple message"))


class ContactForm(forms.Form):
    sujet = forms.ChoiceField(label=_("Topic"), choices=SUBJECTS)
    message = forms.CharField(widget=forms.Textarea)
    envoyeur = forms.EmailField(label=_("Your mail address"))
    renvoi = forms.BooleanField(label=_("Receive a copy"), help_text=_("Check if you wish to receive a copy of this email"), required=False)


class CompareUserForm(forms.Form):
    to_compare = forms.ChoiceField(
        choices=(("Mes tunes favoris appris", _("Only my favorite learned Tunes")), ("Mes tunes favoris", _("All my favorite Tunes"))),
        initial="Mes tunes favoris appris",
        widget=forms.Select(attrs={'class': ''}),
        label=_("Compare : "),
        required=True
    )

    def __init__(self, *args, **kwargs):
        USER_CHOICES = [(o.username, o.username) for o in User.objects.order_by("username")]
        USER_CHOICES.insert(0, ("not_chosen", _("Select a user")))
        GROUP_CHOICES = [(o.name, o.name) for o in GroupExtend.objects.order_by("name")]
        GROUP_CHOICES.insert(0, ("not_chosen", _("Select a group")))
        super(CompareUserForm, self).__init__(*args, **kwargs)
        self.fields['username'] = forms.ChoiceField(
        choices=USER_CHOICES,
        label=_("With one of the following users : "),
        )
        self.fields['groupname'] = forms.ChoiceField(
        choices=GROUP_CHOICES,
        label=_("Or one of the following groups : "),
        )

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        groupname = self.cleaned_data.get("groupname")
        if (username == "not_chosen" and groupname == "not_chosen"):
            raise forms.ValidationError(_("You must choose a user or a group"))
        if (not username == "not_chosen" and not groupname == "not_chosen"):
            raise forms.ValidationError(_("You must choose a user OR a group, but not both"))
        return super(CompareUserForm, self).clean(*args, **kwargs)


class GroupForm(forms.Form):
    name = forms.CharField(label=_('Group'), max_length=100)
    description = forms.CharField(label='Description', widget=forms.Textarea, required=True)


class UserForm(forms.Form):
    username = forms.CharField(
        max_length=150,
    )
    # first_name = forms.CharField(max_length=30, required=False)
    # last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField()


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Confirm password'), widget=forms.PasswordInput)
    username = forms.CharField(label=_('Username'))
    email = forms.CharField(label='Email')

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords don't match"))
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        # Create a new hash to activing
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'is_active', 'is_staff', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]
