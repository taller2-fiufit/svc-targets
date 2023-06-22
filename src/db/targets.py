from http import HTTPStatus
from typing import List
from fastapi import HTTPException

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.model.target import (
    CreateTarget,
    PatchTarget,
    Target,
)
from src.db.model.target import DBTarget
from src.common import limit_is_expired


async def get_all_targets(
    session: AsyncSession,
    user: int,
    offset: int,
    limit: int,
) -> List[Target]:
    query = select(DBTarget).filter_by(author=user)

    res = await session.scalars(query.offset(offset).limit(limit))
    targets = res.all()

    return list(map(DBTarget.to_api_model, targets))


async def get_target_by_id(session: AsyncSession, id: int) -> Target:
    target = await session.get(DBTarget, id)

    if target is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Target not found")

    return target.to_api_model()


async def create_target(
    session: AsyncSession, author: int, target: CreateTarget
) -> Target:
    new_target = DBTarget.from_api_model(author, target)

    session.add(new_target)
    await session.commit()

    return new_target.to_api_model()


def modifies_expired(target: DBTarget, patch: PatchTarget) -> bool:
    if patch.limit is not None and patch.limit // 1000 != target.limit:
        return False

    curr_was_modified = patch.current is not None and patch.current != target.current
    targ_was_modified = patch.target is not None and patch.target != target.target
    return limit_is_expired(target.limit) and (curr_was_modified or targ_was_modified)


async def patch_target(
    session: AsyncSession, author: int, id: int, patch: PatchTarget
) -> Target:
    """Updates the target's info"""

    target = await session.get(DBTarget, id)

    if target is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Target not found")

    if target.author != author:
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, "User isn't author of the target"
        )

    if modifies_expired(target, patch):
        raise HTTPException(
            HTTPStatus.CONFLICT, "Cannot modify expired target"
        )

    target.update(**patch.dict())

    session.add(target)
    await session.commit()

    return target.to_api_model()


async def delete_target(session: AsyncSession, author: int, id: int) -> Target:
    """Deletes the target"""

    target = await session.get(DBTarget, id)

    if target is None:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Target not found")

    if target.author != author:
        raise HTTPException(
            HTTPStatus.UNAUTHORIZED, "User isn't author of the target"
        )

    await session.delete(target)

    return target.to_api_model()
