# DC2DM backlog portraits and four-line layout

The refreshed `Released_patch.rar` includes a DC2DM EXE with translated speaker-name mappings, the blank Yoshiyuki portrait, Yuto/Yuki mappings, and 24px dialogue/backlog line pitch. These changes live in the EXE; the C# converter preserves names/newlines and the DLL provides the runtime patch settings.

`<GameDir>` means your installation folder containing `DC2DM.EXE`. Run `<GameDir>\DC2DMLauncher.exe` after installing the release. See the [main guide](../../../README.md) for installation and word wrap.

## Speaker mappings

Keep `Yuto` / `勇斗` (portrait 15), `Yuki` / `由姫` (portrait 14), and `Yuuki` / `桜姫` (portraits 20–23, selected by scene) distinct. `Yoshiyuki` / `義之` uses the game's blank portrait 17. Other verified Japanese/Indonesian names and scene-specific Otome/Yuuki variants retain their mappings. Portrait images come from the original `LOG_CHIP.CRX`.

The line-pitch patch changes normal horizontal body layout from 32px to 24px. It preserves glyph sizes, nameplates, vertical layouts, and ruby offsets. Converter word wrap defaults to 46 half-width cells and rejects body text exceeding four lines; it does not change the EXE.

## Rebuild the EXE fixes

Install Python 3 and `pefile`; the tests additionally use `unicorn`:

```powershell
python -m pip install pefile unicorn
```

Run the following from this directory. Put a supported pre-backlog EXE at `input/DC2DM.EXE`; `input` and `out` are working folders you choose. Every stage verifies the exact input hash and writes a separate output. The final released EXE is already patched and must not be used as the first-stage input.

```powershell
python patch_backlog.py "input/DC2DM.EXE" --output "out/DC2DM.backlog.EXE"
python patch_yoshiyuki.py "out/DC2DM.backlog.EXE" --output "out/DC2DM.yoshiyuki.EXE"
python patch_line_pitch.py "out/DC2DM.yoshiyuki.EXE" --output "out/DC2DM.line_pitch.EXE"
python patch_yuto_yuki.py "out/DC2DM.line_pitch.EXE" --output "out/DC2DM.EXE"
```

Supported initial SHA-256:

```text
377fa93b408b829b5e44198f441a9ef2805c0881d374899641e320e076c19d0c
```

Final released EXE SHA-256:

```text
ad6acbc21d24ff78eb79722021cf00095c945f27f480c452eb98c0e2170ff880
```

The final output is 1,014,784 bytes. Close the game, back up your current EXE, then copy the final output to `<GameDir>/DC2DM.EXE`. Restore your own backup to undo the EXE changes. Each script also supports `--install`, which creates a timestamped backup and replaces its input EXE after validation; the commands above only produce separate candidates.

## Validation

The prior Yuto/Yuki verification covered 30,374 native x86 lookups and 1,148 portrait-coordinate checks across 287 script names. The user confirmed the portrait result in-game on 10 October 2026. The converter's current suite passes 519 checks, including exact names, four-line text, byte-stable repeated import, legacy JSON, and preserving existing output on rejected imports.

For a new verification run, generate name evidence from corresponding original and translated JSON folders, then test the matching intermediate EXEs:

```powershell
python audit_names.py "input/json_original" "input/json_translated" --output "out/name_evidence.json"
python test_backlog.py "input/DC2DM.EXE" --audit "out/name_evidence.json" --output "out/backlog_tests.json"
python test_yoshiyuki.py "out/DC2DM.backlog.EXE" --audit "out/name_evidence.json" --output "out/yoshiyuki_tests.json"
python test_line_pitch.py "out/DC2DM.yoshiyuki.EXE" --output "out/line_pitch_tests.json"
python test_yuto_yuki.py "out/DC2DM.line_pitch.EXE" --audit "out/name_evidence.json" --output "out/yuto_yuki_tests.json"
dotnet run --project converter_tests/ConverterTests.csproj -c Release -- "input/sin_1931_f1.mes" "out/converter_tests"
```

The converter integration suite requires the original `sin_1931_f1.mes` from your game and uses separate generated test text. Local game scripts, debugger databases, backups, and verification outputs are not prerequisites for compiling the converter or DLL and are not included as test fixtures.

The publication rebuild does not repeat a full in-game playtest with the new DLL/launcher. The released EXE is checked against the previously verified final hash.
