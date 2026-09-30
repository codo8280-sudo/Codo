from __future__ import annotations

import json
from typing import Any

from ..policy import normalize_question
from ..providers.llm import LlmProvider
from ..repositories.legal import LegalRepository
from ..schemas import AnswerRequest, CodoAnswerOut
from .citation_verifier import CitationVerifier
from .search import SearchService

INSUFFICIENT = "CODO ne dispose pas actuellement d’une source vérifiée suffisante pour confirmer ce point."

SYSTEM_PROMPT = """Tu es le moteur de rédaction CODO. Tu n'utilises QUE les preuves fournies.
N'invente aucun article, numéro de loi, jurisprudence, juridiction, délai, document ou procédure.
Distingue le texte officiel de l'explication CODO. N'affirme pas qu'un projet est du droit en vigueur.
Si les preuves ne suffisent pas, mets sufficient=false.
Réponds uniquement en JSON avec les clés: sufficient, situation, law_summary, next_steps,
documents_needed, where_to_act, deadlines, attention_points, used_evidence_ids.
used_evidence_ids doit contenir uniquement les identifiants evidence_id fournis.
"""


class AnswerService:
    def __init__(
        self,
        search: SearchService,
        repository: LegalRepository,
        llm: LlmProvider,
        verifier: CitationVerifier,
    ):
        self.search_service = search
        self.repository = repository
        self.llm = llm
        self.verifier = verifier

    async def answer(self, request: AnswerRequest) -> CodoAnswerOut:
        question = normalize_question(request.question)
        search_response = await self.search_service.search(question, limit=8)
        article_results = [item for item in search_response.results if item.article is not None]
        if not article_results:
            return self._insufficient(question, request.mode)

        evidence: list[dict[str, Any]] = []
        for item in article_results:
            article = item.article
            assert article is not None
            # The internal evidence identifier is the article version primary key.
            # Retrieve it from the same verified public row to prevent model-created citations.
            rows = await self.repository.article_by_codo_id(article.codo_id)
            if not rows:
                continue
            evidence.append(
                {
                    "evidence_id": rows["article_version_pk"],
                    "document": item.document.codo_id,
                    "article": article.codo_id,
                    "label": article.label,
                    "version": article.version,
                    "status": article.status,
                    "source": article.source.name,
                    "trust_level": article.source.trust_level,
                    "source_url": str(article.source.url),
                    "official_text": article.official_text,
                    "snippet": item.snippet,
                }
            )

        if not evidence:
            return self._insufficient(question, request.mode)

        prompt = json.dumps(
            {"question": question, "mode": request.mode, "evidence": evidence},
            ensure_ascii=False,
        )
        try:
            draft = await self.llm.answer_json(SYSTEM_PROMPT, prompt)
        except Exception:
            draft = None
        if not draft or not bool(draft.get("sufficient")):
            return self._insufficient(question, request.mode)

        allowed = {int(item["evidence_id"]) for item in evidence}
        used_raw = draft.get("used_evidence_ids")
        if not isinstance(used_raw, list):
            return self._insufficient(question, request.mode)
        used_ids: list[int] = []
        for value in used_raw:
            try:
                evidence_id = int(value)
            except (TypeError, ValueError):
                return self._insufficient(question, request.mode)
            if evidence_id not in allowed:
                return self._insufficient(question, request.mode)
            used_ids.append(evidence_id)

        verification = await self.verifier.verify(used_ids)
        if not verification.sufficient:
            return self._insufficient(question, request.mode)

        answer = CodoAnswerOut(
            situation=str(draft.get("situation") or question),
            law_summary=str(draft.get("law_summary") or ""),
            next_steps=self._strings(draft.get("next_steps")),
            documents_needed=self._strings(draft.get("documents_needed")),
            where_to_act=self._strings(draft.get("where_to_act")),
            deadlines=self._strings(draft.get("deadlines")),
            attention_points=self._strings(draft.get("attention_points")),
            citations=verification.citations,
            has_sufficient_verified_sources=True,
            answer_mode=request.mode,
        )
        try:
            await self.repository.save_answer(
                question,
                answer.model_dump_json(),
                True,
                verification.verified_rows,
            )
        except Exception:
            # Persistence failure must not alter a response already verified against
            # published evidence. Operational telemetry should handle the failure.
            pass
        return answer

    @staticmethod
    def _strings(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [str(item).strip() for item in value if str(item).strip()]

    @staticmethod
    def _insufficient(question: str, mode: str) -> CodoAnswerOut:
        return CodoAnswerOut(
            situation=question,
            law_summary=INSUFFICIENT,
            next_steps=[],
            citations=[],
            has_sufficient_verified_sources=False,
            attention_points=[INSUFFICIENT],
            answer_mode=mode,
        )
