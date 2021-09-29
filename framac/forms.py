from django import forms
from django.views.generic.edit import UpdateView
from django.utils.safestring import mark_safe

from .models import File, Directory, User
from . import variables


class FileForm(forms.Form):
    name = forms.CharField(label=mark_safe('File name'), max_length=100)
    description = forms.CharField(required=False, label=mark_safe('File description:'), max_length=100)

    file = forms.FileField()

    CHOICES = list()
    CHOICES.append(('', ''))

    dirs = Directory.objects.filter(availability_flag=True, owner=variables.user_model)
    for dir in dirs.iterator():
        CHOICES.append((dir.name, dir.name))

    placed_in = forms.TypedChoiceField(required=False, choices=CHOICES, coerce=str)

    def __init__(self, *args, **kwargs):
        super(FileForm, self).__init__(*args, **kwargs)
        CHOICES = list()
        CHOICES.append(('', ''))

        dirs = Directory.objects.filter(availability_flag=True, owner=variables.user_model)
        for dir in dirs.iterator():
            CHOICES.append((dir.name, dir.name))

        placed_in = forms.TypedChoiceField(required=False, choices=CHOICES, coerce=str)
        self.fields['placed_in'] = placed_in


class DirectoryForm(forms.Form):
    name = forms.CharField(label='Directory name', max_length=100)
    description = forms.CharField(required=False, label='Directory description', max_length=100)

    CHOICES = list()
    CHOICES.append(('', ''))

    dirs = Directory.objects.filter(availability_flag=True, owner=variables.user_model)
    for dir in dirs.iterator():
        CHOICES.append((dir.name, dir.name))

    placed_in = forms.TypedChoiceField(required=False, choices=CHOICES, coerce=str)

    def __init__(self, *args, **kwargs):
        super(DirectoryForm, self).__init__(*args, **kwargs)

        CHOICES = list()
        CHOICES.append(('', ''))

        dirs = Directory.objects.filter(availability_flag=True, owner=variables.user_model)
        for dir in dirs.iterator():
            CHOICES.append((dir.name, dir.name))

        placed_in = forms.TypedChoiceField(required=False, choices=CHOICES, coerce=str)
        self.fields['placed_in'] = placed_in


class DeleteDirForm(forms.Form):
    CHOICES = list()

    dirs = Directory.objects.filter(availability_flag=True, owner=variables.user_model)
    for dir in dirs.iterator():
        CHOICES.append(('d'+dir.name, 'DIR: ' + dir.name))

    files = File.objects.filter(availability_flag=True, owner=variables.user_model)
    for file in files.iterator():
        CHOICES.append(('f'+file.name, 'FILE: ' + file.name))

    choice = forms.TypedChoiceField(choices=CHOICES, coerce=str)

    def __init__(self, *args, **kwargs):
        CHOICES = list()
        super(DeleteDirForm, self).__init__(*args, **kwargs)

        dirs = Directory.objects.filter(availability_flag=True, owner=variables.user_model)
        for dir in dirs.iterator():
            CHOICES.append(('d' + dir.name, 'DIR: ' + dir.name))

        files = File.objects.filter(availability_flag=True, owner=variables.user_model)
        for file in files.iterator():
            CHOICES.append(('f' + file.name, 'FILE: ' + file.name))

        choice = forms.TypedChoiceField(choices=CHOICES, )
        self.fields['choice'] = choice


class ProverForm(forms.Form):
    CHOICES = [('alt-ergo', 'Alt_ergo'),
               ('Z3', 'Z3'),
               ('cvc4', 'CVC4')]

    Provers = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)


class VeriFrorm(forms.Form):
    CHOICES = [(' -wp-rte', 'wp-rte compilation flag'),
               ('-@lemma', '@lemma'),
               ('-@requires', '@requires'),
               ('-@assigns', '@assigns'),
               ('-@ensures', '@ensures'),
               ('-@exits', '@exits'),
               ('-@assert', '@assert'),
               ('-@check', '@check'),
               ('-@invariant', '@invariant'),
               ('-@variant', '@variant'),
               ('-@breaks', '@breaks'),
               ('-@continues', '@continues'),
               ('-@returns', '@returns'),
               ('-@complete_behaviors', '@complete_behaviors'),
               ('-@disjoint_behaviors', '@disjoint_behaviors')]

    Properties = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, choices=CHOICES)


class UserForm(forms.Form):
    login = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

