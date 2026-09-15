import sys
import os
import re
import json
import shutil
import subprocess
from pathlib import Path

def get_script_paths():
    """Defines and returns the core paths based on the script's execution location."""
    script_dir = Path(__file__).resolve().parent  # ./.dev/
    root_dir = script_dir.parent                  # ./
    addon_dir = root_dir / "PrephUI"              # ./PrephUI/
    packaged_dir = root_dir / ".packaged"         # ./.packaged/
    globalvars_path = script_dir / "globalvars.preph"
    
    return script_dir, root_dir, addon_dir, packaged_dir, globalvars_path

def load_globalvars(globalvars_path):
    """Loads the global configuration from the JSON file."""
    if not globalvars_path.exists():
        print(f"Error: Could not find {globalvars_path}")
        sys.exit(1)
    with open(globalvars_path, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_folder_junction(wow_addon_dir_str, addon_dir):
    """Generates a folder junction to the WoW Addon directory if it doesn't exist."""
    print("\n--- Generating Folder Junction ---")
    wow_addon_dir = Path(wow_addon_dir_str)
    
    if not wow_addon_dir.exists():
        print(f"Error: WoW Addon directory not found at {wow_addon_dir}")
        return

    dest_path = wow_addon_dir / "PrephUI"

    if dest_path.exists():
        print(f"Skipped: Destination already exists at {dest_path}")
        return

    safe_dest = os.path.normpath(str(dest_path))
    safe_source = os.path.normpath(str(addon_dir))
    
    command = f'mklink /J "{safe_dest}" "{safe_source}"'
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, errors="replace")
        if result.returncode == 0:
            print(f"Success: Created junction link {safe_dest} -> {safe_source}")
        else:
            err_msg = (result.stderr or result.stdout or "Unknown error").strip()
            print(f"Error creating junction: {err_msg}")
    except Exception as e:
        print(f"Exception occurred during junction creation: {e}")

def update_toc_version(addon_dir, version_string):
    """Parses the version into the PrephUI.toc file."""
    print("\n--- Updating TOC Version ---")
    toc_path = addon_dir / "PrephUI.toc"
    
    if not toc_path.exists():
        print(f"Error: TOC file not found at {toc_path}")
        return

    with open(toc_path, 'r', encoding='utf-8') as f:
        toc_content = f.read()

    # Replaces the ## Version: <anything> line with the new version
    updated_toc = re.sub(
        r"^(## Version:).*$", 
        rf"\1 {version_string}", 
        toc_content, 
        flags=re.MULTILINE
    )

    if updated_toc != toc_content:
        with open(toc_path, 'w', encoding='utf-8') as f:
            f.write(updated_toc)
        print(f"Success: Updated TOC version to {version_string}")
    else:
        print(f"Skipped: TOC version is already {version_string} or tag missing.")

def update_changelog(root_dir, addon_dir, changelog_lua_rel_path):
    """Parses the README.md changelog and injects it into the specified Lua file."""
    print("\n--- Updating Changelog in Lua ---")
    readme_path = addon_dir / "README.md"
    
    if not readme_path.exists():
        print(f"Error: README.md not found at {readme_path}")
        return

    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()

    # Extract everything from '## Changelog' to the end of the file
    changelog_match = re.search(r"(## Changelog\n.*)", readme_content, re.DOTALL)
    if not changelog_match:
        print("Error: Could not find '## Changelog' section in README.md")
        return
    
    changelog_text = changelog_match.group(1).strip()
    
    # Resolve the lua path. The JSON might have 'PrephUI\Modules\...' so we resolve it from root
    changelog_lua_path = root_dir / changelog_lua_rel_path

    if not changelog_lua_path.exists():
        print(f"Warning: Changelog lua file {changelog_lua_path} does not exist. Creating it.")
        changelog_lua_path.parent.mkdir(parents=True, exist_ok=True)
        original_lua_content = ""
    else:
        with open(changelog_lua_path, 'r', encoding='utf-8') as f:
            original_lua_content = f.read()

    # Create the Lua string block using [=[ ]=] to avoid quote escaping issues
    lua_changelog_variable = f"PrephUI_Changelog = [=[\n{changelog_text}\n]=]\n"

    # Regex to find and replace an existing PrephUI_Changelog assignment, or append if missing
    existing_var_pattern = re.compile(r"PrephUI_Changelog\s*=\s*\[=\[.*?\]=\]", re.DOTALL)
    
    if existing_var_pattern.search(original_lua_content):
        updated_lua = existing_var_pattern.sub(lua_changelog_variable.strip(), original_lua_content)
    else:
        updated_lua = original_lua_content + "\n" + lua_changelog_variable

    with open(changelog_lua_path, 'w', encoding='utf-8') as f:
        f.write(updated_lua)
        
    print(f"Success: Parsed changelog into {changelog_lua_path.name}")

