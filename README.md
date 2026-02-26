# miniface backend (FastAPI + Supabase)

Backend base para **miniface** usando:

- FastAPI
- Uvicorn
- SQLAlchemy
- psycopg2-binary (PostgreSQL)
- python-multipart (subida de imágenes)
- passlib (hash de contraseñas)
- python-jose (JWT)
- Base de datos en Supabase (PostgreSQL)

## 1) Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Variables de entorno

```bash
cp .env.example .env
```

Completa `.env` con la URL de conexión de Supabase y una `SECRET_KEY` segura.

## 3) Correr el servidor

```bash
uvicorn app.main:app --reload
```

## 4) Endpoints

- `GET /health`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/users/me` (Bearer token)
- `POST /api/posts` (form-data: `content` + opcional `image`)
- `GET /api/posts`

Swagger:

- `http://127.0.0.1:8000/docs`

## 5) Notas sobre Supabase

- Usa la **Connection string** del proyecto (Database → Connection string).
- En producción evita usar el usuario `postgres` y rota credenciales periódicamente.
- Este proyecto crea tablas al iniciar (`Base.metadata.create_all`). Para producción real, migra con Alembic.
