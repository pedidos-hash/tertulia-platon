# Buscador de fallos — Platón nivel 2

Buscador léxico BM25 (librería de código abierto `rank_bm25`) sobre las 120 sentencias del Tribunal de Locaciones.

## Entradas
- Carpeta `fallos/` con los archivos `F-NNN.md` (por defecto `../fallos`).
- Una consulta en texto libre.

## Instalación
```
pip install rank_bm25
```

## Uso
```
python buscar.py "batería central cuotas bien común" --fallos ../fallos -k 10
```

## Cómo funciona
- **Carga** (`cargar`): lee cada sentencia, extrae número, Sala/Plenario, fecha de publicación y las doctrinas que revoca, y la divide en fragmentos por párrafo.
- **Indexación** (`indexar`): normaliza (minúsculas, sin acentos) y construye el índice BM25 en memoria. No se guardan índices binarios.
- **Consulta** (`consultar`): devuelve los fragmentos más relevantes con su `F-NNN`, excluye lo posterior al corte (30/09/2026) y marca como `[REVOCADO]` los fallos cuya doctrina revocó un plenario (art. 32).

La selección final de precedentes se hizo revisando los resultados: se priorizan los plenarios vigentes (art. 31) y no se citan fallos revocados. Cuando la cláusula viola un tope o plazo numérico expreso, no se cita jurisprudencia.
