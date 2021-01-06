from typing import Dict

from fastapi import APIRouter, Depends, Request, Response
from fastapi.exceptions import HTTPException

from fastapi_auth.core.user import User, get_authenticated_user
from fastapi_auth.services import AuthService

"""
POST /register
POST /login
POST /logout
POST /token
POST /token/refresh
GET /confirm
POST /confirm
POST /confirm/{token}
"""


def get_router(
    debug: bool,
    access_expiration: int,
    refresh_expiration: int,
) -> APIRouter:
    def set_access_token_in_response(response, token: str) -> None:
        response.set_cookie(
            key="access_c",
            value=token,
            secure=not debug,
            httponly=True,
            max_age=access_expiration,
        )

    def set_refresh_token_in_response(response, token: str) -> None:
        response.set_cookie(
            key="refresh_c",
            value=token,
            secure=not debug,
            httponly=True,
            max_age=refresh_expiration,
        )

    def set_tokens_in_response(response, tokens: Dict[str, str]) -> None:
        access_token = tokens.get("access")
        refresh_token = tokens.get("refresh")
        set_access_token_in_response(response, access_token)
        set_refresh_token_in_response(response, refresh_token)

    router = APIRouter()

    @router.post("/register", name="auth:register")
    async def register(*, request: Request, response: Response):
        data = await request.json()
        service = AuthService()

        tokens = await service.register(data)
        set_tokens_in_response(response, tokens)
        return None

    @router.post("/login", name="auth:login")
    async def login(*, request: Request, response: Response):
        data = await request.json()
        service = AuthService()

        ip = request.client.host

        tokens = await service.login(data, ip)
        set_tokens_in_response(response, tokens)
        return None

    @router.post("/logout", name="auth:logout")
    async def logout(*, response: Response):
        response.delete_cookie("access_c")
        response.delete_cookie("refresh_c")
        return None

    @router.post("/token", name="auth:token")
    async def token(*, user: User = Depends(get_authenticated_user)):
        return user.data

    @router.post("/token/refresh", name="auth:refresh_access_token")
    async def refresh_access_token(
        *,
        request: Request,
        response: Response,
    ):
        service = AuthService()
        refresh_token = request.cookies.get("refresh_c")
        if refresh_token is None:
            raise HTTPException(401)

        access_token = await service.refresh_access_token(refresh_token)
        set_access_token_in_response(response, access_token)
        return {"access": access_token}

    @router.get("/confirm", name="auth:get_confirmation_status")
    async def get_email_confirmation_status(
        *, user: User = Depends(get_authenticated_user)
    ):
        service = AuthService(user)
        return await service.get_email_confirmation_status()

    @router.post("/confirm", name="auth:request_confirmation")
    async def request_email_confirmation(
        *, user: User = Depends(get_authenticated_user)
    ):
        service = AuthService(user)
        return await service.request_email_confirmation()

    @router.post("/confirm/{token}", name="auth:confirm")
    async def confirm_email(*, token: str):
        service = AuthService()
        return await service.confirm_email(token)

    return router