from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..dependencies import (
    admin_identity_service,
    current_admin_principal,
    require_admin_roles,
    require_database,
)
from ..rbac import AdminPrincipal, MEMBERSHIP_ADMIN_ROLES
from ..schemas import AdminMembershipGrantIn, AdminMembershipOut, AdminPrincipalOut
from ..services.admin_identity import AdminIdentityService

router = APIRouter(prefix="/v1/admin", tags=["admin-auth"])


@router.get("/me", response_model=AdminPrincipalOut)
async def me(
    _: None = Depends(require_database),
    principal: AdminPrincipal = Depends(current_admin_principal),
) -> AdminPrincipalOut:
    return AdminPrincipalOut(
        subject=principal.subject,
        roles=sorted(principal.roles),
        authentication_method=principal.authentication_method,
    )


@router.get("/memberships", response_model=list[AdminMembershipOut])
async def memberships(
    auth_subject: str | None = Query(default=None, max_length=512),
    _: None = Depends(require_database),
    actor: str = Depends(require_admin_roles(*MEMBERSHIP_ADMIN_ROLES)),
    service: AdminIdentityService = Depends(admin_identity_service),
) -> list[AdminMembershipOut]:
    del actor
    return [AdminMembershipOut(**row) for row in await service.list_memberships(auth_subject)]


@router.post("/memberships", response_model=AdminMembershipOut)
async def grant_membership(
    request: AdminMembershipGrantIn,
    _: None = Depends(require_database),
    actor: str = Depends(require_admin_roles(*MEMBERSHIP_ADMIN_ROLES)),
    service: AdminIdentityService = Depends(admin_identity_service),
) -> AdminMembershipOut:
    try:
        row = await service.grant(request.auth_subject, request.role_key, actor)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AdminMembershipOut(**row)


@router.delete("/memberships/{auth_subject}/{role_key}", response_model=AdminMembershipOut)
async def revoke_membership(
    auth_subject: str,
    role_key: str,
    _: None = Depends(require_database),
    actor: str = Depends(require_admin_roles(*MEMBERSHIP_ADMIN_ROLES)),
    service: AdminIdentityService = Depends(admin_identity_service),
) -> AdminMembershipOut:
    try:
        row = await service.revoke(auth_subject, role_key, actor)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return AdminMembershipOut(**row)
