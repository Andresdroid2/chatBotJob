from datetime import UTC, datetime
from sqlalchemy import BigInteger, DateTime, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Filter(Base):
    """Es una función que te permite buscar con el bot de telegram ofertas que te interesen. """

    __tablename__="filters"
    __table_args__=(UniqueConstraint("chat_id","keyword"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger,index=True)
    keyword: Mapped[str] = mapped_column(String(50))

class SentAlert(Base):
    """ Verifica que trabajo se ha enviado y a que chat, para evitar recibir duplicados """

    __tablename__="sent_alerts"
    __table_args__=(UniqueConstraint("chat_id","job_url"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger,index=True)
    job_url: Mapped[str] = mapped_column(String(500))
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda:datetime.now(UTC))