from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

ALL_ADMIN_ROLES = {
    "SUPER_ADMIN",
    "RESPONSABLE_JURIDIQUE",
    "VALIDATEUR_JURIDIQUE",
    "DOCUMENTALISTE",
    "REDACTEUR",
    "DATA_MANAGER",
    "MODERATEUR",
    "AUDITEUR",
}

INGESTION_ROLES = {
    "SUPER_ADMIN",
    "RESPONSABLE_JURIDIQUE",
    "DOCUMENTALISTE",
    "DATA_MANAGER",
}

LEGAL_REVIEW_ROLES = {
    "SUPER_ADMIN",
    "RESPONSABLE_JURIDIQUE",
    "VALIDATEUR_JURIDIQUE",
}

AUDIT_ROLES = {
    "SUPER_ADMIN",
    "RESPONSABLE_JURIDIQUE",
    "AUDITEUR",
}

RELATIONSHIP_EDITOR_ROLES = {
    "SUPER_ADMIN",
    "RESPONSABLE_JURIDIQUE",
    "VALIDATEUR_JURIDIQUE",
    "DATA_MANAGER",
}

MEMBERSHIP_ADMIN_ROLES = {"SUPER_ADMIN"}


@dataclass(frozen=True)
class UserPrincipal:
    subject: str
    issuer: str
    claims: dict


@dataclass(frozen=True)
class AdminPrincipal:
    subject: str
    roles: frozenset[str]
    claims: dict
    authentication_method: str

    def has_any_role(self, roles: Iterable[str]) -> bool:
        required = set(roles)
        return bool(self.roles.intersection(required))

    @property
    def is_super_admin(self) -> bool:
        return "SUPER_ADMIN" in self.roles


def is_authorized(principal: AdminPrincipal, roles: Iterable[str]) -> bool:
    return principal.has_any_role(roles)
