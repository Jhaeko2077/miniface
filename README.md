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

Ejemplo mínimo:

```env
DATABASE_URL=postgresql+psycopg2://postgres:tu_password@db.tu-proyecto.supabase.co:5432/postgres
SECRET_KEY=pon_una_clave_larga_y_dificil
```

Si ves un error diciendo que faltan `database_url` o `secret_key`, significa que `.env`
no existe o está incompleto.

## 3) Correr el servidor

```bash
uvicorn app.main:app --reload
```

## 4) Interfaz gráfica (`miniface.html`)

Con esta versión, la interfaz ya se sirve desde FastAPI.

1. Levanta el backend:
   ```bash
   uvicorn app.main:app --reload
   ```
2. Abre en tu navegador:
   - `http://127.0.0.1:8000/`
   - o `http://127.0.0.1:8000/miniface.html`
3. En el panel izquierdo de la interfaz:
   - Registra usuario (`email`, `username`, `password`).
   - Inicia sesión (`email`, `password`).
   - Publica texto o imagen (usa `/api/posts`).

La UI consume estos endpoints del backend:
- `POST /api/auth/register`
- `POST /api/auth/token`
- `GET /api/users/me`
- `GET /api/posts`
- `POST /api/posts`
- `DELETE /api/posts/{post_id}`

## 5) Endpoints

- `GET /health`
- `POST /api/auth/register`
- `POST /api/auth/token` (OAuth2 Password Flow, form-data: `username`=email + `password`)
- `GET /api/users/me` (Bearer token)
- `POST /api/posts` (form-data: `content` + opcional `image`)
- `GET /api/posts`

Swagger:

- `http://127.0.0.1:8000/docs`
- Usa el botón **Authorize** y pega el email en `username` (estándar OAuth2).

## 6) Notas sobre Supabase

- Usa la **Connection string** del proyecto (Database → Connection string).
- En producción evita usar el usuario `postgres` y rota credenciales periódicamente.
- Este proyecto crea tablas al iniciar (`Base.metadata.create_all`). Para producción real, migra con Alembic.

## 7) Deploy en Railway

Este repositorio ya incluye configuración para Railway:

- `railway.toml` con comando de arranque y healthcheck.
- `Procfile` como fallback para plataformas compatibles.

### Variables en Railway

Configura estas variables en **Railway → Variables**:

- `DATABASE_URL`
- `SECRET_KEY`
- `ALGORITHM` (opcional, por defecto `HS256`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (opcional)
- `MEDIA_DIR` (opcional, por defecto `uploads`)

> Nota: Railway inyecta `PORT` automáticamente; el comando de arranque ya lo usa (`--port ${PORT:-8000}`).

### Pasos rápidos

1. Crea un proyecto en Railway y conecta este repo.
2. Añade las variables de entorno.
3. Haz deploy.
4. Verifica `GET /health` y luego abre `/docs`.

