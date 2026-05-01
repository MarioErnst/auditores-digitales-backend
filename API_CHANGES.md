# API Changes — Sprint 1 Refactor
Fecha: 2026-04-30

---

## Campos renombrados en requests (lo que el frontend ENVÍA)

### `POST /api/v1/admin/documentos/` — multipart form

| Campo anterior | Campo nuevo |
|----------------|-------------|
| `descripcion`  | `description` |

**Antes:**
```
Content-Type: multipart/form-data

file=<archivo>
descripcion=Normativa IIA 2024
```

**Después:**
```
Content-Type: multipart/form-data

file=<archivo>
description=Normativa IIA 2024
```

---

## Campos renombrados en responses (lo que el frontend RECIBE)

### `GET /api/v1/evidencia/?session_id={id}` — lista de evidencias

| Campo anterior   | Campo nuevo             | Tipo                    |
|------------------|-------------------------|-------------------------|
| `document_name`  | `gemini_resource_name`  | `string \| null`        |
| `file_ref`       | `gemini_ref`            | `string \| null`        |
| _(no existía)_   | `updated_at`            | `string (ISO) \| null`  |

**Antes:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "session_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "filename": "informe_auditoria.pdf",
    "document_name": "files/abc123xyz",
    "store_name": "store_sesion_abc",
    "status": "indexed",
    "file_ref": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2026-04-30T10:00:00"
  }
]
```

**Después:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "session_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "filename": "informe_auditoria.pdf",
    "gemini_resource_name": "files/abc123xyz",
    "store_name": "store_sesion_abc",
    "status": "indexed",
    "gemini_ref": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2026-04-30T10:00:00",
    "updated_at": "2026-04-30T10:05:00"
  }
]
```

> **Nota sobre `updated_at`:** Los registros creados antes de esta migración pueden devolver `null`. Tratarlo como opcional.

---

### `POST /api/v1/admin/documentos/` — respuesta de upload de documento base

| Campo anterior | Campo nuevo   |
|----------------|---------------|
| `descripcion`  | `description` |

**Antes:**
```json
{
  "status": "indexed",
  "filename": "normativa_iia.pdf",
  "descripcion": "Normativa IIA 2024",
  "store": "store_base_principal",
  "timestamp": "2026-04-30T10:00:00"
}
```

**Después:**
```json
{
  "status": "indexed",
  "filename": "normativa_iia.pdf",
  "description": "Normativa IIA 2024",
  "store": "store_base_principal",
  "timestamp": "2026-04-30T10:00:00"
}
```

---

## Header nuevo requerido

Todos los endpoints de negocio requieren el header `X-API-Key`.

### Endpoints que SÍ requieren `X-API-Key`

| Método   | Endpoint                              |
|----------|---------------------------------------|
| `GET`    | `/api/v1/sessions/`                   |
| `POST`   | `/api/v1/sessions/`                   |
| `GET`    | `/api/v1/sessions/{session_id}`       |
| `PATCH`  | `/api/v1/sessions/{session_id}`       |
| `GET`    | `/api/v1/evidencia/`                  |
| `POST`   | `/api/v1/evidencia/`                  |
| `DELETE` | `/api/v1/evidencia/{evidence_id}`     |
| `POST`   | `/api/v1/chat/`                       |
| `GET`    | `/api/v1/chat/{request_id}`           |
| `POST`   | `/api/v1/admin/documentos/`           |

### Endpoints que NO requieren `X-API-Key`

| Método | Endpoint                                   | Razón |
|--------|--------------------------------------------|-------|
| `GET`  | `/`                                        | Health/info público |
| `GET`  | `/health`                                  | Health/info público |
| `POST` | `/api/v1/webhook/evidence-uploaded`        | Usa `X-N8N-Secret` (llamado por N8N, no por el frontend) |
| `POST` | `/api/v1/webhook/chat-response`            | Usa `X-N8N-Secret` (llamado por N8N, no por el frontend) |

### Cómo enviarlo

```http
GET /api/v1/sessions/ HTTP/1.1
Host: localhost:8000
X-API-Key: tu-clave-aqui
```

```js
// fetch
const res = await fetch('/api/v1/sessions/', {
  headers: { 'X-API-Key': API_KEY }
});

// axios
axios.get('/api/v1/sessions/', {
  headers: { 'X-API-Key': API_KEY }
});
```

Respuesta si la clave es incorrecta o está ausente:
```json
HTTP 401
{ "detail": "API key inválida o ausente" }
```

> **Modo desarrollo:** Si el servidor arranca con `APP_ENV=development` y sin `API_KEY` configurada, los endpoints responden igual que antes (sin bloquear). El servidor loguea un warning una vez al iniciar. Esto permite desarrollar sin configurar la key.

---

