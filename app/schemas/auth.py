from pydantic import BaseModel


class Token(BaseModel):
    # What the login endpoint returns. "bearer" tells the client to send
    # it back later as: Authorization: Bearer <access_token>
    access_token: str
    token_type: str = "bearer"