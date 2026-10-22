"""Bounded ELF/role helpers for the independent thirteen-region image review."""
import hashlib
import json
from pathlib import Path
import re
import runpy
from collections import Counter

TX='.text.tsl9v4160.code_continuation_8a56'
CANONICAL='__tsl9v4160_call_8a56'
FW='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'
PARSER='00a231e3bbd881a9961c12fefd15565364cd813250a46a7b20851a6b9f3a2141'
HELPER='4d7e1b4ffa5101347970a662390c4cb8ff6455161e47d6e68f2144a27b8ca7e1'
OLD_REVIEW='bbd6a2ed530e299e53aae8980dc02c39ef5640f6df70b1452515846b6f9319cc'


def need(value,message):
    if not value:
        raise ValueError(message)


def H(raw):
    return hashlib.sha256(raw).hexdigest()


def sha(path):
    return H(path.read_bytes())


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'))


def count(values):
    return Counter(canonical(v) for v in values)


def digest(values):
    return H(canonical(sorted(count(values).items())).encode())


def case(root,slug):
    return next(p for p in (root/'apk-analysis'/('tsl9-'+slug),root/'analysis'/slug) if p.is_dir())


def pinned(path,pin):
    need(sha(path)==pin,'Pinned source dependency: '+path.name)
    return runpy.run_path(str(path))


def context(root):
    helper=pinned(case(root,'v4160-flash-image-integration-2026-10-22')/'ABI-review/review.py',HELPER)
    parser=pinned(case(root,'v4160-irq-native-2026-10-21')/'compiler-review/elf32.py',PARSER)
    return dict(old=helper,ELF=parser['ELF'])


def roles(e,c):
    referenced={canonical(c['old']['role'](e,r['symbol'],e.kind==2)) for r in e.relocations}
    out=[]
    for s in e.symbols:
        r=c['old']['role'](e,s,e.kind==2)
        if (not r['info'] and not r['bytes'] and not r['other'] and
            re.fullmatch(r'\$[xd](?:\.\d+)?',r['name']) and canonical(r) not in referenced):
            r['name']=r['name'].split('.')[0]
        out.append(r)
    return out


def non_TX_relocations(e,c,old_size):
    result=[];projected=[]
    for raw in e.relocations:
        if raw['owner']==TX:
            continue
        r=c['old']['relocation'](e,raw)
        if r['symbol']['name']==CANONICAL:
            need(r['symbol']==dict(name=CANONICAL,owner=TX,offset=0,bytes=old_size,info=18,other=0),
                 'Canonical incoming target remains real allocated section-relative FUNC')
            r['symbol']['bytes']=8
            projected.append(dict(owner=r['owner'],offset=r['offset'],type=r['type'],addend=r['addend']))
        result.append(r)
    need(len(projected)==9,'Exactly nine recorded external TX references receive the explicit FUNC-size projection')
    return result,projected


def write(path,value):
    path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
