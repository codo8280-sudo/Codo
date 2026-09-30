import unittest

from app.schemas import (
    AnswerRequest,
    CitationOut,
    LegalArticleOut,
    LegalDocumentOut,
    LegalSourceOut,
    SearchResponse,
    SearchResultOut,
)
from app.services.answers import AnswerService
from app.services.citation_verifier import CitationVerification


class FakeSearch:
    async def search(self, query, limit=None):
        source = LegalSourceOut(
            id="1",
            name="Source officielle",
            institution_name="Institution",
            trust_level="A",
            url="https://example.org/source",
            is_official=True,
        )
        document = LegalDocumentOut(
            codo_id="CODO-CI-TEST-1",
            title="Texte test",
            nature="loi",
            status="in_force",
            source=source,
            current_version="v1",
        )
        article = LegalArticleOut(
            codo_id="CODO-CI-TEST-1-ART-1",
            document_id=document.codo_id,
            label="Article 1",
            official_text="Texte officiel de test.",
            status="in_force",
            version="v1",
            source=source,
        )
        return SearchResponse(
            results=[SearchResultOut(document=document, article=article, snippet=article.official_text)],
            semantic_search_used=False,
        )


class FakeRepo:
    def __init__(self):
        self.saved = False

    async def article_by_codo_id(self, codo_id):
        return {"article_version_pk": 7}

    async def save_answer(self, *args, **kwargs):
        self.saved = True
        return 1


class FakeLlm:
    def __init__(self, evidence_ids):
        self.evidence_ids = evidence_ids

    async def answer_json(self, system_prompt, user_prompt):
        return {
            "sufficient": True,
            "situation": "Situation test",
            "law_summary": "Résumé fondé sur la preuve.",
            "next_steps": [],
            "documents_needed": [],
            "where_to_act": [],
            "deadlines": [],
            "attention_points": [],
            "used_evidence_ids": self.evidence_ids,
        }


class FakeVerifier:
    async def verify(self, evidence_ids):
        if evidence_ids != [7]:
            return CitationVerification(False, [], [])
        citation = CitationOut(
            source_id="1",
            document_id="CODO-CI-TEST-1",
            article_id="CODO-CI-TEST-1-ART-1",
            version="v1",
            source_url="https://example.org/source",
            trust_level="A",
        )
        return CitationVerification(
            True,
            [citation],
            [{
                "source_pk": 1,
                "document_pk": 1,
                "document_version_pk": 1,
                "article_pk": 1,
                "article_version_pk": 7,
            }],
        )


class AnswerEvidenceGuardTests(unittest.IsolatedAsyncioTestCase):
    async def test_model_cannot_inject_unknown_evidence_id(self):
        repo = FakeRepo()
        service = AnswerService(FakeSearch(), repo, FakeLlm([999]), FakeVerifier())
        answer = await service.answer(AnswerRequest(question="Question test"))
        self.assertFalse(answer.has_sufficient_verified_sources)
        self.assertEqual(answer.citations, [])
        self.assertFalse(repo.saved)

    async def test_verified_supplied_evidence_can_pass(self):
        repo = FakeRepo()
        service = AnswerService(FakeSearch(), repo, FakeLlm([7]), FakeVerifier())
        answer = await service.answer(AnswerRequest(question="Question test", mode="legal"))
        self.assertTrue(answer.has_sufficient_verified_sources)
        self.assertEqual(len(answer.citations), 1)
        self.assertEqual(answer.answer_mode, "legal")
        self.assertTrue(repo.saved)


if __name__ == "__main__":
    unittest.main()
