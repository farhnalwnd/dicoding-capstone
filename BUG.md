# Dokumentasi Potensi Bug - Fine-Tuning System

Berikut adalah detail potensi bug yang diidentifikasi pada file jupyter dan generator dataset script.

---

## 1. Pemblokiran Output Log pada Notebook (Kritikal)

* **Lokasi**: `training/notebooks/finetuning-model.ipynb`
* **Gejala**: Sel jupyter terlihat "freeze" / "hang" (bintang `[*]`) tanpa menampilkan progress training apapun selama berjam-jam.
* **Penyebab**: 
  Penggunaan `subprocess.run(cmd, capture_output=True, text=True)` menahan standard output (stdout) dari script training ke memori. Log training (seperti progress bar epoch, loss values, learning rate) baru akan dicetak ke notebook sekaligus setelah seluruh proses training selesai (4-12 jam kemudian).
* **Dampak**: User tidak bisa memonitor progress training secara real-time dan rentan salah mengira Jupyter/server hang.

---

## 2. Dependensi Kaku pada Placeholder `{skill1}` dan `{skill2}`

* **Lokasi**: `training/scripts/generate_dataset.py` (Fungsi `_fill_template()`)
* **Gejala**: Teks placeholder `"{skill1}"` atau `"{skill2}"` tidak ter-replace (muncul mentah di CSV).
* **Penyebab**: 
  Logic penggantian menggunakan pengecekan AND:
  ```python
  if "{skill1}" in template and "{skill2}" in template:
  ```
* **Dampak**: Jika user membuat template kustom baru yang hanya berisi `{skill1}` saja (tanpa `{skill2}`), proses penggantian tidak akan tereksekusi. Ini membatasi kebebasan variasi template.

---

## 3. Ketidaksesuaian Interpreter Python pada Subprocess

* **Lokasi**: `training/notebooks/finetuning-model.ipynb`
* **Gejala**: Error `ModuleNotFoundError: No module named 'sentence_transformers'` saat dijalankan dari notebook, meskipun library sudah terinstal.
* **Penyebab**: 
  Notebook memanggil sub-proses dengan string `'python'` secara langsung:
  ```python
  cmd = ['python', ...]
  ```
  Ini akan mengeksekusi system-default Python interpreter, bukan path Python interpreter dari virtual environment (venv) aktif yang sedang digunakan oleh Jupyter Kernel.
* **Dampak**: Training gagal dijalankan lewat notebook karena tidak menemukan dependency yang terinstal di virtual environment.
