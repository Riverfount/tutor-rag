# Registro de Decisões de Arquitetura — Tutor RAG

Este arquivo é a memória de longo prazo das decisões técnicas do projeto. Cada
entrada registra **o que** foi decidido, **quais alternativas** foram
consideradas e **por quê** — para que qualquer pessoa (o próprio autor meses
depois, ou um revisor técnico) reconstrua o raciocínio sem precisar adivinhá-lo.

Formato de cada entrada: `data · decisão · alternativas consideradas · motivo`.
Entradas novas são adicionadas ao final.

---

## 1. Estrutura de pacotes: pacote único `tutor_rag` com subpacotes por responsabilidade

- **Data:** 27/08/2026
- **Decisão:** Um único pacote de topo em `src/tutor_rag/`, com subpacotes por
  responsabilidade — `core` (domínio puro, sem framework), `infra` (settings,
  banco, clients externos), `api` (FastAPI: app, rotas, schemas) e `ingestion`
  (pipeline offline). Regra de direção de dependência: `api` e `ingestion`
  dependem de `core` e `infra`; **`core` não importa nada** — nem framework, nem
  os demais subpacotes.
- **Alternativas consideradas:** Quatro pacotes de topo soltos
  (`src/core`, `src/api`, `src/infra`, `src/ingestion`) sem o pacote agregador
  `tutor_rag`.
- **Motivo:** O pacote único dá um namespace coeso
  (`from tutor_rag.core import ...`) e evita "possuir" nomes genéricos e
  colidíveis (`core`, `api`, `infra`) no namespace global de imports. Mantém a
  auto-descoberta do build backend (hatchling) sem configuração manual de
  pacotes. A regra de dependência garante que a função de retrieval nasça limpa
  em `core` e seja reaproveitada como está pelo agente (Fase 2) e pelo servidor
  MCP (Fase 3), sem refactor — é o que faz valer a promessa de que "as fases
  seguintes só preenchem".

## 2. Layout `src/` em vez de flat

- **Data:** 27/08/2026
- **Decisão:** `src` layout (`src/tutor_rag/`).
- **Alternativas consideradas:** Flat layout (`tutor_rag/` na raiz do repo).
- **Motivo:** O `src` layout impede que os testes importem o diretório local por
  acidente (o clássico "passa porque o CWD está no path") e força o teste contra
  o pacote instalado em modo editável (`uv sync`). O custo — exigir o pacote
  instalado para resolver imports — é baixo e resolvido pelo uv. Para um
  serviço/portfólio, tanto `src` quanto flat leem como idiomáticos; escolhido
  `src` pela proteção de import nos testes.

## 3. Configuração com `pydantic-settings` (não Dynaconf)

- **Data:** 27/08/2026
- **Decisão:** `pydantic-settings` para carregar e validar configuração.
- **Alternativas consideradas:** Dynaconf.
- **Motivo:** `pydantic-settings` entrega um objeto `Settings` tipado — mypy
  estrito valida, a IDE autocompleta e a validação acontece no load — e mantém
  coerência com o ecossistema pydantic que o FastAPI já usa de ponta a ponta
  (schemas de request/response). O Dynaconf é maduro e superior em config em
  camadas por ambiente, múltiplos formatos (toml/yaml) e backends de secret
  (ex.: Vault), mas o projeto não tem essas dores ainda (cenário local + um
  deploy): pagaríamos por flexibilidade não usada, e seu acesso dinâmico rema
  contra a convenção de mypy estrito do projeto.

## 4. Redis fora do escopo da infra mínima inicial

- **Data:** 27/08/2026
- **Decisão:** Não subir Redis no setup inicial. A infra mínima é apenas
  Postgres/pgvector + FastAPI.
- **Alternativas consideradas:** Incluir Redis já no setup, como o documento de
  intenção sugeria no escopo do Chat 1.
- **Motivo:** Na fatia vertical fina não há cache nem fila para justificar
  Redis. Ele entra quando existir ingestão assíncrona (Celery) ou necessidade
  real de cache — momento em que ganhará sua própria entrada aqui. Disciplina de
  "uma novidade por vez".

## 5. Fluxo de trabalho no Git: issue → feature-branch → PR → squash-merge

- **Data:** 27/08/2026
- **Decisão:** O bootstrap do repositório (estrutura de pastas + este decision
  log) vai direto na `main`. A partir daí, todo trabalho segue o fluxo:
  issue → feature-branch curta a partir da `main` → PR com `Closes #N` →
  squash-merge. Conventional Commits em todo o histórico; o título do PR é um
  conventional commit válido (vira o commit da `main` no squash). Nome de branch
  no padrão `tipo/slug` (ex.: `feat/rag-retrieval`).
