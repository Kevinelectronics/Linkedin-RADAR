"""Versión animada de una plantilla para LinkedIn: spec JSON -> MP4 (H.264, 1080x1350, 30 fps).

Uso:
  python scripts/render_video.py spec.json salida.mp4 [--hold 3] [--fps 30] [--music auto|archivo.wav] [--volume 0.35]

--music auto genera una música de fondo suave y libre de derechos (scripts/make_music.py) y la mezcla muy baja.

La plantilla tiene que admitir SPEC.animate (por ahora: stack). Se pausan las animaciones CSS y se avanza fotograma a
fotograma, así el vídeo sale fluido aunque la captura sea lenta. Al final se mantiene la imagen completa --hold segundos.
"""
import argparse, json, os, shutil, subprocess, sys
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import build, SIZES, DEFAULT_SIZE

ap = argparse.ArgumentParser()
ap.add_argument("spec"); ap.add_argument("out")
ap.add_argument("--fps", type=int, default=30); ap.add_argument("--hold", type=float, default=3.0)
ap.add_argument("--music"); ap.add_argument("--volume", type=float, default=0.35)
a = ap.parse_args()

spec = json.load(open(a.spec, encoding="utf-8")); spec["animate"] = True
w, h = SIZES[spec.get("size", DEFAULT_SIZE)]
ff = shutil.which("ffmpeg") or sys.exit("Falta ffmpeg en el PATH.")
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": w, "height": h})
    pg.set_content(build(spec), wait_until="networkidle")
    pg.wait_for_function("window.READY === true", timeout=30000)
    end = pg.evaluate("document.getAnimations().forEach(function(x){x.pause()}); window.ANIM_END || 6")
    frames = int((end + a.hold) * a.fps)
    enc = subprocess.Popen([ff, "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(a.fps), "-i", "-",
                            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "medium", "-movflags", "+faststart", a.out],
                           stdin=subprocess.PIPE)
    for i in range(frames):
        pg.evaluate("t => document.getAnimations().forEach(function(x){x.currentTime=t})", i * 1000 / a.fps)
        enc.stdin.write(pg.locator("#canvas").screenshot(type="png", animations="allow"))
    enc.stdin.close(); enc.wait(); b.close()
dur = frames / a.fps
if a.music:
    here = os.path.dirname(os.path.abspath(__file__))
    wav = a.music
    if a.music == "auto":
        wav = os.path.splitext(a.out)[0] + "_music.wav"
        subprocess.run([sys.executable, os.path.join(here, "make_music.py"), wav, "--dur", "%.2f" % dur], check=True)
    tmp = os.path.splitext(a.out)[0] + "_tmp.mp4"; os.replace(a.out, tmp)
    subprocess.run([ff, "-y", "-loglevel", "error", "-i", tmp, "-i", wav, "-filter:a", "volume=%s" % a.volume, "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", a.out], check=True)
    os.remove(tmp)
    if a.music == "auto": os.remove(wav)
print(a.out, "%.1fs" % dur)
