"""Local reset/masked-writer origins and decoded index/field envelopes."""
import hashlib
from oracle import need,sx
def derive(image):
    need(len(image)==76800 and hashlib.sha256(image).hexdigest()=='0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667','APP identity')
    def raw(pc,n):return image[pc-0x8000:pc-0x8000+n]
    def pair(pc,rd):
        u,a=int.from_bytes(raw(pc,4),'little'),int.from_bytes(raw(pc+4,4),'little')
        need(u&127==0x17 and u>>7&31==rd and a&0x707f==0x13 and a>>7&31==rd and a>>15&31==rd,'AUIPC/ADDI')
        return (pc+(u&0xfffff000)+sx(a>>20,12))&0xffffffff
    gp=pair(0x186aa,3);zero_end=pair(0x186e2,11)
    need(raw(0x186de,26)==bytes.fromhex('138501089745ff1f938565276377b500232005001105e36db5fe'),'reset zero loop')
    # Actual loop window ends at 186f8; expected bytes above are 26 bytes.
    need(gp==0x20004000 and gp+128<=gp+176<zero_end,'counter belongs to configured zero range')
    need(raw(0xa0f2,12)==bytes.fromhex('83c7010b85078d8b2388f10a'),'first local masked writer')
    need(raw(0xa33a,18)==bytes.fromhex('83c7010b85078d8b22442388f10ab2409244'),'second local masked writer and restores')
    histogram=[0]*4
    for old in range(256):histogram[(old+1)&3]+=1
    base=pair(0xa14e,15)
    need(raw(0xa146,8)==bytes.fromhex('83c7010b13971700') and raw(0xa156,6)==bytes.fromhex('ba9783d70700'),'fresh byte index, shift and halfword read')
    need(base==0x1ab48,'selected window base')
    addresses=[base+2*i for i in range(256)]
    need(addresses[-1]+2==0x1ad48,'byte-index envelope')
    values=[int.from_bytes(raw(base+2*i,2),'little') for i in range(4)]
    need(values==[150,180,65386,65356],'four selected halfwords')
    accepted=[v for v in range(4096) if ((v-1961)&65535)<=178]
    need(accepted==list(range(1961,2140)),'12-bit field gate')
    need(raw(0xa122,16)==bytes.fromhex('93877785c207c1831307200b636df70a'),'actual subtract/low16/upper guard')
    return dict(reset_counter_address=hex(gp+176),reset_zero_word_PC='0x186ee',reset_counter_zero_is_conditional_on_reset_execution=True,
        local_masked_writer_PCs=['0xa0fa','0xa344'],old_byte_values_checked=256,masked_result_histogram=histogram,
        read_PC='0xa158',read_index_PC='0xa146',read_has_no_local_index_mask=True,
        selected_window_start=hex(base),selected_window_end_exclusive='0x1ab50',selected_halfwords=values,
        selected_numeric_outputs=[(v+2050)&65535 for v in values],byte_index_envelope_end_exclusive='0x1ad48',
        byte_index_values_checked=256,envelope_bytes=512,envelope_bytes_beyond_APP=328,
        geometry_fields_checked=4096,accepted_geometry_fields=[1961,2139],global_index_invariant_proved=False,
        original_full_table_extent_proved=False,unselected_table_values_modeled=0)
