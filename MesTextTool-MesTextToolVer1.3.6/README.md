# MesTextTool — Da Capo 2 Dearest Marriage

This bundled C++ tool is restricted to **Da Capo 2 Dearest Marriage** (`dc2dm`, MES version `0x9D72`).
Original tool by iTsukezigen: https://github.com/cokkeijigen/MesTextTool. The original LICENSE is retained.

For JSON ↔ MES conversion, use `../bin/Release/net8.0-windows/DC2DMMesTextTool_GUI.exe` and the project README.
The C++ tool uses its own plain-text export format, not JSON.

## Supported game

| Game | Option |
| --- | --- |
| Da Capo 2 Dearest Marriage | `-dc2dm` |

## Export plain text

Run the bundled executable with a MES file or folder. Replace `<GameDir>` with
your game installation folder (the directory containing `DC2DM.EXE`):

```powershell
.\MesTextTool.exe -log -cp932 -dc2dm "<GameDir>\AdvData\MES"
```

You can also use `MesTextTool-cp932-dc2dm.exe` or drag a MES file/folder onto it.
Exports are written beside the executable. Keep the generated `.MesTextTool` metadata file with the exported text.

## Import plain text

Pass the exported text folder (including `.MesTextTool`) back to the executable.
Set `#InputPath` in `.MesTextTool` to the original MES directory and `#UseCodePage` to `932`.
Use a separate output directory and retain the originals.

## Build on Windows

Install Visual Studio 2022 with Desktop development with C++ and CMake, then run `MesTextTool/build.bat`.
The output is `MesTextTool/build/Release/MesTextTool.exe`.
