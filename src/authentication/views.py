from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from src.authentication.exceptions import AuthError
from src.authentication.forms import (
    CabinetPasswordForm,
    CabinetPasswordResetForm,
    EmailAuthenticationForm,
    ProfileForm,
    RegisterForm,
    ResetSetPasswordForm,
)
from src.authentication.services import complete_login, register_user, update_profile


class LoginView(auth_views.LoginView):
    template_name = 'authentication/login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Вхід'
        return context

    def form_valid(self, form):
        complete_login(self.request, form.get_user())
        return redirect(self.get_success_url())


class RegisterView(FormView):
    template_name = 'authentication/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('authentication:account')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Реєстрація'
        return context

    def form_valid(self, form):
        try:
            user = register_user(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data.get('last_name') or '',
                phone=form.cleaned_data.get('phone') or '',
            )
        except AuthError as exc:
            form.add_error('email', str(exc))
            return self.form_invalid(form)
        complete_login(self.request, user)
        messages.success(self.request, 'Акаунт створено.')
        return super().form_valid(form)


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('content:home')
    http_method_names = ['post', 'options']


class PasswordResetView(auth_views.PasswordResetView):
    template_name = 'authentication/password_reset.html'
    form_class = CabinetPasswordResetForm
    email_template_name = 'authentication/password_reset_email.txt'
    subject_template_name = 'authentication/password_reset_subject.txt'
    success_url = reverse_lazy('authentication:password_reset_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Скидання пароля'
        return context


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'authentication/password_reset_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Лист надіслано'
        return context


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'authentication/password_reset_confirm.html'
    form_class = ResetSetPasswordForm
    success_url = reverse_lazy('authentication:password_reset_complete')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Новий пароль'
        return context


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'authentication/password_reset_complete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Пароль змінено'
        return context


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'authentication/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Акаунт'
        context['account_nav'] = 'profile'
        context['profile_form'] = kwargs.get('profile_form') or ProfileForm(
            instance=self.request.user
        )
        context['password_form'] = kwargs.get('password_form') or CabinetPasswordForm(
            user=self.request.user
        )
        return context

    def post(self, request, *args, **kwargs):
        action = request.POST.get('action')
        if action == 'password':
            password_form = CabinetPasswordForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Пароль змінено.')
                return redirect('authentication:account')
            return self.render_to_response(
                self.get_context_data(password_form=password_form)
            )
        profile_form = ProfileForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            update_profile(
                request.user,
                first_name=profile_form.cleaned_data['first_name'],
                last_name=profile_form.cleaned_data['last_name'],
                phone=profile_form.cleaned_data.get('phone') or '',
            )
            messages.success(request, 'Профіль збережено.')
            return redirect('authentication:account')
        return self.render_to_response(self.get_context_data(profile_form=profile_form))
