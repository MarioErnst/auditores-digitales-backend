# auditores-digitales-backend

Backend FastAPI para los auditores autónomos genéricos de ASAI.  
Recibe archivos de evidencia y preguntas, los despacha a **N8N** vía webhooks y expone endpoints para que N8N devuelva resultados procesados.  
**Vertex AI RAG** se integra desde el lado de N8N (no directamente desde FastAPI).

Este repositorio forma parte del monorepo **proyectoasai**, junto con los subproyectos [`frontend`](https://github.com/mtrharry/asai-test-dashboard) y [`google-alvi`](https://github.com/innova-net-co/google_filestore_manager).

---

## Stack

- **FastAPI** – API REST versionada bajo `/api/v1/`
- **SQLAlchemy 2.0 + PostgreSQL** – Base de datos local
- **Pydantic v2** – Validación y schemas
- **N8N** – Orquestador de flujos (RAG, Vertex AI Gemini)
- **Vertex AI Gemini** – Motor RAG (administrado desde N8N y desde `google-alvi`)

---

## Requisitos previos

- Python **3.11** (no se recomienda 3.14 aún)
- PostgreSQL corriendo en `localhost:5432`
- Base de datos `auditores_digitales_db` creada
- Node.js (v18+) y npm (para N8N, que se ejecuta con `npx n8n start`)
- Conexión a internet para que N8N pueda llamar a las APIs de Google

---

## Instalación y configuración

### 1. Clonar el repositorio y preparar el entorno

```bash
git clone https://github.com/MarioErnst/auditores-digitales-backend.git backend
cd backend
python3.11 -m venv .venv
source .venv/bin/activate      # Linux/Mac
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

> Nota sobre Ubuntu: si falta el módulo venv, instálalo con
> `sudo apt install python3.12-venv` y luego vuelve a crear el entorno virtual.

### 2. Archivo de entorno `.env`

Copia el ejemplo y edítalo con tus credenciales:

```bash
cp .env.example .env
nano .env
```

El contenido mínimo que debes configurar:

```env
DATABASE_URL=postgresql://postgres:TU_PASSWORD@localhost:5432/auditores_digitales_db
N8N_BASE_URL=http://localhost:5678
DEBUG=true
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

- **DATABASE_URL**: debe coincidir con las credenciales reales de tu PostgreSQL.
- **CORS_ORIGINS**: contiene los puertos del frontend de test (`3000`) y del Google File Search Manager (`5173`).
  Si el test dashboard se levanta en otro puerto, agrégalo aquí (por ejemplo, `http://localhost:5174`) o alinea su puerto para que sea `3000`.

---

## Levantar el servidor

Desde la carpeta `backend` y con el entorno virtual activado:

```bash
python main.py
# o bien
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- API: http://localhost:8000
- Documentación interactiva (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## Mapa de servicios y puertos (ecosistema completo)

| Puerto | Servicio                     | Proyecto                                  |
|--------|------------------------------|-------------------------------------------|
| 8000   | Backend FastAPI              | `backend/`                                |
| 5678   | N8N                          | (externo, se levanta con `npx n8n start`) |
| 5173   | Google File Search Manager   | `google-alvi/`                            |
| 3000   | Frontend Test Dashboard      | `frontend/`                               |
| 5432   | PostgreSQL                   | (servicio local)                          |

El script de arranque global `iniciar-asai.sh` (ubicado en el escritorio) levanta todos estos componentes en el orden correcto.  
Si arrancas los servicios manualmente, el orden recomendado es: **PostgreSQL → Backend → N8N → Google-Alvi → Frontend**.

---

## Endpoints principales

| Método | Ruta                                       | Descripción                                |
|--------|--------------------------------------------|--------------------------------------------|
| POST   | `/api/v1/sessions/`                        | Crear sesión de auditoría                  |
| GET    | `/api/v1/sessions/{session_id}`            | Obtener sesión por ID                      |
| POST   | `/api/v1/evidencia/?session_id=`           | Subir archivo (PDF/DOCX/XLSX) → despacha a N8N |
| POST   | `/api/v1/chat/`                            | Enviar pregunta → despacha a N8N           |
| POST   | `/api/v1/webhook/evidence-uploaded`        | N8N notifica que procesó evidencia         |
| POST   | `/api/v1/webhook/chat-response`            | N8N devuelve respuesta RAG                 |

Los endpoints de webhook **siempre retornan 200** para que N8N no reintente.

---

## Flujo de request

1. El cliente (test dashboard u otra UI) hace `POST /api/v1/evidencia/` o `POST /api/v1/chat/`.
2. El service valida los datos, guarda en la base de datos con `status="processing"` y dispara el webhook correspondiente hacia N8N.
3. N8N ejecuta el flujo (consulta PostgreSQL, llama a Gemini con File Search, etc.) y luego responde llamando al webhook de retorno (`/webhook/evidence-uploaded` o `/webhook/chat-response`).
4. FastAPI matchea por `request_id`, actualiza la base de datos y retorna `{"received": true}`.

> Si N8N no está disponible durante el desarrollo, los endpoints del backend **no fallan**: guardan en base de datos y devuelven una respuesta placeholder.

---

## Webhooks N8N ↔ FastAPI

| Dirección         | Endpoint                                          |
|-------------------|---------------------------------------------------|
| N8N → FastAPI     | `POST /api/v1/webhook/evidence-uploaded`          |
| N8N → FastAPI     | `POST /api/v1/webhook/chat-response`              |
| FastAPI → N8N     | `POST {N8N_BASE_URL}/webhook/upload-evidence`     |
| FastAPI → N8N     | `POST {N8N_BASE_URL}/webhook/chat-query`          |

---

## Configuración de N8N y flujos versionados

La carpeta `flujosn8n/` (en la raíz de este repositorio) contiene los workflows exportados como JSON.  
Cada desarrollador debe importarlos manualmente en su instancia local de N8N y luego activarlos uno a uno.

### Credenciales necesarias en N8N

Antes de usar los flujos, crea dos credenciales en N8N (**Settings → Credentials**):

1. **PostgreSQL**
   - Host: `localhost`
   - Puerto: `5432`
   - Base de datos: `auditores_digitales_db`
   - Usuario: `postgres`
   - Password: la misma del archivo `.env` del backend
   - Nombre sugerido: `PostgreSQL ASAI Local`

2. **Google Gemini(PaLM) Api**
   - API Key: tu clave de Google AI Studio
   - Nombre sugerido: `Google Gemini ASAI`

Después de importar un flujo, asegúrate de asignar estas credenciales en los nodos correspondientes (Postgres y Google Gemini).

---

## Estructura del repositorio

```text
auditores-digitales-backend/
├── main.py                        # Punto de entrada alternativo (uvicorn)
├── requirements.txt
├── flujosn8n/                     # Workflows de N8N versionados (JSON)
├── app/
│   ├── main.py                    # FastAPI app, lifespan, CORS, routers
│   ├── config.py                  # Settings (pydantic-settings, .env)
│   ├── database.py                # Engine SQLAlchemy, SessionLocal, get_db()
│   ├── api/v1/
│   │   ├── dependencies.py        # get_db
│   │   └── endpoints/
│   │       ├── sessions.py
│   │       ├── evidencia.py
│   │       ├── chat.py
│   │       └── webhooks.py
│   ├── core/
│   │   ├── constants.py           # Extensiones permitidas, tamaño máximo
│   │   ├── exceptions.py          # Excepciones de dominio
│   │   └── security.py            # JWT/auth (fase futura)
│   ├── models/                    # ORM SQLAlchemy
│   │   ├── session.py
│   │   ├── chat_history.py
│   │   ├── evidence.py
│   │   └── audit_log.py
│   ├── schemas/                   # Pydantic v2
│   ├── services/                  # Lógica de negocio
│   ├── repository/                # Acceso a datos
│   └── utils/
├── tests/
│   ├── unit/
│   └── integration/
└── n8n-workflows/                 # (legado) flujos de ejemplo o de versiones anteriores
```

---

## Testing

```bash
pytest                      # todos los tests
pytest tests/unit           # solo unit
pytest tests/integration    # solo integration
```