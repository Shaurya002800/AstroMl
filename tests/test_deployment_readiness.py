import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT, "scripts"))

from check_deployment_readiness import build_deployment_readiness


class DeploymentReadinessTests(unittest.TestCase):
    def test_private_pilot_deployment_files_are_ready(self):
        result = build_deployment_readiness()

        self.assertTrue(result["deployable_for_private_pilot"])
        self.assertFalse(result["paid_production_ready"])
        self.assertTrue(result["checks"]["required_files_present"])
        self.assertTrue(
            result["checks"]["env_template_documents_required_secrets"]
        )
        self.assertTrue(
            result["checks"]["docker_excludes_sensitive_runtime_data"]
        )
        self.assertIn(
            "25 independent reference fixtures",
            result["remaining_release_gates"],
        )


if __name__ == "__main__":
    unittest.main()
