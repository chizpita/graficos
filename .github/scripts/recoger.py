#!/usr/bin/env python3
"""Recoge de la API de pedidos los graficos subidos en la app y escribe los que falten."""
import base64, json, os, re, sys, urllib.parse, urllib.request

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
