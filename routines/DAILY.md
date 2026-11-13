# Rutina diaria: post de LinkedIn para Kevin

Instrucciones para la tarea programada (7:00). Objetivo: dejar en el radar **2 versiones en inglés** de un post (texto + imagen) inspirado en las ideas virales, y aprender de lo que Kevin elige.

Radar: <YOUR_RADAR_ARTIFACT_URL>
Colecciones de la base de datos del radar: `posts` (ideas virales y oportunidades), `votes` (sus me gusta: v 1/2/-1 y aspects hook|texto|visual), `drafts` (posts generados: date, variant A/B, text, imageUrl, pattern, inspiredBy, status pending|chosen|rejected|not_chosen, feedback), `profile/style` (lo aprendido).

## Pasos


1. **Aprender.** Leer `votes`, `drafts` (status y feedback) y `profile/style`. Actualizar `profile/style` con: hooks, formatos, creadores, temas y tipos de imagen que Kevin elige o descarta, y sus comentarios de "¿Qué cambiarías?". Las versiones elegidas pesan más que los me gusta; las rechazadas y su feedback indican qué evitar.
2. **Traer ideas nuevas: solo lunes y jueves** (ahorro de Apify, decidido por Kevin el 2026-11-03: el plan gratuito da $5/mes). Los demás días, saltar este paso y trabajar con los posts que ya hay en el radar y en `data/raw/`. Lunes y jueves: `python scripts/fetch_creators.py week` (necesita APIFY_TOKEN; cargarlo en PowerShell con `$env:APIFY_TOKEN=[Environment]::GetEnvironmentVariable("APIFY_TOKEN","User")`). Los posts nuevos con buen engagement entran en `posts` (kind "viral") con niche, hookType, why e idea, como los existentes. Descargar sus imágenes y subirlas como asset del radar para guardarlas en `imageUrl`. Ver las imágenes de los posts que Kevin guardó o marcó con "visual".
3. **Elegir los temas del día.** No hablar siempre de datos financieros. Rotar entre estos temas (A y B, temas distintos entre sí):
   - **AI agents y MCP**: cómo funcionan, casos reales, errores comunes.
   - **Claude Code**: tips, flujos de trabajo, skills, cómo usarlo mejor.
   - **Web scraping**: técnicas, herramientas, anti-bot, casos de uso.
   - **Listas de herramientas**: «11 tools for X» (scraping, agentes, escritura técnica, datos…).
   - **Repo de GitHub destacado**: qué hace, por qué importa y cómo empezar.
   - **Datos financieros y APIs**: el nicho original, pero como un tema más.
   - **Experiencia personal**: carrera de technical writer, freelance, clientes, aprendizajes.
   - **Tips de escritura técnica y contenido**.

   No repetir un tema en los últimos 3 días ni un patrón en los últimos 5. Dar más peso a los temas y patrones que Kevin elige (ver `profile/style`) sin dejar de probar los demás de vez en cuando.
   - Herramientas y repos: **verificar que existen** (buscar con SerpApi o en GitHub), enlazarlos y no inventar estrellas, precios ni funciones.
   - Experiencia personal: escribir la estructura y el hook, y dejar `[tu experiencia aquí: …]` con una pista de qué contar. Nunca inventar la anécdota.
4. **Escribir 2 versiones en inglés** con la skill linkedin-viral-post, con patrones distintos (ej. A = opinión/historia, B = concepto/lista con diagrama), priorizando los patrones que `profile/style` dice que le gustan.
   - Nunca inventar experiencias personales de Kevin. Si el patrón lo pide, escribir en general o dejar `[tu experiencia aquí]`.
   - Nunca inventar el post de otra persona en una captura. Si el formato es "captura + opinión", citar un post real y enlazarlo.
