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
| `/api/activities` | GET | Listar actividades |
| `/api/activities/{id}` | GET | Detalle de actividad |
| `/api/stats` | GET | Estadísticas generales |

## Variables de Entorno

### Backend (.env)
```
STRAVA_CLIENT_ID=tu_client_id
STRAVA_CLIENT_SECRET=tu_client_secret
SECRET_KEY=tu_secret_key_seguro
DEBUG=false
```

**Requisitos de seguridad**
- `SECRET_KEY` es obligatorio y debe ser un valor seguro (no uses el placeholder del `.env.example`).
- `STRAVA_CLIENT_SECRET` es obligatorio y la API fallará al iniciar si falta.
- Mantén `DEBUG=false` en entornos no locales.

## Licencia

MIT
