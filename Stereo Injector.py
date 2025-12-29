import os
import urllib.request
import glob
import json
import re
from pathlib import Path

# ===== Konfigurasi GitHub =====
github_user = "justfarissss"
github_repo = "Database-Stereo-Discord"
github_branch = "main"

# ===== Varian Discord =====
discord_variants = ["Discord", "DiscordPTB", "DiscordCanary"]

localappdata = os.environ.get("LOCALAPPDATA")
if not localappdata:
    raise RuntimeError("Env %LOCALAPPDATA% tidak ditemukan.")

# Regex contoh untuk folder app-1.0.N (jika nanti dipakai filter 'terbaru')
APP_VER_RE = re.compile(r"^app-1\.0\.(\d+)$")

def resolve_targets(path_pattern: str) -> list[str]:
    """Kembalikan SEMUA hasil glob. Tidak memilih hanya satu."""
    matches = glob.glob(path_pattern)
    if not matches:
        print(f"  [INFO] Tidak ada match untuk pola: {path_pattern}")
        return []
    # Hapus duplikat + urutkan biar output rapi
    uniq = sorted(set(matches))
    print(f"  [MATCH] {len(uniq)} target ditemukan untuk pola ini.")
    for m in uniq:
        print(f"    - {m}")
    return uniq

def githubfiles(user, repo, branch, file_path, destination_file) -> bool:
    """Unduh 1 file mentah dari GitHub ke path file tujuan."""
    url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"
    try:
        print(f"    [GET] {url}")
        dest_dir = os.path.dirname(destination_file)
        if not os.path.isdir(dest_dir):
            print(f"    [ERROR] Direktori tujuan tidak ada: {dest_dir}")
            return False
        urllib.request.urlretrieve(url, destination_file)
        print(f"    [OK] File tertulis: {destination_file}")
        return True
    except Exception as e:
        print(f"    [ERROR] Unduh/ganti gagal: {e}")
        return False

def githubfolder(user, repo, branch, folder_path, destination_dir) -> bool:
    """Unduh semua file pada folder GitHub (level 1) ke direktori tujuan."""
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{folder_path}?ref={branch}"
    try:
        print(f"    [API] {api_url}")
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Python-Script'})
        with urllib.request.urlopen(req) as resp:
            contents = json.loads(resp.read().decode())

        if not isinstance(contents, list):
            print("    [ERROR] Respons API tidak valid.")
            return False

        if not os.path.isdir(destination_dir):
            print(f"    [ERROR] Direktori tujuan tidak ada: {destination_dir}")
            return False

        ok_all = True
        for item in contents:
            if item.get('type') != 'file':
                continue
            file_url = item.get('download_url')
            file_name = item.get('name')
            dest_file = os.path.join(destination_dir, file_name)
            try:
                print(f"      - Unduh {file_name}")
                urllib.request.urlretrieve(file_url, dest_file)
            except Exception as e:
                print(f"        [ERROR] {file_name}: {e}")
                ok_all = False

        if ok_all:
            print("    [OK] Semua file folder terunduh.")
        else:
            print("    [WARN] Beberapa file gagal diunduh.")
        return ok_all
    except Exception as e:
        print(f"    [ERROR] Gagal ambil folder: {e}")
        return False

print("        Stereo Injector by justfarissss")
print("             Stereo Node by Skenzo")
print("⋆⁺₊⋆ ━━━━━━━━━━━━━━━━━━━ • ━━━━━━━━━━━━━━━━━━━ ⋆⁺₊⋆")
print(f"Sumber Berkas: {github_user}/{github_repo}\n")

grand_success = 0
grand_fail = 0

for variant in discord_variants:
    print(f"\n=== VARIANT: {variant} ===")
    base = Path(localappdata) / variant
    if not base.exists():
        print(f"[SKIP] {variant} tidak terinstal di {base}")
        continue
    mappings = [
        {
            "Kind": "folder",
            "Source": "discord-node",
            "DestPattern": os.path.join(localappdata, variant, "app-*", "modules", "discord_voice-*", "discord_voice"),
        },
    ]

    for i, mapping in enumerate(mappings, 1):
        print(f"\n[{i}/{len(mappings)}] Pasang: {mapping['Source']} (Kind={mapping['Kind']})")
        targets = resolve_targets(mapping["DestPattern"])

        if not targets:
            print("  [INFO] Tidak ada target untuk pola ini. Lanjut.")
            continue

        for t in targets:
            if mapping["Kind"] == "file":
                ok = githubfiles(github_user, github_repo, github_branch, mapping["Source"], t)
            else:
                ok = githubfolder(github_user, github_repo, github_branch, mapping["Source"], t)

            if ok:
                grand_success += 1
            else:
                grand_fail += 1

print("\n=== RINGKASAN ===")
print(f"Berhasil: {grand_success}")
print(f"Gagal   : {grand_fail}")
if grand_fail == 0 and grand_success > 0:
    print("Stereo telah dipasang pada semua target yang ditemukan. Silakan buka Discord untuk uji.")
elif grand_success == 0:
    print("Tidak ada perubahan yang dilakukan. Cek log di atas. Jangan Lupa Close Discord sebelum menjalankan script ini.")
else:
    print("Beberapa pemasangan gagal. Cek log di atas.")