## Endpoints disponibles completos

```
GET    /api/v1/sessions/                              [X-API-Key]
POST   /api/v1/sessions/                              [X-API-Key]
GET    /api/v1/sessions/{session_id}                  [X-API-Key]
PATCH  /api/v1/sessions/{session_id}                  [X-API-Key]
GET    /api/v1/evidencia/                             [X-API-Key]
POST   /api/v1/evidencia/                             [X-API-Key]
DELETE /api/v1/evidencia/{evidence_id}                [X-API-Key]
POST   /api/v1/chat/                                  [X-API-Key]
GET    /api/v1/chat/{request_id}                      [X-API-Key]
POST   /api/v1/webhook/evidence-uploaded              [X-N8N-Secret]
POST   /api/v1/webhook/chat-response                  [X-N8N-Secret]
POST   /api/v1/admin/documentos/                      [X-API-Key]
GET    /                                              [abierto]
GET    /health                                        [abierto]
```

---

## Sin cambios (para confirmar al equipo front)

### Rutas — sin cambios
Ninguna URL cambió. Todos los paths son idénticos a antes.

### `POST /api/v1/sessions/` — sin cambios

Request:
```json
{ "audit_name": "Auditoría Q1 2026", "audit_id": null }
```
Response: igual que antes (`id`, `audit_id`, `audit_name`, `created_at`, `status`).

### `GET /api/v1/sessions/` — sin cambios

Response sigue siendo `{ "items": [...], "total": N }` con los mismos campos por item.

### `GET /api/v1/sessions/{session_id}` y `PATCH /api/v1/sessions/{session_id}` — sin cambios

Request del PATCH: `{ "audit_name": "Nuevo nombre" }` — igual que antes.

### `POST /api/v1/evidencia/` — sin cambios

Request (multipart): `file` + `session_id` query param — igual que antes.

Response:
```json
{
  "status": "processing",
  "session_id": "...",
  "request_id": "...",
  "filename": "informe.pdf"
}
```

### `DELETE /api/v1/evidencia/{evidence_id}?session_id={id}` — sin cambios

Response: `{ "deleted": true, "filename": "informe.pdf" }` — igual que antes.

### `POST /api/v1/chat/` — sin cambios

Request: `{ "question": "¿Qué dice el informe?", "session_id": "..." }` — igual.

Response (202):
```json
{ "request_id": "...", "session_id": "...", "status": "processing" }
```

### `GET /api/v1/chat/{request_id}` — sin cambios

Response:
```json
{
  "status": "ready",
  "answer": "El informe indica...",
  "sources": [{ "texto": "...", "store": "...", "pagina": 1, "titulo": "..." }]
}
```
o `{ "status": "pending" }` si N8N aún no respondió.

---

## Notas de migración

Pasos en orden para el dev de frontend:

**1. Agregar el header `X-API-Key` a todas las llamadas protegidas**

Configurarlo una sola vez en el cliente HTTP (axios instance, fetch wrapper, etc.):
```js
// Leer la clave desde variable de entorno
const API_KEY = import.meta.env.VITE_API_KEY;

// Axios: agregar a la instancia base
axiosInstance.defaults.headers.common['X-API-Key'] = API_KEY;
```

Agregar `VITE_API_KEY=<clave>` al `.env` del frontend.
Pedir la clave al equipo de backend.

**2. Renombrar `document_name` → `gemini_resource_name` en la vista de lista de evidencias**

Buscar en el código frontend dónde se usa `evidence.document_name` o `.document_name` y reemplazar por `.gemini_resource_name`. Este campo se usa típicamente para mostrar un identificador interno o para operaciones de borrado. Si no se muestra en la UI, el único impacto es si el frontend lo pasa a alguna operación.

**3. Renombrar `file_ref` → `gemini_ref` en la vista de lista de evidencias**

Mismo proceso: buscar `.file_ref` en el código frontend y reemplazar por `.gemini_ref`.

**4. Agregar soporte para `updated_at` en la lista de evidencias (opcional)**

El campo `updated_at` ahora viene en cada item. Si la UI muestra una fecha de última actualización, puede usarse. Tratar como `string | null` ya que registros viejos pueden traer `null`.

**5. Renombrar el campo del form en el upload de documento base**

Si el frontend tiene un formulario que llama a `POST /api/v1/admin/documentos/`:
```js
// Antes
formData.append('descripcion', texto);

// Después
formData.append('description', texto);
```

Y actualizar el parsing de la response: `.descripcion` → `.description`.

**6. Verificar en desarrollo sin key antes de configurar**

En entorno de desarrollo con `APP_ENV=development` el servidor no bloquea aunque no se envíe `X-API-Key`. Útil para verificar que los pasos 2-5 funcionan antes de agregar la key.
