"""Add Yuto / 勇斗 and Yuki / 由姫 to the existing native backlog name table.

Input is the verified 24px line-pitch EXE. Only .bknames data, its virtual
size and the PE checksum change; the existing LOG_CHIP artwork is reused.
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

SOURCE_SHA256 = "6ada85370274f5815d8d696110922f13271b24c7cfd636a95903e21558044dad"
ADDITIONS = ((15, "Yuto"), (15, "勇斗"), (14, "Yuki"), (14, "由姫"))
SOURCE_RECTS = {14: [400, 364, 516, 480], 15: [516, 364, 632, 480]}


def build(source: bytes) -> tuple[bytes, dict]:
    require(sha256(source) == SOURCE_SHA256, "Expected the verified 24px line-pitch EXE")
    pe = pefile.PE(data=source)
    sections = [s for s in pe.sections if s.Name == SECTION_NAME]
    require(len(sections) == 1, "Expected one existing .bknames section")
    section = sections[0]
    require(section.Characteristics == 0x40000040, "Name section must be read-only data")
    table_va = BASE + section.VirtualAddress
    entries = []
    for index in range(48):
        icon, ptr = struct.unpack("<II", pe.get_data(section.VirtualAddress + index * 8, 8))
        require(0 <= icon <= 24, "Invalid existing portrait ID")
        entries.append((icon, ptr, pe.get_string_at_rva(ptr - BASE)))
    require(pe.get_data(section.VirtualAddress + 48 * 8, 8) == struct.pack("<iI", -1, 0), "Missing existing sentinel")
    known_names = {name for _, _, name in entries}
    require(all(name.encode("cp932") not in known_names for _, name in ADDITIONS), "Name already present")
    entries.extend((icon, 0, name.encode("cp932")) for icon, name in ADDITIONS)
    table_size = (len(entries) + 1) * 8
    table, strings = bytearray(), bytearray()
    for icon, ptr, name in entries:
        if ptr == 0 or table_va <= ptr < table_va + section.SizeOfRawData:
            ptr = table_va + table_size + len(strings)
            strings.extend(name + b"\0")
        table.extend(struct.pack("<II", icon, ptr))
    table.extend(struct.pack("<iI", -1, 0))
    payload = table + strings
    require(len(payload) <= section.SizeOfRawData, "Insufficient existing section capacity")
    result = bytearray(source)
    start = section.PointerToRawData
    result[start:start + section.SizeOfRawData] = payload.ljust(section.SizeOfRawData, b"\0")
    size_offset = section.get_field_absolute_offset("Misc_VirtualSize")
    struct.pack_into("<I", result, size_offset, len(payload))
    checksum_offset = pe.OPTIONAL_HEADER.get_field_absolute_offset("CheckSum")
    struct.pack_into("<I", result, checksum_offset, 0)
    struct.pack_into("<I", result, checksum_offset, pefile.PE(data=bytes(result)).generate_checksum())
    allowed = set(range(start, start + section.SizeOfRawData))
    allowed.update(range(size_offset, size_offset + 4))
    allowed.update(range(checksum_offset, checksum_offset + 4))
    changed = {i for i, (a, b) in enumerate(zip(source, result)) if a != b}
    require(len(result) == len(source) and changed <= allowed, "Unexpected change outside names / PE metadata")
    return bytes(result), {
        "source_sha256": SOURCE_SHA256, "patched_sha256": sha256(result),
        "table_va": hex(table_va), "entries": len(entries),
        "section_raw_offset": start, "section_raw_size": section.SizeOfRawData,
        "section_payload_size": len(payload), "changed_bytes": len(changed),
        "added_names": [{"name": name, "icon_id": icon, "source_rectangle": SOURCE_RECTS[icon]} for icon, name in ADDITIONS],
        "file_size": len(result), "line_pitch_preserved": 24,
        "graphics_changes": False, "instruction_changes": False,
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
    candidate, manifest = build(previous)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(candidate)
    if args.install:
        require(source.read_bytes() == previous, "EXE changed during build")
        backup = source.with_name(source.name + ".bak_yuto_yuki_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
        with backup.open("xb") as handle:
            handle.write(previous)
        shutil.copystat(source, backup)
        require(backup.read_bytes() == previous, "Backup verification failed")
        staging = source.with_name(source.name + ".yuto_yuki_pending")
        with staging.open("xb") as handle:
            handle.write(candidate)
        require(staging.read_bytes() == candidate, "Staged EXE verification failed")
        os.replace(staging, source)
        require(source.read_bytes() == candidate, "Installed EXE verification failed")
        manifest.update(backup=str(backup), installed_exe=str(source))
    output.with_suffix(".manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=True))


if __name__ == "__main__":
    main()
