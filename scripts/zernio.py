"""Publicar en LinkedIn a través de Zernio (https://docs.zernio.com).

Lee ZERNIO_API_KEY y ZERNIO_ACCOUNT_ID del entorno o, si no están, de las variables de usuario de Windows
(no hace falta cargarlas antes; ver PUBLISH.md).

Uso:
  python scripts/zernio.py accounts
      Lista las cuentas de LinkedIn conectadas (el _id es el accountId).
  python scripts/zernio.py post --text-file post.txt [--account <id>] [--image img.png | --pdf carrusel.pdf --title "Título" | --video animacion.mp4]
                               [--at 2026-11-03T09:00 --tz Europe/Madrid | --now] [--key <id-idempotencia>]
      Sube el archivo (si hay), crea el post y muestra {postId, status, url}.
  python scripts/zernio.py status <postId>
  python scripts/zernio.py cancel <postId>

Reglas de seguridad: se niega a publicar textos con huecos sin rellenar ([tu experiencia...], [@...], TODO).
El texto admite **negrita**: se convierte a negrita Unicode, igual que el botón "Copiar para LinkedIn" del radar.
"""
import argparse, json, mimetypes, os, re, sys, unicodedata, urllib.error, urllib.request

API = "https://zernio.com/api/v1"
def user_env(name):
    """Lee una variable de entorno; si no está en el proceso, la busca en las variables de usuario de Windows."""
    v = os.environ.get(name)
    if v or os.name != "nt":
        return v
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as k:
            return winreg.QueryValueEx(k, name)[0]
    except OSError:
        return None


KEY = user_env("ZERNIO_API_KEY")
PLACEHOLDER = re.compile(r"\[(tu |@|tu_|fundador|placeholder|TODO)|\bTODO\b|\[[^\]]*aquí", re.I)


