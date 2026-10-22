"""Four retained BOOT response shapes, offline bounded original-opcode comparison."""
from pathlib import Path
import ast,hashlib,json,struct,subprocess,sys

_paths = __import__("runpy").run_path(str(next(p for p in Path(__file__).resolve().parents if (p / "scripts/project_paths.py").is_file()) / "scripts/project_paths.py"))
sys.dont_write_bytecode=True
W=Path(__file__).resolve().parents[3];OUT=Path(__file__).parent;ROOT=W/'exports/TSL-firmware-options-22-BINs-2026-10-20/BINs'
SHA=lambda b:hashlib.sha256(b).hexdigest();SX=lambda v,n:v-(1<<n)if v&(1<<(n-1))else v
SPECS={2349:dict(sha='8aa3d7eeeeea1a05bd41917ef5c1e6404af670e296e04b72aa322e5634c91f4e',W=(0x2246,0x22E2),S=(0x230E,0x2362),helper=0x2AE4,ack=0x22D8,UID=0x1C82,mode_PC=0x232A,origin_PC=0x226E,origin_add_PC=0x2272,sub_PC=0x225C,limit_PC=0x2280,n_PC=0x224C),2492:dict(sha='2889084225f808f799e10aa65c6fe31e01a832eed0a1ae149c681088c8e38423',W=(0x2246,0x22E2),S=(0x230E,0x2362),helper=0x2AE4,ack=0x22D8,UID=0x1C82,mode_PC=0x232A,origin_PC=0x226E,origin_add_PC=0x2272,sub_PC=0x225C,limit_PC=0x2280,n_PC=0x224C),2580:dict(sha='650cbb626d45c94ea7617c4647c6fc184bc6dcf0d21615f62c5d4b119e8162bb',W=(0x2202,0x229E),S=(0x22CA,0x231E),helper=0x2AA0,ack=0x2294,UID=0x1C82,mode_PC=0x22E6,origin_PC=0x222A,origin_add_PC=0x222E,sub_PC=0x2218,limit_PC=0x223C,n_PC=0x2208),2815:dict(sha='7d42d74eadcb675e2ae74836f4847f6f3ff334c9cfb269c72812578c7d40deaa',W=(0x227E,0x232A),S=(0x2358,0x23AE),helper=0x29A0,ack=0x2310,UID=0x1CF6,mode_PC=0x2374,origin_PC=0x2294,origin_add_PC=0x22A8,sub_PC=0x22B0,limit_PC=0x22B8,n_PC=0x2284)}

