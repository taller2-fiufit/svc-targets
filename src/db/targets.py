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
