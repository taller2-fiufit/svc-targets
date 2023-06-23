from http import HTTPStatus
from typing import List, Annotated
from fastapi import APIRouter, Depends

from src.api.model.target import (
    CreateTarget,
    FilterParams,
    PatchTarget,
    Target,
)
from src.api.aliases import SessionDep, UserDep
from src.auth import get_user
from src.db.utils import get_session
from src.logging import info
import src.db.targets as targets_db


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
    # List of dependencies that get run ALWAYS for router and subrouters.
    # For a single-route dependency use the route decorator's parameter "dependencies"
    dependencies=[Depends(get_session), Depends(get_user)],
)

Filters = Annotated[FilterParams, Depends()]


@router.post("")
async def post_report(
    session: SessionDep,
    user: UserDep,
    f: Filters,
) -> List[Target]:
    """Get all the user's targets"""
    return await targets_db.get_all_targets(
        session,
        user.sub,
        f.offset,
        f.limit,
    )


@router.get("/{id}")
async def get_target(session: SessionDep, id: int) -> Target:
    """Get the target with the specified id"""
    return await targets_db.get_target_by_id(session, id)


@router.post("", status_code=HTTPStatus.CREATED)
async def post_target(
    session: SessionDep,
    user: UserDep,
    training: CreateTarget,
) -> Target:
    """Create a new target"""
    new_target = await targets_db.create_target(session, user.sub, training)
    info(f"New target created: {new_target}")
    return new_target


@router.patch("/{id}")
async def patch_target(
    session: SessionDep,
    user: UserDep,
    id: int,
    target_patch: PatchTarget,
) -> Target:
    """Edit target's attributes"""
    edited_target = await targets_db.patch_target(
        session, user.sub, id, target_patch
    )
    info(f"Target edited: {edited_target}")
    return edited_target


@router.delete("/{id}")
async def delete_target(
    session: SessionDep,
    user: UserDep,
    id: int,
) -> Target:
    """Edit target's attributes"""
    deleted_target = await targets_db.delete_target(session, user.sub, id)
    info(f"Target deleted: {deleted_target}")
    return deleted_target
