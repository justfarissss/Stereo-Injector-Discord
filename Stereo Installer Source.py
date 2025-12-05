import os
import urllib.request
import glob
import json

github_user = "justfarissss"
github_repo = "BetterDiscord-Stereo-Files"
github_branch = "main"

mappings = [
    {
        "Source": "ffmpeg.dll",
        "Destination": os.path.join(os.getenv('LOCALAPPDATA'), "Discord", "*app*", "ffmpeg.dll"),
        "UsePattern": True,
        "IsFolder": False
    },
    {
        "Source": "VoiceModules",
        "Destination": os.path.join(os.getenv('LOCALAPPDATA'), "Discord", "*app-*", "modules", "discord_voice-1", "discord_voice"),
        "UsePattern": True,
        "IsFolder": True
    }
]

def pattern(path):
    matches = glob.glob(path)
    
    if len(matches) == 0:
        raise Exception(f"No folder found matching pattern: {path}")
    elif len(matches) > 1:
        print(f"  Multiple matches found. Using first match:")
        for match in matches:
            print(f"    - {match}")
    
    return matches[0]

def githubfiles(user, repo, branch, file_path, destination_path, use_pattern):
    url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{file_path}"
    
    try:
        print(f"  Source URL : {url}")
        print(f"  Destination : {destination_path}")
        
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
            print(f"  [ERROR] Destination directory does not exist: {dest_dir}")
            return False
        
        urllib.request.urlretrieve(url, final_path)
        print("  [SUCCESS] File replaced successfully!")
        return True
    except Exception as e:
        print(f"  [ERROR] Failed to download: {e}")
        return False

def githubfolder(user, repo, branch, folder_path, destination_path, use_pattern):
    api_url = f"https://api.github.com/repos/{user}/{repo}/contents/{folder_path}?ref={branch}"
    
    try:
        print(f"  Fetching folder contents from: {folder_path}")
        print(f"  Destination : {destination_path}")
        
        final_path = destination_path
        if use_pattern:
            try:
                final_path = pattern(destination_path)
                print(f"  Resolved to: {final_path}")
            except Exception as e:
                print(f"  [ERROR] {e}")
                return False
        
        if not os.path.exists(final_path):
            print(f"  [ERROR] Destination directory does not exist: {final_path}")
            return False
        
        req = urllib.request.Request(api_url)
        req.add_header('User-Agent', 'Python-Script')
        
        with urllib.request.urlopen(req) as response:
            contents = json.loads(response.read().decode())
        
        if not isinstance(contents, list):
            print(f"  [ERROR] Invalid response from GitHub API")
            return False
        
        success = True
        for item in contents:
            if item['type'] == 'file':
                file_url = item['download_url']
                file_name = item['name']
                dest_file = os.path.join(final_path, file_name)
                
                print(f"    Downloading: {file_name}")
                try:
                    urllib.request.urlretrieve(file_url, dest_file)
                except Exception as e:
                    print(f"    [ERROR] Failed to download {file_name}: {e}")
                    success = False
        
        if success:
            print("  [SUCCESS] All files in folder downloaded successfully!")
        else:
            print("  [WARNING] Some files failed to download")
        
        return success
    except Exception as e:
        print(f"  [ERROR] Failed to fetch folder: {e}")
        return False


print("                 Stereo Installation")
print("⋆⁺₊⋆ ━━━━━━━━━━━━━━━━━━━ • ━━━━━━━━━━━━━━━ ⋆⁺₊⋆")
print(f"Source of Files: {github_user}/{github_repo}")
print()

success_count = 0
fail_count = 0
counter = 0

for mapping in mappings:
    counter += 1
    print(f"[{counter}/{len(mappings)}] Installing : {mapping['Source']}")
    
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
    print("\nStereo has been installed, start Discord and see if it works!")
    print("\nNote : There are current issues with playing some mp3(s) and mp4(s) please be aware of this.")
else:
    print("\nSome files failed to update. Check the output above.")

print("\nPress Enter to exit...")
input()
