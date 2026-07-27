# Cadastro de Frases Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Monorepo CRUD de frases — backend FastAPI + SQLite, frontend Next.js.

**Architecture:** Backend expõe API REST (`/frases`) sobre SQLite via SQLAlchemy. Frontend Next.js consome a API direto via fetch, sem proxy. Sem auth, sem Docker.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy, SQLite, pytest, httpx (TestClient); Node 18+, Next.js (App Router), TypeScript.

## Global Constraints

- Frase tem só campo `texto` (string, obrigatório, não pode ser vazio/branco).
- Sem autenticação em nenhum endpoint.
- Sem Docker — dev roda `uvicorn` e `npm run dev` separados.
- Sem migrações (alembic) — usar `Base.metadata.create_all`.
- CORS liberado para `http://localhost:3000`.
- Sem testes automatizados de frontend (fora de escopo).
- Sem git nesta pasta — pular passos de `git commit` (marcar como concluído sem comitar).

---

## File Structure

```
backend/
  app/
    __init__.py
    database.py       # engine, SessionLocal, Base
    models.py          # modelo Frase
    schemas.py         # Pydantic: FraseCreate, FraseUpdate, FraseOut
    crud.py             # funções de acesso a dados
    main.py             # app FastAPI, CORS, startup, rotas
  requirements.txt
  tests/
    __init__.py
    test_frases.py

frontend/
  (gerado por create-next-app, App Router + TypeScript)
  lib/
    api.ts              # funções fetch: listFrases, createFrase, updateFrase, deleteFrase
  app/
    page.tsx             # página única: lista + form + editar/deletar
```

---

### Task 1: Backend — modelo e banco

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/database.py`
- Create: `backend/app/models.py`
- Test: `backend/tests/__init__.py`
- Test: `backend/tests/test_database.py`

**Interfaces:**
- Produces: `database.Base` (declarative base), `database.SessionLocal` (sessionmaker), `database.engine`, `database.get_db()` (generator, yields `Session`), `models.Frase` (colunas: `id: int` PK autoincrement, `texto: str` not null, `criado_em: datetime` default now).

- [ ] **Step 1: Criar `backend/requirements.txt`**

```
fastapi==0.115.0
uvicorn[standard]==0.30.6
sqlalchemy==2.0.35
pytest==8.3.3
httpx==0.27.2
```

- [ ] **Step 2: Criar venv e instalar dependências**

Run (PowerShell, dentro de `backend/`):
```
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
```

- [ ] **Step 3: Criar `backend/app/__init__.py` (vazio) e `backend/tests/__init__.py` (vazio)**

- [ ] **Step 4: Escrever teste que falha — `backend/tests/test_database.py`**

```python
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
```

- [ ] **Step 5: Rodar teste e confirmar falha**

Run (dentro de `backend/`): `.\venv\Scripts\pytest tests/test_database.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'app.database'` (ou similar)

- [ ] **Step 6: Implementar `backend/app/database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./frases.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 7: Implementar `backend/app/models.py`**

```python
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class Frase(Base):
    __tablename__ = "frases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    texto = Column(String, nullable=False)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False)
```

- [ ] **Step 8: Rodar teste e confirmar sucesso**

Run: `.\venv\Scripts\pytest tests/test_database.py -v`
Expected: PASS

---

### Task 2: Backend — schemas, CRUD e endpoints

**Files:**
- Create: `backend/app/schemas.py`
- Create: `backend/app/crud.py`
- Create: `backend/app/main.py`
- Test: `backend/tests/test_frases.py`

**Interfaces:**
- Consumes: `database.Base`, `database.SessionLocal`, `database.engine`, `database.get_db` (Task 1); `models.Frase` (Task 1).
- Produces: `schemas.FraseCreate {texto: str}`, `schemas.FraseUpdate {texto: str}`, `schemas.FraseOut {id: int, texto: str, criado_em: datetime}`; `crud.criar_frase(db, frase: FraseCreate) -> Frase`, `crud.listar_frases(db) -> list[Frase]`, `crud.atualizar_frase(db, frase_id: int, frase: FraseUpdate) -> Frase | None`, `crud.deletar_frase(db, frase_id: int) -> bool`; FastAPI `app` em `app.main` com rotas `GET /frases`, `POST /frases`, `PUT /frases/{id}`, `DELETE /frases/{id}`.

- [ ] **Step 1: Escrever testes que falham — `backend/tests/test_frases.py`**

