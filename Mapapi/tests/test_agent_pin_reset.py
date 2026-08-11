"""Tests for the field-agent "forgot PIN" flow: AgentRequestResetPinView
(request an email with a reset link) and AgentResetPinLinkView (the public
link that lets the agent set a new PIN).

`send_email.delay` and `send_sms_task.delay` are always mocked — no real
email/SMS is ever sent by these tests.
"""
from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from Mapapi.models import PasswordReset, ORG_ROLE_FIELD


class AgentRequestResetPinViewTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.client = APIClient()
        self.agent = User.objects.create_user(
            email='agent@test.com',
            password='unused',
            first_name='Agent',
            last_name='Terrain',
            phone='+22370000000',
            org_role=ORG_ROLE_FIELD,
            is_active=True,
        )

    @patch('Mapapi.Send_mails.send_email.delay')
    def test_request_by_email_creates_reset_and_sends_email(self, mock_send_email):
        url = reverse('agent-request-reset-pin')
        response = self.client.post(url, {'email': 'agent@test.com'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reset = PasswordReset.objects.filter(user=self.agent, used=False).first()
        self.assertIsNotNone(reset)
        self.assertEqual(len(reset.code), 36)  # uuid4

        mock_send_email.assert_called_once()
        call_kwargs = mock_send_email.call_args[1]
        self.assertEqual(call_kwargs['to_email'], 'agent@test.com')
        self.assertIn(reset.code, call_kwargs['context']['reset_link'])

    @patch('Mapapi.Send_mails.send_email.delay')
    def test_request_by_phone(self, mock_send_email):
        url = reverse('agent-request-reset-pin')
        response = self.client.post(url, {'phone': '+22370000000'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_send_email.assert_called_once()

    def test_missing_email_and_phone_returns_400(self):
        url = reverse('agent-request-reset-pin')
        response = self.client.post(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unknown_agent_returns_404(self):
        url = reverse('agent-request-reset-pin')
        response = self.client.post(url, {'email': 'nobody@test.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('Mapapi.Send_mails.send_email.delay')
    def test_inactive_agent_not_found(self, mock_send_email):
        self.agent.is_active = False
        self.agent.save(update_fields=['is_active'])
        url = reverse('agent-request-reset-pin')
        response = self.client.post(url, {'email': 'agent@test.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        mock_send_email.assert_not_called()


class AgentResetPinLinkViewTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.client = APIClient()
        self.agent = User.objects.create_user(
            email='agent2@test.com',
            password='unused',
            first_name='Agent',
            last_name='Deux',
            phone='+22370000001',
            org_role=ORG_ROLE_FIELD,
            is_active=True,
            pin_code=make_password('9999'),
            must_change_pin=True,
        )
        self.reset = PasswordReset.objects.create(user=self.agent, code='a' * 36)

    def test_get_valid_token_renders_form(self):
        url = reverse('agent-reset-pin-link', args=[self.reset.code])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'new_pin', response.content)

    def test_get_unknown_token_returns_error_page(self):
        url = reverse('agent-reset-pin-link', args=['does-not-exist'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('invalide', response.content.decode())

    def test_get_expired_token_returns_error_page(self):
        self.reset.date_created = timezone.now() - timedelta(hours=2)
        self.reset.save(update_fields=['date_created'])
        url = reverse('agent-reset-pin-link', args=[self.reset.code])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('expiré', response.content.decode())

    def test_post_sets_new_pin_and_consumes_token(self):
        url = reverse('agent-reset-pin-link', args=[self.reset.code])
        response = self.client.post(url, {'new_pin': '4321', 'confirm_pin': '4321'})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.content.lower())

        self.agent.refresh_from_db()
        self.assertTrue(self.agent.check_pin('4321'))
        self.assertFalse(self.agent.must_change_pin)

        self.reset.refresh_from_db()
        self.assertTrue(self.reset.used)
        self.assertIsNotNone(self.reset.date_used)

    def test_post_mismatched_pins_returns_error(self):
        url = reverse('agent-reset-pin-link', args=[self.reset.code])
        response = self.client.post(url, {'new_pin': '4321', 'confirm_pin': '1234'})
        self.assertEqual(response.status_code, 400)
        self.reset.refresh_from_db()
        self.assertFalse(self.reset.used)

    def test_post_weak_pin_returns_error(self):
        url = reverse('agent-reset-pin-link', args=[self.reset.code])
        response = self.client.post(url, {'new_pin': '1234', 'confirm_pin': '1234'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('simple', response.content.decode())

    def test_post_non_numeric_pin_returns_error(self):
        url = reverse('agent-reset-pin-link', args=[self.reset.code])
        response = self.client.post(url, {'new_pin': 'abcd', 'confirm_pin': 'abcd'})
        self.assertEqual(response.status_code, 400)

    def test_used_token_cannot_be_reused(self):
        self.reset.used = True
        self.reset.save(update_fields=['used'])
        url = reverse('agent-reset-pin-link', args=[self.reset.code])
        response = self.client.post(url, {'new_pin': '4321', 'confirm_pin': '4321'})
        self.assertEqual(response.status_code, 400)


class FieldAgentCreateSmsTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from Mapapi.models import Organisation, ORG_ROLE_ADMIN
        User = get_user_model()
        self.client = APIClient()
        self.org = Organisation.objects.create(name="Org Test")
        self.admin = User.objects.create_user(
            email='admin@test.com',
            password='testpass123',
            first_name='Admin',
            last_name='Org',
            org_role=ORG_ROLE_ADMIN,
            organisation_member=self.org,
            is_active=True,
        )
        self.client.force_authenticate(user=self.admin)

    @patch('Mapapi.Send_mails.send_sms_task.delay')
    @patch('Mapapi.Send_mails.send_email.delay')
    def test_creating_field_agent_queues_sms_when_phone_present(self, mock_send_email, mock_send_sms):
        url = reverse('organisation-field-agent-create', args=[self.org.id])
        response = self.client.post(url, {
            'first_name': 'New',
            'last_name': 'Agent',
            'email': 'newagent@test.com',
            'phone': '+22371111111',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data.get('sms_sent'))
        mock_send_sms.assert_called_once()
        args = mock_send_sms.call_args[0]
        self.assertEqual(args[0], '+22371111111')
