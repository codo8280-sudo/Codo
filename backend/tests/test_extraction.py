import hashlib
import unittest

from app.schemas import DraftMetadataIn, LegalDecisionRequest
from app.services.extraction import LegalTextParser


class LegalTextParserTests(unittest.TestCase):
    def test_page_markers_never_enter_official_text(self):
        source = """
[CODO_PAGE 1]
Article premier.
Le premier texte.
[CODO_PAGE 2]
Article 2
Le deuxième texte.
"""
        articles, diagnostics = LegalTextParser.parse_articles(source)
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0].label, "Article 1")
        self.assertEqual(articles[1].label, "Article 2")
        self.assertNotIn("CODO_PAGE", articles[0].official_text)
        self.assertNotIn("CODO_PAGE", articles[1].official_text)
        self.assertEqual(diagnostics.numeric_gaps, [])

    def test_gaps_and_suffixes_are_reported_conservatively(self):
        source = """
Article 1
Texte A.
Article 3 bis
Texte B.
"""
        articles, diagnostics = LegalTextParser.parse_articles(source)
        self.assertEqual([a.label for a in articles], ["Article 1", "Article 3 bis"])
        self.assertEqual(diagnostics.numeric_gaps, [2])
        self.assertTrue(diagnostics.warnings)

    def test_draft_package_is_never_marked_applicable_automatically(self):
        source = "Article 1\nDisposition test.\nArticle 2\nAutre disposition."
        metadata = DraftMetadataIn(
            codo_id="CODO-CI-TEST-1",
            domain_slug="droit-constitutionnel",
            nature="constitution",
            title="Texte de test",
            document_number="TEST-1",
            version_key="v1",
        )
        package, diagnostics = LegalTextParser.build_package(
            source_snapshot_hash=hashlib.sha256(b"official").hexdigest(),
            metadata=metadata,
            extracted_text=source,
        )
        self.assertEqual(package.status, "verification_pending")
        self.assertEqual(diagnostics.article_count, 2)
        self.assertTrue(all(a.status == "verification_pending" for a in package.articles))

    def test_legal_decision_cannot_use_verification_pending(self):
        with self.assertRaises(Exception):
            LegalDecisionRequest(document_status="verification_pending")


if __name__ == "__main__":
    unittest.main()
