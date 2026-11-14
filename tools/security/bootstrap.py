"""Fetch exact official security tools, verify checksums, never run an installer."""
from pathlib import Path
import argparse
import hashlib
import json
import tarfile
import time
import urllib.request

VERSIONS = {'syft':'1.57.1','grype':'0.121.3'}


def download(url, target):
    deadline = time.monotonic() + 240
    temporary = target.with_suffix(target.suffix + '.partial')
    total = 0
    with urllib.request.urlopen(url, timeout=30) as response, temporary.open('wb') as output:
        while block := response.read(128 * 1024):
            total += len(block)
            if total > 200 * 1024 * 1024 or time.monotonic() > deadline:
                raise RuntimeError('Bounded scanner acquisition exceeded limits')
            output.write(block)
    temporary.replace(target)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--platform',required=True,choices=['linux_amd64','darwin_arm64'])
    parser.add_argument('--directory',default='.local/security-tools')
    args=parser.parse_args()
    dest=Path(args.directory);dest.mkdir(parents=True,exist_ok=True)
    cache=Path('work/security/downloads');cache.mkdir(parents=True,exist_ok=True)
    records=[]
    for name,version in VERSIONS.items():
        base=f'https://github.com/anchore/{name}/releases/download/v{version}/'
        archive=f'{name}_{version}_{args.platform}.tar.gz';checks=f'{name}_{version}_checksums.txt'
        for file in [checks,archive]:
            if not (cache/file).exists():download(base+file,cache/file)
        expected=next(x.split()[0] for x in (cache/checks).read_text().splitlines() if x.split()[-1].lstrip('*')==archive)
        actual=hashlib.sha256((cache/archive).read_bytes()).hexdigest()
        if actual!=expected:raise RuntimeError('Official archive checksum mismatch: '+name)
        notices=[]
        with tarfile.open(cache/archive) as tar:
            for member in tar.getmembers():
                leaf=Path(member.name).name
                if member.isfile() and leaf in [name,'LICENSE','NOTICE']:
                    target=dest/(name if leaf==name else name+'-'+leaf)
                    target.write_bytes(tar.extractfile(member).read())
                    if leaf==name:target.chmod(0o755)
                    else:notices.append({'path':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
        records.append({'name':name,'version':version,'platform':args.platform,'source':base+archive,'archive_sha256':actual,'checksum_source':base+checks,'notices':notices,'limitations':'Checksum over HTTPS; no independent signing/whole-source audit claimed'})
    output=Path('work/f2-security');output.mkdir(parents=True,exist_ok=True)
    (output/'tools.json').write_text(json.dumps(records,indent=2)+'\n')
    print('Exact security-tool checksums verified; no install script executed.')


if __name__=='__main__':main()
