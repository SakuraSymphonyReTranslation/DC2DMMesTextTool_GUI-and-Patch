"""Map Yoshiyuki to the existing blank backlog portrait (LOG_CHIP ID 17).

Apply after patch_backlog.py. Only the existing .bknames payload, its virtual
size, and the PE checksum change. No graphics, instructions or fonts change.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import struct

import pefile

from patch_backlog import BASE, SECTION_NAME, require, sha256

PREVIOUS_SHA256 = "49b8f14b3bf38c8c546fa1f507d91c93f4ea8d03cc7d3a0d281d1b2b7b50da19"
BLANK_ICON = 17
MC_NAMES = ("Yoshiyuki", "義之")


def build(previous: bytes) -> tuple[bytes, dict]:
    require(sha256(previous) == PREVIOUS_SHA256, "Expected the verified Indonesian backlog patch from 9 October 2026")
    pe = pefile.PE(data=previous)
    section = pe.sections[-1]
    require(section.Name == SECTION_NAME and section.Characteristics == 0x40000040, "Unexpected name section")
    table_va = BASE + section.VirtualAddress
    entries = []
    for index in range(46):
        icon, ptr = struct.unpack("<II", pe.get_data(section.VirtualAddress + index * 8, 8))
        require(0 <= icon <= 24, "Invalid portrait ID")
        name = pe.get_string_at_rva(ptr - BASE)
        entries.append((icon, ptr, name))
    require(pe.get_data(section.VirtualAddress + 46 * 8, 8) == struct.pack("<iI", -1, 0), "Missing previous sentinel")
    entries.extend((BLANK_ICON, 0, name.encode("cp932")) for name in MC_NAMES)
    table_size = (len(entries) + 1) * 8
    table, strings = bytearray(), bytearray()
    for icon, ptr, name in entries:
        # Keep original Japanese name pointers; relocate strings owned by this section.
        if ptr == 0 or table_va <= ptr < table_va + section.SizeOfRawData:
            ptr = table_va + table_size + len(strings)
            strings.extend(name + b"\0")
        table.extend(struct.pack("<II", icon, ptr))
    table.extend(struct.pack("<iI", -1, 0))
    payload = table + strings
    require(len(payload) <= section.SizeOfRawData, "Insufficient existing section capacity")
    result = bytearray(previous)
    start = section.PointerToRawData
    result[start:start + section.SizeOfRawData] = payload.ljust(section.SizeOfRawData, b"\0")
    size_offset = section.get_field_absolute_offset("Misc_VirtualSize")
    struct.pack_into("<I", result, size_offset, len(payload))
    checksum_offset = pe.OPTIONAL_HEADER.get_field_absolute_offset("CheckSum")
    struct.pack_into("<I", result, checksum_offset, 0)
    struct.pack_into("<I", result, checksum_offset, pefile.PE(data=bytes(result)).generate_checksum())
    allowed = set(range(start, start + section.SizeOfRawData)) | set(range(size_offset, size_offset + 4)) | set(range(checksum_offset, checksum_offset + 4))
    changed = {i for i, (a, b) in enumerate(zip(previous, result)) if a != b}
    require(len(result) == len(previous) and changed <= allowed, "Unexpected change outside name data / PE metadata")
    output = bytes(result)
    return output, {
        "previous_sha256": PREVIOUS_SHA256, "patched_sha256": sha256(output),
        "table_va": hex(table_va), "entries": len(entries),
        "section_raw_offset": start, "section_raw_size": section.SizeOfRawData,
        "section_payload_size": len(payload), "changed_bytes": len(changed),
        "added_names": list(MC_NAMES), "portrait_id": BLANK_ICON,
        "source_rectangle": [748, 364, 864, 480],
        "file_size": len(output),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exe", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--install", action="store_true")
    args = parser.parse_args()
    source, output = args.exe.resolve(), args.output.resolve()
    require(source != output, "Candidate must be separate from the installed EXE")
    previous = source.read_bytes()
    patched, manifest = build(previous)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(patched)
    if args.install:
        require(source.read_bytes() == previous, "EXE changed during build")
        backup = source.with_name(source.name + ".bak_yoshiyuki_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
        with backup.open("xb") as handle:
            handle.write(previous)
        shutil.copystat(source, backup)
        require(backup.read_bytes() == previous, "Backup verification failed")
        staging = source.with_name(source.name + ".yoshiyuki_pending")
        with staging.open("xb") as handle:
            handle.write(patched)
        require(staging.read_bytes() == patched, "Staged EXE verification failed")
        os.replace(staging, source)
        require(source.read_bytes() == patched, "Installed EXE verification failed")
        manifest.update(backup=str(backup), installed_exe=str(source))
    output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=True))


if __name__ == "__main__":
    main()
