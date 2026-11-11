import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('scan', Path(__file__).resolve().parents[1] / 'scripts/scan-rf-pointer-direct.py')
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)

class PointerScanTests(unittest.TestCase):
    def test_actual_image_and_mutation(self):
        data = scan.IMAGE.read_bytes()
        hits = scan.verify(data)
        self.assertEqual([x['access_pc'] for x in hits], ['0x40e82', '0x59ef4', '0x6092c', '0x64334'])
        for index in (0, 0x40e82 - scan.BASE, len(data)-1):
            mutated = bytearray(data)
            mutated[index] ^= 1
            with self.assertRaises(ValueError):
                scan.verify(mutated)
        with self.assertRaises(ValueError):
            scan.verify(data[:-1])

    def test_store_and_alias_mutations(self):
        # lui a4,0x20003; addi a4,a4,0x514; c.sw a5,36(a4)
        lui = (0x20003737).to_bytes(4, 'little')
        addi = (0x51470713).to_bytes(4, 'little')
        csw = (0xd35c).to_bytes(2, 'little')
        hit = scan.scan(lui + addi + csw)
        self.assertEqual(len(hit), 1)
        self.assertEqual((hit[0]['kind'], hit[0]['source_register']), ('store', 15))
        altered = bytearray(lui + addi + csw)
        altered[4] ^= 0x80  # change ADDI destination: no same-register alias
        self.assertEqual(scan.scan(altered), [])
        # Direct sw a5,0x538(a4)
        sw = ((0x538 >> 5) << 25 | 15 << 20 | 14 << 15 | 2 << 12 | (0x538 & 31) << 7 | 0x23).to_bytes(4, 'little')
        self.assertEqual(scan.scan(lui + sw)[0]['source_register'], 15)
        self.assertEqual(scan.scan(lui + sw[:-1]), [])

if __name__ == '__main__':
    unittest.main()
