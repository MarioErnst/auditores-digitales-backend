# auditores-digitales-backend

Backend para los auditores autónomos genéricos de ASAI. Expone una API REST que orquesta el procesamiento de evidencia documental y consultas RAG a través de N8N y Vertex AI.

## Stack

- **FastAPI** — API REST
- **PostgreSQL** — Base de datos local
- **N8N** — Orquestador de flujos (RAG, Vertex AI)
- **Vertex AI** — Motor RAG (integrado desde N8N)

## Requisitos

- Python 3.11
- PostgreSQL corriendo en `localhost:5432`
- Base de datos `auditores_digitales_db` creada

## Instalación

```bash
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Configurar `.env` en la raíz:

```env
DATABASE_URL=postgresql://postgres:PASSWORD@localhost:5432/auditores_digitales_db
N8N_BASE_URL=http://localhost:5678
```

## Levantar servidor

```bash
python -m uvicorn backend.main:app --reload
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Endpoints

| Método | Ruta                              | Descripción                              |
|--------|-----------------------------------|------------------------------------------|
| POST   | `/sessions`                       | Crear sesión de auditoría                |
| GET    | `/sessions/{id}`                  | Obtener sesión                           |
| POST   | `/evidencia?session_id=`          | Subir archivo (PDF/DOCX/XLSX) → N8N      |
| POST   | `/chat`                           | Enviar pregunta → N8N                    |
| POST   | `/webhook/evidence-uploaded`      | N8N notifica que procesó evidencia       |
| POST   | `/webhook/chat-response`          | N8N devuelve respuesta RAG               |

## Estructura

```
backend/
├── main.py, config.py, database.py, models.py, schemas.py
├── routes/       sessions, evidencia, chat, webhooks
└── utils/        n8n.py (cliente HTTP hacia N8N)
n8n-workflows/    Exports de flujos N8N
```
