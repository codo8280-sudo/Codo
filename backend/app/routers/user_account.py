from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from ..dependencies import current_user_principal, require_database, user_identity_service
from ..rbac import UserPrincipal
from ..schemas import (
    AccessibilitySettingsIn,
    AccessibilitySettingsOut,
    FavoriteIn,
    FavoriteOut,
    UserProfileOut,
    UserProfileUpdateIn,
    UserFolderCreateIn,
    UserFolderOut,
    UserFolderItemIn,
    UserFolderItemOut,
    UserAlertCreateIn,
    UserAlertUpdateIn,
    UserAlertOut,
)
from ..services.user_identity import UserIdentityService

router = APIRouter(prefix="/v1/me", tags=["user-account"])


@router.get("", response_model=UserProfileOut)
async def profile(
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> UserProfileOut:
    return UserProfileOut(**(await service.sync_profile(principal)))


@router.patch("", response_model=UserProfileOut)
async def update_profile(
    request: UserProfileUpdateIn,
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> UserProfileOut:
    row = await service.update_profile(
        principal,
        display_name=request.display_name,
        locale=request.locale,
    )
    return UserProfileOut(**row)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> Response:
    await service.delete_account(principal)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/accessibility", response_model=AccessibilitySettingsOut)
async def accessibility(
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> AccessibilitySettingsOut:
    return AccessibilitySettingsOut(**(await service.get_accessibility(principal)))


@router.put("/accessibility", response_model=AccessibilitySettingsOut)
async def update_accessibility(
    request: AccessibilitySettingsIn,
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> AccessibilitySettingsOut:
    return AccessibilitySettingsOut(**(await service.update_accessibility(
        principal,
        text_scale=request.text_scale,
        high_contrast=request.high_contrast,
        reduce_motion=request.reduce_motion,
        offline_cache_enabled=request.offline_cache_enabled,
    )))


@router.get("/favorites", response_model=list[FavoriteOut])
async def favorites(
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> list[FavoriteOut]:
    return [FavoriteOut(**row) for row in await service.list_favorites(principal)]


@router.post("/favorites", response_model=FavoriteOut, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    request: FavoriteIn,
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> FavoriteOut:
    return FavoriteOut(**(await service.add_favorite(
        principal,
        entity_type=request.entity_type,
        entity_key=request.entity_key,
    )))


@router.delete("/favorites/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_favorite(
    favorite_id: int,
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> Response:
    deleted = await service.remove_favorite(principal, favorite_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/folders", response_model=list[UserFolderOut])
async def folders(
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> list[UserFolderOut]:
    return [UserFolderOut(**row) for row in await service.list_folders(principal)]


@router.post("/folders", response_model=UserFolderOut, status_code=status.HTTP_201_CREATED)
async def create_folder(
    request: UserFolderCreateIn,
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> UserFolderOut:
    return UserFolderOut(**(await service.create_folder(
        principal, name=request.name, description=request.description
    )))


@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: UUID,
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> Response:
    deleted = await service.delete_folder(principal, str(folder_id))
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/folders/{folder_id}/items", response_model=list[UserFolderItemOut])
async def folder_items(
    folder_id: UUID,
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> list[UserFolderItemOut]:
    rows = await service.list_folder_items(principal, str(folder_id))
    if rows is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
    return [UserFolderItemOut(**row) for row in rows]


@router.post("/folders/{folder_id}/items", response_model=UserFolderItemOut, status_code=status.HTTP_201_CREATED)
async def add_folder_item(
    folder_id: UUID,
    request: UserFolderItemIn,
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> UserFolderItemOut:
    row = await service.add_folder_item(
        principal, str(folder_id), entity_type=request.entity_type, entity_key=request.entity_key
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
    return UserFolderItemOut(**row)


@router.delete("/folders/{folder_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder_item(
    folder_id: UUID,
    item_id: int,
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> Response:
    deleted = await service.remove_folder_item(principal, str(folder_id), item_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder item not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/alerts", response_model=list[UserAlertOut])
async def alerts(
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> list[UserAlertOut]:
    return [UserAlertOut(**row) for row in await service.list_alerts(principal)]


@router.post("/alerts", response_model=UserAlertOut, status_code=status.HTTP_201_CREATED)
async def create_alert(
    request: UserAlertCreateIn,
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> UserAlertOut:
    return UserAlertOut(**(await service.create_alert(
        principal, scope_type=request.scope_type, scope_key=request.scope_key
    )))


@router.patch("/alerts/{alert_id}", response_model=UserAlertOut)
async def update_alert(
    alert_id: UUID,
    request: UserAlertUpdateIn,
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> UserAlertOut:
    row = await service.update_alert(principal, str(alert_id), enabled=request.enabled)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return UserAlertOut(**row)


@router.delete("/alerts/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: UUID,
    _: None = Depends(require_database),
    principal: UserPrincipal = Depends(current_user_principal),
    service: UserIdentityService = Depends(user_identity_service),
) -> Response:
    deleted = await service.delete_alert(principal, str(alert_id))
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
