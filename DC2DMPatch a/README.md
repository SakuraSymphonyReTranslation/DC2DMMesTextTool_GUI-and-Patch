# Da Capo 2 Dearest Marriage — Indonesian Patch

This project builds `DC2DMPatch.dll` and `DC2DMLauncher.exe` for **Da Capo 2 Dearest Marriage**.
The DLL source is `src/dc2dmpatch.cpp`. Patch settings are stored in `DC2DM.ini` beside the game EXE.

## Build

Install Visual Studio 2022 with Desktop development with C++ and CMake, then run `build.bat`.
It builds for Win32 and writes the patch and launcher to `build`, with distribution copies in `build/Released`.
`build_agent.bat` and `run_build.bat` use the same build entry point.
Building does not install files into the game folder.

## Installation

`<GameDir>` means your installation folder containing `DC2DM.EXE`.
Close the game and back up existing files, then copy `build/Released/DC2DM.EXE`,
`build/Released/DC2DMPatch.dll`, and `build/Released/DC2DMLauncher.exe` into `<GameDir>`.
The released EXE includes the backlog portrait and 24px line-pitch fixes.
Keep the existing `DC2DM.ini` to preserve font and layout settings.
Launch the game from that folder using `DC2DMLauncher.exe`.
The launcher embeds `LoaderDll.dll` and `LocaleEmulator.dll` for Japanese locale support.
Place Indonesian MES translations in `<GameDir>/id_Data/MES` and English MES
translations in `<GameDir>/eng_data/MES`; graphics and movies use the corresponding
`GRP` and `MOVIE` subfolders.

## Converter and backlog

See the [project README](../README.md) for the GUI/CLI MES ↔ JSON converter.
The DC2DM portrait and line-pitch patches are maintained in [tools/backlog_fix](tools/backlog_fix/README.md).
They are applied to the game EXE separately; rebuilding this DLL does not replace that EXE.
