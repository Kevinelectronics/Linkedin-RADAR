"""Motor de imágenes para los posts de LinkedIn: plantilla HTML + especificación JSON -> PNG (o PDF para carruseles).

Uso:
  python scripts/render.py spec.json salida.png     # imagen
  python scripts/render.py spec.json salida.pdf     # carrusel (una página por slide)

La especificación lleva "template" (nombre de un archivo en templates/) y los datos que esa plantilla espera.
Formatos ("size"): landscape 1920x1080 (por defecto: así lo quiere Kevin para LinkedIn), portrait 1080x1350, square 1080x1080.
Opcional: "theme" (plex|geist|clash|jakarta, ver templates/themes.json) e iconos "fluent:Nombre" (Fluent Emoji 3D de Microsoft) o "lucide:nombre".
Plantillas: flow (Mermaid), sketch (estilo dibujado a mano con rough.js), code (captura de código tipo Carbon),
chart (Chart.js), versus, list, hub, stack (caos vs sistema con logos reales), wheel (rueda/ruleta), landscape (mapa por capas),
bento (panel del sistema), demo (vídeo de demo de producto, 16:9), carousel (PDF multipágina).
"""
import base64, json, os, sys
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, "templates")
SIZES = {"portrait": (1080, 1350), "square": (1080, 1080), "landscape": (1600, 900)}
DEFAULT_SIZE = "landscape"  # Kevin: las imágenes de LinkedIn van a 1920x1080 (16:9); LinkedIn recorta las 4:5
SCALE = {"landscape": 1.2}  # 1600x900 x1.2 = 1920x1080 exactos; el resto x2 (retina)

def build(spec):
    base = open(os.path.join(TPL, "_base.html"), encoding="utf-8").read()
    body = open(os.path.join(TPL, spec["template"] + ".html"), encoding="utf-8").read()
    themes = json.load(open(os.path.join(TPL, "themes.json"), encoding="utf-8"))
    t = themes.get(spec.get("theme", "plex"), themes["plex"])
    head = "".join('<link rel="stylesheet" href="%s">' % u for u in t.get("css", []))
    head += "<style>:root{--display:%s;--body:%s;%s}</style>" % (t["display"], t["body"], ("--mono:%s;" % t["mono"]) if t.get("mono") else "")
    # Marca personal (config/brand.json): foto en círculo + web en el pie de todas las plantillas
    brand = json.load(open(os.path.join(ROOT, "config", "brand.json"), encoding="utf-8"))
    av = os.path.join(ROOT, brand.get("avatar", ""))
    if brand.get("avatar") and os.path.exists(av):
        brand["avatar"] = "data:image/jpeg;base64," + base64.b64encode(open(av, "rb").read()).decode()
    head += "<script>window.BRAND=%s;</script>" % json.dumps(brand)
    base = base.replace("</head>", head + "</head>", 1)
    return base.replace("{{BODY}}", body).replace("{{SPEC}}", json.dumps(spec, ensure_ascii=False).replace("</", "<\\/"))

def render(spec, out):
    size = spec.get("size", DEFAULT_SIZE)
    w, h = SIZES[size]
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=SCALE.get(size, 2) if not out.endswith(".pdf") else 1)
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))
        pg.set_content(build(spec), wait_until="networkidle")
        try:
            pg.wait_for_function("window.READY === true", timeout=30000)
        except Exception:
            sys.exit("La plantilla no terminó de cargar. Errores JS: %s" % errors)
        if errors: print("AVISO errores JS:", errors)
        if out.endswith(".pdf"):
            pg.pdf(path=out, width=f"{w}px", height=f"{h}px", print_background=True)
        else:
            pg.locator("#canvas").screenshot(path=out)
        b.close()
    print(out)

if __name__ == "__main__":
    render(json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2])
