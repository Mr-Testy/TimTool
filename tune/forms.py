from django import forms
from .models import Tune
from django.utils.translation import ugettext_lazy as _


distinct_keys = Tune.objects.values('key').distinct()
AMONG = (("Tunes favoris appris", _("Only favorite learned Tunes")), ("Tunes Favoris non appris", _("Only favorite not learned Tunes")),
         ("Tous les Tunes Favoris", _("All favorite Tunes")), ("Tous les Tunes du site", _("All Tunes of Timtool")))


class GenerateurForm(forms.Form):
    list_of = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={'class': 'list-unstyled list-inline'}),
        choices=(("Sets", _("Sets")), ('Tunes', _('Tunes'))),
        initial="Sets",
        label=_("List of "),
        required=True
    )
    among = forms.ChoiceField(
        choices=AMONG,
        initial="Tunes Favoris appris",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label=_("Among "),
        required=True
    )

    def __init__(self, *args, **kwargs):
        super(GenerateurForm, self).__init__(*args, **kwargs)
        self.fields['types'] = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'list-unstyled list-inline check1'}),
        choices=[(o.type, o.type) for o in Tune.objects.order_by("type").distinct("type")],
        # initial=[c[0] for c in Tune.objects.order_by("type").distinct("type")],
        label="Types ",
        required=True,
        error_messages={'required': _("Please select at least one type")}
        )

        self.fields['keys'] = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'list-unstyled list-inline check2'}),
        choices=[(o.key, o.key) for o in Tune.objects.order_by("key").distinct("key")],
        # initial=[c[0] for c in Tune.objects.order_by("key").distinct("key")],
        label=_("Keys "),
        required=True,
        error_messages={'required': _("Please select at least a key")}
    )


class UploadABCFileForm(forms.Form):
    file = forms.FileField(
        label=_("File "),
        required=True,
        error_messages={'required': _("Select a file")}
    )


class TextAreaABCForm(forms.Form):
    abc = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': _(".abc file here")}),
        label=_("Copy / Paste .abc file content"))


class ClypForm(forms.Form):
    name = forms.CharField(label=_("Title"), max_length=50)
    description = forms.CharField(
        label=_("Description of the sound to add"),
        widget=forms.Textarea(attrs={
            'placeholder': _('Recording of the Tune "xxx" that I have learned from "Abcdef" on "yyy" festival'),
            'rows': "2"
        }),
        required=True)
    href = forms.URLField(
        label=_("Link of the audio Clyp sound"),
        required=True,
        widget=forms.URLInput(attrs={'placeholder': 'https://clyp.it/abcdefg'}),
        error_messages={'required': _("The link of the sound is mandatory")},
    )

    def clean_href(self):
        href = self.cleaned_data['href']
        if not href.startswith("https://clyp.it/"):
            raise forms.ValidationError(_('The link must start with "https://clyp.it/"'))
        return href
