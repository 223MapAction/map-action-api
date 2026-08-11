"""Firebase Admin SDK initialization for push notifications (FCM).

Call :func:`init_firebase` once at app startup (see ``Mapapi.apps.MapapiConfig.ready``).
Safe to call more than once (e.g. autoreload) — reuses the existing app instead
of re-initializing.
"""
import logging

import firebase_admin
from firebase_admin import credentials
from django.conf import settings

logger = logging.getLogger(__name__)


def init_firebase():
    try:
        firebase_admin.get_app()
        return
    except ValueError:
        pass

    credentials_path = getattr(settings, 'FCM_CREDENTIALS_PATH', None)
    if not credentials_path:
        logger.warning(
            "FCM_CREDENTIALS_PATH non configuré : les notifications push FCM sont désactivées."
        )
        return

    cred = credentials.Certificate(credentials_path)
    firebase_admin.initialize_app(cred)