def call(method, path, body=None, extra=None):
    if not KEY:
        sys.exit("Falta ZERNIO_API_KEY. Ver PUBLISH.md.")
    h = {"Authorization": "Bearer " + KEY, "Content-Type": "application/json"}
    h.update(extra or {})
    req = urllib.request.Request(API + path, method=method, headers=h,
                                 data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            txt = r.read().decode()
            return r.status, (json.loads(txt) if txt else {})
    except urllib.error.HTTPError as e:
        txt = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(txt)
        except ValueError:
            return e.code, {"error": txt[:500]}


def boldify(s):
    out = []
    for ch in unicodedata.normalize("NFD", s):
        c = ord(ch)
        if 65 <= c <= 90: out.append(chr(0x1D5D4 + c - 65))
        elif 97 <= c <= 122: out.append(chr(0x1D5EE + c - 97))
        elif 48 <= c <= 57: out.append(chr(0x1D7EC + c - 48))
        else: out.append(ch)
    return unicodedata.normalize("NFC", "".join(out))


def to_linkedin(text):
    return re.sub(r"\*\*([^*\n]+?)\*\*", lambda m: boldify(m.group(1)), text)


def check_text(text):
    """Comprueba las reglas de Kevin y devuelve el texto listo para LinkedIn (negrita Unicode)."""
    if PLACEHOLDER.search(text):
        sys.exit("El texto tiene huecos sin rellenar (%s). No se publica." % PLACEHOLDER.search(text).group(0))
    # EODHD: siempre a su web y con el afiliado de Kevin (docs /financial-apis/ pueden ir sin parámetros).
    if re.search(r"github\.com/EodHistoricalData", text, re.I):
        sys.exit("El post enlaza al GitHub de EODHD: debe apuntar a eodhd.com con el enlace de afiliado (ver DAILY.md).")
    for url in re.findall(r"(?:https?://)?(?:www\.)?eodhd\.com[^\s)]*", text, re.I):
        if "/financial-apis/" in url and "mcp-server" not in url:
            continue
        if "via=kmg" not in url:
            sys.exit("Enlace a EODHD sin afiliado (via=kmg): %s" % url)
    # Kevin no quiere tono promocional: sin cupones ni descuentos (2026-11-03).
    promo = re.search(r"KEVIN10|\b\d+\s?% off\b|discount code|coupon", text, re.I)
    if promo:
        sys.exit("El texto suena a promoción (%s): quítalo, Kevin no quiere cupones." % promo.group(0))
    text = to_linkedin(text)
    if len(text) > 3000:
        sys.exit("El texto supera los 3.000 caracteres de LinkedIn (%d)." % len(text))
    return text


def upload(path):
    ctype = mimetypes.guess_type(path)[0] or ""
    if ctype not in ("image/png", "image/jpeg", "image/gif", "image/webp", "application/pdf", "video/mp4"):
        sys.exit("Tipo de archivo no admitido: %s (%s)" % (path, ctype))
    size = os.path.getsize(path)
    st, pre = call("POST", "/media/presign", {"filename": os.path.basename(path), "contentType": ctype, "size": size})
    if st != 200 or "uploadUrl" not in pre:
        sys.exit("Error en presign (%s): %s" % (st, pre))
    with open(path, "rb") as f:
        put = urllib.request.Request(pre["uploadUrl"], method="PUT", data=f.read(), headers={"Content-Type": ctype})
        with urllib.request.urlopen(put, timeout=300) as r:
            if r.status not in (200, 201):
                sys.exit("Error subiendo el archivo: HTTP %s" % r.status)
    return pre["publicUrl"], ("document" if ctype == "application/pdf" else "video" if ctype.startswith("video/") else "image")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("accounts")
    p = sub.add_parser("post")
    p.add_argument("--text-file", required=True)
    p.add_argument("--account", default=user_env("ZERNIO_ACCOUNT_ID"), help="por defecto, la variable ZERNIO_ACCOUNT_ID")
    p.add_argument("--image"); p.add_argument("--pdf"); p.add_argument("--video"); p.add_argument("--title")
    p.add_argument("--at"); p.add_argument("--tz", default="Europe/Madrid"); p.add_argument("--now", action="store_true")
    p.add_argument("--key", help="Idempotency-Key (usa el id del draft para no duplicar)")
    for c in ("status", "cancel"):
        sub.add_parser(c).add_argument("post_id")
    e = sub.add_parser("edit")
    e.add_argument("post_id"); e.add_argument("--text-file", required=True)
    a = ap.parse_args()

    if a.cmd == "edit":
        text = check_text(open(a.text_file, encoding="utf-8").read().strip())
        st, r = call("POST", "/posts/%s/edit" % a.post_id, {"content": text, "platform": "linkedin"})
        print(st, json.dumps(r, ensure_ascii=False)[:800])
        if st >= 300: sys.exit(1)
        return

    if a.cmd == "accounts":
        st, r = call("GET", "/accounts?platform=linkedin")
        for acc in r.get("accounts", []):
            print(json.dumps({k: acc.get(k) for k in ("_id", "displayName", "username", "profileUrl", "isActive", "needsReconnection")}, ensure_ascii=False))
        if st != 200: print(st, r)
        return
    if a.cmd == "status":
        st, r = call("GET", "/posts/" + a.post_id)
        post = r.get("post", r)
        print(json.dumps({"status": post.get("status"), "scheduledFor": post.get("scheduledFor"),
                          "platforms": [{k: x.get(k) for k in ("status", "platformPostUrl", "errorMessage")} for x in post.get("platforms", [])]}, ensure_ascii=False))
        return
    if a.cmd == "cancel":
        st, r = call("DELETE", "/posts/" + a.post_id)
        print(st, json.dumps(r, ensure_ascii=False)); return

    if not a.account:
        sys.exit("Falta --account o la variable ZERNIO_ACCOUNT_ID.")
    text = check_text(open(a.text_file, encoding="utf-8").read().strip())
    if not (a.now or a.at):
        sys.exit("Indica --at <fecha y hora> o --now.")
    body = {"content": text, "platforms": [{"platform": "linkedin", "accountId": a.account}]}
    if a.image or a.pdf or a.video:
        url, kind = upload(a.image or a.pdf or a.video)
        body["mediaItems"] = [{"url": url, "type": kind}]
        if kind == "document":
            body["platforms"][0]["platformSpecificData"] = {"documentTitle": a.title or "Guide"}
    if a.now:
        body["publishNow"] = True
    else:
        body["scheduledFor"] = a.at
        body["timezone"] = a.tz
    st, r = call("POST", "/posts", body, {"Idempotency-Key": a.key} if a.key else None)
    post = r.get("post", {})
    plat = (post.get("platforms") or [{}])[0]
    print(json.dumps({"http": st, "postId": post.get("_id"), "status": post.get("status"), "scheduledFor": post.get("scheduledFor"),
                      "url": plat.get("platformPostUrl"), "error": r.get("error") or r.get("message") if st >= 300 else None}, ensure_ascii=False))
    if st >= 300 and st != 207:
        sys.exit(1)


if __name__ == "__main__":
    main()
