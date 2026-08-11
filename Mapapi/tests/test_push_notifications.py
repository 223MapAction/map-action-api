"""Tests for FCM push notifications: the Celery task, the token-registration
endpoint, and the incident state-change trigger.

`firebase_admin.messaging.send` is always mocked — these tests never make a
real network call to Firebase.
"""
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from Mapapi.models import Incident, Zone, TAKEN, RESOLVED_DEFINITIVE, Notification
from Mapapi.tasks import send_push_notification_task

User = get_user_model()


class SendPushNotificationTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='citizen@test.com',
            password='testpass123',
            first_name='Citizen',
            last_name='One',
            fcm_token='device-token-abc',
        )

    @patch('firebase_admin.messaging.send')
    def test_sends_with_correct_token_and_message(self, mock_send):
        mock_send.return_value = 'projects/x/messages/1'

        send_push_notification_task(
            str(self.user.id), "Incident pris en compte", "Votre incident a été pris en compte.",
            data={"incident_id": "abc-123"},
        )

        mock_send.assert_called_once()
        message = mock_send.call_args[0][0]
        self.assertEqual(message.token, 'device-token-abc')
        self.assertEqual(message.notification.title, "Incident pris en compte")
        self.assertEqual(message.notification.body, "Votre incident a été pris en compte.")
        self.assertEqual(message.data, {"incident_id": "abc-123"})

    @patch('firebase_admin.messaging.send')
    def test_no_op_when_user_has_no_fcm_token(self, mock_send):
        self.user.fcm_token = None
        self.user.save(update_fields=['fcm_token'])

        send_push_notification_task(str(self.user.id), "Titre", "Message")

        mock_send.assert_not_called()

    @patch('firebase_admin.messaging.send')
    def test_no_op_when_user_does_not_exist(self, mock_send):
        send_push_notification_task('00000000-0000-0000-0000-000000000000', "Titre", "Message")

        mock_send.assert_not_called()

    @patch('firebase_admin.messaging.send')
    def test_invalid_token_is_cleared(self, mock_send):
        from firebase_admin import messaging
        mock_send.side_effect = messaging.UnregisteredError("token invalide")

        send_push_notification_task(str(self.user.id), "Titre", "Message")

        self.user.refresh_from_db()
        self.assertIsNone(self.user.fcm_token)


class UpdateFCMTokenViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='mobile@test.com',
            password='testpass123',
            first_name='Mobile',
            last_name='User',
        )
        self.url = reverse('update-fcm-token')

    def test_requires_authentication(self):
        response = self.client.post(self.url, {'fcm_token': 'abc'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_registers_token(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'fcm_token': 'new-token'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.fcm_token, 'new-token')

    def test_updates_existing_token_via_put(self):
        self.user.fcm_token = 'old-token'
        self.user.save(update_fields=['fcm_token'])
        self.client.force_authenticate(user=self.user)

        response = self.client.put(self.url, {'fcm_token': 'updated-token'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.fcm_token, 'updated-token')

    def test_missing_token_returns_400(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class IncidentStatusChangePushTests(TestCase):
    def setUp(self):
        self.citizen = User.objects.create_user(
            email='reporter@test.com',
            password='testpass123',
            first_name='Reporter',
            last_name='Citizen',
            fcm_token='citizen-device-token',
        )
        self.org_user = User.objects.create_user(
            email='org@test.com',
            password='testpass123',
            first_name='Org',
            last_name='Agent',
        )
        self.zone = Zone.objects.create(name="Test Zone", description="desc")
        self.incident = Incident.objects.create(
            title="Nid de poule",
            description="desc",
            zone=self.zone.name,
            user_id=self.citizen,
        )

    @patch('Mapapi.tasks.send_push_notification_task.delay')
    def test_taken_into_account_triggers_push_and_notification(self, mock_delay):
        self.incident.etat = TAKEN
        self.incident.taken_by = self.org_user
        self.incident.save()

        mock_delay.assert_called_once()
        args, kwargs = mock_delay.call_args
        self.assertEqual(args[0], str(self.citizen.id))
        self.assertEqual(kwargs['data'], {"incident_id": str(self.incident.id)})

        notification = Notification.objects.filter(
            user=self.citizen, notif_type='incident_taken_into_account',
        ).first()
        self.assertIsNotNone(notification)

    @patch('Mapapi.tasks.send_push_notification_task.delay')
    def test_resolved_triggers_push_and_notification(self, mock_delay):
        self.incident.etat = RESOLVED_DEFINITIVE
        self.incident.save()

        mock_delay.assert_called_once()
        notification = Notification.objects.filter(
            user=self.citizen, notif_type='incident_resolved',
        ).first()
        self.assertIsNotNone(notification)

    @patch('Mapapi.tasks.send_push_notification_task.delay')
    def test_unrelated_field_change_does_not_trigger_push(self, mock_delay):
        self.incident.description = "description mise à jour"
        self.incident.save()

        mock_delay.assert_not_called()
