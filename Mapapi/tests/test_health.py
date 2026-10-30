"""/MapApi/health/ must report AI outages that do not raise errors.

Model_deploy answers 200 with default values when Gemini fails, so those
predictions are saved as completed_with_warning, never failed (project suspended
on 2026-10-23: /health stayed "ok" for a week).
"""
from unittest.mock import patch

from django.test import SimpleTestCase

from Mapapi.models import PredictionStatus
from Mapapi.views import health

OK = PredictionStatus.COMPLETED
WARN = PredictionStatus.COMPLETED_WITH_WARNING
FAILED = PredictionStatus.FAILED


def check_predictions(newest_first):
    with patch.object(health, "Prediction") as prediction:
        prediction.objects.order_by.return_value.values_list.return_value = newest_first
        return health._check_predictions()


class PredictionsCheckTests(SimpleTestCase):
    def test_all_good_is_ok(self):
        result = check_predictions([OK] * 20)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["failure_ratio"], 0.0)

    def test_no_predictions_is_ok(self):
        self.assertEqual(check_predictions([])["status"], "ok")

    def test_degraded_results_count_as_failures(self):
        result = check_predictions([WARN] * 20)
        self.assertEqual(result["status"], "warn")
        self.assertEqual(result["degraded"], 20)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(result["failure_ratio"], 1.0)

    def test_failed_results_still_count(self):
        result = check_predictions([FAILED, OK] * 5 + [FAILED] + [OK] * 9)
        self.assertEqual(result["status"], "ok")
        self.assertEqual(check_predictions([FAILED, OK] * 8 + [FAILED] * 4)["status"], "warn")

    def test_five_bad_in_a_row_warns_before_the_ratio_trips(self):
        result = check_predictions([WARN, FAILED, WARN, WARN, WARN] + [OK] * 15)
        self.assertEqual(result["status"], "warn")
        self.assertLessEqual(result["failure_ratio"], health._PREDICTION_FAIL_RATIO)

    def test_four_in_a_row_is_tolerated(self):
        self.assertEqual(check_predictions([WARN] * 4 + [OK] * 16)["status"], "ok")

    def test_old_streak_does_not_warn_once_recovered(self):
        self.assertEqual(check_predictions([OK] + [WARN] * 5 + [OK] * 14)["status"], "ok")

    def test_a_lone_genuine_autre_classification_is_tolerated(self):
        self.assertEqual(check_predictions([WARN] + [OK] * 19)["status"], "ok")


class HealthViewTests(SimpleTestCase):
    def test_degraded_predictions_fail_the_monitor_keyword(self):
        good = {"status": "ok"}
        with patch.object(health, "_check_database", return_value=good), \
                patch.object(health, "_check_redis", return_value=good), \
                patch.object(health, "_check_celery", return_value=good), \
                patch.object(health, "_check_model_deploy", return_value=good), \
                patch.object(health, "Prediction") as prediction:
            prediction.objects.order_by.return_value.values_list.return_value = [WARN] * 20
            response = self.client.get("/MapApi/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "degraded")
        self.assertNotIn('{"status":"ok","checks"', response.content.decode())
