from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

    token_type: str
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class LogoutResponse(BaseModel):
    message: str