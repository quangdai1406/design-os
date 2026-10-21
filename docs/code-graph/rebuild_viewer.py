import os
import json

S = os.path.dirname(os.path.abspath(__file__))
t = open(f'{S}/viewer-template.html', encoding='utf-8').read()

# UI labels only (not structure, not data). The template ships in Spanish; the graph is read in English.
EN = [
 ('Las lineas son las dependencias reales entre nodos. Click en un nodo: ', 'Lines are the real dependencies between nodes. Click a node: '),
 ('>solidas<', '>solid<'),
 (' = lo que ese nodo usa, ', ' = what that node uses, '),
 ('>punteadas<', '>dashed<'),
 (' = quien lo usa.<', ' = what uses it.<'),
 (' solo sin curar', ' uncurated only'),
 ('>Capas<', '>Layers<'),
 ('>Aristas<', '>Edges<'),
 ('>Selecciona un nodo para ver su rol y resaltar sus conexiones.</div>', '>Select a node to see its role and highlight its connections.</div>'),
 ("'curado':'sin curar'", "'curated':'uncurated'"),
 ('>Empieza por los de mayor <', '>Start with the highest <'),
 ('>✕ limpiar<', '>✕ clear<'),
 (' lo usan<', ' used by<'),
 (' usa<', ' uses<'),
 ('Que hace</div>', 'What it does</div>'),
 ('Por que</div>', 'Why</div>'),
 ('Nodo sin curar todavia. Su descripcion (que hace / por que) se escribe leyendo el archivo.', 'Not curated yet. Its description (what it does / why) is written by reading the file.'),
 ('Usa (${outs.length})', 'Uses (${outs.length})'),
 ('>Sin resultados<', '>No results<'),
 ('placeholder="Buscar nodo por nombre o archivo…"', 'placeholder="Search node by name or file…"'),
 ('Selecciona un nodo para ver su rol y resaltar sus conexiones.${hint}', 'Select a node to see its role and highlight its connections.${hint}'),
 ('${totalCurated}/${DATA.nodes.length} curados', '${totalCurated}/${DATA.nodes.length} curated'),
]
for old, new in EN:
    n = t.count(old)
    assert n >= 1, f'label not found: {old!r}'
    t = t.replace(old, new)

s = json.load(open(f'{S}/skeleton.json'))
cur = json.load(open(f'{S}/curation.json'))
meta = s['meta']
layers = [{'id': int(k), 'name': v['name'], 'sub': v['sub']} for k, v in sorted(meta['layers'].items(), key=lambda kv: int(kv[0]))]
data = {'nodes': [{k: n[k] for k in ('id', 'label', 'file', 'layer', 'in', 'out')} for n in s['nodes']],
        'edges': [{'s': e['s'], 't': e['t'], 'r': e['r']} for e in s['edges']]}
curation = {p: {k: v for k, v in c.items() if k in ('what', 'why', 'gotcha')} for p, c in cur.items()}
out = (t.replace('__TITLE__', meta['titulo'])
        .replace('__SUBTITLE__', meta['contexto'])
        .replace('__LAYERS__', json.dumps(layers, ensure_ascii=False))
        .replace('__DATA__', json.dumps(data, ensure_ascii=False))
        .replace('__CURATION__', json.dumps(curation, ensure_ascii=False)))
open(f'{S}/graph.html', 'w', encoding='utf-8').write(out)
print('bytes', len(out), 'curated', len(curation), 'markers left', [m for m in ['__TITLE__','__SUBTITLE__','__LAYERS__','__DATA__','__CURATION__'] if m in out])
