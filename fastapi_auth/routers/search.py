from typing import Callable, Optional

from fastapi import APIRouter, Depends

from fastapi_auth.repositories import UsersRepo
from fastapi_auth.services import SearchService


def get_router(repo: UsersRepo, admin_required: Callable):

    SearchService.setup(repo)

    router = APIRouter()

    @router.get("/{id}", name="auth:get_user", dependencies=[Depends(admin_required)])
    async def get_user(id: int):
        service = SearchService()
        return await service.get_user(id)

    @router.get("", name="auth:search", dependencies=[Depends(admin_required)])
    async def search(
        *, id: Optional[int] = None, username: Optional[str] = None, p: int = 1
    ):
        service = SearchService()
        return await service.search(id, username, p)

    return router
