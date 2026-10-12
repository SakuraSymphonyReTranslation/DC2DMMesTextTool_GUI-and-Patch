"""Execute the original native layout/parser/character queue in Unicorn."""
import argparse
import json
from pathlib import Path
import struct
import unittest

import pefile
from unicorn.x86_const import *
from test_backlog import NativeLookup, SP
from patch_line_pitch import build, HOOK


def put(uc,address,value):
    uc.mem_write(address,struct.pack('<I',value & 0xffffffff))


def get(uc,address):
    return struct.unpack('<i',uc.mem_read(address,4))[0]


def layout(machine,pitch,layer=10,name=0):
    uc=machine.uc
    put(uc,0xC294DC,pitch)
    put(uc,SP+24,name)
    uc.reg_write(UC_X86_REG_ESP,SP)
    uc.reg_write(UC_X86_REG_EBX,layer)
    uc.reg_write(UC_X86_REG_EFLAGS,0x246)
    uc.emu_start(HOOK,HOOK+6,count=100)
    assert uc.reg_read(UC_X86_REG_EIP)==HOOK+6
    assert uc.reg_read(UC_X86_REG_ESP)==SP
    assert uc.reg_read(UC_X86_REG_EFLAGS)==0x246
    assert uc.reg_read(UC_X86_REG_EBX)==layer
    return get(uc,0xC294DC)


def glyphs(machine,text,pitch):
    uc=machine.uc
    address=SP+0x2000
    uc.mem_write(address,text+b'\0')
    for a,v in [(0x4962C0,364),(0x4962C4,440),(0xBF99A0,364),(0xBD5628,440),
                (0x4962C8,pitch),(0xBE3F90,22),(0x4DA0E4,0),(0x4E67DC,0),
                (0xC29290,0),(0x49629C,0),(0x4E7924,364),(0x4E7928,440)]:
        put(uc,a,v)
    put(uc,SP,0x400000)
    put(uc,SP+4,address)
    put(uc,SP+8,143)
    uc.reg_write(UC_X86_REG_ESP,SP)
    uc.emu_start(0x426400,0x400000,count=200000)
    assert uc.reg_read(UC_X86_REG_EIP)==0x400000,hex(uc.reg_read(UC_X86_REG_EIP))
    n=get(uc,0x4E67DC)
    return [struct.unpack('<iiii4s',uc.mem_read(0x4E697C+20*i,20)) for i in range(n)]


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=ARGS.exe.read_bytes()
        cls.patched,cls.manifest=build(cls.source)
        cls.before=NativeLookup(cls.source)
        cls.after=NativeLookup(cls.patched)

    def test_scope_and_registers(self):
        for layer in [0,1,10,12,13]:
            for name in [0,1]:
                for pitch in [-36,-32,0,1,2,22,24,30,32,36,40]:
                    expected=24 if (layer,name,pitch)==(10,0,32) else pitch
                    self.assertEqual(layout(self.after,pitch,layer,name),expected)

    def test_native_glyph_commands(self):
        samples=[b'Benar juga. Untuk saat ini, mungkin sebaiknya\nkita sebutkan saja apa pun yang terlintas\ndi pikiran, lalu setelah terkumpul baru kita\nseleksi',
                 b'Sesuai dengan perkataannya, meski sudah jam\npulang sekolah, sebagian besar siswa masih\nbertahan di kelas, kecuali segelintir orang\nyang memang punya urusan yang sangat mendesak.',
                 'あいうえお\n漢字とかな\nかきくけこ\nさしすせそ'.encode('cp932'),
                 b'@sSmall\n@mNormal\n@lLarge\n@mNormal',
                 '漢｛かん｝字\n二行目\n三行目\n四行目'.encode('cp932')]
        for sample in samples:
            old=glyphs(self.before,sample,layout(self.before,32))
            new=glyphs(self.after,sample,layout(self.after,32))
            self.assertEqual(len(old),len(new))
            self.assertGreater(len(old),10)
            # Actual native 20-byte glyph records: X, Y, size, colour, encoded char.
            # Everything except Y must remain identical, including JP/style/ruby.
            deltas=set()
            for a,b in zip(old,new):
                self.assertEqual((a[0],a[2:]),(b[0],b[2:]))
                deltas.add(a[1]-b[1])
            self.assertEqual(deltas,{0,8,16,24})

    def test_preserve_sections(self):
        a,b=pefile.PE(data=self.source),pefile.PE(data=self.patched)
        self.assertTrue(b.verify_checksum())
        for old,new in zip(a.sections,b.sections):
            self.assertEqual(old.__pack__(),new.__pack__())
            data=bytearray(old.get_data())
            if old.Name.rstrip(b'\0')==b'.text':
                offset=HOOK-0x400000-old.VirtualAddress
                data[offset:offset+6]=new.get_data()[offset:offset+6]
            self.assertEqual(bytes(data),new.get_data())

    def test_portraits(self):
        for name in ['Yoshiyuki','義之','Maya','Otome','Yuuki','Unknown','']:
            self.assertEqual(self.before.lookup(name),self.after.lookup(name))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('exe',type=Path)
    p.add_argument('--output',type=Path,required=True)
    ARGS=p.parse_args()
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
    report={'passed':result.wasSuccessful(),'tests':result.testsRun,'manifest':Tests.manifest,
            'comparison':'Actual x86 layout and full text parser + glyph queue; no font changes; each glyph X/size/colour/bytes identical and Y moves by 0/8/16/24 px.'}
    ARGS.output.write_text(json.dumps(report,indent=2)+'\n')
    raise SystemExit(not result.wasSuccessful())
