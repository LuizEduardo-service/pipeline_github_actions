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
