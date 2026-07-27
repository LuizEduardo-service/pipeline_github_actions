from sqlalchemy.orm import Session

from app.models import Frase
from app.schemas import FraseCreate, FraseUpdate


def criar_frase(db: Session, frase: FraseCreate) -> Frase:
    db_frase = Frase(texto=frase.texto.strip())
    db.add(db_frase)
    db.commit()
    db.refresh(db_frase)
    return db_frase


def listar_frases(db: Session) -> list[Frase]:
    return db.query(Frase).order_by(Frase.id).all()


def atualizar_frase(db: Session, frase_id: int, frase: FraseUpdate) -> Frase | None:
    db_frase = db.query(Frase).filter(Frase.id == frase_id).first()
    if db_frase is None:
        return None
    db_frase.texto = frase.texto.strip()
    db.commit()
    db.refresh(db_frase)
    return db_frase


def deletar_frase(db: Session, frase_id: int) -> bool:
    db_frase = db.query(Frase).filter(Frase.id == frase_id).first()
    if db_frase is None:
        return False
    db.delete(db_frase)
    db.commit()
    return True
