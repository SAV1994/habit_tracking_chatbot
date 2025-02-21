from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    String,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Habit(Base):
    __tablename__ = 'habit'

    id: Mapped[int] = mapped_column('id', type_=Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    title: Mapped[str] = mapped_column('title', type_=String, nullable=False)
    description: Mapped[str] = mapped_column('description', type_=String, nullable=False)
    target: Mapped[int] = mapped_column('target', type_=Integer, default=21)
    process: Mapped[int] = mapped_column('process', type_=Integer, default=0)
    alert_time: Mapped[datetime.time] = mapped_column('alert_time', type_=Time, nullable=False)
    alert_date: Mapped[datetime.date] = mapped_column('alert_date', type_=Date, nullable=True)
    completed_date: Mapped[datetime.date] = mapped_column('completed_date', type_=Date, nullable=True)

    __table_args__ = (CheckConstraint(target > 0, name='check_target_positive'),)

    @property
    def days_left(self) -> int:
        return self.target - self.process
