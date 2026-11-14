"""Buscador de fallos del Tribunal de Locaciones de Calípolis (BM25, rank_bm25).

1. CARGA: lee fallos/F-NNN.md y extrae número, sala/plenario y fecha.
2. INDEXACIÓN: divide cada sentencia en fragmentos (párrafos), normaliza y arma un índice BM25 en memoria.
3. CONSULTA: devuelve los fragmentos más relevantes con su número de sentencia.
"""
import argparse, re, unicodedata
from pathlib import Path
from rank_bm25 import BM25Okapi

CORTE = (2026, 9, 30)

def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")

def tokens(t):
    return re.findall(r"[a-z0-9]+", norm(t))

def cargar(carpeta):
    """Carga cada sentencia y la parte en fragmentos con metadatos."""
    frags = []
    for p in sorted(Path(carpeta).glob("F-*.md")):
        txt = p.read_text(encoding="utf-8")
        m = re.search(r"Sentencia (F-\d+)\. ([^.]+)\. Publicación: (\d+)/(\d+)/(\d+)", txt)
        fid, tipo, d, mo, y = m.group(1), m.group(2), int(m.group(3)), int(m.group(4)), int(m.group(5))
        revoca = re.findall(r"revoca expresamente la doctrina de (F-\d+)", txt)
        for par in [x.strip() for x in txt.split("\n\n") if len(x.strip()) > 40]:
            frags.append({"fallo": fid, "tipo": tipo, "fecha": (y, mo, d), "revoca": revoca, "texto": par})
    return frags

def indexar(frags):
    return BM25Okapi([tokens(f["texto"]) for f in frags])

def consultar(frags, bm25, q, k=10):
    """Recupera fragmentos, descarta fallos posteriores al corte y marca los revocados (art. 32)."""
    revocados = {r for f in frags if f["tipo"] == "Plenario" for r in f["revoca"]}
    sc = bm25.get_scores(tokens(q))
    orden = sorted(range(len(frags)), key=lambda i: -sc[i])
    res, vistos = [], set()
    for i in orden:
        f = frags[i]
        if f["fecha"] > CORTE or (f["fallo"], f["texto"][:60]) in vistos:
            continue
        vistos.add((f["fallo"], f["texto"][:60]))
        res.append((sc[i], f, f["fallo"] in revocados))
        if len(res) == k:
            break
    return res

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("consulta")
    ap.add_argument("--fallos", default="../fallos")
    ap.add_argument("-k", type=int, default=10)
    a = ap.parse_args()
    frags = cargar(a.fallos)
    bm25 = indexar(frags)
    for s, f, rev in consultar(frags, bm25, a.consulta, a.k):
        marca = " [REVOCADO]" if rev else ""
        print(f"{f['fallo']} ({f['tipo']}, {'/'.join(map(str, f['fecha'][::-1]))}){marca} score={s:.2f}\n  {f['texto'][:300]}\n")