```python
import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("TESTING", "1")


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "test_frases.db"
    monkeypatch.setattr(
        "app.database.SQLALCHEMY_DATABASE_URL", f"sqlite:///{db_file}"
    )
    from app import database
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    test_engine = create_engine(
        f"sqlite:///{db_file}", connect_args={"check_same_thread": False}
    )
    TestSessionLocal = sessionmaker(bind=test_engine)
    database.Base.metadata.create_all(bind=test_engine)

    from app.main import app, get_db

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def test_create_frase(client):
    response = client.post("/frases", json={"texto": "primeira frase"})
    assert response.status_code == 201
    body = response.json()
    assert body["texto"] == "primeira frase"
    assert "id" in body


def test_create_frase_texto_vazio_retorna_400(client):
    response = client.post("/frases", json={"texto": "   "})
    assert response.status_code == 400


def test_listar_frases(client):
    client.post("/frases", json={"texto": "frase A"})
    client.post("/frases", json={"texto": "frase B"})
    response = client.get("/frases")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2


def test_atualizar_frase(client):
    created = client.post("/frases", json={"texto": "original"}).json()
    response = client.put(f"/frases/{created['id']}", json={"texto": "editada"})
    assert response.status_code == 200
    assert response.json()["texto"] == "editada"


def test_atualizar_frase_inexistente_retorna_404(client):
    response = client.put("/frases/999", json={"texto": "x"})
    assert response.status_code == 404


def test_deletar_frase(client):
    created = client.post("/frases", json={"texto": "para deletar"}).json()
    response = client.delete(f"/frases/{created['id']}")
    assert response.status_code == 204
    assert client.get("/frases").json() == []


def test_deletar_frase_inexistente_retorna_404(client):
    response = client.delete("/frases/999")
    assert response.status_code == 404
```

- [ ] **Step 2: Rodar testes e confirmar falha**

Run: `.\venv\Scripts\pytest tests/test_frases.py -v`
Expected: FAIL (import error, `app.main` não existe)

- [ ] **Step 3: Implementar `backend/app/schemas.py`**

```python
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
```

- [ ] **Step 4: Implementar `backend/app/crud.py`**

```python
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
```

- [ ] **Step 5: Implementar `backend/app/main.py`**

```python
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
```

- [ ] **Step 6: Rodar testes e confirmar sucesso**

Run (dentro de `backend/`): `.\venv\Scripts\pytest tests/ -v`
Expected: PASS (todos os testes de `test_database.py` e `test_frases.py`)

- [ ] **Step 7: Subir servidor manualmente e checar `/docs`**

Run: `.\venv\Scripts\uvicorn app.main:app --reload`
Abrir `http://localhost:8000/docs` e confirmar que os 4 endpoints aparecem.

---

### Task 3: Frontend — scaffold e client de API

**Files:**
- Create: `frontend/` (via `create-next-app`)
- Create: `frontend/lib/api.ts`

**Interfaces:**
- Consumes: backend rodando em `http://localhost:8000` (Task 2).
- Produces: `Frase {id: number, texto: string, criado_em: string}`; `listFrases(): Promise<Frase[]>`, `createFrase(texto: string): Promise<Frase>`, `updateFrase(id: number, texto: string): Promise<Frase>`, `deleteFrase(id: number): Promise<void>` exportados de `lib/api.ts`.

- [ ] **Step 1: Gerar projeto Next.js**

Run (na raiz do monorepo):
```
npx create-next-app@latest frontend --typescript --eslint --app --no-tailwind --no-src-dir --import-alias "@/*"
```
Confirmar defaults quando perguntado.

- [ ] **Step 2: Criar `frontend/lib/api.ts`**

```typescript
const API_URL = "http://localhost:8000";

export interface Frase {
  id: number;
  texto: string;
  criado_em: string;
}

export async function listFrases(): Promise<Frase[]> {
  const res = await fetch(`${API_URL}/frases`);
  if (!res.ok) throw new Error("falha ao listar frases");
  return res.json();
}

export async function createFrase(texto: string): Promise<Frase> {
  const res = await fetch(`${API_URL}/frases`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });
  if (!res.ok) throw new Error("falha ao criar frase");
  return res.json();
}

export async function updateFrase(id: number, texto: string): Promise<Frase> {
  const res = await fetch(`${API_URL}/frases/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });
  if (!res.ok) throw new Error("falha ao editar frase");
  return res.json();
}

