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
- `N8N_BINARY_DATA_ROOT` (opcional, ruta local al storage de binarios de n8n cuando recibes `filesystem-v2:*`)

> Recomendación: usa una clave larga en `N8N_API_KEY` (mínimo 32 caracteres).

---

## 2) Endpoint para n8n

La API expone este endpoint:

- `POST /api/automation/n8n/posts`

### Header obligatorio

- `X-N8N-KEY: <tu N8N_API_KEY>`

### Body soportado

Puedes enviar **uno de estos formatos**:

1. `multipart/form-data`
   - `content` (requerido): texto del post.
   - `image` (opcional): archivo de imagen.
   - `author_email` (opcional): correo del autor.

2. `application/json`
   - `content` (requerido): texto del post.
   - `author_email` (opcional): correo del autor.
   - `image_base64` (opcional): imagen en base64 (puro o data URL).
   - `image_filename` (opcional): nombre sugerido para extensión de archivo.
   - `image_binary` (opcional): objeto binario de n8n (ej. `mimeType`, `fileName`, `fileExtension`, `id`, `data`).

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
   - Send Body: `JSON` (recomendado para evitar problemas de serialización)
     - `content`: `{{ $json.content }}`
     - `author_email`: `{{ $json.author_email }}` (opcional)
     - `image_base64`: `{{ $json.image_base64 }}` (opcional)
     - `image_filename`: `{{ $json.image_filename }}` (opcional)

   > Si la imagen viene de una propiedad binaria de n8n, usa el campo `.data` (base64 puro), por ejemplo:
   > - `image_base64`: `{{ $binary.imagen.data }}`
   > - `image_filename`: `{{ $binary.imagen.fileName }}`
   >
   > No envíes el objeto binario completo (`{{ $binary.imagen }}`), solo su propiedad `data`.

   > Si quieres enviar archivo binario directo, también funciona `Form-Data`.

   > Si tu nodo devuelve solo metadatos como `{ mimeType, fileType, fileExtension, fileName, id, bytes }`,
   > envía ese objeto en `image_binary`. La API intentará resolver la imagen así:
   > 1) usando `image_binary.data` si viene en base64, o
   > 2) leyendo `image_binary.id` (`filesystem-v2:*`) desde `N8N_BINARY_DATA_ROOT`.

Activa el workflow y valida que retorne `201`.

---

## 4) Desplegar a producción gratis con Render

Este repo incluye `render.yaml`, así que el despliegue es casi automático.

### Pasos

1. Sube el repo a GitHub.
2. Entra a Render y crea un **New Web Service** conectado al repo.
3. Render detectará `render.yaml`.
4. En variables de entorno, completa:
   - `PYTHON_VERSION=3.12.8`
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `N8N_API_KEY`
   - `N8N_DEFAULT_AUTHOR_EMAIL` (opcional)
5. Deploy.

> Si no fijas la versión de Python, Render puede usar 3.14 por defecto y algunas combinaciones de dependencias pueden fallar al iniciar la app.

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
  -F "image=@/ruta/a/tu/imagen.png"
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
