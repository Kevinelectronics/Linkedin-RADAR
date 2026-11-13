# Publicación en LinkedIn vía Zernio

Kevin aprueba cada post en el radar (pestaña «Para ti» → «Aprobar y programar», con fecha y hora). Esta rutina **solo** envía a Zernio los drafts que él ha aprobado. Nunca publicar, programar ni editar en LinkedIn nada que no tenga `linkedin.state == "approved"` puesto por Kevin desde el radar.

Radar: <YOUR_RADAR_ARTIFACT_URL> (colección `drafts`).
Script: `python scripts/zernio.py` (ver su docstring). Lee solo las claves `ZERNIO_API_KEY` y `ZERNIO_ACCOUNT_ID` de las variables de usuario de Windows: **no las cargues con `$env:` antes**. Ejecuta siempre el script como un comando suelto que empiece por `python scripts/zernio.py` (sin `;` ni nada delante): así lo cubre la regla de permiso del proyecto y la tarea no se queda parada.
Si falta alguna, no hacer nada y avisar a Kevin en el resumen.

## Configuración inicial (una vez, la hace Kevin)

1. Crear cuenta en https://zernio.com/signup (gratis hasta 2 cuentas, sin tarjeta).
2. En el panel de Zernio, conectar su perfil personal de LinkedIn.
3. Crear una API key en https://zernio.com/dashboard/api-keys y guardarla en Windows como variable de usuario `ZERNIO_API_KEY` (nunca pegarla en el chat).
4. Ejecutar `python scripts/zernio.py accounts` y guardar el `_id` de su cuenta de LinkedIn como variable de usuario `ZERNIO_ACCOUNT_ID`.

## Pasos de cada ejecución

1. Leer todos los drafts con `linkedin.state` en `approved` o `cancel_requested`, y los `scheduled` cuya fecha ya pasó.
2. **approved** →
   - Si `linkedin.now == true` (botón «Publicar ahora»): publicar en esta ejecución con `--now` en lugar de `--at`, siempre que la aprobación (`approvedAt`) sea de hace menos de 24 horas; si es más antigua, marcar `failed` con "Aprobación caducada: vuelve a pulsar Publicar ahora". Con `--now` Zernio devuelve el post ya publicado: guardar directamente `state:"published"`, `url`, `publishedAt` y en el draft `status:"published"` + `publishedAt`.
   - Si no: comprobar que la fecha (`linkedin.at`, zona `linkedin.tz`) es futura o de hace menos de 1 hora; si es más antigua, marcar `failed` con error "La fecha ya pasó: elige otra" y no publicar.
   - Guardar `text` en un archivo UTF-8 temporal en `data/tmp/`.
   - Si tiene `videoUrl` (MP4 animado), descargar `videoAssetId` y pasar `--video`.
   - Si tiene `pdfUrl`, descargar ese asset del radar (Artifact read con `path` = id del asset) y pasar `--pdf` con `--title` (título corto del carrusel). Si no, descargar `imageAssetId` y pasar `--image`.
   - `python scripts/zernio.py post --text-file <txt> [--image|--pdf ...] --at <linkedin.at> --tz <linkedin.tz> --key <id del draft>`.
   - Si responde bien: `linkedin = {state:"scheduled", at, tz, zernioPostId, sentAt}`. Si falla: `state:"failed"` con `error` legible (en español) y sumar 1 a `attempts`. El script se niega a enviar textos con huecos `[ ]`: en ese caso marcar `failed` con "Rellena los huecos del texto".
3. **cancel_requested** → `python scripts/zernio.py cancel <zernioPostId>` y poner `state:"cancelled"`.
4. **scheduled con fecha pasada** → `python scripts/zernio.py status <zernioPostId>`. Si está publicado: `linkedin.state:"published"`, `linkedin.url` (platformPostUrl), `linkedin.publishedAt`, y además `status:"published"` y `publishedAt` (fecha) en el draft para el banco de ideas. Si falló: `state:"failed"` con el error.
5. Usar siempre `update` con `if_version` sobre el draft; no tocar ningún otro campo.
6. Resumen en español de 2 líneas: qué se programó (fecha y hora), qué se publicó (con enlace) y qué falló.