export async function deleteFrase(id: number): Promise<void> {
  const res = await fetch(`${API_URL}/frases/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("falha ao deletar frase");
}
```

- [ ] **Step 3: Verificar build**

Run (dentro de `frontend/`): `npm run build`
Expected: build passa sem erros de TypeScript (página default do `create-next-app` ainda intacta nesse ponto).

---

### Task 4: Frontend — página de cadastro de frases

**Files:**
- Modify: `frontend/app/page.tsx`

**Interfaces:**
- Consumes: `listFrases`, `createFrase`, `updateFrase`, `deleteFrase`, `Frase` de `frontend/lib/api.ts` (Task 3).

- [ ] **Step 1: Substituir `frontend/app/page.tsx` pela página de cadastro**

```tsx
"use client";

import { useEffect, useState } from "react";
import { Frase, createFrase, deleteFrase, listFrases, updateFrase } from "@/lib/api";

export default function Home() {
  const [frases, setFrases] = useState<Frase[]>([]);
  const [novoTexto, setNovoTexto] = useState("");
  const [editandoId, setEditandoId] = useState<number | null>(null);
  const [textoEdicao, setTextoEdicao] = useState("");
  const [erro, setErro] = useState<string | null>(null);

  async function carregar() {
    try {
      setFrases(await listFrases());
    } catch {
      setErro("falha ao carregar frases");
    }
  }

  useEffect(() => {
    carregar();
  }, []);

  async function handleCriar(e: React.FormEvent) {
    e.preventDefault();
    if (!novoTexto.trim()) return;
    try {
      await createFrase(novoTexto);
      setNovoTexto("");
      setErro(null);
      await carregar();
    } catch {
      setErro("falha ao criar frase");
    }
  }

  function iniciarEdicao(frase: Frase) {
    setEditandoId(frase.id);
    setTextoEdicao(frase.texto);
  }

  async function handleSalvarEdicao(id: number) {
    if (!textoEdicao.trim()) return;
    try {
      await updateFrase(id, textoEdicao);
      setEditandoId(null);
      setErro(null);
      await carregar();
    } catch {
      setErro("falha ao editar frase");
    }
  }

  async function handleDeletar(id: number) {
    try {
      await deleteFrase(id);
      setErro(null);
      await carregar();
    } catch {
      setErro("falha ao deletar frase");
    }
  }

  return (
    <main style={{ maxWidth: 600, margin: "2rem auto", padding: "0 1rem" }}>
      <h1>Cadastro de Frases</h1>

      {erro && <p style={{ color: "red" }}>{erro}</p>}

      <form onSubmit={handleCriar} style={{ display: "flex", gap: 8, marginBottom: 24 }}>
        <input
          value={novoTexto}
          onChange={(e) => setNovoTexto(e.target.value)}
          placeholder="Nova frase"
          style={{ flex: 1 }}
        />
        <button type="submit">Adicionar</button>
      </form>

      <ul style={{ listStyle: "none", padding: 0 }}>
        {frases.map((frase) => (
          <li key={frase.id} style={{ display: "flex", gap: 8, marginBottom: 8 }}>
            {editandoId === frase.id ? (
              <>
                <input
                  value={textoEdicao}
                  onChange={(e) => setTextoEdicao(e.target.value)}
                  style={{ flex: 1 }}
                />
                <button onClick={() => handleSalvarEdicao(frase.id)}>Salvar</button>
                <button onClick={() => setEditandoId(null)}>Cancelar</button>
              </>
            ) : (
              <>
                <span style={{ flex: 1 }}>{frase.texto}</span>
                <button onClick={() => iniciarEdicao(frase)}>Editar</button>
                <button onClick={() => handleDeletar(frase.id)}>Deletar</button>
              </>
            )}
          </li>
        ))}
      </ul>
    </main>
  );
}
```

- [ ] **Step 2: Verificar build**

Run (dentro de `frontend/`): `npm run build`
Expected: build passa sem erros.

- [ ] **Step 3: Teste manual end-to-end**

1. Backend rodando: `.\venv\Scripts\uvicorn app.main:app --reload` (dentro de `backend/`)
2. Frontend rodando: `npm run dev` (dentro de `frontend/`)
3. Abrir `http://localhost:3000`
4. Criar frase, confirmar que aparece na lista
5. Editar frase, confirmar texto atualizado
6. Deletar frase, confirmar remoção da lista
7. Testar criar com texto vazio — confirmar que não cria e/ou mostra erro

---

## Self-Review Notes

- Spec coverage: CRUD (Task 2), campo único texto (Tasks 1-2), sem auth (nenhum endpoint protegido), sem docker (comandos diretos), SQLite sem migrações (`create_all`), CORS localhost:3000 (Task 2), validação texto vazio 400 (Task 2), 404 em PUT/DELETE inexistente (Task 2), testes backend com pytest+TestClient (Task 2), frontend sem testes automatizados — só manual (Task 4). Todos cobertos.
- Sem placeholders — todo código é completo e executável.
- Tipos consistentes entre tasks: `Frase` (schemas.FraseOut / lib/api.ts) usa `id, texto, criado_em` em todos os pontos.
