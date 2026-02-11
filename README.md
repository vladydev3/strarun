# StraRun - Strava Dashboard

Monorepo para una aplicación web de visualización de datos y estadísticas de Strava.

## Estructura del Proyecto

```
strarun/
├── apps/
│   ├── frontend/          # Angular 20+ (Standalone Components)
│   └── backend/           # FastAPI (Python)
├── packages/              # Paquetes compartidos
├── .github/
│   └── skills/            # Copilot Skills
└── docs/                  # Documentación
```

## Tecnologías

### Frontend
- **Angular 20+** con Standalone Components
- **Signals** para state management reactivo
- **Angular Material** para UI components
- **Chart.js / ngx-charts** para visualizaciones

### Backend
- **FastAPI** (Python 3.11+)
- **Pydantic** para validación de datos
- **SQLAlchemy** para ORM (futuro)
- **Strava API** integration

## Inicio Rápido

### Backend (FastAPI)

```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

API disponible en: http://localhost:8000
Documentación: http://localhost:8000/docs

### Frontend (Angular)

```bash
cd apps/frontend
npm install
ng serve
```

Aplicación disponible en: http://localhost:4200

## API Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/auth/strava` | GET | Iniciar OAuth con Strava |
| `/api/auth/callback` | GET | Callback de OAuth |
| `/api/auth/token` | POST | Intercambiar code por tokens (setea cookies) |
| `/api/auth/refresh` | POST | Renovar tokens usando cookies (requiere CSRF) |
| `/api/auth/status` | GET | Estado de sesión actual |
| `/api/activities` | GET | Listar actividades |
| `/api/activities/{id}` | GET | Detalle de actividad |
| `/api/stats` | GET | Estadísticas generales |

## Variables de Entorno

### Backend (.env)
```
STRAVA_CLIENT_ID=tu_client_id
STRAVA_CLIENT_SECRET=tu_client_secret
SECRET_KEY=tu_secret_key
COOKIE_SECURE=true
ACCESS_TOKEN_COOKIE_NAME=strava_access_token
REFRESH_TOKEN_COOKIE_NAME=strava_refresh_token
CSRF_COOKIE_NAME=strava_csrf
REFRESH_COOKIE_MAX_AGE_DAYS=30
```

### Cookies y CSRF
- El backend escribe cookies `HttpOnly` y `Secure` para los tokens (`SameSite=Lax` para access y `SameSite=Strict` para refresh).
- Los endpoints que dependen de cookies (por ejemplo `/api/auth/refresh`) validan un token CSRF en el header `X-CSRF-Token` que coincide con la cookie `CSRF_COOKIE_NAME`.
- En desarrollo local sin HTTPS puedes configurar `COOKIE_SECURE=false` para permitir cookies en `http://localhost`.

## Licencia

MIT
