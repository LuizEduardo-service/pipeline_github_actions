# Cadastro de Frases — Design

## Objetivo
Monorepo simples com CRUD de frases: backend FastAPI, frontend Next.js, banco SQLite.

## Escopo
- Frase tem só um campo: texto.
- Sem autenticação — qualquer usuário pode criar/listar/editar/deletar.
- Sem Docker — dev roda backend e frontend separados (venv + npm).

## Estrutura do monorepo
```
/backend       FastAPI + SQLAlchemy + SQLite
/frontend      Next.js (App Router, TypeScript)
```

## Backend
- SQLite em arquivo `frases.db`.
- Tabela `frases`: `id` (PK, autoincrement), `texto` (string, obrigatório), `criado_em` (datetime).
- SQLAlchemy model + `Base.metadata.create_all` no startup do app (sem alembic/migrações).
- Endpoints REST:
  - `GET /frases` — lista todas as frases
  - `POST /frases` — cria frase (`{texto: str}`)
  - `PUT /frases/{id}` — edita frase
  - `DELETE /frases/{id}` — remove frase
- Validação: `texto` não pode ser vazio/branco (400 se for).
- CORS liberado para origem do frontend local (`http://localhost:3000`).
- Rodar: `uvicorn app.main:app --reload` (dentro de venv).

## Frontend
- Next.js App Router, TypeScript.
- Uma página única:
  - Lista de frases cadastradas.
  - Formulário para adicionar nova frase.
  - Botão editar (inline ou modal simples) e deletar por item.
- Chamadas fetch diretas para `http://localhost:8000` (sem proxy/env por ora).
- Rodar: `npm run dev`.

## Erros e validação
- Backend retorna 400 para texto vazio, 404 para id inexistente em PUT/DELETE.
- Frontend mostra mensagem de erro simples (alert ou texto na tela) se request falhar.

## Testes
- Backend: testes básicos de API com pytest + TestClient (create, list, update, delete, texto vazio → 400).
- Frontend: sem testes automatizados nesta primeira versão (fora de escopo).

## Fora de escopo
- Autenticação/autorização.
- Docker/docker-compose.
- Paginação, busca, categorias/tags, autor.
- Migrações de banco (alembic).
