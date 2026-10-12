# Pembersihan proyek DC2DM — 11 Oktober 2026

Proyek ini sekarang khusus **Da Capo 2 Dearest Marriage**. Konfigurasi game lain,
skrip/data game lain, kode hook yang sudah tidak dipakai, serta build lama telah
dikeluarkan dari folder proyek aktif. Sumber patch memakai `src/dc2dmpatch.cpp`,
menu memakai nama DC2DM, dan pengaturan patch memakai `DC2DM.ini`.

Hasil terbaru:

- GUI/CLI: `bin/Release/net8.0-windows/DC2DMMesTextTool_GUI.exe`.
- Patch/launcher: `DC2DMPatch a/build/Released/DC2DMPatch.dll` dan `DC2DMLauncher.exe`.
- Alat teks C++: `DC2DMPatch a/tools/MesTextTool.exe` dan `MesTextTool-cp932-dc2dm.exe`.

Ketiga proyek berhasil dibangun. Uji konversi lulus **519 pemeriksaan**, termasuk
penolakan versi MES yang tidak didukung tanpa menimpa output. Sebanyak **311 MES
asli** memiliki versi DC2DM yang sesuai. Ekspor satu MES melalui alat C++ juga berhasil.
Build GUI masih melaporkan 18 peringatan nullability/field dari kode yang sudah ada.
Patch/launcher belum diuji ulang di dalam game dalam pekerjaan ini.

Berkas game terpasang di `<GameDir>` (EXE, DLL, launcher, dan INI) tetap
identik menurut SHA-256. Hasil build tersedia di lokasi proyek di atas.

## Pemulihan

Salinan pemulihan berada di luar proyek:
`<CleanupBackupDir>`.

- `before`: sumber dan program sebelum perubahan.
- `removed`: 129 berkas/direktori yang dikeluarkan dari proyek aktif.
- `removed-manifest.json`: daftar lokasi relatif untuk pemulihan.
- `verification.json`: pemeriksaan identitas program dan hash berkas game terpasang.

Pulihkan hanya berkas yang diperlukan ke lokasi relatif yang sama. Snapshot
konverter sebelum perubahan jarak baris juga tersimpan di `removed`, sehingga
riwayat pekerjaan sebelumnya tetap tersedia.

Catatan lokasi: <GameDir> adalah direktori instalasi game pilihan pengguna. <CleanupBackupDir> menunjuk cadangan lokal sesi pembersihan; cadangan tersebut tidak disertakan dalam repositori/rilis.
