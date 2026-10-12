"""Run the game's real x86 lookup and portrait-coordinate branch in Unicorn."""
import argparse
import json
from pathlib import Path
import struct
import unittest

import pefile
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP, UC_X86_REG_EIP

from patch_backlog import BASE, NAMES, SECTION_NAME
from patch_yoshiyuki import MC_NAMES
from patch_yuto_yuki import ADDITIONS, SOURCE_RECTS, build
from test_backlog import NativeLookup


class PortraitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous = ARGS.exe.read_bytes()
        cls.patched, cls.manifest = build(cls.previous)
        cls.before, cls.after = NativeLookup(cls.previous), NativeLookup(cls.patched)
        cls.audit = json.loads(ARGS.audit.read_text(encoding="utf-8"))
        cls.drawing = False
        cls.draw_checks = 0
        cls.after.uc.hook_add(UC_HOOK_CODE, cls.stop_lookup, begin=0x4113F7, end=0x4113F7)

    @classmethod
    def stop_lookup(cls, uc, address, size, data):
        if not cls.drawing:
            uc.emu_stop()

    def test_new_names_and_native_portrait_rectangles_every_scene(self):
        for filename in self.audit["input_hashes"]:
            for icon, name in ADDITIONS:
                scene = Path(filename).stem
                with self.subTest(name=name, scene=scene):
                    self.assertEqual(self.before.lookup(name, scene), -1)
                    self.assertEqual(self.after.lookup(name, scene), icon)
                    uc = self.after.uc
                    uc.mem_write(0xBD5628, struct.pack("<I", 40))
                    sp = uc.reg_read(UC_X86_REG_ESP)
                    type(self).drawing = True
                    try:
                        uc.emu_start(0x4113F7, 0x411475, count=1000)
                    finally:
                        type(self).drawing = False
                    self.assertEqual(uc.reg_read(UC_X86_REG_EIP), 0x411475)
                    self.assertEqual(uc.reg_read(UC_X86_REG_ESP), sp - 32)
                    x, y, _, _ = SOURCE_RECTS[icon]
                    self.assertEqual(struct.unpack("<8I", uc.mem_read(sp - 32, 32)), (0, 240, 40, 356, 156, x, y, 10))
                    type(self).draw_checks += 1

    def test_previous_names_yuuki_variants_and_blank_mc(self):
        names = [name for _, _, jp, aliases in NAMES for name in [jp, *aliases]] + list(MC_NAMES)
        for filename in self.audit["input_hashes"]:
            for name in names:
                scene = Path(filename).stem
                with self.subTest(name=name, scene=scene):
                    self.assertEqual(self.after.lookup(name, scene), self.before.lookup(name, scene))
        for scene, icon in [("sin_1931_f1", 20), ("suc65_0101_a1_otm", 21), ("suc71_0101_a1_otm", 22), ("suc75_0101_a1_otm", 23)]:
            self.assertEqual(self.after.lookup("Yuki", scene), 14)
            self.assertEqual(self.after.lookup("Yuuki", scene), icon)

    def test_exact_names_and_unknown_fallback(self):
        names = set(self.audit["unmapped_names"]) - {name for _, name in ADDITIONS}
        for _, name in ADDITIONS:
            names.update([name + "X", "X" + name, name + " ", " " + name, name[:-1], name.lower(), name.upper()])
        names.difference_update(name for _, name in ADDITIONS)
        for name in names:
            encoded = name.encode("cp932", errors="replace")
            if len(encoded) < 256:
                self.assertEqual(self.after.lookup(encoded), self.before.lookup(encoded), name)

    def test_pe_instruction_font_and_line_pitch_integrity(self):
        old, new = pefile.PE(data=self.previous), pefile.PE(data=self.patched)
        self.assertTrue(new.verify_checksum())
        self.assertEqual(len(self.previous), len(self.patched))
        self.assertEqual(old.OPTIONAL_HEADER.SizeOfImage, new.OPTIONAL_HEADER.SizeOfImage)
        self.assertEqual(old.OPTIONAL_HEADER.AddressOfEntryPoint, new.OPTIONAL_HEADER.AddressOfEntryPoint)
        self.assertEqual(len(old.sections), len(new.sections))
        for a, b in zip(old.sections, new.sections):
            if a.Name == SECTION_NAME:
                self.assertEqual(b.Characteristics, 0x40000040)
                self.assertEqual(new.get_data(b.VirtualAddress + 52 * 8, 8), struct.pack("<iI", -1, 0))
            else:
                self.assertEqual(a.__pack__(), b.__pack__())
                self.assertEqual(a.get_data(), b.get_data(), a.Name)
        self.assertEqual(old.OPTIONAL_HEADER.DATA_DIRECTORY.__repr__(), new.OPTIONAL_HEADER.DATA_DIRECTORY.__repr__())

    def test_reject_unexpected_and_already_patched_exe(self):
        for source in [b"", self.previous[:-1], self.patched, self.previous[:100] + b"X" + self.previous[101:]]:
            with self.assertRaises(ValueError):
                build(source)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exe", type=Path)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    ARGS = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2, failfast=True).run(unittest.defaultTestLoader.loadTestsFromTestCase(PortraitTests))
    report = {"tests_run": result.testsRun, "passed": result.wasSuccessful(), "failures": len(result.failures), "errors": len(result.errors),
              "native_lookups": PortraitTests.before.calls + PortraitTests.after.calls,
              "native_portrait_draw_checks": PortraitTests.draw_checks, "manifest": PortraitTests.manifest}
    ARGS.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    raise SystemExit(0 if result.wasSuccessful() else 1)
