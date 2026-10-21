import json, os, sys
S = os.path.dirname(os.path.abspath(__file__))
CUR_PATH = f'{S}/curation.json'
COMMIT = '8420c62'
batch = json.load(open(sys.argv[1], encoding='utf-8'))
cur = json.load(open(CUR_PATH, encoding='utf-8')) if os.path.exists(CUR_PATH) else {}
added = skipped = 0
for path, fields in batch.items():
    entry = cur.setdefault(path, {})
    for k, v in fields.items():
        if k in entry and entry[k]:
            skipped += 1          # additive: never overwrite curated text
            continue
        entry[k] = v
        added += 1
    entry.setdefault('curated_at', COMMIT)
json.dump(cur, open(CUR_PATH, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f'added={added} skipped_existing={skipped} curated_nodes={len(cur)}')
