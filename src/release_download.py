"""Download pinned release assets, never release-description attachment links."""
import concurrent.futures, hashlib, json, pathlib, urllib.request, zipfile
ROOT = pathlib.Path(__file__).resolve().parents[1]
def retrieve(a):
    path = ROOT / 'data/raw/release' / a['name']
    path.parent.mkdir(parents=True, exist_ok=True)
    def valid(p):
        if not p.exists() or p.stat().st_size != a['size']:
            return False
        if 'sha256:' + hashlib.sha256(p.read_bytes()).hexdigest() != a['digest']:
            return False
        try:
            if p.suffix in ('.zip', '.xlsx'):
                with zipfile.ZipFile(p) as z: return z.testzip() is None
            return p.read_bytes().startswith(b'%PDF-')
        except (OSError, zipfile.BadZipFile):
            return False
    if path.exists() and path.stat().st_size==a['size']:
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        if 'sha256:'+digest==a['digest'] and not valid(path):
            return dict(name=a['name'],bytes=path.stat().st_size,sha256=digest,integrity='source_invalid',members=None,
                        error='GitHub-declared bytes and digest match, but file structure or CRC fails')
    for attempt in range(3):
        if valid(path): break
        tmp = path.with_suffix(path.suffix + '.partial')
        with urllib.request.urlopen(a['browser_download_url'], timeout=180) as src, tmp.open('wb') as out:
            while chunk := src.read(1024*1024): out.write(chunk)
        tmp.replace(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if not valid(path):
        return dict(name=a['name'],bytes=path.stat().st_size if path.exists() else None,sha256=digest,integrity='failed',members=None)
    if path.suffix in ('.zip', '.xlsx'):
        with zipfile.ZipFile(path) as z:
            assert z.testzip() is None
            members = len(z.namelist())
    else:
        assert path.read_bytes().startswith(b'%PDF-')
        members = None
    return dict(name=a['name'], bytes=path.stat().st_size, sha256=digest, integrity='passed', members=members)
if __name__ == '__main__':
    assets = json.loads((ROOT/'reports/release_assets.json').read_text())['assets']
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures={pool.submit(retrieve,a):a for a in assets}
        results=[]
        for future,a in futures.items():
            try: results.append(future.result())
            except Exception as exc: results.append(dict(name=a['name'],integrity='failed',error=str(exc)))
    (ROOT/'reports/release_integrity.json').write_text(json.dumps(results, indent=2)+'\n')
    print(json.dumps(results, indent=2))
