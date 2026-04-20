# auditores-digitales-backend

Backend FastAPI para los auditores autónomos genéricos de ASAI. Recibe archivos de evidencia y preguntas, los despacha a N8N vía webhooks, y expone endpoints para que N8N devuelva resultados procesados. Vertex AI RAG se integra desde el lado de N8N.

## Stack

- **FastAPI** — API REST versionada bajo `/api/v1/`
- **PostgreSQL** — Base de datos local (SQLAlchemy 2.0)
- **Pydantic v2** — Validación y schemas
- **N8N** — Orquestador de flujos (RAG, Vertex AI)
- **Vertex AI** — Motor RAG (integrado desde N8N)

## Requisitos

- Python 3.11
- PostgreSQL corriendo en `localhost:5432`
- Base de datos `auditores_digitales_db` creada

## Instalación

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

Configurar `.env` en la raíz:

```env
DATABASE_URL=postgresql://postgres:PASSWORD@localhost:5432/auditores_digitales_db
N8N_BASE_URL=http://localhost:5678
DEBUG=true
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
# Fase futura:
# GOOGLE_PROJECT_ID=
# GEMINI_API_KEY=
```

## Levantar servidor

```bash
python main.py
# o bien
python -m uvicorn app.main:app --reload
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Endpoints

| Método | Ruta                                       | Descripción                              |
|--------|--------------------------------------------|------------------------------------------|
| POST   | `/api/v1/sessions/`                        | Crear sesión de auditoría                |
| GET    | `/api/v1/sessions/{session_id}`            | Obtener sesión                           |
| POST   | `/api/v1/evidencia/?session_id=`           | Subir archivo (PDF/DOCX/XLSX) → N8N      |
| POST   | `/api/v1/chat/`                            | Enviar pregunta → N8N                    |
| POST   | `/api/v1/webhook/evidence-uploaded`        | N8N notifica que procesó evidencia       |
| POST   | `/api/v1/webhook/chat-response`            | N8N devuelve respuesta RAG               |

## Estructura

```
auditores-digitales-backend/
├── main.py                        # Punto de entrada (uvicorn)
├── requirements.txt
├── app/
│   ├── main.py                    # FastAPI app, lifespan, CORS, routers
│   ├── config.py                  # Settings (pydantic-settings, .env)
│   ├── database.py                # Engine SQLAlchemy, SessionLocal, get_db()
│   │
│   ├── api/v1/
│   │   ├── dependencies.py        # get_db
│   │   └── endpoints/
│   │       ├── sessions.py
│   │       ├── evidencia.py
│   │       ├── chat.py
│   │       └── webhooks.py
│   │
│   ├── core/
│   │   ├── constants.py           # Extensiones permitidas, tamaño máximo
│   │   ├── exceptions.py          # Excepciones de dominio
│   │   └── security.py            # JWT/auth (fase futura)
│   │
│   ├── models/                    # ORM SQLAlchemy
│   │   ├── session.py
│   │   ├── chat_history.py
│   │   ├── evidence.py
│   │   └── audit_log.py
│   │
│   ├── schemas/                   # Pydantic v2
│   │   ├── common.py
│   │   ├── session.py
│   │   ├── chat.py
│   │   ├── evidence.py
│   │   └── webhook.py
│   │
│   ├── services/                  # Lógica de negocio
│   │   ├── session_service.py
│   │   ├── chat_service.py
│   │   ├── evidence_service.py
│   │   └── n8n_service.py
│   │
│   ├── repository/                # Acceso a datos
│   │   ├── session_repository.py
│   │   ├── chat_repository.py
│   │   ├── evidence_repository.py
│   │   └── audit_log_repository.py
│   │
│   └── utils/
│       ├── n8n.py                 # N8NClient: cliente HTTP hacia N8N
│       ├── logger.py
│       ├── validators.py
│       └── uuid_helper.py
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_services.py
│   │   └── test_repositories.py
│   └── integration/
│       └── test_api.py
│
└── n8n-workflows/                 # Exports de flujos N8N
```

## Flujo de request

1. Cliente → `POST /api/v1/evidencia/` o `POST /api/v1/chat/` → endpoint delega al service
2. Service valida dominio → guarda en BD con `status="processing"` → dispara N8N vía `N8NService`
3. N8N procesa (RAG, Vertex AI) → llama `POST /api/v1/webhook/evidence-uploaded` o `/webhook/chat-response`
4. FastAPI matchea por `request_id`, actualiza BD → retorna `{"received": true}`

> N8N offline en desarrollo: los endpoints no fallan — guardan en BD y retornan respuesta placeholder.

## Webhooks N8N ↔ FastAPI

| Dirección         | Endpoint                                          |
|-------------------|---------------------------------------------------|
| N8N → FastAPI     | `POST /api/v1/webhook/evidence-uploaded`          |
| N8N → FastAPI     | `POST /api/v1/webhook/chat-response`              |
| FastAPI → N8N     | `POST {N8N_BASE_URL}/webhook/upload-evidence`     |
| FastAPI → N8N     | `POST {N8N_BASE_URL}/webhook/chat-query`          |

## Testing

```bash
pytest                      # todos los tests
pytest tests/unit           # solo unit
pytest tests/integration    # solo integration
```
