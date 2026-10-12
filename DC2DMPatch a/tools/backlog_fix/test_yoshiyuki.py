"""Execute the native lookup and blank-portrait render branch in Unicorn."""
import argparse
import json
from pathlib import Path
import struct
import unittest

import pefile
from unicorn import UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_ESP, UC_X86_REG_EIP

from patch_backlog import NAMES, BASE
from patch_yoshiyuki import build, MC_NAMES, BLANK_ICON
from test_backlog import NativeLookup


class YoshiyukiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.previous = ARGS.exe.read_bytes()
        cls.patched, cls.manifest = build(cls.previous)
        cls.before, cls.after = NativeLookup(cls.previous), NativeLookup(cls.patched)
        cls.drawing = False
        # An explicit hook splits cached translation blocks at the lookup
        # boundary even after a draw run has translated past that address.
        cls.after.uc.hook_add(UC_HOOK_CODE, cls.stop_lookup, begin=0x4113F7, end=0x4113F7)
        cls.audit = json.loads(ARGS.audit.read_text(encoding="utf-8"))

    @classmethod
    def stop_lookup(cls, uc, address, size, data):
        if not cls.drawing:
            uc.emu_stop()

    def test_mc_all_scenes_and_native_draw_coordinates(self):
        for filename in self.audit["input_hashes"]:
            for name in MC_NAMES:
                with self.subTest(name=name, scene=filename):
                    self.assertEqual(self.before.lookup(name, Path(filename).stem), -1)
                    self.assertEqual(self.after.lookup(name, Path(filename).stem), BLANK_ICON)
                    uc = self.after.uc
                    uc.mem_write(0xBD5628, struct.pack("<I", 40))
                    sp = uc.reg_read(UC_X86_REG_ESP)
                    # Stop immediately before the real image blit, after native
                    # instructions choose the portrait branch and source rectangle.
                    type(self).drawing = True
                    try:
                        uc.emu_start(0x4113F7, 0x411475, count=1000)
                    finally:
                        type(self).drawing = False
                    self.assertEqual(uc.reg_read(UC_X86_REG_EIP), 0x411475)
                    self.assertEqual(uc.reg_read(UC_X86_REG_ESP), sp - 32)
                    self.assertEqual(struct.unpack("<8I", uc.mem_read(sp - 32, 32)),
                                     (0, 240, 40, 356, 156, 748, 364, 10))

    def test_existing_names_and_scene_variants(self):
        for filename in self.audit["input_hashes"]:
            scene = Path(filename).stem
            for _, _, jp, translations in NAMES:
                for name in [jp, *translations]:
                    with self.subTest(name=name, scene=scene):
                        self.assertEqual(self.after.lookup(name, scene), self.before.lookup(name, scene))

    def test_exact_name_match_and_unknown_fallback(self):
        names = set(self.audit["unmapped_names"]) - set(MC_NAMES)
        names.update(["", "YoshiyukiX", "XYoshiyuki", "Yoshiyuk", "Yoshiyuki ", " Yoshiyuki",
                      "yoshiyuki", "YOSHIYUKI", "義之X", "義", "義之 ", "義之たち", "Unknown", "X" * 255])
        for name in names:
            encoded = name.encode("cp932", errors="replace")
            if len(encoded) < 256:
                with self.subTest(name=name):
                    self.assertEqual(self.after.lookup(encoded), self.before.lookup(encoded))

    def test_pe_and_instructions_unchanged(self):
        old, new = pefile.PE(data=self.previous), pefile.PE(data=self.patched)
        self.assertTrue(new.verify_checksum())
        self.assertEqual(len(self.previous), len(self.patched))
        self.assertEqual(old.OPTIONAL_HEADER.SizeOfImage, new.OPTIONAL_HEADER.SizeOfImage)
        self.assertEqual(old.OPTIONAL_HEADER.AddressOfEntryPoint, new.OPTIONAL_HEADER.AddressOfEntryPoint)
        for a, b in zip(old.sections[:-1], new.sections[:-1]):
            self.assertEqual(a.__pack__(), b.__pack__())
            self.assertEqual(a.get_data(), b.get_data(), a.Name)
        self.assertEqual(old.OPTIONAL_HEADER.DATA_DIRECTORY.__repr__(), new.OPTIONAL_HEADER.DATA_DIRECTORY.__repr__())
        self.assertEqual(new.sections[-1].Characteristics, 0x40000040)
        self.assertEqual(new.get_data(int(self.manifest["table_va"], 16) - BASE + 48 * 8, 8), struct.pack("<iI", -1, 0))

    def test_reject_unexpected_or_already_patched_exe(self):
        for data in [b"", self.previous[:-1], self.patched, self.previous[:100] + b"X" + self.previous[101:]]:
            with self.assertRaises(ValueError):
                build(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exe", type=Path, help="EXE with the previous Indonesian backlog patch")
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    ARGS = parser.parse_args()
    result = unittest.TextTestRunner(verbosity=2, failfast=True).run(unittest.defaultTestLoader.loadTestsFromTestCase(YoshiyukiTests))
    report = {"tests_run": result.testsRun, "passed": result.wasSuccessful(),
              "failures": len(result.failures), "errors": len(result.errors),
              "native_lookups": YoshiyukiTests.before.calls + YoshiyukiTests.after.calls,
              "native_mc_draw_checks": 2 * len(YoshiyukiTests.audit["input_hashes"]),
              "manifest": YoshiyukiTests.manifest}
    ARGS.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=True))
    raise SystemExit(0 if result.wasSuccessful() else 1)
