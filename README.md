# DC2DM MES Text Tool (GUI + CLI) and Patch

Windows tools for **Da Capo 2 Dearest Marriage** (`dc2dm`): export MES scripts to JSON, import translated JSON into the original MES, and run the game with the custom patch and launcher. Only DC2DM is supported.

## Downloads and requirements

Download both archives from [GitHub Releases](https://github.com/SakuraSymphonyReTranslation/DC2DMMesTextTool_GUI-and-Patch/releases):

| Archive | Contents |
| --- | --- |
| `DC2DMMesTextTool_GUI.rar` | GUI/CLI converter, .NET companion files, and this guide |
| `Released_patch.rar` | Game EXE with backlog/line-pitch fixes, patch DLL, custom launcher, default INI, icon, scenario titles, and this guide |

The converter requires **Windows and the .NET 8 Desktop Runtime**. Keep its EXE, DLL, `.deps.json`, and `.runtimeconfig.json` together. The patch requires an existing DC2DM installation; the archive does not contain the full game or a complete translation.

## Directory names in this guide

- **`<GameDir>`**: your game installation folder, containing `DC2DM.EXE`.
- **`<ToolDir>`**: the folder where you extracted `DC2DMMesTextTool_GUI.rar`.
- **`<RepoDir>`**: the source repository root, containing this README and the `.csproj` file.

These are placeholders for folders you choose, not literal names or required drive letters. A *repository root* means `<RepoDir>`; a *game directory* means `<GameDir>`.

## Installation: custom launcher required

1. Close the game and back up the files you will replace, especially `DC2DM.EXE` and `DC2DM.ini`.
2. Extract `Released_patch.rar` to a temporary folder. Copy `DC2DM.EXE`, `DC2DMPatch.dll`, and `DC2DMLauncher.exe` into `<GameDir>`. The included EXE contains the backlog portrait mappings and 24px dialogue/backlog line pitch described below.
3. Use the supplied `DC2DM.ini` for a new installation. Keep your existing working INI to preserve font/layout settings. Copy the scenario-title JSON and icon if needed for your setup.
4. Place translation files in the appropriate `id_Data` or `eng_data` folders for your patch configuration.
5. Run **`<GameDir>\DC2DMLauncher.exe`**. Starting `DC2DM.EXE` directly may bypass the patch.

The launcher embeds the locale-support DLLs. Keep the launcher and patch beside the game EXE. Rebuilding the patch DLL alone does not apply the separate EXE fixes.

## Word wrap and four-line messages

GUI single import, GUI batch import, and CLI import use **46 half-width cells** by default. At the normal 22px font size, this is 506 native pixels and fits the narrower backlog body. Japanese/full-width glyphs occupy more space than Latin half-width characters: the setting measures display width, not a simple character count.

- GUI import and CLI `batch-import -w` allow widths from **10 to 46**. CLI single `import` uses the fixed default of 46.
- Dialogue and narration allow **at most four lines** after wrapping.
- Speaker/nameplate entries are **never word-wrapped**. Choice and UI labels retain their original formatting.
- Explicit newlines are preserved; CRLF, CR, and literal `\n` are normalized.
- More than four lines, an unbreakable word wider than the selected width, or a mismatched MES entry count causes that file's import to fail before writing its output. The error identifies the affected entry.
- Shorten/reword the message or revise its newlines when validation fails. The converter never truncates text or shrinks the font to force it to fit. Other files in a batch may still succeed.

The old width examples of 60 and the old CLI default of 28 no longer apply.

## JSON format and speaker names

```json
[
  { "name": "Otome", "message": "「Dialogue line」" },
  { "message": "Narration or inner monologue line" }
]
```

DC2DM stores the speaker and dialogue as consecutive MES text entries. Export combines a short speaker name immediately followed by quoted dialogue (`「...」`, `『...』`, or `“...”`) into one `name`/`message` object. Import expands it back into the original two entries. Legacy JSON with separate speaker and dialogue `message` objects remains supported.

Keep speaker names exact: `Yuto` / `勇斗`, `Yuki` / `由姫`, and `Yuuki` / `桜姫` are distinct backlog mappings. Yoshiyuki / 義之 uses the original blank portrait. The released EXE includes these mappings and 24px line spacing. MES/JSON conversion preserves names and line breaks but does not modify the EXE. See [backlog patch documentation](DC2DMPatch%20a/tools/backlog_fix/README.md) for rebuild instructions.

## Quick start: GUI

1. Open `<ToolDir>\DC2DMMesTextTool_GUI.exe`.
2. Choose **Single File** or **Batch**.
3. Select the input file/folder and output destination.
4. For import, set **Word Wrap Width** (default **46**) and check the log for validation errors.

### Export MES to JSON

In **Single File**, choose a `.mes` file in **Input MES/JSON**, optionally set **Output JSON/MES**, and click **Export (MES -> JSON)**. With no output path, the JSON uses the same name beside the MES.

### Import JSON to MES

For **Single File**, put the original `.mes` beside the translated `.json`, with the same base filename. The GUI finds the original by replacing `.json` with `.mes`; import fails if it is missing. Set an explicit output path to retain your original MES, then click **Import (JSON -> MES)**.

For **Batch**, provide the JSON folder, original MES folder, and output folder. Files are paired by name, such as `scene01.json` with `scene01.mes`. A missing original is reported and skipped.

## CLI tutorial

Open PowerShell in `<ToolDir>`, or `<RepoDir>\bin\Release\net8.0-windows` for a source build. These examples use a `scripts` working folder beside the tool; replace paths with your own. Use separate output folders to retain originals.

### Export one file

```powershell
.\DC2DMMesTextTool_GUI.exe export ".\scripts\original\scene01.mes" ".\scripts\json\scene01.json"
```

The output argument is optional; it defaults to the input filename with `.json`.

### Import one file

```powershell
.\DC2DMMesTextTool_GUI.exe import ".\scripts\json\scene01.json" ".\scripts\original\scene01.mes" ".\scripts\rebuilt\scene01.mes"
```

The original MES is required. With no output argument, the output is `output_scene01.mes` beside the original. Single CLI import uses width **46**.

### Batch export

```powershell
.\DC2DMMesTextTool_GUI.exe batch-export ".\scripts\original" ".\scripts\json"
```

With no output folder, the tool uses `json_output` inside the input folder.

### Batch import

```powershell
.\DC2DMMesTextTool_GUI.exe batch-import ".\scripts\json" ".\scripts\original" ".\scripts\rebuilt" -w 46
```

`-w` is optional (default **46**, allowed **10–46**). With no output folder, the tool uses `mes_output` inside the original MES folder.

### Normalize legacy JSON

```powershell
.\DC2DMMesTextTool_GUI.exe normalize-json ".\scripts\json"
```

This combines legacy consecutive speaker/dialogue objects. Before replacing JSON files, the tool creates a timestamped full backup beside the source folder. Supply an explicit backup folder as the second argument if desired.

### Drag and drop

- Drop a `.mes` file onto the EXE to export JSON beside it.
- Drop a folder onto the EXE to batch-export its MES files.

## Build from source

Clone with submodules so the patch has its Detours dependency:

```powershell
git clone --recurse-submodules https://github.com/SakuraSymphonyReTranslation/DC2DMMesTextTool_GUI-and-Patch.git
```

For an existing checkout, run `git submodule update --init --recursive` from `<RepoDir>`.

The GUI/CLI requires the **.NET 8 SDK**. Run from `<RepoDir>`:

```powershell
dotnet build .\DC2DMMesTextTool_GUI.csproj -c Release
```

The patch/launcher requires **Visual Studio 2022, Desktop development with C++, a Windows SDK, and CMake on PATH**:

```powershell
& ".\DC2DMPatch a\build.bat"
```

| Component | Source/output relative to `<RepoDir>` |
| --- | --- |
| Converter executable | `bin\Release\net8.0-windows\DC2DMMesTextTool_GUI.exe` |
| Patch source | `DC2DMPatch a\src\dc2dmpatch.cpp` |
| Win32 patch/launcher output | `DC2DMPatch a\build` |
| Distribution files | `DC2DMPatch a\build\Released` |
| Patch settings | `DC2DM.ini`, beside the installed game EXE |

Builds do not install files into `<GameDir>`. The separate [C++ text tool](MesTextTool-MesTextToolVer1.3.6/README.md) is also restricted to DC2DM; the word-wrap workflow above belongs to the C# GUI/CLI converter.

## Verification and troubleshooting

The refreshed converter passed **519 checks**, including eight Japanese/translated speaker names, four-line text, legacy JSON, repeated byte-identical MES imports, and rejection of unsupported MES versions without overwriting existing output. The patch and launcher build successfully; this publication has not repeated an in-game playtest with the newly built DLL/launcher.

- **Original MES not found:** provide the original with the same base filename. GUI single import requires it beside the JSON.
- **More than four lines / width exceeded:** shorten the message or revise its newlines; use width 10–46.
- **Wrong speaker portrait:** preserve the exact `name` and use the released EXE with its backlog mappings.
- **Tool will not start:** install the .NET 8 **Desktop** Runtime and keep all converter companion files together.
- **Patch is not loaded:** launch `<GameDir>\DC2DMLauncher.exe` with `DC2DMPatch.dll` beside it.
- **No output:** check the log, validation errors, and write access to the output folder.
