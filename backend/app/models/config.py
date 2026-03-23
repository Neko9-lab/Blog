from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.models.base import Base


class SiteConfig(Base):
    __tablename__ = "site_config"

    id = Column(Integer, primary_key=True, index=True)
    site_name = Column(String(128), default="BlogForum")
    announcement = Column(String(512), default="")
    comment_enabled = Column(Boolean, default=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
