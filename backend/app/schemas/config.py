from pydantic import BaseModel


class SiteConfigOut(BaseModel):
    site_name: str
    announcement: str
    comment_enabled: bool


class SiteConfigUpdate(BaseModel):
    site_name: str | None = None
    announcement: str | None = None
    comment_enabled: bool | None = None
