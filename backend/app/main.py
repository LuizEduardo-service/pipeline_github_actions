from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import Base, engine, get_db

app = FastAPI(title="Cadastro de Frases")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.get("/frases", response_model=list[schemas.FraseOut])
def get_frases(db: Session = Depends(get_db)):
    return crud.listar_frases(db)


@app.post("/frases", response_model=schemas.FraseOut, status_code=201)
def post_frase(frase: schemas.FraseCreate, db: Session = Depends(get_db)):
    if not frase.texto.strip():
        raise HTTPException(status_code=400, detail="texto não pode ser vazio")
    return crud.criar_frase(db, frase)


@app.put("/frases/{frase_id}", response_model=schemas.FraseOut)
def put_frase(frase_id: int, frase: schemas.FraseUpdate, db: Session = Depends(get_db)):
    if not frase.texto.strip():
        raise HTTPException(status_code=400, detail="texto não pode ser vazio")
    atualizada = crud.atualizar_frase(db, frase_id, frase)
    if atualizada is None:
        raise HTTPException(status_code=404, detail="frase não encontrada")
    return atualizada


@app.delete("/frases/{frase_id}", status_code=204)
def delete_frase(frase_id: int, db: Session = Depends(get_db)):
    removida = crud.deletar_frase(db, frase_id)
    if not removida:
        raise HTTPException(status_code=404, detail="frase não encontrada")
