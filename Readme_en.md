# DC2DM MES Text Tool — GUI and CLI

[Bahasa Indonesia](README.md) | **English**

An importer/exporter for **D.C.II Dearest Marriage**.

This distribution supports **Da Capo 2 Dearest Marriage** only (`dc2dm`, MES version `0x9D72`). The GUI, CLI, C++ reference tables, patch, and launcher are specific to this game. The main patch source is `DC2DMPatch a/src/dc2dmpatch.cpp`.

## Downloads and game folder

Download both packages from [GitHub Releases](https://github.com/SakuraSymphonyReTranslation/DC2DMMesTextTool_GUI-and-Patch/releases/latest):

- **DC2DMMesTextTool_GUI.rar**: MES ↔ JSON importer/exporter with a GUI and CLI. Includes Indonesian and English documentation.
- **Released_patch.rar**: game executable with backlog fixes, launcher, patch DLL, INI configuration, icon, and scenario-title JSON.

`<GAME_DIR>` means **your game's installation folder**, which contains `DC2DM.EXE` and `AdvData`. It is a documentation placeholder: replace it with your actual game folder, without the `<` and `>` characters. No particular drive or installation path is required.

1. Close the game and back up any files that will be replaced, especially `DC2DM.EXE` and `DC2DM.ini`.
2. Extract `Released_patch.rar` to a temporary folder. Copy `DC2DM.EXE`, `DC2DMLauncher.exe`, and `DC2DMPatch.dll` into `<GAME_DIR>`. Use the supplied `DC2DM.ini` for a new installation; keep an existing working INI to preserve font and layout settings. Copy the icon and scenario-title JSON if needed.
3. Run **`<GAME_DIR>\DC2DMLauncher.exe`** with `<GAME_DIR>` as the working directory. If you use a shortcut, set its **Start in** field to that folder.
4. Select the appropriate language in the patch settings. Place Indonesian MES files in `<GAME_DIR>\id_Data\MES`; for English, use `<GAME_DIR>\eng_data\MES`. The `Language` setting in the `[Settings]` section of `DC2DM.ini` uses `0` for Japanese, `1` for Indonesian, and `2` for English.

```text
<GAME_DIR>/
├── DC2DM.EXE
├── DC2DMLauncher.exe
├── DC2DMPatch.dll
├── DC2DM.ini
├── AdvData/
├── id_Data/
│   └── MES/
└── eng_data/
    └── MES/
```

The launcher embeds the locale-support DLLs. The two archives provide the tool and patch; they do not include the full game or complete translated scripts. The repository's source folder can be placed anywhere. The patch package is also available under `DC2DMPatch a/build/Released` in the source tree.

## Opening the application

Extract `DC2DMMesTextTool_GUI.rar` to a folder of your choice and run `DC2DMMesTextTool_GUI.exe`. If you are using the source repository, run `bin\Release\net8.0-windows\DC2DMMesTextTool_GUI.exe`.
The ready-to-use package, `DC2DMMesTextTool_GUI.rar`, is in the same folder.
The application requires the **.NET 8 Desktop Runtime**. Keep the EXE, DLL, `.deps.json`, and `.runtimeconfig.json` together.

## Single File

**MES → JSON (export)**

1. Set **Input MES/JSON** to the original MES file.
2. Set **Output JSON/MES**, or leave it empty to create the JSON file next to the input.
3. Click **Export (MES -> JSON)**.

The default output combines consecutive character names and dialogue:

```json
[
  { "message": "Narration." },
  { "name": "Otome", "message": "「Character dialogue.」" }
]
```

Both the Single File and Batch tabs use the same format. A short name followed by dialogue beginning with `「`, `『`, or `“` is combined into a `name`/`message` object. Export preserves Japanese/translated name spellings and does not translate names.

**JSON → MES (import)**

1. Set **Input MES/JSON** to the translated JSON file.
2. Put the original MES for the same scenario next to the JSON, with the same base name: `scene.json` uses `scene.mes`. If the original MES is missing, import stops with an error.
3. Choose an **Output JSON/MES** file different from the original MES. If left empty, the result is written as `new_scene.mes` next to the original. Create the destination folder first if you choose another location.
4. Set **Word Wrap Width**: the default is `46`, with a range of `10–46`.
5. Click **Import (JSON -> MES)**.

The importer accepts combined JSON and legacy JSON with separate name/dialogue entries. Each `name`/`message` pair is expanded back into two MES entries during import. The expanded entry count must match the original MES. The original template is required because JSON does not contain all instructions, labels, assets, or scenario flow.

## Batch

- **Export:** set **MES Folder** to the original MES folder and **JSON Folder** to the destination, then click **Batch Export (MES -> JSON)**. If **JSON Folder** is empty, output goes into `json_output` inside the MES folder.
- **Import:** set **JSON Folder**, the original **MES Folder**, and a separate **Output Folder**, then click **Batch Import (JSON -> MES)**. If output is empty, results go into `mes_output` inside the original MES folder.
- File base names must match: `scene.json` uses `scene.mes` as its template.
- Import uses a default **Word Wrap Width** of `46`, with a range of `10–46`.
- Failed files are reported in the log; the batch continues with the remaining files. Missing templates are marked **Skipping** and skipped, so check the log before using the results.

## Layout and backlog icons

Word wrapping applies to dialogue/narration. Character names are not wrapped; choice and UI labels retain their original formatting. Keep `Yuto` / `勇斗`, `Yuki` / `由姫`, and `Yuuki` / `桜姫` spelled exactly, because they have distinct portrait mappings. Yoshiyuki / 義之 uses the original blank portrait.

Wrap `46` means **46 half-width cells**, equivalent to 506 pixels at the normal 22px font size. Full-width characters occupy more space than Latin letters. Explicit line breaks are preserved; CRLF, CR, and literal `\n` are normalized.

**Messages exceeding four lines or containing an unbreakable word wider than the limit are rejected before the MES is written.** Shorten the message or revise its line breaks if validation fails. The importer does not truncate text or shrink the font to force it to fit.

**The released `DC2DM.EXE` contains the portrait mappings and 24px line-spacing fixes.** Wrapping controls text width during import; the EXE contains the backlog fixes, while the DLL provides runtime patch settings. MES/JSON conversion and rebuilding the DLL alone do not apply those EXE changes. To play imported scripts, start the game through `DC2DMLauncher.exe` from `<GAME_DIR>`.

See the [patch README](DC2DMPatch%20a/README.md) and [backlog fix documentation](DC2DMPatch%20a/tools/backlog_fix/README.md) for technical details.

## Validation and encoding

- The converter uses UTF-8 for JSON and CP932 for MES text. Use characters supported by CP932 in translations.
- Unsupported MES versions, mismatched entry counts, widths outside `10–46`, and dialogue exceeding the line/width limits are rejected before output is written.
- Keep object order and `name` fields intact; do not add or remove scenario entries.
- Spaces in encrypted MES text are stored as `_` so they do not become text terminators. The patch renders them as spaces while the game is running.
- Use output files/folders separate from the source so the original MES remains available for future imports.

## CLI

Open PowerShell in the executable's folder. These examples use `scene.mes` and the `original`/`json` folders as inputs; replace them with your own paths. Create the destination folder before running a single-file import:

```powershell
New-Item -ItemType Directory -Force ".\new" | Out-Null
.\DC2DMMesTextTool_GUI.exe export "scene.mes" "scene.json"
.\DC2DMMesTextTool_GUI.exe import "scene.json" "original\scene.mes" "new\scene.mes"
.\DC2DMMesTextTool_GUI.exe batch-export "original" "json"
.\DC2DMMesTextTool_GUI.exe batch-import "json" "original" "mes_output" -w 46
.\DC2DMMesTextTool_GUI.exe normalize-json "json"
```

Single-file CLI `import` uses a fixed width of **46**. The `-w` option is available on `batch-import`, with a default of **46** and a range of **10–46**.

When output is omitted, single-file export creates JSON next to the input; single-file import creates `output_scene.mes` next to the original MES. Batch uses `json_output` inside the input MES folder or `mes_output` inside the original MES folder.

`normalize-json` combines legacy name/dialogue entries and creates a timestamped full backup before replacing JSON files. You can supply a backup folder as the second argument. Drop an MES file onto the executable to export JSON beside it, or drop a folder to export its MES files into `json_output`.

## Verification results

- The converter passed **519 checks**, covering eight Japanese/translated names, four-line messages, legacy JSON, byte-identical repeated imports, and rejection of invalid input without overwriting existing output.
- The packaged converter passed a CLI export → import test with byte-identical results.
- The EXE fixes passed four line-spacing test groups and five portrait test groups, including **30,374 native lookups** and **1,148 portrait-coordinate checks**.
- The release EXE hash matches the version previously verified in the game. The DLL and launcher were built successfully; those builds have not had a new interactive game test.

## Building and testing

Clone with submodules to include the Detours dependency:

```powershell
git clone --recurse-submodules https://github.com/SakuraSymphonyReTranslation/DC2DMMesTextTool_GUI-and-Patch.git
```

For an existing checkout, run `git submodule update --init --recursive`. From the project's source folder:

```powershell
dotnet build .\DC2DMMesTextTool_GUI.csproj -c Release
dotnet run --project ".\DC2DMPatch a\tools\backlog_fix\converter_tests\ConverterTests.csproj" -c Release -- "<ORIGINAL_MES_DIR>\sin_1931_f1.mes" "<VALIDATION_OUTPUT_DIR>"
```

Replace the placeholders with your own folders before running the commands. Building the GUI requires the **.NET 8 SDK**. The converter tests use the original `sin_1931_f1.mes` from your game; this corpus is not included in the repository. Use a separate test output folder, away from the game's active scripts.

Building the patch DLL/launcher requires **Visual Studio 2022, Desktop development with C++, a Windows SDK, and CMake on PATH**:

```powershell
& ".\DC2DMPatch a\build.bat"
```

Output is written to `DC2DMPatch a/build`, with distribution copies in `build/Released`. Builds do not install files into the game folder. See the [patch README](DC2DMPatch%20a/README.md) for DLL/launcher builds and the [backlog documentation](DC2DMPatch%20a/tools/backlog_fix/README.md) to rebuild the EXE fixes. The [C++ text tool](MesTextTool-MesTextToolVer1.3.6/README.md) has a separate guide.
