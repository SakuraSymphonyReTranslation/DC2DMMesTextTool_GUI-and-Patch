"""Run inside the already-connected IDA database via the MCP py_eval tool.

Keeps a pre-patch IDB snapshot, then mirrors the installed section and six operands.
Does not use IDA's Apply patches to input file (the PE section was built separately).
"""
from pathlib import Path
import hashlib
import json
import struct

import ida_auto
import ida_bytes
import ida_dbg
import ida_loader
import ida_name
import ida_nalt
import ida_segment
import idc

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / "out/DC2DM.manifest.json").read_text(encoding="utf-8"))
exe = Path(manifest["installed_exe"])
data = exe.read_bytes()
assert Path(ida_nalt.get_input_file_path()).resolve() == exe.resolve()
assert ida_dbg.get_process_state() == 0, "Stop debugging before synchronizing the database"
assert hashlib.sha256(data).hexdigest() == manifest["patched_sha256"]
table = int(manifest["table_va"], 16)
refs = [(0x4110B6, "391db0b44800", 2, 0), (0x4110C2, "bdb0b44800", 1, 0),
        (0x4110D0, "8b96b4b44800", 2, 4), (0x411112, "8b86b4b44800", 2, 4),
        (0x4113E0, "83beb0b44800ff", 2, 0), (0x4113E7, "8daeb0b44800", 2, 0)]
for va, expected, _, _ in refs:
    assert ida_bytes.get_bytes(va, len(bytes.fromhex(expected))) == bytes.fromhex(expected), hex(va)
assert ida_segment.get_segm_by_name(".bknames") is None
database = ida_loader.get_path(ida_loader.PATH_TYPE_IDB)
snapshot = ROOT / "out/DC2DM.before_backlog.i64"
assert not snapshot.exists(), "Preserve the existing pre-patch snapshot"
assert ida_loader.save_database(str(snapshot), 0)

segment = ida_segment.segment_t()
segment.start_ea, segment.end_ea = table, table + 0x1000
segment.bitness = 1  # x86
segment.perm = ida_segment.SEGPERM_READ
segment.type = ida_segment.SEG_DATA
assert ida_segment.add_segm_ex(segment, ".bknames", "DATA", ida_segment.ADDSEG_OR_DIE)
file_offset = manifest["section_raw_offset"]
assert ida_loader.mem2base(data[file_offset:], table, file_offset)
for va, _, offset, displacement in refs:
    ida_bytes.patch_dword(va + offset, table + displacement)
    idc.set_cmt(va, "DC2DM backlog: redirected to JP + Indonesian exact-name table; native portrait selection unchanged.", 0)
assert idc.parse_decls("typedef struct { int icon_id; const char *name; } DC2DMBacklogName;", 0) == 0
assert ida_name.set_name(0x410CF0, "DC2DM_DrawBacklog", ida_name.SN_CHECK)
assert ida_name.set_name(0x48B4B0, "DC2DM_BacklogNames_Japanese", ida_name.SN_CHECK)
assert ida_name.set_name(table, "DC2DM_BacklogNames_Translated", ida_name.SN_CHECK)
assert idc.SetType(0x48B4B0, "DC2DMBacklogName names[21];")
assert idc.SetType(table, "DC2DMBacklogName names[47];")
idc.set_func_cmt(0x410CF0,
    "Backlog renderer. Exact speaker lookup at 4110AD..4113F7. Original table 48B4B0; "
    "installed translated table 1107000 contains 20 original JP entries + 26 verified aliases + sentinel. "
    "Native Otome IDs 0/19 and Yuuki IDs 20/21/22/23 depend on the history scene. "
    "Hiver/イベール uses ID16. μ describes the android type in narration, not a speaker key in this corpus. "
    "Unknown names (including Yoshiyuki) keep the text fallback. Fonts, voice, history and drawing code unchanged.", 1)
idc.set_cmt(0x411131, "Matched exact speaker name: use native portrait ID, then apply scene variants.", 0)
idc.set_cmt(0x411279, "Otome later-life portrait: native ID 19.", 0)
idc.set_cmt(0x4113CF, "Yuuki childhood variant: native ID 21.", 0)
idc.set_cmt(0x4113C8, "Yuuki middle variant: native ID 22.", 0)
idc.set_cmt(0x4113C1, "Yuuki later variant: native ID 23.", 0)
idc.set_cmt(0x411482, "No matching portrait: native text-name fallback (preserved).", 0)
for index, alias in enumerate(manifest["aliases"]):
    entry = table + (20 + index) * 8
    pointer = ida_bytes.get_dword(entry + 4)
    ida_bytes.create_strlit(pointer, pointer + len(alias["name"]) + 1, 0)
    idc.set_cmt(entry, f"{alias['name']} -> native portrait {alias['icon_id']}", 0)
ida_auto.auto_wait()
for va, _, offset, displacement in refs:
    assert ida_bytes.get_dword(va + offset) == table + displacement
assert ida_bytes.get_bytes(table, len(data) - file_offset) == data[file_offset:]
assert ida_loader.save_database(database, 0)
print(json.dumps({"database": database, "pre_patch_snapshot": str(snapshot),
                  "table": hex(table), "references_updated": len(refs),
                  "installed_exe_sha256": manifest["patched_sha256"]}))
