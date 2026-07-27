from datetime import datetime

from pydantic import BaseModel


class FraseCreate(BaseModel):
    texto: str


class FraseUpdate(BaseModel):
    texto: str


class FraseOut(BaseModel):
    id: int
    texto: str
    criado_em: datetime

    class Config:
        from_attributes = True
