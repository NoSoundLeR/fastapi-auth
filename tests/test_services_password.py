from unittest import mock

import pytest
from fastapi import HTTPException

from fastapi_auth.repositories import UsersRepo
from fastapi_auth.services import PasswordService
from fastapi_auth.utils.strings import create_random_string, hash_string

from .utils import (
    MockAuthBackend,
    MockCacheBackend,
    MockDatabaseBackend,
    MockEmailClient,
    User,
    mock_verify_password,
    private_key,
    public_key,
)

admin = User(1, "admin", True)
user = User(2, "user", False)
social_user = User(5, "socialuser", False)
non_existing = User(999, "nonexisting", False)

RECAPTCHA_SECRET = "RECAPTCHA_SECRET"

auth_backend = MockAuthBackend("RS256", private_key, public_key)

# PasswordService.setup(
#     UsersRepo(MockDatabaseBackend("test"), MockCacheBackend()),
#     auth_backend,
#     False,
#     "RU",
#     "http://127.0.0.1",
#     "127.0.0.1",
#     RECAPTCHA_SECRET,
#     None,
#     None,
#     None,
#     None,
# )


@pytest.fixture(autouse=True)
def password_service_setup():
    PasswordService.setup(
        UsersRepo(MockDatabaseBackend("test"), MockCacheBackend(), []),
        auth_backend,
        False,
        "RU",
        "http://127.0.0.1",
        "127.0.0.1",
        RECAPTCHA_SECRET,
        None,
        None,
        None,
        None,
        None,
    )


CAPTCHA = "CAPTCHA"


@pytest.mark.asyncio
@mock.patch("fastapi_auth.services.password.EmailClient", MockEmailClient)
async def test_forgot_password():
    service = PasswordService()
    # TODO: exceptions

    await service.forgot_password({"email": "admin@gmail.com"}, "127.0.0.1")


@pytest.mark.asyncio
async def test_password_status():
    service = PasswordService(user)
    # TODO: exceptions
    # TODO: social
    res = await service.password_status()
    assert isinstance(res, dict)
    assert res.get("status") == "change"


@pytest.mark.asyncio
async def test_password_set():
    service = PasswordService(social_user)
    await service.password_set(
        {
            "password1": "12345678",
            "password2": "12345678",
        }
    )

    service = PasswordService(user)
    with pytest.raises(HTTPException) as e:
        await service.password_set(
            {
                "password1": "12345678",
                "password2": "12345678",
            }
        )
    assert e.type is HTTPException
    assert e.value.args[0] == 400


@pytest.mark.asyncio
async def test_password_reset():
    token = create_random_string()
    token_hash = hash_string(token)
    service = PasswordService()
    await service._repo.set_password_reset_token(1, token_hash)

    await service.password_reset(
        {
            "password1": "87654321",
            "password2": "87654321",
        },
        token,
    )

    item = await service._repo.get(1)
    assert item.get("password") != "12345678"


@pytest.mark.asyncio
@mock.patch("fastapi_auth.services.password.verify_password", mock_verify_password)
async def test_password_change():
    service = PasswordService(user)
    item = await service._repo.get(user.id)
    with pytest.raises(HTTPException) as e:
        await service.password_change(
            {
                "old_password": "WRONGPASSWORD",
                "password1": "87654321",
                "password2": "87654321",
            }
        )

    assert e.type is HTTPException
    assert e.value.args[0] == 400

    await service.password_change(
        {
            "old_password": "12345678",
            "password1": "87654321",
            "password2": "87654321",
        }
    )
    item = await service._repo.get(user.id)
    assert item.get("password") != "12345678"
