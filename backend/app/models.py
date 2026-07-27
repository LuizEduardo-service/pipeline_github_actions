from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class Frase(Base):
    __tablename__ = "frases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    texto = Column(String, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
