#!/usr/bin/env python3
"""Plan/check public path redaction; preserve original bytes in a private ZIP.

This tool never applies source edits, changes Git settings, rewrites history,
executes firmware, or contacts the network. Apply reviewed plans with a file
editor. Hash-reference changes are recorded separately from original evidence.
"""
import argparse
import collections
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import uuid
import zipfile

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = 'analysis/public-path-redaction-2026-10-23/manifest.json'
HEX = re.compile(r'(?<![0-9A-Fa-f])[0-9A-Fa-f]{64}(?![0-9A-Fa-f])')
HOME = re.compile(r'(?i)[A-Z]:[\\/]+Users[\\/]+[^\\/\r\n"\x27<>]+|/(?:Users|home)/[^/\r\n"\x27<>]+')


def need(ok,message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git','-C',str(ROOT),*args]).decode().strip()


def inventory():
    result = {}
    for name in git('ls-files','-z').split('\0'):
        if not name or name==PUBLIC:
            continue
        path = ROOT/name
        need(path.is_file() and not path.is_symlink(),'Regular tracked file required: '+name)
        data = path.read_bytes()
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            continue
        if '\0' not in text:
            result[name] = (data,text)
    return result


def aliases():
    result = {Path.home().name}
    remote = git('remote','get-url','origin')
    m = re.search(r'github\.com[:/]([^/]+)/[^/]+',remote)
    if m:
        result.add(m[1])
    return sorted(x for x in result if x)


def redact(text,labels):
    # Match separators in plain text AND escaped JSON/LLVM string literals.
    sep = r'[\\/]+'
    # Local evidence roots, legacy project names and standard tool subtrees
    # are mapped to variables before the generic user-home prefix.
    home = r'(?:[A-Za-z]:[\\/]+Users[\\/]+[^\\/\r\n"\x27<>]+|/(?:Users|home)/[^/\r\n"\x27<>]+)'
    replacements = [
        (home+sep+r'Documents'+sep+r'projects'+sep+r'(?:tsl9-reversed|re-tsl9)(?=[\\/"\x27\s]|$)', '${PROJECT_ROOT}'),
        (home+sep+r'Documents'+sep+r'Codex'+sep+r'2026-10-13'+sep+r'rea-https-github-com-morluto-rea(?=[\\/"\x27\s]|$)', '${ANALYSIS_WORKSPACE}'),
        (home+sep+r'AppData'+sep+r'Local'+sep+r'Android'+sep+r'Sdk'+sep+r'ndk'+sep+r'[^\\/"\x27\s]+'+sep+r'toolchains'+sep+r'llvm'+sep+r'prebuilt'+sep+r'[^\\/"\x27\s]+'+sep+r'bin', '${LLVM_BIN}'),
        (home+sep+r'AppData'+sep+r'Local'+sep+r'hermes'+sep+r'hermes-agent'+sep+r'venv'+sep+r'Scripts'+sep+r'python\.exe', '${PYTHON}'),
        (home+sep+r'Tools'+sep+r'radare2'+sep+r'bin'+sep+r'r2\.exe', '${RADARE2}'),
        (home,'${HOME}'),
    ]
    for pattern,value in replacements:
        text = re.sub(pattern,lambda _:value,text,flags=re.I)
    for label in labels:
        text = re.sub(r'(?<![A-Za-z0-9_])'+re.escape(label)+r'(?![A-Za-z0-9_])',
                      lambda _:'${LOCAL_ACCOUNT}',text,flags=re.I)
    return text


def plan(files,labels):
    bases = {n:redact(t,labels) for n,(_,t) in files.items()}
    # A changed public member may have a SHA pin in a reader or seal. Rebase
    # these explicit TEXT-member references, preserving all BIN/APK hashes.
    # Every original/public digest pair is retained in the public ledger.
    # Resolve the acyclic reference graph once. The historical tree currently
    # has long pin chains; rescanning every file once per depth is unnecessary.
    owners = collections.defaultdict(list)
    for name,(raw,_) in files.items():
        owners[digest(raw)].append(name)
    texts,new_hashes,active,depths = {},{},set(),{}
    def resolve(name):
        if name in texts:
            return texts[name]
        need(name not in active,'Cyclic text-member SHA reference; no edits applied: '+name)
        active.add(name);depth=0
        def replace(match):
            nonlocal depth
            targets=owners.get(match[0].lower(),[])
            if not targets:
                return match[0]
            values=[]
            for target in targets:
                resolve(target);values.append(new_hashes[target]);depth=max(depth,depths[target])
            need(len(set(values))==1,'Conflicting identical original members')
            return values[0].upper() if match[0].isupper() else values[0]
        text=HEX.sub(replace,bases[name])
        if text!=files[name][1]:
            text=text.replace('\r\n','\n')
            if not text.endswith('\n'):
                text+='\n'
        texts[name]=text;new_hashes[name]=digest(text.encode())
        active.remove(name);depths[name]=depth+1
        return texts[name]
    for name in files:
        resolve(name)
    changed = {}
    for name,(raw,old) in files.items():
        new = texts[name]
        if new==old:
            continue
        if name.endswith('.json'):
            json.loads(new.lstrip('\ufeff'))
        need(not HOME.search(new),'Unredacted home path: '+name)
        need(all(not re.search(r'(?<![A-Za-z0-9_])'+re.escape(v)+r'(?![A-Za-z0-9_])',new,re.I) for v in labels),
             'Unredacted local account label: '+name)
        changed[name] = dict(original_sha256=digest(raw),public_sha256=digest(new.encode()),
                             original_bytes=len(raw),public_bytes=len(new.encode()),
                             personal_path_or_label_changed=bases[name]!=old,
                             dependent_text_hash_pins_changed=HEX.findall(new)!=HEX.findall(bases[name]),
                             native_editor_LF_representation=True,
                             status='anonymized historical/public derivative; not the original receipt')
    return texts,changed,max(depths.values(),default=0)-1


def backup(files,directory):
    directory = directory.resolve()
    need(not directory.is_relative_to(ROOT),'Private backup must be outside the project')
    directory.mkdir(parents=True,exist_ok=True)
    output = directory/('TSL9-original-evidence-20261023-'+uuid.uuid4().hex+'.zip')
    manifest = dict(schema='TSL9-private-original-evidence-v1',HEAD=git('rev-parse','HEAD'),
                    files={n:dict(bytes=len(b),sha256=digest(b)) for n,(b,_) in files.items()},
                    no_network=True,original_bytes_preserved=True)
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for n,(raw,_) in files.items():
            z.writestr(n,raw)
        z.writestr('_private-backup-manifest.json',json.dumps(manifest,indent=2)+'\n')
    verify_backup(output,manifest)
    return output


def verify_backup(path,expected=None):
    with zipfile.ZipFile(path) as z:
        saved = json.loads(z.read('_private-backup-manifest.json'))
        if expected is not None:
            need(saved==expected,'Private backup metadata equality')
        need(set(z.namelist())==set(saved['files'])|{'_private-backup-manifest.json'},'Exact backup members')
        for n,record in saved['files'].items():
            raw = z.read(n)
            need(len(raw)==record['bytes'] and digest(raw)==record['sha256'],'Original backup byte equality: '+n)
    return saved


def check_public():
    record = json.loads((ROOT/PUBLIC).read_bytes())
    for n,item in record['files'].items():
        need(digest((ROOT/n).read_bytes())==item['public_sha256'],'Public derivative digest: '+n)
    labels = aliases()
    residual = [n for n,(_,t) in inventory().items() if HOME.search(t) or redact(t,labels)!=t]
    need(not residual,'Remaining personal path/account fields: '+str(residual[:10]))
    return dict(passed=True,public_derivatives=len(record['files']),residual_personal_fields=0,
                original_receipt_replay_claimed=False,Git_history_rewritten=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument('--plan',action='store_true')
    action.add_argument('--backup',type=Path,metavar='PRIVATE_DIRECTORY')
    action.add_argument('--check',action='store_true')
    action.add_argument('--verify-private',type=Path)
    action.add_argument('--patch-batch',type=Path,metavar='PRIVATE_ZIP')
    action.add_argument('--prepare-private-plan',type=Path,metavar='ORIGINAL_PRIVATE_ZIP')
    action.add_argument('--public-manifest',type=Path,metavar='PRIVATE_PLAN_ZIP')
    p.add_argument('--offset',type=int,default=0)
    p.add_argument('--limit',type=int,default=8)
    p.add_argument('--patch-part',type=int)
    p.add_argument('--part-chars',type=int,default=48000)
    a = p.parse_args()
    if a.check:
        print(json.dumps(check_public()));return
    if a.verify_private:
        saved=verify_backup(a.verify_private)
        print(json.dumps(dict(verified=True,original_files=len(saved['files']),HEAD=saved['HEAD'])));return
    if a.public_manifest:
        with zipfile.ZipFile(a.public_manifest) as z:
            public=json.loads(z.read('_public-manifest.json'))
            for name,item in public['files'].items():
                old=z.read('original/'+name).decode()
                new=z.read('public/'+name).decode()
                item['dependent_text_hash_pins_changed']=HEX.findall(new)!=HEX.findall(old)
            print(json.dumps(public,indent=2))
        return
    if a.prepare_private_plan:
        saved=verify_backup(a.prepare_private_plan)
        with zipfile.ZipFile(a.prepare_private_plan) as z:
            files={n:(z.read(n),z.read(n).decode('utf-8')) for n in saved['files']}
        texts,changed,iterations=plan(files,aliases())
        public=dict(schema='TSL9-public-path-redaction-v1',original_HEAD=saved['HEAD'],
                    original_receipts_preserved_privately=True,Git_history_rewritten=False,
                    semantics='Personal paths/account labels and dependent text SHA pins only; historical derivatives do not replace original receipts.',
                    variables=['PROJECT_ROOT','ANALYSIS_WORKSPACE','LLVM_BIN','PYTHON','RADARE2','HOME','LOCAL_ACCOUNT'],
                    hash_reference_closure_iterations=iterations,files=changed)
        output=a.prepare_private_plan.with_name(a.prepare_private_plan.stem+'-public-plan-'+uuid.uuid4().hex+'.zip')
        with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr('_public-manifest.json',json.dumps(public,indent=2)+'\n')
            for n in changed:
                z.writestr('original/'+n,files[n][0]);z.writestr('public/'+n,texts[n].encode())
        with zipfile.ZipFile(output) as z:
            for n,item in changed.items():
                need(digest(z.read('original/'+n))==item['original_sha256'] and
                     digest(z.read('public/'+n))==item['public_sha256'],'Prepared immutable edit byte equality')
        print(json.dumps(dict(cache=str(output),files=len(changed),direct=sum(v['personal_path_or_label_changed'] for v in changed.values()),
                              original_backup_sha256=digest(a.prepare_private_plan.read_bytes()),
                              plan_sha256=digest(output.read_bytes()),hash_reference_depth=iterations+1)))
        return
    if a.patch_batch:
        with zipfile.ZipFile(a.patch_batch) as z:
            public=json.loads(z.read('_public-manifest.json'));changed=public['files']
            names=sorted(changed)[a.offset:a.offset+a.limit]
            files={n:(z.read('original/'+n),z.read('original/'+n).decode()) for n in names}
            texts={n:z.read('public/'+n).decode() for n in names}
        output=[]
        for name in names:
            raw=(ROOT/name).read_bytes();old=files[name][1];new=texts[name]
            need(digest(files[name][0])==changed[name]['original_sha256'] and digest(new.encode())==changed[name]['public_sha256'],'Immutable edit-cache hashes')
            if raw!=new.encode() and raw.replace(b'\r\n',b'\n')==new.encode():
                output.append(dict(path=name,replace_with=new))
                continue
            need(digest(raw) in (changed[name]['original_sha256'],changed[name]['public_sha256']),
                 'File changed outside the plan: '+name)
            if digest(raw)==changed[name]['public_sha256']:continue
            diff=list(difflib.unified_diff(old.splitlines(),new.splitlines(),n=2,lineterm=''))[2:]
            # apply_patch uses its own file header and optional line-free @@.
            diff=[re.sub(r'^@@.*@@$','@@',line) if line.startswith('@@') else line for line in diff]
            output.append(dict(path=name,patch='\n'.join(diff)))
        serialized=json.dumps(dict(total=len(changed),offset=a.offset,files=output))
        if a.patch_part is not None:
            need(a.patch_part>=0 and a.part_chars>0,'Positive patch fragment bounds')
            count=(len(serialized)+a.part_chars-1)//a.part_chars
            need(a.patch_part<count,'Patch fragment index')
            print(json.dumps(dict(parts=count,part=a.patch_part,
                                  fragment=serialized[a.patch_part*a.part_chars:(a.patch_part+1)*a.part_chars])))
        else:
            print(serialized)
        return
    files=inventory()
    if a.backup:
        output=backup(files,a.backup)
        print(json.dumps(dict(backup=str(output),sha256=digest(output.read_bytes()),files=len(files))));return
    _,changed,iterations=plan(files,aliases())
    print(json.dumps(dict(schema='TSL9-public-path-redaction-v1',original_HEAD=git('rev-parse','HEAD'),
                         original_receipts_preserved_privately=True,Git_history_rewritten=False,
                         semantics='Personal paths/account labels and dependent text SHA pins only; historical derivatives do not replace original receipts.',
                         variables=['PROJECT_ROOT','ANALYSIS_WORKSPACE','LLVM_BIN','PYTHON','RADARE2','HOME','LOCAL_ACCOUNT'],
                         hash_reference_closure_iterations=iterations,files=changed),indent=2))


if __name__=='__main__':
    main()
