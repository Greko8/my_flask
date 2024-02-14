import datetime
import os

from sqlalchemy import DateTime, String, create_engine, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")
POSTGRES_USER = os.getenv("POSTGRES_USER", "app")
POSTGRES_DB = os.getenv("POSTGRES_DB", "app")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "127.0.0.1")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5431")


PG_DSN = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "app_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    password: Mapped[str] = mapped_column(String(100), nullable=False)

    @property
    def dict(self):
        return {
            "id": self.id,
            "name": self.name,
        }

class Ad(Base):
    __tablename__ = "app_ads"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    description: Mapped[str] = mapped_column(String(1500), nullable=False)
    creation_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    owner_id: Mapped[int] = mapped_column(ForeignKey("User.id"), nullable=False)
    owner: Mapped["User"] = relationship(back_populates="ads")

    @property
    def dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "creation_time": self.creation_time.isoformat(),
            "owner_id": self.owner_id
        }

Base.metadata.create_all(bind=engine)
