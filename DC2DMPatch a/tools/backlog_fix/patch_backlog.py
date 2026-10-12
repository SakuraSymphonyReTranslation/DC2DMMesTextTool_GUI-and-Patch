"""Add Indonesian aliases to the verified DC2DM backlog portrait table.

Requires pefile. Builds a separate candidate by default; --install also creates
an exact backup and atomically replaces the verified original EXE.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
from datetime import datetime

import pefile

BASE = 0x400000
ORIGINAL_SHA256 = "377fa93b408b829b5e44198f441a9ef2805c0881d374899641e320e076c19d0c"
TABLE_VA = 0x48B4B0
SECTION_NAME = b".bknames"

# Original ID, original Shift-JIS name address, Japanese name, reviewed aliases.
# IDs are consumed by the game's existing scene-dependent portrait selection.
NAMES = [
    (0, 0x46A9B4, "音姫", ["Otome"]),
    (1, 0x46A9AC, "由夢", ["Yume"]),
    (2, 0x46A9A4, "小恋", ["Koko"]),
    (3, 0x46A99C, "ななか", ["Nanaka"]),
    (4, 0x46A998, "杏", ["Anzu"]),
    (5, 0x46A990, "美夏", ["Minatsu"]),
    (6, 0x46A988, "エリカ", ["Erika"]),
    (7, 0x46A984, "渉", ["Wataru"]),
    (8, 0x46A980, "茜", ["Akane"]),
    (9, 0x46A978, "麻耶", ["Maya"]),
    (10, 0x46A970, "まゆき", ["Mayuki"]),
    (11, 0x46A968, "杉並", ["Suginami"]),
    (12, 0x46A960, "さくら", ["Sakura"]),
    (13, 0x46A958, "水越", ["Mizukoshi"]),
    (13, 0x46A950, "舞佳", ["Maika"]),
    (16, 0x46A944, "イベール", ["Hiver", "Yver", "Yvel", "Yve", "Ivair", "Ybel", "Yvers"]),
    (18, 0x46A93C, "立夏", ["Rikka"]),
    (18, 0x46A934, "森園", ["Morizono"]),
    (20, 0x46A92C, "桜姫", ["Yuuki"]),
    (24, 0x46A920, "はりまお", ["Harimao"]),
]

# Instruction VA, complete original instruction bytes, operand offset, table offset.
REFERENCES = [
    (0x4110B6, bytes.fromhex("39 1D B0 B4 48 00"), 2, 0),
    (0x4110C2, bytes.fromhex("BD B0 B4 48 00"), 1, 0),
    (0x4110D0, bytes.fromhex("8B 96 B4 B4 48 00"), 2, 4),
    (0x411112, bytes.fromhex("8B 86 B4 B4 48 00"), 2, 4),
    (0x4113E0, bytes.fromhex("83 BE B0 B4 48 00 FF"), 2, 0),
    (0x4113E7, bytes.fromhex("8D AE B0 B4 48 00"), 2, 0),
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def align(value: int, alignment: int) -> int:
    return (value + alignment - 1) // alignment * alignment


def aliases() -> list[tuple[int, str]]:
    result = {}
    for icon, _, _, translations in NAMES:
        for name in translations:
            require(name not in result or result[name] == icon, f"Ambiguous alias: {name}")
            require(name.isascii() and name and "\0" not in name, f"Invalid alias: {name}")
            result[name] = icon
    return [(icon, name) for name, icon in result.items()]


def build(original: bytes) -> tuple[bytes, dict]:
    require(sha256(original) == ORIGINAL_SHA256, "Unsupported EXE: SHA-256 differs from the IDA-verified original")
    pe = pefile.PE(data=original)
    require(pe.FILE_HEADER.Machine == 0x14C and pe.OPTIONAL_HEADER.ImageBase == BASE, "Expected x86 image at 0x400000")
    require(pe.FILE_HEADER.TimeDateStamp == 0x551E8DB7, "Unexpected build timestamp")
    require(pe.FILE_HEADER.Characteristics & 1 != 0, "Expected relocations stripped")
    require(pe.OPTIONAL_HEADER.DllCharacteristics & 0x40 == 0, "Expected fixed-base EXE")
    require(pe.get_overlay_data_start_offset() is None, "Unexpected overlay")
    require(not pe.OPTIONAL_HEADER.DATA_DIRECTORY[5].Size, "Unexpected relocation directory")
    require(not pe.OPTIONAL_HEADER.DATA_DIRECTORY[4].Size, "Unexpected certificate directory")
    for i, (icon, ptr, jp, _) in enumerate(NAMES):
        require(pe.get_data(TABLE_VA - BASE + i * 8, 8) == struct.pack("<II", icon, ptr), f"Original table mismatch at entry {i}")
        require(pe.get_string_at_rva(ptr - BASE) == jp.encode("cp932"), f"Original name mismatch: {jp}")
    require(pe.get_data(TABLE_VA - BASE + len(NAMES) * 8, 8) == struct.pack("<iI", -1, 0), "Missing original sentinel")
    for va, expected, _, _ in REFERENCES:
        require(pe.get_data(va - BASE, len(expected)) == expected, f"Instruction mismatch at {va:#x}")

    header_offset = pe.sections[-1].get_file_offset() + 40
    require(header_offset + 40 <= pe.OPTIONAL_HEADER.SizeOfHeaders, "No section-header space")
    require(original[header_offset:header_offset + 40] == bytes(40), "Section-header space is occupied")
    last_end = max(s.VirtualAddress + max(s.Misc_VirtualSize, s.SizeOfRawData) for s in pe.sections)
    rva = align(last_end, pe.OPTIONAL_HEADER.SectionAlignment)
    require(rva == pe.OPTIONAL_HEADER.SizeOfImage, "Unexpected image layout")
    raw_offset = align(len(original), pe.OPTIONAL_HEADER.FileAlignment)
    new_table_va = BASE + rva
    translated = aliases()
    table_size = (len(NAMES) + len(translated) + 1) * 8
    table = bytearray(pe.get_data(TABLE_VA - BASE, len(NAMES) * 8))
    strings = bytearray()
    for icon, name in translated:
        table.extend(struct.pack("<II", icon, new_table_va + table_size + len(strings)))
        strings.extend(name.encode("ascii") + b"\0")
    table.extend(struct.pack("<iI", -1, 0))
    payload = table + strings
    raw_size = align(len(payload), pe.OPTIONAL_HEADER.FileAlignment)
    patched = bytearray(original)
    patched.extend(bytes(raw_offset - len(patched)))
    patched.extend(payload)
    patched.extend(bytes(raw_size - len(payload)))

    # PE bookkeeping and a read-only initialized-data section, no executable code.
    struct.pack_into("<8sIIIIIIHHI", patched, header_offset, SECTION_NAME, len(payload), rva,
                     raw_size, raw_offset, 0, 0, 0, 0, 0x40000040)
    fields = [
        (pe.FILE_HEADER, "NumberOfSections", "<H", pe.FILE_HEADER.NumberOfSections + 1),
        (pe.OPTIONAL_HEADER, "SizeOfInitializedData", "<I", pe.OPTIONAL_HEADER.SizeOfInitializedData + raw_size),
        (pe.OPTIONAL_HEADER, "SizeOfImage", "<I", align(rva + len(payload), pe.OPTIONAL_HEADER.SectionAlignment)),
    ]
    for header, field, fmt, value in fields:
        struct.pack_into(fmt, patched, header.get_field_absolute_offset(field), value)
    for va, _, offset, table_offset in REFERENCES:
        struct.pack_into("<I", patched, pe.get_offset_from_rva(va - BASE) + offset, new_table_va + table_offset)
    checksum_offset = pe.OPTIONAL_HEADER.get_field_absolute_offset("CheckSum")
    struct.pack_into("<I", patched, checksum_offset, 0)
    struct.pack_into("<I", patched, checksum_offset, pefile.PE(data=bytes(patched)).generate_checksum())

    # Reject unintended edits to any existing bytes (including font-related code).
    allowed = set(range(header_offset, header_offset + 40))
    for header, field, fmt, _ in fields:
        pos = header.get_field_absolute_offset(field)
        allowed.update(range(pos, pos + struct.calcsize(fmt)))
    allowed.update(range(checksum_offset, checksum_offset + 4))
    for va, _, offset, _ in REFERENCES:
        pos = pe.get_offset_from_rva(va - BASE) + offset
        allowed.update(range(pos, pos + 4))
    changed = [i for i, value in enumerate(original) if value != patched[i]]
    require(set(changed) <= allowed, "Unintended edit outside backlog operands / PE bookkeeping")
    output = bytes(patched)
    manifest = {
        "original_sha256": ORIGINAL_SHA256,
        "patched_sha256": sha256(output),
        "original_size": len(original), "patched_size": len(output),
        "table_va": hex(new_table_va), "section_rva": hex(rva),
        "section_raw_offset": raw_offset, "section_payload_size": len(payload),
        "original_entries": len(NAMES), "translated_aliases": len(translated),
        "instruction_operands": [hex(va + offset) for va, _, offset, _ in REFERENCES],
        "changed_original_byte_count": len(changed),
        "aliases": [{"name": name, "icon_id": icon} for icon, name in translated],
    }
    return output, manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exe", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="Separate candidate EXE")
    parser.add_argument("--install", action="store_true", help="Back up and replace the input EXE after building")
    args = parser.parse_args()
    source, output = args.exe.resolve(), args.output.resolve()
    require(source != output, "Candidate must be separate from the active EXE")
    original = source.read_bytes()
    patched, manifest = build(original)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(patched)
    if args.install:
        # Re-check just before installation so an intervening edit is not overwritten.
        require(source.read_bytes() == original, "Input EXE changed during build")
        backup = source.with_name(source.name + ".bak_backlog_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
        with backup.open("xb") as handle:
            handle.write(original)
        shutil.copystat(source, backup)
        require(backup.read_bytes() == original, "Backup verification failed")
        temporary = source.with_name(source.name + ".backlog_pending")
        with temporary.open("xb") as handle:
            handle.write(patched)
        require(temporary.read_bytes() == patched, "Staged EXE verification failed")
        os.replace(temporary, source)
        require(source.read_bytes() == patched, "Installed EXE verification failed")
        manifest["backup"] = str(backup)
        manifest["installed_exe"] = str(source)
    manifest_path = output.with_suffix(".manifest.json")
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
