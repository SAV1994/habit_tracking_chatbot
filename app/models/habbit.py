from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Habit(Base):
    __tablename__ = 'habit'

    id: Mapped[int] = mapped_column('id', type_=Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    title: Mapped[str] = mapped_column('title', type_=String)
    description: Mapped[str] = mapped_column('description', type_=String)
    target: Mapped[int] = mapped_column('target', type_=Integer)
    process: Mapped[int] = mapped_column('process', type_=Integer, default=0)
    is_active: Mapped[bool] = mapped_column('is_active', type_=Boolean, default=False)
    is_completed: Mapped[bool] = mapped_column('is_completed', type_=Boolean, default=False)
    completed_date: Mapped[str] = mapped_column('completed_date', type_=DateTime, nullable=True)

    __table_args__ = (CheckConstraint(target > 0, name='check_target_positive'),)
