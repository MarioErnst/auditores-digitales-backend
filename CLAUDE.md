# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Backend FastAPI para los auditores autónomos genéricos de ASAI. Recibe archivos de evidencia y preguntas, los despacha a N8N vía webhooks, y expone endpoints para que N8N devuelva resultados procesados. Vertex AI RAG se integra desde el lado de N8N.

Stack: **FastAPI + PostgreSQL + N8N + Vertex AI RAG**

## Environment Setup

```bash
# Crear venv con Python 3.11 (requerido — 3.14 no es compatible con las dependencias)
py -3.11 -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac

pip install -r requirements.txt

# Levantar servidor (dos opciones)
python main.py
# o bien
python -m uvicorn app.main:app --reload
```

## Environment Variables (.env)

```env
DATABASE_URL=postgresql://postgres:PASSWORD@localhost:5432/auditores_digitales_db
N8N_BASE_URL=http://localhost:5678                # opcional, este es el default
GOOGLE_PROJECT_ID=                                 # para Vertex AI (fase futura)
GEMINI_API_KEY=                                    # para Vertex AI (fase futura)
DEBUG=true                                         # echo SQL de SQLAlchemy
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

## Architecture

Arquitectura en capas (endpoints → services → repositories → models). La API está versionada bajo `/api/v1/`.

```
auditores-digitales-backend/
├── main.py                        # Punto de entrada: uvicorn
├── app/
│   ├── main.py                    # FastAPI app, lifespan, CORS, routers
│   ├── config.py                  # Settings (pydantic-settings, .env)
│   ├── database.py                # Engine SQLAlchemy, SessionLocal, Base, get_db()
│   │
│   ├── api/v1/
│   │   ├── dependencies.py        # get_db, auth (futuro)
│   │   └── endpoints/             # Routers FastAPI (solo orquestan)
│   │       ├── sessions.py        # POST/GET /api/v1/sessions
│   │       ├── evidencia.py       # POST /api/v1/evidencia
│   │       ├── chat.py            # POST /api/v1/chat
│   │       └── webhooks.py        # POST /api/v1/webhook/*
│   │
│   ├── core/
│   │   ├── constants.py           # Constantes globales (extensiones, tamaños)
│   │   ├── exceptions.py          # Excepciones de dominio
│   │   └── security.py            # JWT/auth (fase futura)
│   │
│   ├── models/                    # ORM SQLAlchemy (un archivo por entidad)
│   │   ├── session.py
│   │   ├── chat_history.py
│   │   ├── evidence.py
│   │   └── audit_log.py
│   │
│   ├── schemas/                   # Pydantic v2 (request/response)
│   │   ├── common.py              # ErrorResponse
│   │   ├── session.py
│   │   ├── chat.py                # ChatRequest, ChatResponse, SourceInfo
│   │   ├── evidence.py
│   │   └── webhook.py             # Payloads entrantes desde N8N
│   │
│   ├── services/                  # Lógica de negocio
│   │   ├── session_service.py
│   │   ├── chat_service.py
│   │   ├── evidence_service.py
│   │   └── n8n_service.py         # Wrapper sobre N8NClient
│   │
│   ├── repository/                # Acceso a datos (queries SQLAlchemy)
│   │   ├── session_repository.py
│   │   ├── chat_repository.py
│   │   ├── evidence_repository.py
│   │   └── audit_log_repository.py
│   │
│   └── utils/
│       ├── n8n.py                 # N8NClient: cliente HTTP puro
│       ├── logger.py              # Helpers de logging con emojis
│       ├── validators.py          # validate_extension, validate_size
│       └── uuid_helper.py         # generate_uuid()
│
└── tests/
    ├── conftest.py                # Fixtures (db_session, client)
    ├── unit/                      # Tests unitarios de services/repos
    └── integration/               # Tests de API con TestClient
```

### Request flow

1. Cliente → `POST /api/v1/evidencia` o `POST /api/v1/chat` → endpoint delega al service
2. Service valida dominio (sesión existente, extensión, tamaño) → llama al repository para guardar en BD con `status="processing"` → dispara N8N vía `N8NService`
3. N8N procesa (RAG, Vertex AI) → llama `POST /api/v1/webhook/evidence-uploaded` o `POST /api/v1/webhook/chat-response`
4. FastAPI matchea el registro por `request_id` y actualiza BD → retorna `{"received": true}` (siempre 200 — N8N no reintenta si recibe error)

### Key conventions

- Capas: los **endpoints** solo orquestan (reciben request → llaman service → retornan response). La **lógica de negocio** vive en services. El **acceso a BD** vive en repositories.
- Naming: todo en inglés (`question`, `answer`, `sources`). Para compatibilidad con N8N actual, los schemas de webhooks entrantes usan `validation_alias` (`respuesta`, `fuentes`, `nombre`, `relevancia`).
- IDs: `String(36)` UUIDs generados con `generate_uuid()` en `app/utils/uuid_helper.py`
- DateTime defaults: `datetime.utcnow` sin paréntesis en `Column(default=...)`
- `ChatHistory.request_id` es el identificador que liga la pregunta con la respuesta del webhook
- N8N offline en desarrollo: los endpoints de chat y evidencia no fallan — guardan en BD y retornan respuesta placeholder
- Webhooks nunca lanzan excepciones hacia afuera: capturan todo con `try/except` y loggean con `log_warning`
- Todos los archivos Python tienen `# -*- coding: utf-8 -*-` al inicio
- Type hints en todas las funciones

