import os
import json, collections, re

S = os.path.dirname(os.path.abspath(__file__))
raw = json.load(open(f'{S}/ast-raw.json'))
nodes_raw, edges_raw = raw['nodes'], raw['edges']
id2file = {x['id']: x['source_file'] for x in nodes_raw}
files = sorted({x['source_file'] for x in nodes_raw})

# Layer assignment: folder first, then flat src/core prefixes (proposal, awaiting human confirmation)
LAYERS = {
    1: ('Commands', 'the `ui` subcommands (src/commands)'),
    2: ('Adapters and types', 'per-runtime wrappers and shared types'),
    3: ('Component kit', 'component generation (src/core/component-kit)'),
    4: ('Extractors and design facts', 'reads CSS/HTML/web/native sources into facts'),
    5: ('Delivery and rendered', 'delivery pipeline and rendered output'),
    6: ('Prompt plan', 'prompt planning (src/core/prompt-plan)'),
    7: ('Design system core', 'tokens, DESIGN.md, layout, html, css, color'),
    8: ('Figma and sync', 'Figma reconcile, ksync, seam, registry, capabilities'),
    9: ('Knowledge and templates', 'knowledge base, templates, personas, rulings'),
    10: ('Taste and quality gates', 'taste, tell, judge, lint, a11y, audit, evidence'),
    11: ('Memory and product context', 'memory store, product context, brief, tenant'),
    12: ('Other core', 'flat core modules not covered above (to review)'),
}
PREFIX_LAYER = [
    ('ds', 7), ('designmd', 7), ('token', 7), ('design', 7), ('color', 7), ('css', 7),
    ('stylesheet', 7), ('svg', 7), ('layout', 7), ('html', 7), ('build', 10), ('specimen', 7),
    ('snapshot', 7), ('figma', 8), ('ksync', 8), ('seam', 8), ('registry', 8), ('capability', 8),
    ('adapter', 8), ('knowledge', 9), ('template', 9), ('persona', 9), ('rulings', 9),
    ('content', 9), ('method', 9), ('brief', 11), ('taste', 10), ('tell', 10), ('judge', 10),
    ('scrub', 10), ('lint', 10), ('a11y', 10), ('audit', 10), ('vr', 10), ('evidence', 10),
    ('trace', 10), ('memory', 11), ('product', 11), ('tenant', 11),
]
FOLDER_LAYER = {
    'src/commands/': 1, 'src/adapters/': 2, 'src/types/': 2,
    'src/core/component-kit/': 3, 'src/core/extractors/': 4, 'src/core/design-facts/': 4,
    'src/core/delivery/': 5, 'src/core/rendered/': 5, 'src/core/prompt-plan/': 6,
}

def layer_of(path):
    for prefix, layer in FOLDER_LAYER.items():
        if path.startswith(prefix):
            return layer
    name = path.split('/')[-1].replace('.ts', '')
    head = re.split(r'[-.]', name)[0]
    for prefix, layer in PREFIX_LAYER:
        if head == prefix:
            return layer
    return 12

def label_of(path):
    return path[len('src/'):] if path.startswith('src/') else path

nodes = []
for f in files:
    nodes.append({'id': f, 'label': label_of(f), 'file': f, 'layer': layer_of(f)})
node_ids = {n['id'] for n in nodes}

REL = {'imports_from': 'imports', 'imports': 'imports', 're_exports': 'imports',
       'calls': 'calls', 'indirect_call': 'calls', 'references': 'references',
       'inherits': 'inherits', 'method': 'references'}
agg = collections.Counter()
for x in edges_raw:
    if x['relation'] not in REL:
        continue
    s = id2file.get(x['source']); t = id2file.get(x['target'])
    if not s or not t or s == t or s not in node_ids or t not in node_ids:
        continue
    agg[(s, t, REL[x['relation']])] += 1

edges = [{'s': s, 't': t, 'r': r, 'n': c} for (s, t, r), c in sorted(agg.items())]

ins = collections.Counter(); outs = collections.Counter()
for e in edges:
    outs[e['s']] += 1; ins[e['t']] += 1
for n in nodes:
    n['in'] = ins[n['id']]; n['out'] = outs[n['id']]

orphans = [n['id'] for n in nodes if n['in'] == 0 and n['out'] == 0]
per_layer = collections.Counter(n['layer'] for n in nodes)
skeleton = {
    'meta': {
        'titulo': 'ease-design: TypeScript kernel (src/)',
        'contexto': 'File-level graph of the ui kernel: commands, adapters, core modules.',
        'extract_mode': 'code', 'unit': 'file', 'seeds': ['src/core', 'src/commands', 'src/adapters', 'src/types'],
        'edge_relations': ['imports', 'calls', 'references', 'inherits'],
        'degree_definition': 'in/out = number of aggregated file-level edges (AST) in each direction',
        'excluded': ['tests', 'external node builtins (ref_node_*)', 'edges within a single file'],
        'source_commit': '8420c6222abc12d9f3b55a271a9ba43f8c2f123e',
        'layers': {str(k): {'name': v[0], 'sub': v[1]} for k, v in LAYERS.items()},
    },
    'nodes': nodes, 'edges': edges,
}
json.dump(skeleton, open(f'{S}/skeleton.json', 'w'), indent=1)
print('nodes', len(nodes), 'edges', len(edges), 'orphans', len(orphans))
for k in sorted(per_layer):
    print(f'  L{k:<2} {LAYERS[k][0]:32s} {per_layer[k]:4d}')
print('edge relations:', collections.Counter(e['r'] for e in edges))