5. **Generar la imagen** de cada versión con el motor HTML: `python scripts/render.py spec.json salida.png` (o `.pdf` para carruseles). Plantillas en `templates/` (ejemplos en `examples/*.json`):
   - `flow`: diagrama de flujo con Mermaid (agentes, pipelines, arquitecturas).
   - `sketch`: estilo dibujado a mano tipo Excalidraw (procesos, ideas personales).
   - `code`: captura de código tipo Carbon (tips de Python, Claude Code, APIs).
   - `chart`: gráfico con Chart.js; **solo con datos reales y con fuente**. Estilo que gusta a Kevin (2026-11-04, ver `examples/chart_nvda.json`): `titleParts` con un giro en verde («NVIDIA didn't crash 90%. **Your data did.**»), `annotation` sobre el evento clave, `xTicks` que incluyan la fecha del evento, 2 `metrics` grandes en contraste (rojo/verde) y `source` en dos líneas. Datos de mercado reales: conector FMP (`chart`) o EODHD.
   - `list`: lista tipo «11 tools for X».
   - `versus`: contraste A vs B.
   - `hub`: hub central con herramientas alrededor (estilo «Top APIs for X», le encanta a Kevin): ideal para listas de herramientas, integraciones y ecosistemas.
   - `stack`: «caos vs sistema» con **logos reales de apps** (estilo del post «Design 2025 vs Design 2026» de Charlie Hills, que encanta a Kevin, 2026-11-04; referencia `data/ref_charlie_ai_os.jpg`, ejemplo `examples/stack.json`). Izquierda: apps desordenadas y giradas; derecha: ventana de repo con árbol (CLAUDE.md, skills/, herramientas conectadas con bandejas de logos). Ideal para «mi stack antes vs ahora», flujos con Claude Code y listas de herramientas. Logos: `logo:<nombre>` (gilbarbara/logos), `si:<slug>` (Simple Icons), `fav:<dominio>` (favicon de cualquier web, p. ej. `fav:eodhd.com`). Comprobar en el render que ningún logo sale vacío o como texto. **Versión animada para LinkedIn** (MP4 1920x1080, ~10 s): `python scripts/render_video.py spec.json salida.mp4 --music auto` (música de fondo muy suave y libre de derechos, generada por `scripts/make_music.py`; a Kevin le gusta así, 2026-11-04); subirla como asset y guardar `videoUrl`/`videoAssetId` en el draft (además de la imagen estática en `imageUrl`).
   - **Logos reales > emojis** cuando se nombran productos o empresas: usar `logo:`/`si:`/`fav:` también en `hub`, `list` y `carousel` (los acepta cualquier plantilla que use `logo()`; si no, `fluent:`).
   - **Catálogo de formatos virales** (pestaña «Formatos» del radar, colección `formats`; pedido por Kevin el 10/11): elegir la tipología antes que la plantilla y **rotar familias** (ecosistemas, antes/después, sistemas, datos, listas) sin repetir familia en 3 días. Plantillas nuevas:
     - `wheel`: rueda/ruleta de un stack por categorías alrededor de un núcleo (ref. Maja Voje). En vídeo gira como una ruleta y se para en `pointerTo`.
     - `landscape`: mapa por capas, «N herramientas en M capas» (ref. AEO Landscape). Muy guardable para las categorías de los listicles.
     - `bento`: «el sistema detrás de…» con tarjetas de pasos, cifras, flujos y viñetas (ref. Charlie Hills).
     - `demo` (vídeo 16:9, `"size": "landscape"`): demo animada de una función de un SaaS/API (ref. Scrapingdog). Es un servicio para clientes; en posts propios, solo con productos reales que Kevin use o con permiso del cliente.
     - `datastory` (vídeo 16:9, **pendiente de plantilla**): historia con datos estilo informe editorial (ref. Corey Haines, /reverse-engineer-marketing, `data/refs/corey_reverse/`): cifra que cuenta → comando → gráfico de línea que se dibuja → eventos fechados sobre la curva → conclusión en rojo con tarjeta de evidencia → CTA. Ideal con precios reales de EODHD (resultados, splits, dividendos marcados). Kevin lo pidió el 2026-11-12.
    Las imágenes `stack`, `wheel`, `landscape` y `bento` tienen versión vídeo: `python scripts/render_video.py spec.json salida.mp4 --music auto`. Cuando Kevin mande un ejemplo nuevo, añadirlo como referencia en `formats` (y como tipología «pendiente» si no encaja en ninguna).
   - `carousel`: carrusel PDF (5–8 slides) para posts tipo guía o tips. Estilo que gusta a Kevin (2026-11-04, ver `examples/carousel_tools.json`): portada `cover` con rejilla de iconos 3D, slides `tool` con 1–2 tarjetas (icono, qué hace en ≤8 palabras, qué reemplaza tachado, comando) y cierre `cta` con pregunta; evitar slides `point` de solo texto. Generar el PDF y también un PNG de la portada (spec con solo la primera slide y la plantilla `carousel`, o `list`/`flow` como portada); subir ambos y guardar `imageUrl` (portada) y `pdfUrl` en el draft.
   - El antiguo `scripts/render_image.py` (PIL) queda solo como respaldo.
   - **Marca personal** (Kevin, 2026-11-04): todas las plantillas llevan en el pie su foto en círculo y `kevinmeneses.com` en una píldora verde; sale sola de `config/brand.json` + `assets/avatar.jpg` vía `footer()`. No quitarla.
   - **EODHD es el proveedor de datos principal**: cuando un post o carrusel toque APIs o datos de mercado, el ejemplo apunta a EODHD (en `carousel`, campo `source` de la slide `tool`), con su enlace de afiliado en el texto y tono de «yo lo uso».
   Revisar la imagen antes de subirla (que no haya texto cortado). Para fotos o ilustraciones usar el conector de Runway.
   - **Tamaño: 1920x1080 (16:9) siempre** (Kevin, 2026-11-11: LinkedIn le recortaba arriba las 1080x1350, p. ej. el título del post «financial data stack»). `render.py` ya lo usa por defecto; no pongas `"size": "portrait"` salvo que Kevin lo pida. Al diseñar, piensa en horizontal: contenido en columnas/filas anchas, título de una línea si cabe, y revisa el render a tamaño real.
   - **Más visual, menos texto** (Kevin, 2026-11-04: las columnas de texto «no le gustan del todo»). Cada elemento de la imagen lleva un icono y como mucho ~5 palabras; el mensaje tiene que entenderse sin leer (posición, color, tamaño, una métrica grande). En `versus`, usar `items` con icono + etiqueta corta, `mark` para destacar el momento clave y `metric` con un número/dato grande (ver `examples/versus.json`), nunca listas de frases largas.
   - La imagen tiene que **aportar algo visual** (contraste, diagrama, lista, dato destacado), nunca repetir el texto del post. No usar `card` (tarjeta blanca de texto) salvo que el formato sea "captura de un post real + opinión": a Kevin le pareció que no había imagen.
   - Cada versión con un tipo de imagen distinto.
6. **Publicar en el radar.** Subir las imágenes como assets del radar y escribir los 2 documentos en `drafts` con id **único** `<YYYY-MM-DD>-<HHMM>-A` / `<YYYY-MM-DD>-<HHMM>-B` (hora local de la ejecución), campos `date`, `createdAt`, `variant` y status "pending". **Antes de escribir, comprobar con `get` que el id no existe**; usar siempre `set` solo sobre ids nuevos y nunca tocar drafts existentes (el 2026-10-30 una ejecución sobrescribió dos ideas de Kevin por reutilizar el id).
7. **No publicar nunca en LinkedIn.** Kevin revisa, elige y publica.

## Formato del texto

LinkedIn no admite Markdown. En `text` usar `**negrita**` solo en frases cortas clave (el radar las convierte en negrita Unicode al copiar). No usar `#` títulos, `*cursiva*`, tablas ni bloques de código; para listas, `→` o `-`.

### Enlaces (pedido por Kevin el 2026-11-03)

- **Cada enlace va justo debajo de lo que menciona**, en la línea siguiente, nunca agrupados al final en un bloque «Links:». Ejemplo:
  ```
  → Playwright MCP — drives a real browser through the accessibility tree.
  github.com/microsoft/playwright-mcp
  ```
- **EODHD siempre apunta a su web** (nunca al repo de GitHub) y lleva el enlace de afiliado de Kevin:
  `https://eodhd.com/?via=kmg&ref1=Meneses&utm_source=linkedin&utm_medium=post&utm_campaign=<slug-del-post>&utm_content=Meneses`
  - Para una página concreta, añadir la misma query: p. ej. el MCP de EODHD → `https://eodhd.com/financial-apis/mcp-server-for-financial-data-by-eodhd?via=kmg&ref1=Meneses&utm_source=linkedin&utm_medium=post&utm_campaign=<slug>&utm_content=Meneses`.
  - `<slug-del-post>`: tema corto en kebab-case (p. ej. `mcp-servers-list`).
  - **Sin cupones ni tono promocional** (Kevin, 2026-11-03): nada de KEVIN10, «10% off», «sign up now» ni «get started». El CTA se escribe como recomendación personal de quien lo usa: «I use EODHD for my backtests…», «This is the API I pull my data from», seguido del enlace en la línea siguiente.
  - Los enlaces a la documentación de EODHD pueden ir sin parámetros.

## Banco de ideas (pedido por Kevin el 2026-10-30)

- **Nunca borrar ni sobrescribir drafts antiguos.** Cada draft nuevo lleva `date` (YYYY-MM-DD, día de creación) y `createdAt` (ISO con hora). Los que Kevin no usa se quedan en el banco con su fecha.
- Kevin marca los que publica: `status: "published"` y `publishedAt` (fecha). Es la señal de aprendizaje **más fuerte** (más que "chosen"): esos temas, patrones y plantillas son los que de verdad usa.
- Al elegir temas, contar como "usados recientemente" los publicados (por `publishedAt`) y los generados de los últimos 3 días; no generar una idea casi igual a otra que ya está sin usar en el banco.
- **Aplicar su feedback.** Si un draft no publicado ni programado tiene `feedback` nuevo (distinto de `feedbackApplied`), aplicar ese cambio al `text` (y a la imagen si lo pide), guardar `feedbackApplied` = el texto del feedback y `editedAt`. Es la única modificación permitida sobre drafts existentes: no tocar nada más. Aplicar siempre las reglas de «Enlaces» (EODHD con afiliado, sin cupón, tono de «yo lo uso»).
- En el resumen final, decir cuántas ideas hay sin usar en el banco y cuál es la más antigua (con fecha), por si quiere rescatarla.