## Database

PostgreSQL local, puerto 5432, BD `auditores_digitales_db`. Las tablas se crean automáticamente al iniciar el servidor (`create_tables()` en lifespan de `app/main.py`). No hay migraciones por ahora.

### Columnas agregadas manualmente (ejecutar en PgAdmin en el servidor)

```sql
ALTER TABLE chat_history ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'processing';
ALTER TABLE evidence_metadata ADD COLUMN IF NOT EXISTS document_name VARCHAR(500);
ALTER TABLE evidence_metadata ADD COLUMN IF NOT EXISTS store_name VARCHAR(255);
ALTER TABLE sessions ADD COLUMN IF NOT EXISTS audit_name VARCHAR(255);
```

## API versioning

Todos los endpoints cuelgan de `/api/v1/`. Para agregar `v2`, crear `app/api/v2/endpoints/` y registrar el nuevo router en `app/main.py` con `prefix="/api/v2"`.

## N8N Webhooks esperados por FastAPI

| Evento       | N8N llama a FastAPI en…                   |
|--------------|--------------------------------------------|
| Evidencia    | `POST /api/v1/webhook/evidence-uploaded`  |
| Chat         | `POST /api/v1/webhook/chat-response`      |

FastAPI llama a N8N en:

| Acción       | Endpoint N8N                                       |
|--------------|----------------------------------------------------|
| Subir archivo| `POST {N8N_BASE_URL}/webhook/upload-evidence`      |
| Chat query   | `POST {N8N_BASE_URL}/webhook/chat-query`           |

## Testing

```bash
pytest                      # todos los tests
pytest tests/unit           # solo unit
pytest tests/integration    # solo integration
```

---

## Reglas que SIEMPRE hay que seguir

### HTTP y async
- NUNCA usar `requests` — este proyecto usa exclusivamente `httpx` con async/await
- NUNCA declarar `async def` en una función que no tiene ningún `await`
- SIEMPRE configurar timeout en todas las llamadas HTTP: `httpx.AsyncClient(timeout=10.0)`
- Para llamadas a N8N, SIEMPRE usar el cliente en `app/utils/n8n.py`, nunca instanciar httpx directamente en services o endpoints

### Seguridad
- NUNCA dejar un endpoint de webhook sin verificar el header `X-N8N-Secret`
- NUNCA exponer URLs internas, tokens, o IPs en respuestas de endpoints públicos
- La variable `DEBUG` debe ser `False` por defecto en `config.py`
- Los secrets SIEMPRE vienen de `settings` (pydantic-settings), nunca hardcodeados

### Base de datos
- NUNCA hacer queries SQLAlchemy directamente en endpoints o services
- El acceso a datos SIEMPRE pasa por la capa repository
- SIEMPRE cerrar la sesión DB en un bloque `finally` o usar el `get_db()` dependency

### N8N
- El health check de N8N usa `GET {base_url}/healthz` — NUNCA hacer POST al webhook real para verificar disponibilidad
- Los endpoints de webhook SIEMPRE retornan HTTP 200 con `{"received": true}` — N8N no reintenta si recibe un error
- SIEMPRE validar el header `X-N8N-Secret` antes de procesar cualquier payload entrante de N8N
- Los payloads de webhook SIEMPRE usan `Literal` o `Enum` para campos de status, nunca `str` libre

### Errores y logging
- NUNCA usar `except Exception: pass` — siempre loguear con `log_warning(f"mensaje: {e}")`
- NUNCA englobar en el mismo `try/except` operaciones independientes (ej: procesar webhook Y escribir audit log)
- Las conexiones a BD SIEMPRE se cierran en `finally`, no en el happy path

---

## Decisiones de arquitectura tomadas

- Se eligió `httpx` sobre `requests` para no bloquear el event loop de uvicorn
- Los webhooks usan secreto compartido por header (`X-N8N-Secret`) en lugar de JWT porque N8N es el único caller y no hay sesiones de usuario
- El audit log es una operación separada e independiente del procesamiento principal del webhook
- `BackgroundTasks` de FastAPI se usa para despachar a N8N y no bloquear la respuesta al cliente

---

## Errores conocidos que ya fueron corregidos (no reintroducir)

- `requests` bloqueando el event loop desde funciones `async def`
- Health check haciendo POST al webhook real de N8N con payload `{"ping": True}`
- Webhooks sin autenticación aceptando cualquier llamada externa
- `debug: bool = True` como default exponiendo queries SQL en logs
- Connection leak en health check de BD (db.close() dentro del try sin finally)
- Lógica de persistencia (audit log) directamente en endpoints en lugar de services
