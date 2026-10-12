"""Audit reviewed aliases against the Japanese and Indonesian JSON inputs."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from patch_backlog import NAMES, aliases, require, sha256


def audit(raw: Path, translated: Path) -> dict:
    native = {jp: icon for icon, _, jp, _ in NAMES}
    accepted = {name: icon for icon, name in aliases()}
    evidence = defaultdict(list)
    pair_counts = Counter()
    totals = Counter()
    skipped, aligned = [], []
    inputs = {}
    for path in sorted(translated.glob("*.json")):
        original_path = raw / path.name
        a_bytes, b_bytes = original_path.read_bytes(), path.read_bytes()
        a, b = json.loads(a_bytes.decode("utf-8-sig")), json.loads(b_bytes.decode("utf-8-sig"))
        inputs[path.name] = {"japanese_sha256": sha256(a_bytes), "indonesian_sha256": sha256(b_bytes)}
        totals.update(item["name"] for item in b if "name" in item)
        # Do not zip speaker-only streams: exporter errors can reclassify narration.
        if len(a) != len(b) or [sorted(item) for item in a] != [sorted(item) for item in b]:
            skipped.append(path.name)
            continue
        aligned.append(path.name)
        for index, (x, y) in enumerate(zip(a, b)):
            jp, name = x.get("name"), y.get("name")
            if jp not in native or name not in accepted:
                continue
            require(native[jp] == accepted[name], f"Conflicting portrait mapping in {path.name}:{index}")
            pair_counts[name] += 1
            if len(evidence[name]) < 2:
                evidence[name].append({"file": path.name, "japanese_index": index,
                                       "indonesian_index": index, "japanese_name": jp,
                                       "method": "entire file has identical object and field structure"})

    # These files have merged narration elsewhere. The dialogue at these exact
    # indices was manually compared in both languages; do not infer other pairs.
    manual = [
        ("Ybel", "イベール", "sin_0703_b1.json", 145, 144),
        ("Yvers", "イベール", "suc75_0413_f1_otm.json", 131, 131),
        ("Morizono", "森園", "suc75_0323_e1_otm.json", 96, 95),
    ]
    for name, jp, filename, ai, bi in manual:
        a = json.loads((raw / filename).read_text(encoding="utf-8-sig"))
        b = json.loads((translated / filename).read_text(encoding="utf-8-sig"))
        require(a[ai].get("name") == jp and b[bi].get("name") == name, f"Reviewed evidence changed: {filename}")
        require(native[jp] == accepted[name], f"Conflicting reviewed alias: {name}")
        evidence[name].append({"file": filename, "japanese_index": ai, "indonesian_index": bi,
                               "japanese_name": jp, "method": "manually reviewed dialogue pair",
                               "japanese_message": a[ai]["message"], "indonesian_message": b[bi]["message"]})
    require(all(evidence[name] for name in accepted), "Alias missing evidence")
    return {
        "raw_directory": str(raw.resolve()), "translated_directory": str(translated.resolve()),
        "file_count": len(inputs), "strictly_aligned_files": len(aligned),
        "skipped_for_automatic_alignment": skipped,
        "note": "Counts cover all translated name fields; evidence uses aligned files or explicit reviewed pairs. Unknown, collective and voice-only names retain native text fallback. Yoshiyuki has no native portrait entry.",
        "aliases": [{"name": name, "icon_id": icon, "total_occurrences": totals[name],
                     "strictly_aligned_pairs": pair_counts[name], "evidence": evidence[name]}
                    for icon, name in aliases()],
        "unmapped_names": dict(sorted((name, count) for name, count in totals.items() if name not in accepted)),
        "input_hashes": inputs,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path)
    parser.add_argument("translated", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.raw, args.translated)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"files": report["file_count"], "strictly_aligned_files": report["strictly_aligned_files"],
                      "verified_aliases": len(report["aliases"]),
                      "covered_name_occurrences": sum(x["total_occurrences"] for x in report["aliases"]),
                      "report": str(args.output.resolve())}))
