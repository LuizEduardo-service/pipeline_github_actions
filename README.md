# Cadastro de Frases — Aprendizado CI/CD com GitHub Actions

Projeto simples (FastAPI + Next.js + SQLite) usado como base pra aprender GitHub Actions na prática: CI (testes/lint) e CD (deploy) do zero.

## Estrutura do projeto

```
backend/    FastAPI + SQLAlchemy + SQLite — API REST de frases
frontend/   Next.js (App Router) — CRUD de frases
.github/    workflows de CI/CD
```

## O que é CI vs CD

- **CI (Continuous Integration)**: roda em todo Pull Request. Valida que o código não quebrou — lint + testes + build. Não sobe nada em produção.
- **CD (Continuous Deployment)**: roda em push na branch de produção (`master`). Depois que o código já foi validado pelo CI e mergeado, o CD publica a versão nova onde a aplicação roda de verdade.

## Como um workflow funciona

- Qualquer `.yaml`/`.yml` dentro de `.github/workflows/` é um workflow — GitHub detecta automático, sem registro manual.
- `on:` define o gatilho (`pull_request`, `push`, etc) e pra quais branches.
- `jobs:` são unidades que rodam em paralelo, cada uma numa VM limpa (runner).
- `steps:` dentro de um job rodam em sequência, na mesma VM.
- `uses: owner/repo@versao` chama uma Action pronta (ex: `actions/checkout`, `actions/setup-python`).
- `run:` executa um comando shell direto — os mesmos comandos que rodaríamos manualmente no terminal.

## CI implementado (`.github/workflows/pull_requests.yaml`)

Dispara em PR pra `main`, `dev` ou `master`. Dois jobs em paralelo:

- **backend**: instala deps (`pip install -r requirements.txt`), roda lint (`ruff check .`) e testes (`pytest`).
- **frontend**: instala deps (`npm ci`), roda lint (`npm run lint`) e build (`npm run build`).

Se qualquer step falhar, o job fica vermelho e o PR fica marcado como falho.

### Erros reais que apareceram e o que ensinaram

1. **`branches: [main, dev]` sem incluir a branch real (`master`)** → workflow nunca disparava, aparecia "0 workflow runs". Lição: o filtro de branch do `pull_request` se refere à branch **base** (destino) do PR — se ela não estiver na lista, não roda.
2. **`npm ci` falhando por lockfile desincronizado** (`Missing: @emnapi/core... from lock file`) → `package-lock.json` comitado não batia com as deps instaladas localmente (dependências opcionais nativas do Turbopack variam por plataforma). Lição: `npm ci` é estrito — exige lockfile exatamente sincronizado com `package.json`; resolvido regenerando o lockfile (`rm -rf node_modules package-lock.json && npm install`) e comitando.
3. **Regra de lint nova (`react-hooks/set-state-in-effect`)** flagou um `useEffect` clássico de fetch-on-mount. Lição: versões novas de tooling (Next 16 / React 19 / eslint-plugin-react-hooks v5) endurecem regras; padrão de fetch-on-mount ainda é válido, mas precisa de `eslint-disable` pontual e justificado.

## Docker no backend (`backend/Dockerfile`)

Empacota a API FastAPI numa imagem, eliminando dependência de venv/Python instalado na máquina de destino:

```bash
cd backend
docker build -t backend .
docker run -d --name backend -p 8000:8000 backend
```

`.dockerignore` evita mandar `venv/`, `tests/` e `*.db` pro contexto de build (mais rápido, imagem mais limpa).

## CD planejado (`.github/workflows/cd.yaml`)

Dispara em push pra `master`. Conecta via SSH numa VM (GCP Compute Engine) e recria o container:

```yaml
script: |
  git pull origin master
  cd backend && docker build -t backend .
  docker stop backend || true && docker rm backend || true
  docker run -d --name backend -p 8000:8000 --restart unless-stopped backend
```

Requer, no GitHub (Settings → Secrets and variables → Actions):
- `GCP_HOST` — IP da VM
- `GCP_USER` — usuário SSH
- `GCP_SSH_KEY` — chave privada SSH

**Ainda não ativo de verdade** — falta criar a VM no GCP e configurar os secrets. Workflow existe, mas depende de infra real pra rodar.

## Principais conceitos fixados

- Secrets nunca vão no YAML — sempre em GitHub Secrets, referenciados via `${{ secrets.NOME }}`.
- CI protege qualidade (roda em PR); CD entrega (roda em push na branch de produção).
- `needs:` entre jobs garante ordem/dependência (ex: só deployar se os testes passarem).
- Lockfiles (`package-lock.json`) precisam estar sempre sincronizados e comitados — `npm ci` não perdoa divergência.
- Docker resolve "funciona na minha máquina" ao empacotar runtime + deps junto com o código.
