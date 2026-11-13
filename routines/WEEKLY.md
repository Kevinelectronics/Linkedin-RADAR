# Rutina semanal: radar de oportunidades (lunes 8:00)

Objetivo: dejar en la pestaña **Oportunidades** del radar las 10–15 mejores oportunidades de la semana para que Kevin venda sus servicios de technical writing / copywriting (APIs, datos financieros, scraping, IA, dev tools). Nunca contactar a nadie ni publicar nada: solo encontrar, verificar y priorizar.

Radar: <YOUR_RADAR_ARTIFACT_URL> (colecciones `posts` con kind "opp", `votes`, documento `profile/opps`).
Token: variable de entorno APIFY_TOKEN. Actor de Apify: harvestapi~linkedin-post-search (máx. 10 authorUrls por ejecución; el filtro authorsCompanies necesita searchQueries y no funciona junto a authorKeywords).

## Pasos

1. **Aprender.** Leer `votes` de oportunidades (v y `reasons`) y actualizar `profile/opps`: qué tipos de empresa, roles, sectores, modalidades e idiomas le interesan y por qué descarta. Aplicarlo como filtro y para puntuar.
2. **Personas a seguir** (`config/people.json`). Traer sus posts de la última semana (authorUrls, postedLimit "week"). Buscar señales: contratación de contenido/DevRel/writers, lanzamientos, documentación nueva, quejas sobre contenido o docs, peticiones de recomendaciones. Guardar como oportunidad (`signal: "persona"`) solo si hay una señal clara.
3. **Búsqueda en LinkedIn (Apify).** searchQueries de contratación: "hiring technical writer", "looking for a technical writer", "freelance technical writer", "developer content writer", "looking for a content writer SaaS", "devrel content", "API documentation writer"; postedLimit "week", **sin** scrapeComments en la búsqueda general (los comentarios se piden después solo para las 5 mejores, maxComments 15). Descartar: quien busca empleo ("open to work", "seeking", "available for", "estou em busca", "busco empleo"), autopromoción de writers, agregadores de empleo, roles presenciales fuera de remoto.
4. **Google sobre LinkedIn (SerpApi, conector SearchApi).** `site:linkedin.com/posts` con las mismas frases y `tbs=qdr:w`. Quedarse solo con enlaces `linkedin.com/posts/...`, no duplicar lo del paso 3.
5. **Comentarios.** Solo en las **5 mejores** (ahorro de Apify, 2026-11-03), mirar los comentarios: cuántos writers se han ofrecido (competencia), si el autor da detalles, y si otros comentaristas buscan lo mismo (nuevas oportunidades).
6. **Programas pagados** (solo el primer lunes del mes): revisar `config/paid-programs.json` si existe y comprobar que siguen activos.
7. **Enriquecer** cada oportunidad que pase el filtro con SerpApi: web de la empresa, ronda reciente, si tiene blog/docs y su calidad, tamaño.
8. **Puntuar 0–100** (encaje con su nicho + urgencia + accesibilidad del decisor + baja competencia) y escribir en `posts` (kind "opp") con: role, company, author, headline, url, date, fit (alta/media/baja), score, signal ("contratando" | "persona" | "programa"), competition (nº de writers en comentarios), why, angle (cómo venderle, concreto), lang, batch (fecha del lunes). Marcar las oportunidades de semanas anteriores sin voto como `stale: true` en lugar de borrarlas.
9. Terminar con un resumen en español de 3 líneas: nº de oportunidades, la mejor y por qué, y una cosa aprendida de sus votos.
