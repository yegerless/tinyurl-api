from pydantic import BaseModel, Field

class PostShortenLinkRequestBody(BaseModel):
    source_link: str
    custom_alias: str | None = None
    expires_at: str | None = None



class UpdateShortLinkRequest(BaseModel):
    pass 
