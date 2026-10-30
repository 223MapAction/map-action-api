"""A re-run must replace the fallback text left by a failed analysis."""
from types import SimpleNamespace
from unittest.mock import MagicMock

from django.test import SimpleTestCase

from Mapapi.models import PredictionStatus
from Mapapi.services.prediction_mapper import fill_prediction_from_model_response

FALLBACK = "L'analyse visuelle a échoué. Détails: service indisponible."


def model_response(macro, sub, description, recommendation):
    return {
        "ai_analysis": {"macro_category": macro, "sub_category": sub, "description": description},
        "recommendation": recommendation,
    }


def blank_prediction(**fields):
    prediction = SimpleNamespace(
        incident_type="", piste_solution="", analysis="", status="", error_message="", save=MagicMock()
    )
    prediction.__dict__.update(fields)
    return prediction


class LegacyMirrorFieldsTests(SimpleTestCase):
    def test_rerun_replaces_the_fallback_values(self):
        prediction = blank_prediction(
            incident_type="Autre", piste_solution="Rayon par défaut", analysis=FALLBACK,
        )

        fill_prediction_from_model_response(
            prediction, model_response("Eau & Assainissement", "Eaux usées", "Eaux stagnantes.", "Curer."),
        )

        self.assertEqual(prediction.status, PredictionStatus.COMPLETED)
        self.assertEqual(prediction.incident_type, "Eau & Assainissement")
        self.assertEqual(prediction.analysis, "Eaux stagnantes.")
        self.assertEqual(prediction.piste_solution, "Curer.")

    def test_first_run_fills_the_fields(self):
        prediction = blank_prediction()

        fill_prediction_from_model_response(
            prediction, model_response("Déchets", "Dépôt sauvage", "Tas d'ordures.", "Enlever."),
        )

        self.assertEqual(prediction.incident_type, "Déchets")
        self.assertEqual(prediction.analysis, "Tas d'ordures.")
        self.assertEqual(prediction.piste_solution, "Enlever.")

    def test_fallback_response_stays_flagged_as_warning(self):
        prediction = blank_prediction()

        fill_prediction_from_model_response(
            prediction, model_response("Autre", "Incident non répertorié", FALLBACK, "Rayon par défaut"),
        )

        self.assertEqual(prediction.status, PredictionStatus.COMPLETED_WITH_WARNING)
        self.assertEqual(prediction.analysis, FALLBACK)
