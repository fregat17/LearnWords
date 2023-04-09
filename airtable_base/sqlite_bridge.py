from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Words(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(primary_key=True)
    hieroglyph: Mapped[str] = mapped_column()
    pinyin: Mapped[str] = mapped_column()
    meaning: Mapped[str] = mapped_column()
    haohan: Mapped[Optional[str]] = mapped_column()
    trainch: Mapped[Optional[str]] = mapped_column()


class Probabilities(Base):
    __tablename__ = "probs"

    id: Mapped[int] = mapped_column(primary_key=True)
    hieroglyph: Mapped[float] = mapped_column()


def test():
    engine = create_engine("sqlite+pysqlite:///testbase.db", echo=True)


if __name__ == "__main__":
    test()