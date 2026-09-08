from django.test import TestCase
from django.urls import reverse

from src.users.models import User


class AuthFlowTests(TestCase):
    def test_login_lowercases_email(self):
        User.objects.create_user(
            email='olena@example.com',
            password='DemoBride123!',
            first_name='Олена',
        )
        response = self.client.post(
            reverse('authentication:login'),
            {'username': 'Olena@Example.com', 'password': 'DemoBride123!'},
        )
        self.assertRedirects(response, reverse('authentication:account'))
        self.assertTrue(self.client.session.get('_auth_user_id'))

    def test_register_creates_customer(self):
        response = self.client.post(
            reverse('authentication:register'),
            {
                'first_name': 'Марія',
                'last_name': 'Іваненко',
                'email': 'maria@example.com',
                'phone': '+380671110000',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
        )
        self.assertRedirects(response, reverse('authentication:account'))
        user = User.objects.get(email='maria@example.com')
        self.assertEqual(user.role, User.Role.CUSTOMER)
        self.assertEqual(user.first_name, 'Марія')

    def test_account_requires_login(self):
        response = self.client.get(reverse('authentication:account'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_duplicate_email_rejected(self):
        User.objects.create_user(email='taken@example.com', password='StrongPass123!')
        response = self.client.post(
            reverse('authentication:register'),
            {
                'first_name': 'Інша',
                'email': 'taken@example.com',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email='taken@example.com').count(), 1)
