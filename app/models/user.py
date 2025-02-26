from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column('id', type_=Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column('username', type_=String)
    password: Mapped[str] = mapped_column('password', type_=String)
    first_name: Mapped[str] = mapped_column('first_name', type_=String)
    last_name: Mapped[str] = mapped_column('last_name', type_=String)
    access_token: Mapped[str] = mapped_column('access_token', type_=String)
    refresh_token: Mapped[str] = mapped_column('refresh_token', type_=String)

    @property
    def name(self):
        if self.first_name:
            name = self.first_name
            if self.last_name:
                name += f' {self.last_name}'
        else:
            name = self.username
        return name
