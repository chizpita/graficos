#!/usr/bin/env python3
"""Recoge de la API de pedidos los graficos subidos en la app y escribe los que falten."""
import base64, io, json, os, re, sys, urllib.parse, urllib.request

API = os.environ["API"]
NOMBRE = re.compile(r"^grafico-\d{4}-\d{2}-\d{2}-[a-z0-9]+\.(jpg|png|webp|gif|pdf)$")
MAX = 8 * 1024 * 1024


def pedir(g):
    with urllib.request.urlopen(API + "?g=" + urllib.parse.quote(g), timeout=120) as r:
        return json.load(r)


lista = pedir("lista")
if not lista.get("ok"):
    sys.exit("La API no dio la lista: " + json.dumps(lista)[:200])
for nombre in lista["archivos"]:
    if not NOMBRE.match(nombre):
        print("Nombre rechazado:", nombre[:80])
        continue
    if os.path.exists(nombre):
        continue
    d = pedir(nombre)
    if not d.get("ok"):
        print("No se pudo traer", nombre)
        continue
    datos = base64.b64decode(d["base64"], validate=True)
    if len(datos) > MAX:
        print("Demasiado grande:", nombre)
        continue
    with open(nombre, "wb") as f:
        f.write(datos)
    print("Nuevo:", nombre, len(datos), "bytes")

# Vista previa del link de pedido en WhatsApp: el grafico vigente o, sin el, la imagen de la marca.
MARCA = "https://cdn.jsdelivr.net/gh/chizpita/brand@v3.0.0/exports/social/og-image-1200x630.png"
quiere = lista.get("portada") or "marca"
if not (quiere == "marca" or (NOMBRE.match(quiere) and not quiere.endswith(".pdf") and os.path.exists(quiere))):
    quiere = "marca"
actual = open("portada.txt").read().strip() if os.path.exists("portada.txt") else ""
if quiere != actual:
    from PIL import Image

    fuente = io.BytesIO(urllib.request.urlopen(MARCA, timeout=60).read()) if quiere == "marca" else quiere
    img = Image.open(fuente).convert("RGB")
    img.thumbnail((1200, 1200))
    # WhatsApp no muestra imagenes pesadas: se baja la calidad hasta que quede ligera
    for calidad in (85, 75, 65, 55):
        img.save("portada.jpg", "JPEG", quality=calidad, optimize=True)
        if os.path.getsize("portada.jpg") < 280 * 1024:
            break
    with open("portada.txt", "w") as f:
        f.write(quiere + "\n")
    print("Portada:", quiere, img.size, os.path.getsize("portada.jpg"), "bytes")
