from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    file_hash: Mapped[str | None] = mapped_column(
    String(64),
    nullable=True,
    )

    sum_type: Mapped[str | None] = mapped_column(
    String(20),
    nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="uploaded",
    )

    created_at: Mapped[datetime] = mapped_column(
    DateTime,
    nullable=False,
    server_default=func.current_timestamp(),
)

updated_at: Mapped[datetime] = mapped_column(
    DateTime,
    nullable=False,
    server_default=func.current_timestamp(),
    server_onupdate=func.current_timestamp(),
)