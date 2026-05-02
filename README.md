# DC2DM MES Text Tool (GUI + CLI)

A Windows tool for converting **Da Capo 2 Dearest Marriage** script files between:

- `MES -> JSON` (export)
- `JSON -> MES` (import)

It supports both:

- Single file conversion
- Batch conversion (entire folder)

## Tool Location

Main executable:

- `bin\Release\net8.0-windows\DC2DMMesTextTool_GUI.exe`

## Output Build Locations (Patch + Launcher)

Patch and launcher build output:

- `DC2DMPatch a\build`

Ready-to-use release output:

- `DC2DMPatch a\build\Released`

## Important: Custom Launcher Required

To use this patch correctly, you must launch the game using the custom launcher:

For example - `H:\Games\DC2DM` is your game directory
put - `DC2DMMesTextTool_GUI and Patch` or somewhere else

- `H:\Games\DC2DM\DC2DMMesTextTool_GUI and Patch\DC2DMPatch a\build\Released\DC2DMLauncher.exe`

This patch is built to work with that launcher. Running the game directly from `DC2DM.EXE` may not load the patch properly.

## Features

- GUI mode (double-click executable)
- CLI mode (run commands from terminal)
- Drag-and-drop support for `.mes` and folders
- Shift-JIS handling for game script text

## JSON Format

Exported JSON is an array of entries like:

```json
[
  { "name": "Character Name", "message": "Dialogue line" },
  { "message": "Narration line" }
]
```

## Quick Start (GUI)

1. Open `DC2DMMesTextTool_GUI.exe`.
2. Use **Single File** tab for one file.
3. Use **Batch** tab for folder-based conversion.
4. Check the log panel at the bottom for success/error details.

### Single File: Export (MES -> JSON)

1. In **Input MES/JSON**, select a `.mes` file.
2. In **Output JSON/MES**, set output `.json` path (optional).
3. Click **Export (MES -> JSON)**.

### Single File: Import (JSON -> MES)

Important behavior in current GUI:

- GUI auto-detects original MES by replacing `.json` with `.mes` in the same folder.
- If matching original `.mes` is not found, import will fail.

Steps:

1. In **Input MES/JSON**, select `.json`.
2. Make sure original `.mes` with the same base filename is in the same folder.
3. Set output `.mes` path (optional).
4. Set **Word Wrap Width** (default: `60`). if 60 isn't enough you can change its value to fit textbox
5. Click **Import (JSON -> MES)**.

## CLI Tutorial

Open terminal in:

- `bin\Release\net8.0-windows`

Use:

- `./DC2DMMesTextTool_GUI.exe <command> ...`

### 1) Export Single File (MES -> JSON)

```powershell
./DC2DMMesTextTool_GUI.exe export "H:\path\script.mes" "H:\path\script.json"
```

If output path is omitted, output defaults to same name with `.json`.

### 2) Import Single File (JSON -> MES)

```powershell
./DC2DMMesTextTool_GUI.exe import "H:\path\script.json" "H:\path\script.mes" "H:\path\script_new.mes"
```

Notes:

- The second argument (`original.mes`) is required.
- For single CLI import, wrap width uses internal default (`28`).

### 3) Batch Export (Folder) (MES -> JSON)

```powershell
./DC2DMMesTextTool_GUI.exe batch-export "H:\path\mes_folder" "H:\path\json_output"
```

If output folder is omitted, defaults to `mes_folder\json_output`.

### 4) Batch Import (Folder) (JSON -> MES)

```powershell
./DC2DMMesTextTool_GUI.exe batch-import "H:\path\json_folder" "H:\path\mes_folder" "H:\path\mes_output" -w 67
```

Arguments:

- `json_folder`: translated `.json` files
- `mes_folder`: original `.mes` files used as base
- `mes_output`: output folder for rebuilt `.mes`
- `-w`: wrap width (optional, default `67`)

Matching is done by filename:

- `scene01.json` -> uses `scene01.mes`

If original MES file is missing, that JSON file is skipped.

## Drag & Drop

- Drop a `.mes` file onto the EXE: auto export to `.json` with same filename.
- Drop a folder onto the EXE: auto batch export all `.mes` files in that folder.

## Troubleshooting

- **"original MES not found"**: ensure matching `.mes` exists for each `.json`.
- **Import output looks broken**: try different wrap width for batch import (`-w`).
- **No output file**: check write permission for output folder.

## Build & Release Summary

- Active build folder: `DC2DMPatch a\build`
- Final ready release folder: `DC2DMPatch a\build\Released`
