"""Run through IDA MCP py_eval after installing the blank Yoshiyuki patch."""
from pathlib import Path
import hashlib
import json

import ida_auto
import ida_bytes
import ida_dbg
import ida_loader
import ida_nalt
import idc

ROOT = Path(__file__).resolve().parent
manifest = json.loads((ROOT / "out/DC2DM.yoshiyuki.manifest.json").read_text(encoding="utf-8"))
exe = Path(manifest["installed_exe"])
data = exe.read_bytes()
previous = Path(manifest["backup"]).read_bytes()
assert Path(ida_nalt.get_input_file_path()).resolve() == exe.resolve()
assert ida_dbg.get_process_state() == 0
assert hashlib.sha256(data).hexdigest() == manifest["patched_sha256"]
assert hashlib.sha256(previous).hexdigest() == manifest["previous_sha256"]
table = int(manifest["table_va"], 16)
offset, size = manifest["section_raw_offset"], manifest["section_raw_size"]
assert ida_bytes.get_bytes(table, size) == previous[offset:offset + size], "Expected IDB with the previous backlog patch"
database = ida_loader.get_path(ida_loader.PATH_TYPE_IDB)
snapshot = ROOT / "out/DC2DM.before_yoshiyuki.i64"
# A packed pre-change IDB was copied while IDA was closed. Saving to a different
# path through this IDA build's save_database API terminated the process.
assert snapshot.is_file() and snapshot.stat().st_size > 0, "Create a closed-IDB backup before synchronizing"
ida_bytes.del_items(table, ida_bytes.DELIT_SIMPLE, size)
assert ida_loader.mem2base(data[offset:offset + size], table, offset)
assert idc.SetType(table, "DC2DMBacklogName names[49];")
for index in range(48):
    entry = table + index * 8
    pointer = ida_bytes.get_dword(entry + 4)
    icon = ida_bytes.get_dword(entry)
    if pointer >= table:
        encoded = ida_bytes.get_strlit_contents(pointer, -1, 0)
        if encoded:
            ida_bytes.create_strlit(pointer, pointer + len(encoded) + 1, 0)
            idc.set_cmt(entry, f"{encoded.decode('cp932')} -> portrait {icon}" + (" (blank circle)" if icon == 17 else ""), 0)
idc.set_func_cmt(0x410CF0,
    "Backlog renderer. Exact speaker lookup 4110AD..4113F7 uses 48 names + sentinel in 1107000. "
    "Includes 20 original JP entries, 26 Indonesian aliases, and Yoshiyuki/義之 -> blank LOG_CHIP ID17. "
    "Native Otome and Yuuki scene variants remain unchanged. Unknown speakers keep native text fallback.", 1)
idc.set_cmt(0x411434, "Native 6-column LOG_CHIP grid: ID17 selects source x=748,y=364,size=116x116 (blank pink circle).", 0)
ida_auto.auto_wait()
assert ida_bytes.get_bytes(table, size) == data[offset:offset + size]
assert ida_loader.save_database(database, 0)
print(json.dumps({"database": database, "snapshot": str(snapshot), "sha256": manifest["patched_sha256"]}))
