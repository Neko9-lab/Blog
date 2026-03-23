from sqlalchemy import Column, Date, Integer

from app.models.base import Base


class DailyStats(Base):
    __tablename__ = "daily_stats"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False)
    total_users = Column(Integer, default=0)
    total_posts = Column(Integer, default=0)
    new_users = Column(Integer, default=0)
