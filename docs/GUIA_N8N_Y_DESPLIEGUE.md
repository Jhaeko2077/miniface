# Guía simple: automatizar publicaciones con n8n + despliegue gratis en producción

Este documento explica **paso a paso** cómo:

1. Conectar `miniface` con **n8n** para crear publicaciones automáticas.
2. Desplegar la API en producción usando **Render (plan free)**.

---

## 1) Preparar variables de entorno

Define estas variables en tu entorno local y en producción:

- `DATABASE_URL`
- `SECRET_KEY`
- `N8N_API_KEY` (clave secreta que usará n8n en el header `X-N8N-KEY`)
- `N8N_DEFAULT_AUTHOR_EMAIL` (opcional, correo del usuario que firmará publicaciones automáticas)

> Recomendación: usa una clave larga en `N8N_API_KEY` (mínimo 32 caracteres).

---

## 2) Endpoint para n8n

La API expone este endpoint:

- `POST /api/automation/n8n/posts`

### Header obligatorio

- `X-N8N-KEY: <tu N8N_API_KEY>`

### Body (form-data)

Campos:

- `content` (obligatorio): texto del post.
- `image` (opcional): archivo de imagen.
- `author_email` (opcional): correo del autor; si no se envía, usa `N8N_DEFAULT_AUTHOR_EMAIL`.

Este formato permite usar el botón de carga de archivo directamente en Swagger UI, igual que `POST /api/posts`.

### Respuesta esperada

- `201 Created` con el post creado.

---

## 3) Flujo recomendado en n8n (sin código)

Crea un workflow con estos nodos:

1. **Trigger** (Cron, Webhook o el que prefieras)
2. **Set**
   - Campo `content`: texto que quieras publicar.
   - Campo `author_email`: correo del usuario dueño del post.
3. **HTTP Request**
   - Method: `POST`
   - URL: `https://TU_API/api/automation/n8n/posts`
   - Send Headers:
     - `X-N8N-KEY`: `{{ $env.N8N_API_KEY }}` o valor fijo secreto
   - Send Body: Form-Data
     - `content`: `{{ $json.content }}`
     - `author_email`: `{{ $json.author_email }}` (opcional)
     - `image`: archivo binario (opcional)

Activa el workflow y valida que retorne `201`.

---

## 4) Desplegar a producción gratis con Render

Este repo incluye `render.yaml`, así que el despliegue es casi automático.

### Pasos

1. Sube el repo a GitHub.
2. Entra a Render y crea un **New Web Service** conectado al repo.
3. Render detectará `render.yaml`.
4. En variables de entorno, completa:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `N8N_API_KEY`
   - `N8N_DEFAULT_AUTHOR_EMAIL` (opcional)
5. Deploy.

### Verificación

- Salud: `GET https://TU_API/health`
- Docs: `GET https://TU_API/docs`

---

## 5) Prueba rápida con cURL

```bash
curl -X POST "https://TU_API/api/automation/n8n/posts" \
  -H "X-N8N-KEY: TU_N8N_API_KEY" \
  -F "content=Hola desde una automatización" \
  -F "author_email=autor@tu-dominio.com" \
  -F "image=@/ruta/local/imagen.png"
```

---

## 6) Errores comunes

- `401 Invalid n8n key`: el header `X-N8N-KEY` no coincide.
- `404 Author user not found`: no existe ese email en la base de datos.
- `400 author_email is required...`: faltó `author_email` y no hay `N8N_DEFAULT_AUTHOR_EMAIL`.
- `503 N8N integration is not configured`: falta `N8N_API_KEY` en variables.

---

## 7) Recomendaciones de seguridad

- Nunca publiques `N8N_API_KEY` en frontend.
- Guarda secretos en variables de entorno de n8n/Render.
- Rota `N8N_API_KEY` periódicamente.
