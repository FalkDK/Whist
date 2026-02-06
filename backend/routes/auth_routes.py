"""Authentication REST endpoints."""

from fastapi import APIRouter

from ..auth import login
from ..models import LoginRequest, LoginResponse

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def post_login(body: LoginRequest) -> LoginResponse:
    token, display_name = login(body.username, body.password)
    return LoginResponse(token=token, display_name=display_name)
