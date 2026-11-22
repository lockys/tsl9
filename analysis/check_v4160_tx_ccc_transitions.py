"""Original/C/C++ selected TX spans, with projected CCC lookup results (not resident execution)."""
from itertools import product
from check_v4160_linked_tx_selection import run, patched_engine, image, need
import sys


def query(page, count, handle):
    need(len(page) >= 4 * count, 'short CCC fixture')
    for off in range(0, 4 * count, 4):
        if int.from_bytes(page[off:off+2], 'little') == handle:
            return page[off+2]
    return 0


def main(app,c,cpp):
    engine,_ = patched_engine()
    linked = 'ef9d3be753f02d5802a2c2feda99aa94b9b3c3acc2b55d32f8f480719d658a54'
    codes = [image(p,d) for p,d in ((app,'0ee64183daaa140acac7dbb6c0f7c26d1fe625344ed158151731a9b2632fb667'),(c,linked),(cpp,linked))]
    h=7
    # Each snapshot has two rows; fourth byte deliberately differs from value.
    pages=[(bytes([7,0,a,99,7,0,b,88]),n) for a,b,n in product((0,1,3),(0,1),(0,1,2))]
    pages += [(bytes([8,0,1,99,7,0,1,88]),2)]
    stable=changed=single=0
    for p,n in pages:
        for q,m in pages:
            u,v=query(p,n,h),query(q,m,h)
            # Independent expected value from the fixture layout, not query().
            def allowed(buf,k): return k>0 and (buf[2]==1 if buf[0]==7 else k==2 and buf[6]==1)
            for first_match in (True,False):
                x=h if first_match else 8
                want=0 if first_match and allowed(p,n) else (1 if allowed(q,m) else None)
                # Only the second snapshot is queried when the first handle does not match.
                states=[run(engine,code,h,x,h,h,u,v) for code in codes]
                need(states[0]==states[1]==states[2] and states[0][0]==want,'TX selection')
                if first_match and (p,n)==(q,m):
                    need(want!=1,'stable duplicate-handle query'); stable+=1
                if first_match and want==1: changed+=1
                if not first_match and (p,n)==(q,m) and want==1: single+=1
    need((stable,changed,single)==(19,70,5),'case coverage')
    print('PASS 722 cases/profile: stable duplicate handles 19; two-query bank1 70; stable single-query bank1 5')


if __name__=='__main__': main(*sys.argv[1:])
