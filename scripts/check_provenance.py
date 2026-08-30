import json

with open('data/metadata/provenance-manifest.json') as f:
    data = json.load(f)

for ds_name, ds in data.get('datasets', {}).items():
    sha = ds.get('source_sha256', 'MISSING')
    md5 = ds.get('source_hash_md5', 'NONE')
    sha_short = sha[:16] if sha else 'NONE'
    print(f'{ds_name}: sha256={sha_short}... md5={md5}')