def main():
    prior=OUT.parent/'protocol-review/review.json';assert SHA(prior.read_bytes())=='9a66b861219b9d0b2307f5968bd5e44081e40ccb48600ca397713485145d0564'
    r2=_paths["radare2"]();dec=W/'apk-analysis/tsl9-v4160-platform-2026-10-20/vector-review/review-vectors.py';assert SHA(dec.read_bytes())=='0c4a0bb7e12c3be5001c7624b02e9fb1c1cd3cc78f011455485fff268b26151b'
    variants=[]
    for ident,spec in SPECS.items():
        p=ROOT/f'ID-{ident}-V1.0.00-decoded.bin';raw=p.read_bytes();assert len(raw)==12288 and SHA(raw)==spec['sha']
        b=lambda a,n:raw[a-0x1000:a-0x1000+n];word=lambda a:int.from_bytes(b(a,4),'little')
        ns={'B':raw,'BASE':0x1000,'struct':struct,'S':SX};tree=ast.parse(dec.read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in('cj','flow')],type_ignores=[]),str(dec),'exec'),ns)
        ranges=[spec['W'],spec['S'],(spec['helper'],spec['helper']+26)]
        cmd=[str(r2),'-a','riscv','-b','32','-m','0x1000','-q','-c','e scr.color=0; '+'; '.join(f'pDj {z-a} @ {a}'for a,z in ranges)+'; q',str(p)]
        text=subprocess.run(cmd,capture_output=True,check=True).stdout.decode();jd=json.JSONDecoder();pos=0;contexts=[];nodes={}
        for a,z in ranges:
            while pos<len(text)and text[pos].isspace():pos+=1
            rows,pos=jd.raw_decode(text,pos);pc=a
            for row in rows:
                n=4 if int.from_bytes(b(pc,2),'little')&3==3 else 2
                assert row['addr']==pc and row['size']==n and row['bytes']==b(pc,n).hex()and'invalid'not in row['disasm'];nodes[pc]=row;pc+=n
            assert pc==z;contexts.append(dict(start=a,end_exclusive=z,sha256=SHA(b(a,z-a)),instructions=rows))
        w=word(spec['n_PC']);assert w&0x707f==0x13 and w>>7&31==15 and w>>15&31==0 and SX(w>>20,12)==1026
        up=word(spec['origin_PC']);add=word(spec['origin_add_PC']);sub=word(spec['sub_PC']);lim=word(spec['limit_PC'])
        assert up&127==sub&127==0x37 and sub&0xfffff000==0xF7FF8000 and add&0x707f==lim&0x707f==0x13 and SX(lim>>20,12)==-256
        origin=((up&0xfffff000)+SX(add>>20,12))<<10;assert origin==0x08008000
        assert b(spec['UID'],2).hex()=='b947'and b(spec['mode_PC'],2).hex()=='0547'
        if ident==2815:
            assert b(0x2310,26).hex()=='93da8a00230f59ffa30f99fe930620401306e9ff9305700595a0'
            assert word(0x231C)&0x707f==0x13 and word(0x231C)>>7&31==13 and SX(word(0x231C)>>20,12)==1026
            assert ns['flow'](0x2328)[2]==[0x238C]and ns['flow'](0x23A0)[2]==[spec['helper']]
            response=dict(kind='full_page_echo_request',payload_length=1026,BE16_index_store_PCs=[0x2314,0x2318],payload_pointer='aligned_payload_data-2',payload_pointer_PC=0x2320,payload_bytes='BE16 index followed by the1024B aligned source region already compared to Flash',W_reply_merge_PC=0x238C,W_reply_tail_PC=0x23A0,allocator_or_extra_Flash_copy_not_present_in_this_success_slice=True,source_is_live_RAM_not_frozen_original_download=True,source_overlap_and_TX_semantics_unknown=True,APK_shape_can_accept_if_transmitted_bytes_match_download=True)
        else:
            ack=spec['ack'];assert b(ack,10).hex()=='81460146930570058da0'
            target=ns['flow'](ack+8)[2][0];tail=target+16;assert ns['flow'](tail)[2]==[spec['helper']]
            response=dict(kind='empty_payload_request',payload_length=0,payload_pointer=0,zero_length_PC=ack,zero_pointer_PC=ack+2,W_reply_merge_PC=target,W_reply_tail_PC=tail,not_onebyte_zero_status=True,APK_shape_does_not_accept_empty_W_if_PageSize1026=True)
        variant=dict(catalog_ID=ident,version_label='V1.0.00',filename_is_not_hardware_applicability=True,source=dict(path=str(p),bytes=len(raw),sha256=SHA(raw)),numeric_model_base=0x1000,W=dict(requires_active=True,exact_payload_bytes=1026,origin=origin,accepted_page_domain=[0,95],unsigned_start_offset_limit=0x17F00,response=response),S=dict(UID_helper=spec['UID'],UID_bytes=14,length_argument='uint8(n-1)',mode_compare_PC=spec['mode_PC'],accepted_mode=1,response_success='original request payload and original n restored from stack; no new2B capability construction in this slice',failure='clear active and overwrite original payload byte0 with255 before same response helper',not_Runtime_V4160_S_two_byte_capability=True),response_dispatch_helper=spec['helper'],context_and_ABI_unknown=True,raw_r2_contexts=contexts,r2_command=cmd,hardware_applicability_proved=False,actual_transmission_or_ACK_observed=False)
        variants.append(variant)
    assert [x['catalog_ID']for x in variants if x['W']['response']['kind']=='full_page_echo_request']==[2815]
    out=dict(schema='four-retained-BOOT-options-bounded-W-S-response-review-v1',passed=True,blocking_findings=[],prior_protocol_proof=dict(path=str(prior),sha256=SHA(prior.read_bytes())),variants=variants,information_gain='A retained catalogBOOT2815 requests full1026B W echo, unlike2349/2492/2580 emptyW. This can explain the fixedAPK accepting a differentBOOT response shape, but does not identify the installedBOOT or approve any image.',onebyte_zero_W_success_not_found_in_the_four_checked_success_slices=True,not_global_absence_of_other_response_paths=True,source_version_labels_do_not_establish_same_product_or_board=True,r2=dict(path=str(r2),sha256=SHA(r2.read_bytes())),static_flow_decoder=dict(path=str(dec),sha256=SHA(dec.read_bytes())),checker_sha256=SHA(Path(__file__).read_bytes()),limits=['Only the declared original W/S and response-helper slices were checked, not full transport/ROOT/resident/IRQ/hardware closure.','Page arithmetic and echo source shape are static; allocator/copy/alias, actual GATT binding/serialization and transmitted bytes remain conditional.','No installedBOOT correspondence, board compatibility, update package validity or safe replacement is proved.','No network, firmware execution/emulation, wire packets or75page repacking occurred.'],target_execution=False,emulation=False,network=False,hardware=False,flash_write_performed=False,candidate_pack_created=False,wire_frames_created=False,target_ready=False,ota_verified=False)
    (OUT/'review.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,BOOT_options=4,full_page_echo=[2815],empty_payload=[2349,2492,2580],hardware_applicability=False)))
if __name__=='__main__':main()
