from __future__ import annotations

import hmac
from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth import AuthenticationError, oidc_authenticator
from .config import settings
from .db import connection
from .providers.embeddings import build_embedding_provider
from .providers.llm import build_llm_provider
from .rbac import ALL_ADMIN_ROLES, AdminPrincipal, UserPrincipal
from .repositories.legal import LegalRepository
from .services.answers import AnswerService
from .services.citation_verifier import CitationVerifier
from .services.ingestion import IngestionService
from .services.extraction import ExtractionService
from .services.search import SearchService
from .services.workflow import IngestionWorkflowService
from .services.relationships import LegalRelationshipService
from .services.admin_identity import AdminIdentityService
from .services.user_identity import UserIdentityService

_repository = LegalRepository()
_embeddings = build_embedding_provider()
_llm = build_llm_provider()
_search = SearchService(_repository, _embeddings)
_verifier = CitationVerifier(_repository)
_answers = AnswerService(_search, _repository, _llm, _verifier)
_ingestion = IngestionService()
_extraction = ExtractionService()
_workflow = IngestionWorkflowService()
_relationships = LegalRelationshipService()
_admin_identity = AdminIdentityService()
_user_identity = UserIdentityService()
_bearer_scheme = HTTPBearer(auto_error=False)


def legal_repository() -> LegalRepository:
    return _repository


def search_service() -> SearchService:
    return _search


def answer_service() -> AnswerService:
    return _answers


def ingestion_service() -> IngestionService:
    return _ingestion


def extraction_service() -> ExtractionService:
    return _extraction


def ingestion_workflow_service() -> IngestionWorkflowService:
    return _workflow


def legal_relationship_service() -> LegalRelationshipService:
    return _relationships


def admin_identity_service() -> AdminIdentityService:
    return _admin_identity


def user_identity_service() -> UserIdentityService:
    return _user_identity


def _bearer_token(credentials: HTTPAuthorizationCredentials | None) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer" or not credentials.credentials.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials.strip()


async def current_user_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> UserPrincipal:
    token = _bearer_token(credentials)
    if not settings.oidc_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="User authentication is disabled until OIDC is configured.",
        )
    try:
        claims = await oidc_authenticator.verify(token)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    subject = str(claims["sub"])
    issuer = str(claims["iss"])
    return UserPrincipal(subject=subject, issuer=issuer, claims=claims)


async def current_admin_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> AdminPrincipal:
    token = _bearer_token(credentials)

    if settings.admin_bootstrap_token and hmac.compare_digest(token, settings.admin_bootstrap_token):
        return AdminPrincipal(
            subject="bootstrap-admin",
            roles=frozenset({"SUPER_ADMIN"}),
            claims={"sub": "bootstrap-admin"},
            authentication_method="bootstrap",
        )

    if not settings.oidc_configured:
        if settings.admin_bootstrap_token:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid administrative bearer token")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Administrative authentication is disabled until OIDC or bootstrap authentication is configured.",
        )
    if not settings.database_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OIDC administrative authorization requires the CODO corpus database.",
        )

    try:
        claims = await oidc_authenticator.verify(token)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    subject = str(claims["sub"])
    async with connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                select role_key from admin_memberships
                where auth_subject=%s and active=true
                order by role_key
                """,
                (subject,),
            )
            roles = frozenset(row["role_key"] for row in await cur.fetchall())

    roles = frozenset(role for role in roles if role in ALL_ADMIN_ROLES)
    if not roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authenticated identity has no active CODO administrative role",
        )
    return AdminPrincipal(
        subject=subject,
        roles=roles,
        claims=claims,
        authentication_method="oidc",
    )


async def require_admin(
    principal: AdminPrincipal = Depends(current_admin_principal),
) -> str:
    return principal.subject


def require_admin_roles(*roles: str) -> Callable:
    required = frozenset(roles)
    unknown = required.difference(ALL_ADMIN_ROLES)
    if unknown:
        raise ValueError("Unknown CODO admin roles: " + ", ".join(sorted(unknown)))

    async def dependency(
        principal: AdminPrincipal = Depends(current_admin_principal),
    ) -> str:
        if not principal.has_any_role(required):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrative role is not authorized for this operation",
            )
        return principal.subject

    return dependency


def require_database() -> None:
    if not settings.database_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="CODO corpus database is not configured.",
        )
