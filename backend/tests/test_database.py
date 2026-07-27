from app.database import Base, engine, SessionLocal
from app.models import Frase


def test_frase_table_created_and_insertable(tmp_path, monkeypatch):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    frase = Frase(texto="ola mundo")
    db.add(frase)
    db.commit()
    db.refresh(frase)
    assert frase.id is not None
    assert frase.texto == "ola mundo"
    assert frase.criado_em is not None
    db.close()
