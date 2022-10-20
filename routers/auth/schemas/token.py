from pydantic import BaseModel

class JWTToken(BaseModel):
    token_type: str = 'bearer'
    access_token: str