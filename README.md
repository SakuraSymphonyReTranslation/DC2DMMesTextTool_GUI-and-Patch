# DC2DM MES Text Tool — GUI dan CLI

**Bahasa Indonesia** | [English](Readme_en.md)

Importer/exporter untuk **D.C.II Dearest Marriage**.

Distribusi ini hanya mendukung **Da Capo 2 Dearest Marriage** (`dc2dm`, versi MES `0x9D72`). GUI, CLI, tabel referensi C++, patch, dan launcher dikhususkan untuk game ini. Source utama patch: `DC2DMPatch a/src/dc2dmpatch.cpp`.

## Unduhan dan folder instalasi

Unduh kedua paket terbaru dari [GitHub Releases](https://github.com/SakuraSymphonyReTranslation/DC2DMMesTextTool_GUI-and-Patch/releases/latest):

- **DC2DMMesTextTool_GUI.rar**: importer/exporter MES ↔ JSON, GUI dan CLI. Termasuk dokumentasi bahasa Indonesia dan Inggris.
- **Released_patch.rar**: executable game dengan perbaikan backlog, launcher, DLL patch, INI, ikon, dan JSON judul skenario.

`<GAME_DIR>` berarti **folder utama instalasi game pilihan pemain**, yaitu folder yang berisi `DC2DM.EXE` dan `AdvData`. Ini placeholder dokumentasi: ganti dengan lokasi game Anda, tanpa tanda `<` dan `>`. Tidak ada drive atau lokasi instalasi wajib.

1. Tutup game dan simpan salinan berkas lama yang akan diganti, terutama `DC2DM.EXE` dan `DC2DM.ini`.
2. Ekstrak `Released_patch.rar` ke folder sementara. Salin `DC2DM.EXE`, `DC2DMLauncher.exe`, dan `DC2DMPatch.dll` ke `<GAME_DIR>`. Gunakan `DC2DM.ini` bawaan untuk pemasangan baru; pertahankan INI lama yang sudah berfungsi agar pengaturan font dan layout tidak hilang. Salin ikon dan JSON judul skenario bila diperlukan.
3. Jalankan **`<GAME_DIR>\DC2DMLauncher.exe`** dengan working directory `<GAME_DIR>`. Jika memakai shortcut, isi **Start in** dengan folder tersebut.
4. Pilih bahasa yang sesuai pada pengaturan patch. Berkas MES Indonesia ditempatkan di `<GAME_DIR>\id_Data\MES`; untuk bahasa Inggris, gunakan `<GAME_DIR>\eng_data\MES`. Pengaturan `Language` pada bagian `[Settings]` di `DC2DM.ini`: `0` Jepang, `1` Indonesia, `2` Inggris.

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

Launcher sudah menyertakan DLL pendukung locale. Kedua RAR menyediakan tool dan patch; keduanya tidak berisi game lengkap atau seluruh naskah terjemahan. Folder source repositori boleh ditempatkan di mana saja. Paket patch juga tersedia di `DC2DMPatch a/build/Released` pada source.

## Buka aplikasi

Ekstrak `DC2DMMesTextTool_GUI.rar` ke folder pilihan Anda dan jalankan `DC2DMMesTextTool_GUI.exe`. Jika memakai source repositori, jalankan `bin\Release\net8.0-windows\DC2DMMesTextTool_GUI.exe`.
Paket siap pakai berada di folder yang sama: `DC2DMMesTextTool_GUI.rar`.
Aplikasi membutuhkan **.NET 8 Desktop Runtime**. Simpan EXE, DLL, `.deps.json`, dan `.runtimeconfig.json` dalam satu folder.

## Single File

**MES → JSON (exporter)**

1. Isi **Input MES/JSON** dengan MES asli.
2. Isi **Output JSON/MES**, atau kosongkan untuk membuat JSON di sebelah input.
3. Klik **Export (MES -> JSON)**.

Hasil default menggabungkan nama karakter dan dialog yang berurutan:

```json
[
  { "message": "Narasi." },
  { "name": "Otome", "message": "「Dialog karakter.」" }
]
```

Ekspor dari tab Single File dan Batch memakai format yang sama. Nama pendek yang diikuti dialog berawalan `「`, `『`, atau `“` digabung menjadi objek `name`/`message`. Ekspor mempertahankan ejaan nama Jepang/terjemahan dan tidak menerjemahkan nama.

**JSON → MES (importer)**

1. Isi **Input MES/JSON** dengan JSON terjemahan.
2. Letakkan MES asli untuk skenario yang sama di sebelah JSON, dengan nama dasar yang sama: `scene.json` memakai `scene.mes`. Jika MES asli tidak ditemukan, impor berhenti dengan pesan kesalahan.
3. Tentukan **Output JSON/MES** yang berbeda dari MES asli. Jika dikosongkan, hasil ditulis sebagai `new_scene.mes` di sebelah MES asli. Jika memilih folder lain, buat folder tersebut terlebih dahulu.
4. Pilih **Word Wrap Width**: default `46`, rentang `10–46`.
5. Klik **Import (JSON -> MES)**.

Importer menerima JSON gabungan dan JSON lama dengan nama/dialog terpisah. Saat impor, pasangan `name`/`message` dikembalikan menjadi dua entri MES. Jumlah entri setelah pemisahan harus sama dengan MES asli. Template asli dibutuhkan karena JSON tidak memuat seluruh instruksi, label, aset, dan alur skenario.

## Batch

- **Export:** isi **MES Folder** dengan folder MES asli dan **JSON Folder** dengan folder tujuan, lalu klik **Batch Export (MES -> JSON)**. Jika **JSON Folder** kosong, hasil masuk ke `json_output` di dalam folder MES.
- **Import:** isi **JSON Folder**, **MES Folder** asli, dan **Output Folder** yang berbeda, lalu klik **Batch Import (JSON -> MES)**. Jika output kosong, hasil masuk ke `mes_output` di dalam folder MES asli.
- Nama file harus sama: `scene.json` memakai template `scene.mes`.
- **Word Wrap Width** untuk impor memakai default `46`, rentang `10–46`.
- File gagal ditampilkan di log; batch tetap memproses file lain. Template yang hilang ditandai **Skipping** dan dilewati, jadi periksa log sebelum memakai hasilnya.

## Layout dan ikon backlog

Word wrap diterapkan pada isi dialog/narasi. Nama karakter tidak dibungkus; label pilihan dan antarmuka mempertahankan format aslinya. Pertahankan ejaan `Yuto` / `勇斗`, `Yuki` / `由姫`, dan `Yuuki` / `桜姫` karena ketiganya memiliki pemetaan potret yang berbeda. Yoshiyuki / 義之 memakai potret kosong bawaan.

Wrap `46` berarti **46 sel setengah lebar**, setara 506 piksel pada ukuran font normal 22px. Karakter lebar penuh memakan ruang lebih besar daripada huruf Latin. Pemisah baris eksplisit dipertahankan; CRLF, CR, dan teks literal `\n` dinormalisasi.

**Pesan lebih dari empat baris atau kata utuh yang melebihi batas lebar ditolak sebelum MES ditulis.** Pendekkan kalimat atau sesuaikan pemisah baris jika validasi gagal. Importer tidak memangkas teks atau mengecilkan font untuk memaksakannya masuk.

**Pemetaan potret dan perbaikan jarak baris 24px terdapat pada `DC2DM.EXE` dalam paket rilis.** Wrap mengatur lebar teks saat impor; EXE memuat perbaikan backlog, sementara DLL menyediakan pengaturan patch saat runtime. Konversi MES/JSON dan build ulang DLL saja tidak menerapkan perubahan EXE tersebut. Untuk memainkan hasil impor, buka game melalui `DC2DMLauncher.exe` dari `<GAME_DIR>`.

Petunjuk teknis tersedia di [README patch](DC2DMPatch%20a/README.md) dan [dokumentasi perbaikan backlog](DC2DMPatch%20a/tools/backlog_fix/README.md).

## Validasi dan encoding

- Konverter memakai UTF-8 untuk JSON dan CP932 untuk teks MES. Gunakan karakter yang didukung CP932 dalam terjemahan.
- Versi MES yang tidak didukung, jumlah entri yang tidak cocok, lebar di luar `10–46`, serta dialog yang melampaui batas baris/lebar ditolak sebelum output ditulis.
- Pertahankan urutan objek dan field `name`; jangan menambah atau menghapus entri skenario.
- Spasi dalam teks MES terenkripsi disimpan sebagai `_` agar tidak menjadi terminator teks. Patch menampilkannya kembali sebagai spasi saat game berjalan.
- Gunakan file/folder output yang berbeda dari sumber agar MES asli tetap tersedia untuk impor berikutnya.

## CLI

Dari folder executable, buka PowerShell. Contoh berikut memakai `scene.mes` dan folder `original`/`json` sebagai input; ganti dengan lokasi berkas Anda. Buat folder tujuan untuk impor tunggal sebelum menjalankannya:

```powershell
New-Item -ItemType Directory -Force ".\new" | Out-Null
.\DC2DMMesTextTool_GUI.exe export "scene.mes" "scene.json"
.\DC2DMMesTextTool_GUI.exe import "scene.json" "original\scene.mes" "new\scene.mes"
.\DC2DMMesTextTool_GUI.exe batch-export "original" "json"
.\DC2DMMesTextTool_GUI.exe batch-import "json" "original" "mes_output" -w 46
.\DC2DMMesTextTool_GUI.exe normalize-json "json"
```

CLI `import` tunggal memakai lebar tetap **46**. Opsi `-w` tersedia pada `batch-import`, dengan default **46** dan rentang **10–46**.

Jika output dihilangkan, ekspor tunggal membuat JSON di sebelah input; impor tunggal membuat `output_scene.mes` di sebelah MES asli. Batch memakai `json_output` di dalam folder input MES atau `mes_output` di dalam folder MES asli.

`normalize-json` menggabungkan nama/dialog pada JSON lama dan membuat cadangan lengkap dengan penanda waktu sebelum mengganti JSON. Folder cadangan dapat diberikan sebagai argumen kedua. Seret MES ke executable untuk mengekspor JSON di sebelahnya, atau seret folder untuk mengekspor MES di dalamnya ke `json_output`.

## Hasil verifikasi

- Konverter lulus **519 pemeriksaan**, mencakup delapan nama Jepang/terjemahan, empat baris, JSON lama, impor berulang yang identik byte demi byte, serta penolakan input tanpa menimpa output lama.
- Konverter dalam arsip lulus uji ekspor → impor CLI dengan hasil yang identik byte demi byte.
- Perbaikan EXE lulus empat kelompok uji jarak baris dan lima kelompok uji potret, termasuk **30.374 lookup native** dan **1.148 pemeriksaan koordinat potret**.
- Hash EXE rilis cocok dengan versi yang sebelumnya diverifikasi di game. DLL dan launcher berhasil dibangun; build tersebut belum diuji ulang secara interaktif di game.

## Build dan uji

Clone beserta submodule agar dependensi Detours tersedia:

```powershell
git clone --recurse-submodules https://github.com/SakuraSymphonyReTranslation/DC2DMMesTextTool_GUI-and-Patch.git
```

Untuk checkout yang sudah ada, jalankan `git submodule update --init --recursive`. Dari folder source proyek:

```powershell
dotnet build .\DC2DMMesTextTool_GUI.csproj -c Release
dotnet run --project ".\DC2DMPatch a\tools\backlog_fix\converter_tests\ConverterTests.csproj" -c Release -- "<ORIGINAL_MES_DIR>\sin_1931_f1.mes" "<VALIDATION_OUTPUT_DIR>"
```

Ganti placeholder dengan folder Anda sebelum menjalankan perintah. Build GUI membutuhkan **.NET 8 SDK**. Uji konverter memakai MES asli `sin_1931_f1.mes` dari game Anda; korpus ini tidak disertakan dalam repositori. Gunakan folder output pengujian yang terpisah dari script aktif game.

Build patch DLL/launcher membutuhkan **Visual Studio 2022, Desktop development with C++, Windows SDK, dan CMake di PATH**:

```powershell
& ".\DC2DMPatch a\build.bat"
```

Output berada di `DC2DMPatch a/build`, dengan salinan distribusi di `build/Released`. Build tidak memasang berkas ke folder game. Lihat [README patch](DC2DMPatch%20a/README.md) untuk build DLL/launcher dan [dokumentasi backlog](DC2DMPatch%20a/tools/backlog_fix/README.md) untuk build ulang perbaikan EXE. [Tool teks C++](MesTextTool-MesTextToolVer1.3.6/README.md) memiliki panduan terpisah.