def enforce_lua_headers(addon_dir):
    """Runs the integrated headers.py logic to ensure all Lua files have the correct copyright header."""
    print("\n--- Enforcing Lua Headers ---")
    
    NEW_HEADER_TEMPLATE = """--[[
    <{rel_path}>
    Copyright (C) 2026 Prephmage / Prephalia
    All Rights Reserved.

    This software may not be copied, modified, or distributed 
    without the express written permission of the copyright owner.

    -- Additional Metadata --
    Author:  Prephmage / Prephalia
    CurseForge: https://www.curseforge.com/members/prephalia/projects
    GitHub: https://github.com/JulianStiebler/WoW_PrephsFramework
--]]"""

    HEADER_REGEX = re.compile(
        r"--\[\[\s*\n\s*<(.*?)>\s*\n\s*Copyright \(C\) (?:<)?2026(?:>)? (?:<)?Prephmage / Prephalia(?:>)?.*?--\]\]", 
        re.DOTALL
    )

    for dirpath, dirnames, filenames in os.walk(addon_dir):
        # Ignore the 'libs' and 'Libs' folders
        if 'libs' in dirnames:
            dirnames.remove('libs')
        if 'Libs' in dirnames:
            dirnames.remove('Libs')

        for filename in filenames:
            if filename.endswith(".lua"):
                file_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(file_path, addon_dir)
                
                # Format for the addon root structure (PrephUI/...)
                formatted_rel_path = os.path.join("PrephUI", rel_path).replace("/", "\\")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                expected_new_header = NEW_HEADER_TEMPLATE.format(rel_path=formatted_rel_path)
                match = HEADER_REGEX.search(original_content)
                
                if match:
                    existing_header = match.group(0)
                    if existing_header == expected_new_header:
                        pass # Silently skip if already perfect
                    else:
                        new_content = original_content[:match.start()] + expected_new_header + original_content[match.end():]
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f"Updated: Replaced old license header for {formatted_rel_path}")
                else:
                    if "Copyright (C)" in original_content and "Prephmage" in original_content:
                        print(f"Warning: Found copyright but couldn't parse the header structure correctly in {formatted_rel_path}")
                        continue
                    
                    new_content = f"{expected_new_header}\n\n\n{original_content}"
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Success: Added new header to {formatted_rel_path}")

def update_readme_toc(addon_dir):
    """Parses changelog headers from README.md and updates the TOC automatically."""
    print("\n--- Updating README Table of Contents ---")
    readme_path = addon_dir / "README.md"
    
    if not readme_path.exists():
        print(f"Error: README.md not found at {readme_path}")
        return

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    changelog_match = re.search(r"## Changelog\s*\n(.*)", content, re.DOTALL)
    if not changelog_match:
        print("Warning: Could not find '## Changelog' section in README.md")
        return

    versions = re.findall(r"^###\s+(V[\w\.\-]+)", changelog_match.group(1), re.MULTILINE)
    
    # Compute the anchor slug outside of the f-string expression block
    toc_entries = []
    for v in versions:
        slug = re.sub(r'[^\w-]', '', v.lower())
        toc_entries.append(f"  - [{v}](#{slug})")

    new_toc_block = "- [Changelog](#changelog)\n" + "\n".join(toc_entries)

    pattern = r"(- \[Changelog\]\(#changelog\)\n(?:\s+- \[.*?\]\(#.*?\)\n?)*)"
    
    if re.search(pattern, content):
        updated_content = re.sub(pattern, new_toc_block + "\n", content, count=1)
        if updated_content != content:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print("Success: Updated README.md Table of Contents")
        else:
            print("Skipped: README.md Table of Contents is already up to date")
            
def package_addon(addon_dir, packaged_dir, version_string):
    """Packages the PrephUI folder into a zip file inside the .packaged directory."""
    print("\n--- Packaging Addon ---")
    packaged_dir.mkdir(parents=True, exist_ok=True)
    
    zip_filename = packaged_dir / f"PrephUI_v{version_string}"
    
    # shutil.make_archive adds the .zip extension automatically
    shutil.make_archive(
        base_name=str(zip_filename),
        format='zip',
        root_dir=addon_dir.parent, 
        base_dir="PrephUI"
    )
    
    print(f"Success: Packaged addon to {zip_filename}.zip")

def main():
    script_dir, root_dir, addon_dir, packaged_dir, globalvars_path = get_script_paths()
    
    # 1. Load configuration
    cfg = load_globalvars(globalvars_path)
    
    wow_addon_dir = cfg["paths"]["wow_addon_directory"]
    version_data = cfg["version"]
    version_string = f'{version_data["major"]}.{version_data["minor"]}.{version_data["patch"]}'
    changelog_lua_rel_path = cfg["project"]["changelog"]
    
    # 2. Execute process steps
    generate_folder_junction(wow_addon_dir, addon_dir)
    update_toc_version(addon_dir, version_string)
    update_changelog(root_dir, addon_dir, changelog_lua_rel_path)
    update_readme_toc(addon_dir)
    enforce_lua_headers(addon_dir)
    package_addon(addon_dir, packaged_dir, version_string)
    
    print("\nProcess completed successfully.")

if __name__ == "__main__":
    sys.exit(main())