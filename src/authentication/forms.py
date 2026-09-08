from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.password_validation import validate_password

from src.users.models import User


def _input(placeholder: str, input_type: str = 'text', autocomplete: str = 'on') -> forms.TextInput:
    widget_cls = forms.PasswordInput if input_type == 'password' else forms.TextInput
    attrs = {
        'class': 'form-control',
        'placeholder': ' ',
        'autocomplete': autocomplete,
    }
    if input_type == 'email':
        widget_cls = forms.EmailInput
    elif input_type == 'password':
        widget_cls = forms.PasswordInput
    elif input_type == 'tel':
        widget_cls = forms.TextInput
        attrs['type'] = 'tel'
    return widget_cls(attrs=attrs)


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=_input('Email', 'email', 'email'),
    )
    password = forms.CharField(
        label='Пароль',
        widget=_input('Пароль', 'password', 'current-password'),
    )

    def clean_username(self):
        return self.cleaned_data['username'].lower().strip()

    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': 'Невірний email або пароль.',
    }


class RegisterForm(forms.Form):
    first_name = forms.CharField(
        label="Імʼя",
        max_length=150,
        widget=_input("Імʼя", autocomplete='given-name'),
    )
    last_name = forms.CharField(
        label='Прізвище',
        max_length=150,
        required=False,
        widget=_input('Прізвище', autocomplete='family-name'),
    )
    email = forms.EmailField(
        label='Email',
        widget=_input('Email', 'email', 'email'),
    )
    phone = forms.CharField(
        label='Телефон',
        max_length=32,
        required=False,
        widget=_input('Телефон', 'tel', 'tel'),
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=_input('Пароль', 'password', 'new-password'),
    )
    password2 = forms.CharField(
        label='Повторіть пароль',
        widget=_input('Повторіть пароль', 'password', 'new-password'),
    )

    def clean_email(self):
        return self.cleaned_data['email'].lower().strip()

    def clean_password1(self):
        password = self.cleaned_data['password1']
        validate_password(password)
        return password

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') and cleaned.get('password2'):
            if cleaned['password1'] != cleaned['password2']:
                self.add_error('password2', 'Паролі не збігаються.')
        return cleaned


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone')
        widgets = {
            'first_name': _input("Імʼя", autocomplete='given-name'),
            'last_name': _input('Прізвище', autocomplete='family-name'),
            'phone': _input('Телефон', 'tel', 'tel'),
        }


class CabinetPasswordForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget = _input(
            'Поточний пароль', 'password', 'current-password'
        )
        self.fields['new_password1'].widget = _input(
            'Новий пароль', 'password', 'new-password'
        )
        self.fields['new_password2'].widget = _input(
            'Повторіть новий пароль', 'password', 'new-password'
        )


class CabinetPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget = _input('Email', 'email', 'email')
        self.fields['email'].label = 'Email'


class ResetSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget = _input(
            'Новий пароль', 'password', 'new-password'
        )
        self.fields['new_password2'].widget = _input(
            'Повторіть новий пароль', 'password', 'new-password'
        )