- **Alternativas consideradas:** Commitar direto na `main` sem PRs (rápido, mas
  perde o rastro de processo); uma issue/branch por passo fino demais (vira
  ruído em vez de rastreabilidade).
- **Motivo:** Num portfólio para vaga sênior, o rastro issue → branch → PR é
  parte do artefato — evidência de processo que um revisor lê no histórico. O PR
  (mesmo trabalhando solo) é onde mora a narrativa e onde o self-review pega
  bobagem antes de virar histórico. Squash-merge mantém a `main` com um commit
  limpo por feature. O bootstrap vai direto na `main` porque estas decisões
  *precedem* o fluxo de issues — são sobre a estrutura que está sendo commitada.

## 6. Toolchain de qualidade: Ruff (lint + format), mypy estrito, pytest, pre-commit

- **Data:** 27/08/2026
- **Decisão:** Ferramentas de qualidade num grupo de dev separado
  (`[dependency-groups] dev`, via `uv add --dev`), fora das deps de runtime.
  **Ruff** faz lint *e* format (config em `pyproject.toml`), com um `select`
  enxuto de partida (`E`, `F`, `I`, `UP`, `B`) a ser ampliado conforme o código
  cresce. **mypy** em `strict = true`; libs de terceiros sem stubs são tratadas
  uma a uma com `[[tool.mypy.overrides]]`, nunca afrouxando o global. **pytest**
  com `testpaths = ["tests"]` e um teste smoke que importa `tutor_rag`.
  **pre-commit** com `.pre-commit-config.yaml` na raiz rodando só o Ruff
  (`ruff-check --fix` + `ruff-format`) mais hooks baratos do `pre-commit-hooks`
  (trailing-whitespace, end-of-file-fixer, check-toml/yaml, large-files,
  merge-conflict). CI (GitHub Actions) fica para uma issue própria (#3).
- **Alternativas consideradas:** Black + Flake8 + isort como três ferramentas
  separadas; incluir o mypy como hook do pre-commit.
- **Motivo:** O Ruff substitui os três (Black/Flake8/isort) com uma config e uma
  passada, ordens de magnitude mais rápido — menos peça móvel para manter verde.
  O mypy fica fora do pre-commit de propósito: rodar type-check completo exige o
  ambiente com todas as deps, e o env isolado do pre-commit vira um segundo
  gráfico de dependências para manter sincronizado; local + CI resolvem sem essa
  dor. O `select` enxuto evita afogar o começo do projeto em ruído de lint por
  regras que só fazem sentido com mais código. O objetivo é nascer verde e
  *seguir* verde — daqui em diante cada passo é "manter", não "chegar".

## 7. CI no GitHub Actions: Ruff + mypy + pytest a cada push/PR

- **Data:** 27/08/2026
- **Decisão:** Workflow `.github/workflows/ci.yml` dispara em `push` na `main` e
  em todo `pull_request`. Dois jobs paralelos: `quality` (setup do uv com cache
  → `uv sync --locked` → `ruff check` → `ruff format --check` → `mypy` estrito →
  `pytest`), numa matriz de versões de Python com uma entrada (`3.13`, casando
  com `requires-python`); e `pre-commit`, rodando `pre-commit run --all-files`.
  `uv sync --locked` (não `--frozen`) para o CI falhar se o `uv.lock` estiver
  defasado em relação ao `pyproject.toml`. Testes que chamam um provedor LLM
  real são marcados `llm` e excluídos por padrão (`addopts = -m "not llm"`),
  opt-in via `pytest -m llm` — o CI não depende de rede nem gasta tokens
  (spec §12). `concurrency` cancela runs obsoletos no mesmo ref. Branch
  protection na `main` exigindo o check do CI é configurada *depois* do primeiro
  run (o check precisa existir antes de poder ser exigido).
- **Alternativas consideradas:** `pip`/`venv` manual no runner em vez de `uv`
  (mais lento, diverge do ambiente local); `uv sync --frozen` (não pega lock
  defasado); mypy como hook do pre-commit num job único (mistura o env isolado
  do pre-commit com o type-check completo — ver decisão 6); linters e pytest em
  steps de um job só, sem matriz (dificulta acrescentar versões de Python
  depois).
- **Motivo:** O CI transforma "seguir verde" (decisão 6) de disciplina manual em
  verificação automática a cada PR. Reusar o `uv` no runner mantém o CI
  bit-a-bit igual ao ambiente local — o que passa na máquina passa no CI e
  vice-versa. Job de `pre-commit` separado isola quebra de config de hook de
  quebra de código. A matriz com uma entrada não custa nada agora e deixa
  "adicionar Python 3.14" como mudança de uma linha. Fecha a #3 e cumpre a
  spec §14/1b (CI verde antes de a Fase 1 fechar).
