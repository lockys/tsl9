"""Independent compiler-preobject to scheduled-postobject byte/data comparison."""
import hashlib
import json

TOOL='dc680558aca230a54e1fc05f68960f85f4566b0928787caef21839cdd876535d'
POLICY='2af7789f91ceabca11fc29eb264991b96f40664555cdfe08964284f1470a694d'
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(raw):
    word=int.from_bytes(raw,'little');need(word>>13==6 and word&3==2,'Only existing C.SWSP halfwords');return [(word//4)%32,((word//512)%16)*4+((word//128)%4)*64]
def inspect(root,folder,c):
    pre=folder/'compiler-integrated.o';post=folder/'source-integrated.o';before=c['E'](pre);after=c['E'](post);G=c['G'];need(before.kind==after.kind==1 and before.flags==after.flags==1,'Actual integer RV32 relocatable pair')
    need(before.sections==after.sections and before.symbols==after.symbols and before.relocations==after.relocations and len(before.raw)==len(after.raw),'Actual complete ELF metadata/symbol/RELA/size identity')
    for row in c['selected']:
        name=row['name'];rels=[r for r in c['new_owned'] if r['owner']==name];need(G.canonical_code(before.data(before.byname[name]),rels)==G.canonical_code(c['compiler_native'][name],rels),'Every compiler-only native body from sealed component evidence')
    model=root/'experiments/tsl9-v4160-frame-schedule';policy_path=model/'frame-policy.json';need(sha(model/'schedule.py')==TOOL and sha(policy_path)==POLICY,'Exact source-reviewed scheduler and policy');policy=json.loads(policy_path.read_text(encoding='utf-8'));expected=bytearray(before.raw);functions=[]
    for name,rule in policy['functions'].items():
        matches=[s for s in before.symbols if s['name']==rule['symbol']];need(len(matches)==1,'One actual compiled source provider');symbol=matches[0];section=before.sections[symbol['index']];need(section['name']==rule['section'] and section['size']==symbol['size']==rule['bytes'] and symbol['value']==0 and symbol['info']==18 and symbol['other']==0,'Original-size source-owned executable provider')
        a=before.data(section);lo=2;hi=lo+2*len(rule['compiler_order']);words=[a[i:i+2] for i in range(lo,hi,2)];pairs=[save(x) for x in words];need(pairs==rule['compiler_order'],'Actual observed compiler save sequence');mapping={tuple(pair):word for pair,word in zip(pairs,words)};need(len(mapping)==len(words) and set(mapping)=={tuple(x) for x in rule['required_order']},'Permutation of the same existing disjoint save words')
        replacement=b''.join(mapping[tuple(x)] for x in rule['required_order']);need(sorted(words)==sorted(replacement[i:i+2] for i in range(0,len(replacement),2)),'No word synthesis');expected[section['offset']+lo:section['offset']+hi]=replacement;functions.append(name)
    need(bytes(expected)==after.raw,'Every output byte is exactly the independent existing-word permutation');changed=[i for i,(a,b) in enumerate(zip(before.raw,after.raw)) if a!=b];need(len(changed)==14,'Exactly14 whole-object changed bytes')
    receipt=folder/'frame-scheduling.json';r=json.loads(receipt.read_text(encoding='utf-8'));need(r['tool_sha256']==TOOL and r['policy_sha256']==POLICY and r['input']['sha256']==sha(pre) and r['output']['sha256']==sha(post) and r['changed_file_offsets']==changed,'Current actual scheduling receipt identities')
    need((root/r['input']['path']).resolve()==pre.resolve() and (root/r['output']['path']).resolve()==post.resolve(),'Actual recorded scheduling path association')
    return {'actual_compiler_object_sha256':sha(pre),'actual_scheduled_object_sha256':sha(post),'actual_receipt_sha256':sha(receipt),'actual_changed_bytes':14,'existing_words_only':True,'metadata_symbols_RELA_identical':True,'actual_functions':functions,'compiler_alone_emitted_scheduled_order':False,'original_BIN_read_for_generation':False,'source_origin_authenticated_by_ELF_shape_alone':False,'computed_interior_entries_proved_absent':False,'target_execution':False}
