"""Tighten DC2DM's normal horizontal dialogue layout, without touching fonts.

The shared layout constructor supplies both animated dialogue and backlog.
Only layer 10 body layouts (a4 == 0) with the stock 32px pitch become 24px.
Names, vertical layouts, glyph sizes, ruby offsets and portrait patches remain.
"""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import struct

import pefile

from patch_backlog import BASE, align, require, sha256

SOURCE_SHA = "1889ce7fa3a95d3e144daf5e53527215ec84266178619323ae09a9d13e42f55e"
HOOK = 0x42A105
OLD = bytes.fromhex("8b15dc94c200")
PITCH = 24


def build(source):
    require(sha256(source) == SOURCE_SHA, "Expected verified blank-Yoshiyuki EXE")
    pe = pefile.PE(data=source)
    off = pe.get_offset_from_rva(HOOK - BASE)
    require(source[off:off+6] == OLD, "Layout constructor differs")
    last = pe.sections[-1]
    rva = align(last.VirtualAddress + max(last.Misc_VirtualSize, last.SizeOfRawData), pe.OPTIONAL_HEADER.SectionAlignment)
    va = BASE + rva
    # Replay displaced load; preserve incoming flags and all other registers.
    # At this site two saved registers precede return address and four args.
    code = bytearray(OLD + b"\x9c")
    code += b"\x83\xfb\x0a\x75\x15"  # cmp ebx,10; jne unchanged
    code += b"\x83\x7c\x24\x1c\x00\x75\x0e"  # cmp [esp+28],0 (a4)
    code += b"\x83\xfa\x20\x75\x09"  # cmp edx,32
    code += b"\x6a" + bytes([PITCH]) + b"\x5a"  # push 24; pop edx
    code += b"\x89\x15\xdc\x94\xc2\x00"  # update layout scratch, not font
    code += b"\x9d"
    code += b"\xe9" + struct.pack("<i", HOOK+6-(va+len(code)+5))
    raw = align(len(source), pe.OPTIONAL_HEADER.FileAlignment)
    raw_size = align(len(code), pe.OPTIONAL_HEADER.FileAlignment)
    section_off = last.get_file_offset() + 40
    require(section_off+40 <= pe.OPTIONAL_HEADER.SizeOfHeaders, "No section header room")
    require(source[section_off:section_off+40] == bytes(40), "Header padding occupied")
    result = bytearray(source)
    result[off:off+6] = b"\xe9" + struct.pack("<i", va-HOOK-5) + b"\x90"
    result[section_off:section_off+40] = struct.pack("<8sIIIIIIHHI", b".lnpitch", len(code), rva, raw_size, raw, 0,0,0,0,0x60000020)
    struct.pack_into("<H", result, pe.FILE_HEADER.get_field_absolute_offset("NumberOfSections"), len(pe.sections)+1)
    struct.pack_into("<I", result, pe.OPTIONAL_HEADER.get_field_absolute_offset("SizeOfImage"), align(rva+len(code),pe.OPTIONAL_HEADER.SectionAlignment))
    struct.pack_into("<I", result, pe.OPTIONAL_HEADER.get_field_absolute_offset("SizeOfCode"), pe.OPTIONAL_HEADER.SizeOfCode+raw_size)
    result.extend(bytes(raw-len(result)))
    result.extend(code.ljust(raw_size,b"\0"))
    co = pe.OPTIONAL_HEADER.get_field_absolute_offset("CheckSum")
    struct.pack_into("<I",result,co,0)
    struct.pack_into("<I",result,co,pefile.PE(data=bytes(result)).generate_checksum())
    manifest = {"source_sha256":SOURCE_SHA,"patched_sha256":sha256(result),"hook_va":hex(HOOK),"trampoline_va":hex(va),"code_hex":code.hex(),"old_pitch":32,"new_pitch":PITCH,"scope":"layer 10, body layout (a4=0), horizontal pitch exactly 32","font_changes":False,"dll_changes":False,"ini_changes":False}
    return bytes(result),manifest


if __name__ == "__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("exe",type=Path)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--install",action="store_true")
    a=p.parse_args()
    require(a.exe.resolve()!=a.output.resolve(),"Output must be separate")
    source=a.exe.read_bytes()
    candidate,manifest=build(source)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_bytes(candidate)
    if a.install:
        require(a.exe.read_bytes()==source,"Source changed")
        backup=a.exe.with_name(a.exe.name+".bak_line_pitch_"+datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
        with backup.open("xb") as f: f.write(source)
        require(backup.read_bytes()==source,"Backup verification failed")
        staging=a.exe.with_name(a.exe.name+".line_pitch_pending")
        with staging.open("xb") as f: f.write(candidate)
        os.replace(staging,a.exe)
        require(a.exe.read_bytes()==candidate,"Install verification failed")
        manifest["backup"]=str(backup)
    a.output.with_suffix(".manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest))
