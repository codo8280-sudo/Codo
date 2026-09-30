import unittest

from app.policy import host_is_allowed, ingestion_transition_allowed, normalize_question, source_set_is_sufficient


class SourcePolicyTests(unittest.TestCase):
    def test_primary_source_is_sufficient(self):
        self.assertTrue(source_set_is_sufficient(["A"]))

    def test_institutional_copy_is_sufficient(self):
        self.assertTrue(source_set_is_sufficient(["B", "C"]))

    def test_secondary_only_is_not_enough_for_legal_conclusion(self):
        self.assertFalse(source_set_is_sufficient(["C"]))

    def test_unverified_source_invalidates_set(self):
        self.assertFalse(source_set_is_sufficient(["A", "D"]))

    def test_empty_is_not_sufficient(self):
        self.assertFalse(source_set_is_sufficient([]))

    def test_normalize_question(self):
        self.assertEqual(normalize_question("  Bonjour   CODO  "), "Bonjour CODO")

    def test_workflow_does_not_skip_legal_review(self):
        self.assertFalse(ingestion_transition_allowed("sources_verified", "validated"))
        self.assertTrue(ingestion_transition_allowed("sources_verified", "legal_review"))


class AcquisitionHostTests(unittest.TestCase):
    def test_registered_host_allowed(self):
        self.assertTrue(host_is_allowed("https://www.ohada.org/actes-uniformes/", "https://www.ohada.org/"))

    def test_subdomain_allowed(self):
        self.assertTrue(host_is_allowed("https://docs.example.org/a", "https://example.org/"))

    def test_lookalike_host_rejected(self):
        self.assertFalse(host_is_allowed("https://ohada.org.evil.test/a", "https://ohada.org/"))

    def test_parent_domain_is_not_implicitly_allowed(self):
        self.assertFalse(host_is_allowed("https://gouv.ci/a", "https://web.sgg.gouv.ci/"))

    def test_www_normalization(self):
        self.assertTrue(host_is_allowed("https://ohada.org/a", "https://www.ohada.org/"))


if __name__ == "__main__":
    unittest.main()
