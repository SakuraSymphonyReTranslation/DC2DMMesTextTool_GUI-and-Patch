"""Regression tests using the actual x86 game lookup, including its CRT code.

Only the history-index accessor is stubbed (return the prepared history slot).
Rendering is stopped at the native result branch; no simulated lookup algorithm.
"""
import argparse
import json
from pathlib import Path
import struct
import unittest

import pefile
from unicorn import Uc, UC_ARCH_X86, UC_MODE_32, UC_HOOK_CODE, UC_PROT_READ, UC_PROT_WRITE, UC_PROT_EXEC
from unicorn.x86_const import UC_X86_REG_EAX, UC_X86_REG_EBP, UC_X86_REG_EBX, UC_X86_REG_ECX, UC_X86_REG_EDI, UC_X86_REG_EDX, UC_X86_REG_EFLAGS, UC_X86_REG_EIP, UC_X86_REG_ESI, UC_X86_REG_ESP

from patch_backlog import BASE, NAMES, REFERENCES, TABLE_VA, aliases, align, build

STACK_BASE, STACK_SIZE, SP = 0x2000000, 0x10000, 0x2008000


class NativeLookup:
    def __init__(self, image):
        self.pe = pefile.PE(data=image)
        self.uc = Uc(UC_ARCH_X86, UC_MODE_32)
        uc = self.uc
        uc.mem_map(BASE, self.pe.OPTIONAL_HEADER.SizeOfImage)
        uc.mem_write(BASE, self.pe.get_memory_mapped_image())
        uc.mem_protect(BASE, align(self.pe.OPTIONAL_HEADER.SizeOfHeaders, 4096), UC_PROT_READ)
        for section in self.pe.sections:
            permissions = 0
            for flag, permission in [(0x40000000, UC_PROT_READ), (0x80000000, UC_PROT_WRITE), (0x20000000, UC_PROT_EXEC)]:
                if section.Characteristics & flag:
                    permissions |= permission
            uc.mem_protect(BASE + section.VirtualAddress, align(max(section.Misc_VirtualSize, section.SizeOfRawData), 4096), permissions)
        uc.mem_map(STACK_BASE, STACK_SIZE, UC_PROT_READ | UC_PROT_WRITE)
        uc.hook_add(UC_HOOK_CODE, self.history_index, begin=0x410830, end=0x410830)
        self.calls = 0

    @staticmethod
    def history_index(uc, address, size, data):
        sp = uc.reg_read(UC_X86_REG_ESP)
        ret, = struct.unpack("<I", uc.mem_read(sp, 4))
        uc.reg_write(UC_X86_REG_EAX, 0)
        uc.reg_write(UC_X86_REG_ESP, sp + 4)
        uc.reg_write(UC_X86_REG_EIP, ret)

    def lookup(self, name, scene="sin_0401_a2"):
        uc = self.uc
        data = name.encode("cp932") if isinstance(name, str) else name
        assert len(data) < 256 and len(scene.encode("ascii")) < 32
        uc.mem_write(SP - 0x100, bytes(0x900))
        uc.mem_write(SP + 0x28, data + b"\0")
        uc.mem_write(0xBF4858, scene.encode("ascii").ljust(32, b"\0"))
        uc.mem_write(0xB6A18C, struct.pack("<I", 0))
        for register in [UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX, UC_X86_REG_EDX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP]:
            uc.reg_write(register, 0)
        uc.reg_write(UC_X86_REG_ESP, SP)
        uc.reg_write(UC_X86_REG_EFLAGS, 0x202)
        before = bytes(uc.mem_read(SP + 0x28, 256))
        uc.emu_start(0x4110AD, 0x4113F7, count=100000)
        assert uc.reg_read(UC_X86_REG_EIP) == 0x4113F7, "Lookup failed to reach its native result branch"
        assert uc.reg_read(UC_X86_REG_ESP) == SP, "Lookup unbalanced the stack"
        assert bytes(uc.mem_read(SP + 0x28, 256)) == before, "Speaker buffer changed"
        self.calls += 1
        value = uc.reg_read(UC_X86_REG_EBX)
        return value if value < 0x80000000 else value - 0x100000000


class BacklogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = ARGS.exe.read_bytes()
        cls.patched, cls.manifest = build(cls.original)
        cls.before = NativeLookup(cls.original)
        cls.after = NativeLookup(cls.patched)
        cls.report = json.loads(ARGS.audit.read_text(encoding="utf-8"))

    def test_01_pe_and_change_scope(self):
        a, b = pefile.PE(data=self.original), pefile.PE(data=self.patched)
        self.assertEqual(b.sections[-1].Name, b".bknames")
        self.assertEqual(b.sections[-1].Characteristics, 0x40000040)
        self.assertTrue(b.verify_checksum())
        self.assertEqual(a.OPTIONAL_HEADER.AddressOfEntryPoint, b.OPTIONAL_HEADER.AddressOfEntryPoint)
        for old, new in zip(a.sections, b.sections):
            self.assertEqual(old.__pack__(), new.__pack__())
            expected = bytearray(old.get_data())
            if old.Name.rstrip(b"\0") == b".text":
                for va, _, operand, table_offset in REFERENCES:
                    struct.pack_into("<I", expected, va - BASE - old.VirtualAddress + operand,
                                     int(self.manifest["table_va"], 16) + table_offset)
            self.assertEqual(bytes(expected), new.get_data(), old.Name)
        self.assertEqual(a.get_data(TABLE_VA - BASE, 168), b.get_data(TABLE_VA - BASE, 168))
        self.assertEqual(a.OPTIONAL_HEADER.DATA_DIRECTORY.__repr__(), b.OPTIONAL_HEADER.DATA_DIRECTORY.__repr__())

    def test_02_reject_other_or_already_patched_executables(self):
        for data in [b"", self.original[:-1], self.patched, self.original[:100] + b"X" + self.original[101:]]:
            with self.assertRaises(ValueError):
                build(data)

    def test_03_all_original_and_translated_names(self):
        scenes = ["sin_0401_a2", "suc60_1110_f1_otm", "suc60_0101_a1_otm", "suc61_0101_a1_otm",
                  "suc65_0101_a1_otm", "suc66_0101_a1_otm", "suc68_0101_a1_otm", "suc69_0101_a1_otm",
                  "suc71_0101_a1_otm", "suc74_0131_a1_otm", "suc74_0201_a1_otm", "suc74_0203_a1_otm",
                  "suc74_0214_a1_otm", "suc74_0325_a1_otm", "suc74_1011_f1_otm", "suc75_0101_a1_otm",
                  "SUC75_0101_A1_OTM"]
        for _, _, japanese, translations in NAMES:
            for scene in scenes:
                expected = self.before.lookup(japanese, scene)
                with self.subTest(name=japanese, scene=scene):
                    self.assertEqual(self.after.lookup(japanese, scene), expected)
                for name in translations:
                    with self.subTest(name=name, scene=scene):
                        self.assertEqual(self.before.lookup(name, scene), -1)
                        self.assertEqual(self.after.lookup(name, scene), expected)

    def test_04_otome_yuuki_for_every_translated_script(self):
        for filename in self.report["input_hashes"]:
            scene = Path(filename).stem
            for japanese, name in [("音姫", "Otome"), ("桜姫", "Yuuki")]:
                with self.subTest(scene=scene, name=name):
                    self.assertEqual(self.after.lookup(name, scene), self.before.lookup(japanese, scene))
        for name, scene, icon in [("Otome", "sin_0401_a2", 0), ("Otome", "suc60_1110_f1_otm", 19),
                                   ("Otome", "suc75_0101_a1_otm", 19), ("Yuuki", "sin_0401_a2", 20),
                                   ("Yuuki", "suc65_0101_a1_otm", 21), ("Yuuki", "suc71_0101_a1_otm", 22),
                                   ("Yuuki", "suc74_0131_a1_otm", 22), ("Yuuki", "suc75_0101_a1_otm", 23)]:
            self.assertEqual(self.after.lookup(name, scene), icon)

    def test_05_exact_matching_and_native_fallback(self):
        unknown = set(self.report["unmapped_names"])
        unknown.update(["", "Yoshiyuki", "義之", "?", "Unknown", "μ", "Mu", "Myu", "Otome & Yume", "Otome dan Yume", "x" * 255])
        accepted = {name for _, name in aliases()}
        for _, name in aliases():
            unknown.update([name + "X", "X" + name, name + " ", " " + name, name.lower(), name.upper()])
            if name[:-1] not in accepted:
                unknown.add(name[:-1])
        for name in unknown:
            # Name fields have a 256-byte native buffer. Very long malformed JSON
            # narration is not passed as a speaker in this isolated test.
            if len(name.encode("cp932", errors="replace")) >= 256:
                continue
            encoded = name.encode("cp932", errors="replace")
            with self.subTest(name=name):
                self.assertEqual(self.after.lookup(encoded), self.before.lookup(encoded))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exe", type=Path, help="Verified original EXE or backup")
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    ARGS = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BacklogTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {"tests_run": result.testsRun, "passed": result.wasSuccessful(),
              "failures": len(result.failures), "errors": len(result.errors),
              "original_native_lookups": BacklogTests.before.calls,
              "patched_native_lookups": BacklogTests.after.calls,
              "comparison_implementation": "Original x86 instructions including native strncmp and _strnicmp; only history-index accessor stubbed",
              "original_sha256": BacklogTests.manifest["original_sha256"],
              "patched_sha256": BacklogTests.manifest["patched_sha256"],
              "visual_game_test": "not performed by this harness"}
    ARGS.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    raise SystemExit(0 if result.wasSuccessful() else 1)
