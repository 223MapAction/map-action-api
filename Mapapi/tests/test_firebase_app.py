"""Tests for Firebase Admin SDK initialization (Mapapi/firebase_app.py).

Never touches the real Firebase Admin SDK network calls — `credentials.Certificate`
and `firebase_admin.initialize_app` are always mocked.
"""
import base64
import json

from django.test import TestCase, override_settings

from Mapapi.firebase_app import _load_credentials, init_firebase
from unittest.mock import patch, MagicMock

FAKE_KEY_INFO = {"type": "service_account", "project_id": "mapapi-test"}
FAKE_KEY_JSON = json.dumps(FAKE_KEY_INFO)
FAKE_KEY_JSON_B64 = base64.b64encode(FAKE_KEY_JSON.encode()).decode()


class LoadCredentialsTests(TestCase):
    @override_settings(FCM_CREDENTIALS_PATH='/tmp/fake.json',
                        FCM_CREDENTIALS_JSON_BASE64=None, FCM_CREDENTIALS_JSON=None)
    @patch('Mapapi.firebase_app.credentials.Certificate')
    def test_prefers_path_when_set(self, mock_certificate):
        _load_credentials()
        mock_certificate.assert_called_once_with('/tmp/fake.json')

    @override_settings(FCM_CREDENTIALS_PATH=None,
                        FCM_CREDENTIALS_JSON_BASE64=FAKE_KEY_JSON_B64, FCM_CREDENTIALS_JSON=None)
    @patch('Mapapi.firebase_app.credentials.Certificate')
    def test_decodes_base64_json(self, mock_certificate):
        _load_credentials()
        mock_certificate.assert_called_once_with(FAKE_KEY_INFO)

    @override_settings(FCM_CREDENTIALS_PATH=None,
                        FCM_CREDENTIALS_JSON_BASE64=None, FCM_CREDENTIALS_JSON=FAKE_KEY_JSON)
    @patch('Mapapi.firebase_app.credentials.Certificate')
    def test_parses_raw_json(self, mock_certificate):
        _load_credentials()
        mock_certificate.assert_called_once_with(FAKE_KEY_INFO)

    @override_settings(FCM_CREDENTIALS_PATH=None,
                        FCM_CREDENTIALS_JSON_BASE64=None, FCM_CREDENTIALS_JSON=None)
    def test_returns_none_when_nothing_configured(self):
        self.assertIsNone(_load_credentials())


class InitFirebaseTests(TestCase):
    @patch('Mapapi.firebase_app.firebase_admin.get_app', side_effect=ValueError)
    @patch('Mapapi.firebase_app.firebase_admin.initialize_app')
    @override_settings(FCM_CREDENTIALS_PATH=None,
                        FCM_CREDENTIALS_JSON_BASE64=None, FCM_CREDENTIALS_JSON=None)
    def test_no_op_when_unconfigured(self, mock_initialize_app, mock_get_app):
        init_firebase()
        mock_initialize_app.assert_not_called()

    @patch('Mapapi.firebase_app.firebase_admin.get_app', side_effect=ValueError)
    @patch('Mapapi.firebase_app.firebase_admin.initialize_app')
    @override_settings(FCM_CREDENTIALS_PATH=None,
                        FCM_CREDENTIALS_JSON_BASE64=FAKE_KEY_JSON_B64, FCM_CREDENTIALS_JSON=None)
    @patch('Mapapi.firebase_app.credentials.Certificate')
    def test_initializes_once_when_configured(self, mock_certificate, mock_initialize_app, mock_get_app):
        mock_certificate.return_value = MagicMock()
        init_firebase()
        mock_initialize_app.assert_called_once_with(mock_certificate.return_value)

    @patch('Mapapi.firebase_app.firebase_admin.get_app', return_value=MagicMock())
    @patch('Mapapi.firebase_app.firebase_admin.initialize_app')
    def test_skips_when_already_initialized(self, mock_initialize_app, mock_get_app):
        init_firebase()
        mock_initialize_app.assert_not_called()

    @patch('Mapapi.firebase_app.firebase_admin.get_app', side_effect=ValueError)
    @patch('Mapapi.firebase_app.firebase_admin.initialize_app')
    @override_settings(FCM_CREDENTIALS_PATH=None,
                        FCM_CREDENTIALS_JSON_BASE64='not-valid-base64-json!!', FCM_CREDENTIALS_JSON=None)
    def test_invalid_credentials_do_not_crash(self, mock_initialize_app, mock_get_app):
        init_firebase()
        mock_initialize_app.assert_not_called()
