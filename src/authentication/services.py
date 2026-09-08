from django.contrib.auth import login

from src.authentication.exceptions import AuthError
from src.users.models import User


def register_user(
    *,
    email: str,
    password: str,
    first_name: str,
    last_name: str = '',
    phone: str = '',
) -> User:
    email = email.lower().strip()
    if User.objects.filter(email=email).exists():
        raise AuthError('Користувач з таким email вже існує.')
    return User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        phone=phone.strip() or None,
        role=User.Role.CUSTOMER,
    )


def update_profile(user: User, *, first_name: str, last_name: str, phone: str) -> User:
    user.first_name = first_name.strip()
    user.last_name = last_name.strip()
    user.phone = phone.strip() or None
    user.save(update_fields=['first_name', 'last_name', 'phone', 'updated_at'])
    return user


def change_password(user: User, *, old_password: str, new_password: str) -> None:
    if not user.check_password(old_password):
        raise AuthError('Поточний пароль невірний.')
    user.set_password(new_password)
    user.save(update_fields=['password', 'updated_at'])


def complete_login(request, user: User) -> None:
    session_key = request.session.session_key
    login(request, user)
    from src.commerce.services import merge_guest_cart

    merge_guest_cart(user, session_key)
