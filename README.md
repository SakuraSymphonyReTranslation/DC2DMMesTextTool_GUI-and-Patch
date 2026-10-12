# DC2DM MES Text Tool (GUI + CLI) and Patch

**Da Capo 2 Dearest Marriage · v1.0.0**

Pilih bahasa di bawah. Klik judul bahasa untuk membuka atau menutup panduan tanpa meninggalkan halaman ini.

Choose a language below. Click its heading to expand or collapse the guide without leaving this page.

<details name="readme-language">
<summary><strong>🇮🇩 Bahasa Indonesia</strong></summary>

Alat Windows untuk **Da Capo 2 Dearest Marriage** (`dc2dm`): mengekspor skrip MES ke JSON, mengimpor JSON terjemahan menggunakan MES asli, serta menjalankan game dengan patch dan launcher khusus. Proyek ini hanya mendukung DC2DM.

## Unduhan dan persyaratan

Unduh kedua arsip dari [GitHub Releases](https://github.com/SakuraSymphonyReTranslation/DC2DMMesTextTool_GUI-and-Patch/releases):

| Arsip | Isi |
| --- | --- |
| `DC2DMMesTextTool_GUI.rar` | Konverter GUI/CLI, berkas pendamping .NET, dan panduan ini |
| `Released_patch.rar` | EXE game dengan perbaikan potret/jarak baris backlog, DLL patch, launcher khusus, INI bawaan, ikon, judul skenario, dan panduan ini |

Konverter memerlukan **Windows dan .NET 8 Desktop Runtime**. Simpan EXE, DLL, `.deps.json`, dan `.runtimeconfig.json` dalam folder yang sama. Patch memerlukan instalasi DC2DM yang sudah tersedia; arsip ini tidak berisi game lengkap atau terjemahan lengkap.

## Istilah direktori dalam panduan

- **`<GameDir>`**: folder instalasi game Anda yang berisi `DC2DM.EXE`.
- **`<ToolDir>`**: folder tempat Anda mengekstrak `DC2DMMesTextTool_GUI.rar`.
- **`<RepoDir>`**: direktori utama repositori sumber, yang berisi README ini dan berkas `.csproj`.

Istilah tersebut adalah penanda untuk folder pilihan Anda, bukan nama folder yang harus dibuat atau huruf drive tertentu. *Repository root* berarti `<RepoDir>`, sedangkan *game directory* berarti `<GameDir>`.

## Pemasangan: wajib memakai launcher khusus

1. Tutup game dan cadangkan berkas yang akan diganti, terutama `DC2DM.EXE` dan `DC2DM.ini`.
2. Ekstrak `Released_patch.rar` ke folder sementara. Salin `DC2DM.EXE`, `DC2DMPatch.dll`, dan `DC2DMLauncher.exe` ke `<GameDir>`. EXE yang disertakan sudah memuat pemetaan potret backlog serta jarak baris dialog/backlog 24px yang dijelaskan di bawah.
3. Gunakan `DC2DM.ini` bawaan untuk pemasangan baru. Jika INI lama sudah berfungsi, pertahankan berkas tersebut agar pengaturan font/tata letak tidak hilang. Salin JSON judul skenario dan ikon jika diperlukan oleh konfigurasi Anda.
4. Tempatkan berkas terjemahan dalam folder `id_Data` atau `eng_data` yang sesuai dengan konfigurasi patch.
5. Jalankan **`<GameDir>\DC2DMLauncher.exe`**. Menjalankan `DC2DM.EXE` secara langsung dapat melewati pemuatan patch.

DLL pendukung locale sudah tertanam di launcher. Letakkan launcher dan DLL patch di samping EXE game. Build ulang DLL patch saja tidak menerapkan perbaikan yang berada di EXE.

## Word wrap dan batas empat baris

Impor tunggal/batch melalui GUI dan impor melalui CLI memakai nilai bawaan **46 sel setengah lebar**. Pada ukuran font normal 22px, lebar ini setara dengan 506 piksel asli dan sesuai dengan area teks backlog yang lebih sempit. Huruf Jepang/karakter lebar penuh memakan ruang lebih besar daripada karakter Latin setengah lebar: pengaturan ini mengukur lebar tampilan, bukan sekadar jumlah karakter.

- Impor GUI dan CLI `batch-import -w` menerima lebar **10 sampai 46**. CLI `import` tunggal menggunakan nilai tetap 46.
- Dialog dan narasi dibatasi **maksimal empat baris** setelah word wrap.
- Entri nama pembicara/papan nama **tidak dibungkus dengan word wrap**. Label pilihan dan antarmuka mempertahankan format aslinya.
- Pergantian baris yang ditulis sendiri tetap dipertahankan; CRLF, CR, dan teks literal `\n` dinormalisasi.
- Teks lebih dari empat baris, kata utuh yang melebihi batas lebar, atau jumlah entri yang tidak cocok dengan MES menyebabkan impor berkas tersebut gagal sebelum output ditulis. Pesan kesalahan menunjukkan entri yang bermasalah.
- Pendekkan/ubah kalimat atau sesuaikan pergantian baris jika validasi gagal. Konverter tidak memangkas teks atau mengecilkan font untuk memaksakannya masuk. Berkas lain dalam proses batch masih dapat berhasil.

Contoh lebar 60 dan nilai bawaan CLI 28 pada panduan lama sudah tidak berlaku.

## Format JSON dan nama pembicara

```json
[
  { "name": "Otome", "message": "「Baris dialog」" },
  { "message": "Baris narasi atau monolog batin" }
]
```

DC2DM menyimpan nama pembicara dan dialog sebagai entri MES berurutan. Saat ekspor, nama pendek yang langsung diikuti dialog bertanda kutip (`「...」`, `『...』`, atau `“...”`) digabung menjadi satu objek `name`/`message`. Impor memisahkannya kembali menjadi dua entri asli. JSON lama yang menyimpan nama dan dialog sebagai objek `message` terpisah tetap didukung.

Pertahankan ejaan nama: `Yuto` / `勇斗`, `Yuki` / `由姫`, dan `Yuuki` / `桜姫` memiliki pemetaan backlog yang berbeda. Yoshiyuki / 義之 memakai potret kosong bawaan. EXE rilis sudah memuat pemetaan tersebut dan jarak baris 24px. Konversi MES/JSON mempertahankan nama dan pergantian baris, tetapi tidak mengubah EXE. Lihat [dokumentasi patch backlog](DC2DMPatch%20a/tools/backlog_fix/README.md) untuk petunjuk build ulang.

## Panduan singkat: GUI

1. Buka `<ToolDir>\DC2DMMesTextTool_GUI.exe`.
2. Pilih **Single File** atau **Batch**.
3. Pilih berkas/folder input dan lokasi output.
4. Untuk impor, atur **Word Wrap Width** (bawaan **46**) dan periksa log jika ada kesalahan validasi.

### Ekspor MES ke JSON

Pada **Single File**, pilih berkas `.mes` di **Input MES/JSON**, isi **Output JSON/MES** bila diperlukan, lalu klik **Export (MES -> JSON)**. Jika lokasi output dikosongkan, JSON dibuat dengan nama yang sama di samping MES.

### Impor JSON ke MES

Untuk **Single File**, letakkan `.mes` asli di samping `.json` terjemahan dengan nama dasar yang sama. GUI mencari MES asli dengan mengganti ekstensi `.json` menjadi `.mes`; impor gagal jika berkas tersebut tidak ditemukan. Isi lokasi output secara jelas agar MES asli tetap tersimpan, lalu klik **Import (JSON -> MES)**.

Untuk **Batch**, tentukan folder JSON, folder MES asli, dan folder output. Berkas dicocokkan berdasarkan nama, misalnya `scene01.json` dengan `scene01.mes`. Jika MES asli tidak ditemukan, berkas tersebut dilaporkan dan dilewati.

## Tutorial CLI

Buka PowerShell di `<ToolDir>`, atau `<RepoDir>\bin\Release\net8.0-windows` jika memakai hasil build sumber. Contoh di bawah memakai folder kerja `scripts` di samping konverter; ganti path sesuai lokasi Anda. Gunakan folder output terpisah agar berkas asli tetap tersimpan.

### Ekspor satu berkas

```powershell
.\DC2DMMesTextTool_GUI.exe export ".\scripts\original\scene01.mes" ".\scripts\json\scene01.json"
```

Argumen output bersifat opsional; nilai bawaannya adalah nama input dengan ekstensi `.json`.

### Impor satu berkas

```powershell
.\DC2DMMesTextTool_GUI.exe import ".\scripts\json\scene01.json" ".\scripts\original\scene01.mes" ".\scripts\rebuilt\scene01.mes"
```

MES asli wajib diberikan. Tanpa argumen output, hasil ditulis sebagai `output_scene01.mes` di samping MES asli. Impor tunggal CLI memakai lebar **46**.

### Ekspor batch

```powershell
.\DC2DMMesTextTool_GUI.exe batch-export ".\scripts\original" ".\scripts\json"
```

Tanpa folder output, konverter memakai `json_output` di dalam folder input.

### Impor batch

```powershell
.\DC2DMMesTextTool_GUI.exe batch-import ".\scripts\json" ".\scripts\original" ".\scripts\rebuilt" -w 46
```

`-w` bersifat opsional (bawaan **46**, rentang **10–46**). Tanpa folder output, konverter memakai `mes_output` di dalam folder MES asli.

### Normalisasi JSON lama

```powershell
.\DC2DMMesTextTool_GUI.exe normalize-json ".\scripts\json"
```

Perintah ini menggabungkan objek nama/dialog berurutan dari format lama. Sebelum mengganti JSON, konverter membuat cadangan lengkap dengan penanda waktu di samping folder sumber. Anda dapat memberikan folder cadangan sendiri sebagai argumen kedua.

### Seret dan lepas

- Seret berkas `.mes` ke EXE untuk mengekspor JSON di sampingnya.
- Seret folder ke EXE untuk mengekspor seluruh MES di folder tersebut secara batch.

## Build dari kode sumber

Clone beserta submodule agar dependensi Detours ikut tersedia:

```powershell
git clone --recurse-submodules https://github.com/SakuraSymphonyReTranslation/DC2DMMesTextTool_GUI-and-Patch.git
```

Untuk checkout yang sudah ada, jalankan `git submodule update --init --recursive` dari `<RepoDir>`.

GUI/CLI memerlukan **.NET 8 SDK**. Jalankan dari `<RepoDir>`:

```powershell
dotnet build .\DC2DMMesTextTool_GUI.csproj -c Release
```

Patch/launcher memerlukan **Visual Studio 2022, Desktop development with C++, Windows SDK, dan CMake yang tersedia di PATH**:

```powershell
& ".\DC2DMPatch a\build.bat"
```

| Komponen | Sumber/output relatif terhadap `<RepoDir>` |
| --- | --- |
| EXE konverter | `bin\Release\net8.0-windows\DC2DMMesTextTool_GUI.exe` |
| Sumber patch | `DC2DMPatch a\src\dc2dmpatch.cpp` |
| Output patch/launcher Win32 | `DC2DMPatch a\build` |
| Berkas distribusi | `DC2DMPatch a\build\Released` |
| Pengaturan patch | `DC2DM.ini`, di samping EXE game yang terpasang |

Proses build tidak memasang berkas ke `<GameDir>`. [Alat teks C++](MesTextTool-MesTextToolVer1.3.6/README.md) yang terpisah juga hanya mendukung DC2DM; alur word wrap di atas berlaku untuk konverter C# GUI/CLI.

## Verifikasi dan pemecahan masalah

Konverter telah lulus **519 pemeriksaan**, termasuk delapan nama Jepang/terjemahan, teks empat baris, JSON lama, impor MES berulang yang identik byte demi byte, dan penolakan versi MES yang tidak didukung tanpa menimpa output lama. Patch dan launcher berhasil dibangun; publikasi ini belum mencakup pengujian ulang di dalam game memakai DLL/launcher hasil build baru.

- **Original MES not found:** sediakan MES asli dengan nama dasar yang sama. Impor tunggal GUI memerlukannya di samping JSON.
- **Lebih dari empat baris / lebar terlampaui:** pendekkan teks atau sesuaikan pergantian baris; gunakan lebar 10–46.
- **Potret pembicara keliru:** pertahankan `name` yang tepat dan gunakan EXE rilis yang memuat pemetaan backlog.
- **Konverter tidak bisa dibuka:** pasang .NET 8 **Desktop** Runtime dan simpan seluruh berkas pendamping konverter dalam satu folder.
- **Patch tidak dimuat:** jalankan `<GameDir>\DC2DMLauncher.exe` dengan `DC2DMPatch.dll` di sampingnya.
- **Tidak ada output:** periksa log, kesalahan validasi, dan izin menulis ke folder output.

</details>

<details name="readme-language">
<summary><strong>🇬🇧 English</strong></summary>

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

The converter passed **519 checks**, including eight Japanese/translated speaker names, four-line text, legacy JSON, repeated byte-identical MES imports, and rejection of unsupported MES versions without overwriting existing output. The patch and launcher build successfully; this publication has not repeated an in-game playtest with the newly built DLL/launcher.

- **Original MES not found:** provide the original with the same base filename. GUI single import requires it beside the JSON.
- **More than four lines / width exceeded:** shorten the message or revise its newlines; use width 10–46.
- **Wrong speaker portrait:** preserve the exact `name` and use the released EXE with its backlog mappings.
- **Tool will not start:** install the .NET 8 **Desktop** Runtime and keep all converter companion files together.
- **Patch is not loaded:** launch `<GameDir>\DC2DMLauncher.exe` with `DC2DMPatch.dll` beside it.
- **No output:** check the log, validation errors, and write access to the output folder.

</details>
