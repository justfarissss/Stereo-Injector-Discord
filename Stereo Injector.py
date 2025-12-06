import os
import urllib.request
import glob
import json

github_user = "justfarissss"
github_repo = "Database-Stereo-Discord"
github_branch = "main"

mappings = [
    {
        "Source": "ffmpeg.dll",
        "Destination": os.path.join(os.getenv('LOCALAPPDATA'), "Discord", "*app*", "ffmpeg.dll"),
        "UsePattern": True,
        "IsFolder": False
    },
    {
        "Source": "discord-node",
        "Destination": os.path.join(os.getenv('LOCALAPPDATA'), "Discord", "*app-*", "modules", "discord_voice-1", "discord_voice"),
        "UsePattern": True,
        "IsFolder": True
    },
]

def pattern(path):
    matches = glob.glob(path)
    
    if len(matches) == 0:
        raise Exception(f"Tidak ditemukan folder yang sesuai dengan pola yang ditentukan: {path}")
    elif len(matches) > 1:
        print(f"  Ditemukan beberapa hasil yang cocok. Menggunakan hasil pertama yang cocok:")
        for match in matches:
            print(f"    - {match}")
    
    return matches[0]

def githubfiles(user, repo, branch, file_path, destination_path, use_pattern):
    url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"
    
    try:
        print(f"  URL Sumber : {url}")
        print(f"  Tujuan : {destination_path}")
        
        final_path = destination_path
        if use_pattern:
            try:
                final_path = pattern(destination_path)
                print(f"  Resolved to: {final_path}")
            except Exception as e:
                print(f"  [ERROR] {e}")
                return False
        
        dest_dir = os.path.dirname(final_path)
        if not os.path.exists(dest_dir):
            print(f"  [ERROR] Direktori tujuan tidak ada: {dest_dir}")
            return False
        
        urllib.request.urlretrieve(url, final_path)
        print("  [SUCCESS] Berkas telah diganti dengan sukses!")
        return True
    except Exception as e:
        print(f"  [ERROR] Gagal mengunduh: {e}")
        return False

def githubfolder(user, repo, branch, folder_path, destination_path, use_pattern):
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{folder_path}?ref={branch}"
    
    try:
        print(f"  Mengambil isi folder dari: {folder_path}")
        print(f"  Tujuan : {destination_path}")
        
        final_path = destination_path
        if use_pattern:
            try:
                final_path = pattern(destination_path)
                print(f"  Resolved to: {final_path}")
            except Exception as e:
                print(f"  [ERROR] {e}")
                return False
        
        if not os.path.exists(final_path):
            print(f"  [ERROR] Direktori tujuan tidak ada: {final_path}")
            return False
        
        req = urllib.request.Request(api_url)
        req.add_header('User-Agent', 'Python-Script')
        
        with urllib.request.urlopen(req) as response:
            contents = json.loads(response.read().decode())
        
        if not isinstance(contents, list):
            print(f"  [ERROR] Respons tidak valid dari API GitHub")
            return False
        
        success = True
        for item in contents:
            if item['type'] == 'file':
                file_url = item['download_url']
                file_name = item['name']
                dest_file = os.path.join(final_path, file_name)
                
                print(f"    Unduh: {file_name}")
                try:
                    urllib.request.urlretrieve(file_url, dest_file)
                except Exception as e:
                    print(f"    [ERROR] Gagal mengunduh {file_name}: {e}")
                    success = False
        
        if success:
            print("  [SUCCESS] Semua file dalam folder telah diunduh dengan sukses!")
        else:
            print("  [WARNING] Beberapa file gagal diunduh.")
        
        return success
    except Exception as e:
        print(f"  [ERROR] Gagal mengambil folder: {e}")
        return False


print("        Stereo Inejector by justfarissss")
print("⋆⁺₊⋆ ━━━━━━━━━━━━━━━━━━━ • ━━━━━━━━━━━━━━━━━━━ ⋆⁺₊⋆")
print(f"Sumber Berkas: {github_user}/{github_repo}")
print()

success_count = 0
fail_count = 0
counter = 0

for mapping in mappings:
    counter += 1
    print(f"[{counter}/{len(mappings)}] Pemasangan : {mapping['Source']}")
    
    if mapping.get('IsFolder', False):
        result = githubfolder(
            github_user,
            github_repo,
            github_branch,
            mapping['Source'],
            mapping['Destination'],
            mapping['UsePattern']
        )
    else:
        result = githubfiles(
            github_user,
            github_repo,
            github_branch,
            mapping['Source'],
            mapping['Destination'],
            mapping['UsePattern']
        )
    
    if result:
        success_count += 1
    else:
        fail_count += 1
    print()

if fail_count == 0:
    print("\nStereo telah dipasang, buka Discord dan lihat apakah berfungsi!")
    print("\nCatatan: Saat ini terdapat masalah dalam memutar beberapa file MP3 dan MP4. Mohon diperhatikan hal ini.")
else:
    print("\nBeberapa file gagal diperbarui. Periksa output di atas.")

print("\nTekan Enter untuk keluar...")
input()
