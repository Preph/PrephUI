import sys
import os
import re
import json
import shutil
import subprocess
import zipfile
from pathlib import Path


# ---------------------------------------------------------------------------
# Config / paths
# ---------------------------------------------------------------------------

def get_script_paths():
    """Defines and returns the core paths based on the script's execution location."""
    script_dir = Path(__file__).resolve().parent  # ./.dev/
    root_dir = script_dir.parent                  # ./
    packaged_dir = root_dir / ".packaged"         # ./.packaged/
    globalvars_path = script_dir / "globalvars.preph"

    return script_dir, root_dir, packaged_dir, globalvars_path


def rel_path(root_dir, value):
    """Resolves a config path (may contain Windows backslashes) against the repo root."""
    return root_dir / Path(value.replace("\\", "/"))


def load_globalvars(globalvars_path):
    """Loads the global configuration from the JSON file."""
    if not globalvars_path.exists():
        print(f"Error: Could not find {globalvars_path}")
        sys.exit(1)
    with open(globalvars_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_projects(cfg, root_dir):
    """Normalises the 'projects' list from the config into resolved project dicts.

    Optional per project:
        version         {major, minor, patch} (packaging skipped when omitted)
        folder          [name]               addon folder relative to the repo root
        toc             [<folder>/<name>.toc]
        readme          [<folder>/README.md]
        changelog                            lua file containing `local changelogText = [[ ]]`
        github_url, curseforge_url           written into the Lua file headers
        alsoBundleThese                      list of extra folders to bundle into the zip
    """
    projects = []
    for raw in cfg.get("projects", []):
        name = raw["name"]
        folder = raw.get("folder", name)
        v = raw.get("version")

        version_string = f'{v["major"]}.{v["minor"]}.{v["patch"]}' if v else None

        projects.append({
            "name": name,
            "folder": folder,
            "addon_dir": root_dir / folder,
            "toc_path": rel_path(root_dir, raw["toc"]) if "toc" in raw
                        else root_dir / folder / f"{name}.toc",
            "readme_path": rel_path(root_dir, raw["readme"]) if "readme" in raw
                           else root_dir / folder / "README.md",
            "changelog_lua_path": rel_path(root_dir, raw["changelog"]) if raw.get("changelog") else None,
            "github_url": raw.get("github_url"),
            "curseforge_url": raw.get("curseforge_url"),
            "version_string": version_string,
            "also_bundle": [rel_path(root_dir, extra) for extra in raw.get("alsoBundleThese", [])],
        })
    return projects


# ---------------------------------------------------------------------------
# Per-project steps
# ---------------------------------------------------------------------------

def generate_folder_junction(wow_addon_dir_str, project):
    """Generates a folder junction to the WoW Addon directory if it doesn't exist."""
    name = project["name"]
    print(f"\n--- [{name}] Generating Folder Junction for: {wow_addon_dir_str} ---")
    wow_addon_dir = Path(wow_addon_dir_str)

    if not wow_addon_dir.exists():
        print(f"Error: WoW Addon directory not found at {wow_addon_dir}")
        return

    dest_path = wow_addon_dir / project["folder"]

    if dest_path.exists():
        print(f"Skipped: Destination already exists at {dest_path}")
        return

    safe_dest = os.path.normpath(str(dest_path))
    safe_source = os.path.normpath(str(project["addon_dir"]))

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


def update_toc_version(project):
    """Writes the project's version into its .toc file."""
    name = project["name"]
    version_string = project["version_string"]
    print(f"\n--- [{name}] Updating TOC Version ---")

    if not version_string:
        print("Skipped: No version specified for this project.")
        return

    toc_path = project["toc_path"]
    if not toc_path.exists():
        print(f"Skipped: TOC file not found at {toc_path}")
        return

    with open(toc_path, 'r', encoding='utf-8') as f:
        toc_content = f.read()

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


def markdown_changelog_to_addon_format(changelog_md):
    """Converts raw '## Changelog' markdown section from README into colored Lua changelog format."""
    body = re.sub(r"^##\s*Changelog\s*\n+", "", changelog_md.strip(), count=1)

    pieces = re.split(r"^###\s+(.+?)\s*$", body, flags=re.MULTILINE)

    version_blocks = []
    for i in range(1, len(pieces), 2):
        title = pieces[i].strip()
        section_body = pieces[i + 1] if i + 1 < len(pieces) else ""
        version_blocks.append((title, section_body))

    rendered_versions = []
    for title, section_body in version_blocks:
        rendered_lines = [f"|cffffd100{title}|r"]
        for line in section_body.split("\n"):
            if not line.strip():
                continue
            bullet_match = re.match(r"^(\s*)-\s?(.*)$", line)
            if bullet_match:
                indent, text = bullet_match.groups()
                rendered_lines.append(f"{indent}\u2022 {text}".rstrip())
            else:
                rendered_lines.append(line.rstrip())
        rendered_versions.append("\n".join(rendered_lines))

    divider = "\n\n|TInterface\\Common\\UI-TooltipDivider:5:400:0:0|t\n\n"
    return divider.join(rendered_versions)


def update_changelog(project):
    """Parses README changelog and injects it into the configured changelog Lua file."""
    name = project["name"]
    print(f"\n--- [{name}] Updating Changelog in Lua ---")

    changelog_lua_path = project["changelog_lua_path"]
    if changelog_lua_path is None:
        print("Skipped: No 'changelog' file configured for this project.")
        return

    readme_path = project["readme_path"]
    if not readme_path.exists():
        print(f"Skipped: README not found at {readme_path}")
        return

    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()

    changelog_match = re.search(r"(## Changelog\n.*)", readme_content, re.DOTALL)
    if not changelog_match:
        print(f"Error: Could not find '## Changelog' section in {readme_path.name}")
        return

    addon_changelog_text = markdown_changelog_to_addon_format(changelog_match.group(1))

    if not changelog_lua_path.exists():
        print(f"Error: Changelog lua file {changelog_lua_path} does not exist.")
        return

    with open(changelog_lua_path, 'r', encoding='utf-8') as f:
        original_lua_content = f.read()

    changelog_var_pattern = re.compile(
        r"(local\s+changelogText\s*=\s*\[\[\n?)(.*?)(\]\])",
        re.DOTALL
    )

    if not changelog_var_pattern.search(original_lua_content):
        print(f"Error: Could not find 'local changelogText = [[ ... ]]' block in {changelog_lua_path.name}")
        return

    updated_lua = changelog_var_pattern.sub(
        lambda m: f"{m.group(1)}{addon_changelog_text}{m.group(3)}",
        original_lua_content,
        count=1
    )

    stray_var_pattern = re.compile(
        rf"\n*{re.escape(name)}_Changelog\s*=\s*\[=\[.*?\]=\]\n*", re.DOTALL
    )
    updated_lua = stray_var_pattern.sub("\n", updated_lua).rstrip() + "\n"

    with open(changelog_lua_path, 'w', encoding='utf-8') as f:
        f.write(updated_lua)

    print(f"Success: Parsed changelog into {changelog_lua_path.name}")


def enforce_lua_headers(project):
    """Ensures all Lua files in the project have the correct copyright header."""
    name = project["name"]
    folder = project["folder"]
    addon_dir = project["addon_dir"]
    print(f"\n--- [{name}] Enforcing Lua Headers ---")

    metadata_lines = ["    Author:  Prephmage / Prephalia"]
    if project.get("curseforge_url"):
        metadata_lines.append(f"    CurseForge: {project['curseforge_url']}")
    if project.get("github_url"):
        metadata_lines.append(f"    GitHub: {project['github_url']}")
    metadata_block = "\n".join(metadata_lines)

    NEW_HEADER_TEMPLATE = (
        "--[[\n"
        "    <{rel_path}>\n"
        "    Copyright (C) 2026 Prephmage / Prephalia\n"
        "    All Rights Reserved.\n"
        "\n"
        "    This software may not be copied, modified, or distributed \n"
        "    without the express written permission of the copyright owner.\n"
        "\n"
        "    -- Additional Metadata --\n"
        + metadata_block.replace("{", "{{").replace("}", "}}") + "\n"
        "--]]"
    )

    HEADER_REGEX = re.compile(
        r"--\[\[\s*\n\s*<(.*?)>\s*\n\s*Copyright \(C\) (?:<)?2026(?:>)? (?:<)?Prephmage / Prephalia(?:>)?.*?--\]\]",
        re.DOTALL
    )

    for dirpath, dirnames, filenames in os.walk(addon_dir):
        if 'libs' in dirnames:
            dirnames.remove('libs')
        if 'Libs' in dirnames:
            dirnames.remove('Libs')

        for filename in filenames:
            if filename.endswith(".lua"):
                file_path = os.path.join(dirpath, filename)
                file_rel = os.path.relpath(file_path, addon_dir)

                formatted_rel_path = os.path.join(folder, file_rel).replace("/", "\\")

                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()

                expected_new_header = NEW_HEADER_TEMPLATE.format(rel_path=formatted_rel_path)
                match = HEADER_REGEX.search(original_content)

                if match:
                    existing_header = match.group(0)
                    if existing_header != expected_new_header:
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


def update_readme_toc(project):
    """Parses changelog headers from the project's README and updates its TOC automatically."""
    print(f"\n--- [{project['name']}] Updating README Table of Contents ---")
    readme_path = project["readme_path"]

    if not readme_path.exists():
        print(f"Skipped: README not found at {readme_path}")
        return

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    changelog_match = re.search(r"## Changelog\s*\n(.*)", content, re.DOTALL)
    if not changelog_match:
        print(f"Warning: Could not find '## Changelog' section in {readme_path.name}")
        return

    versions = re.findall(r"^###\s+(V[\w\.\-]+)", changelog_match.group(1), re.MULTILINE)

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
            print("Success: Updated README Table of Contents")
        else:
            print("Skipped: README Table of Contents is already up to date")


def package_addon(project, root_dir, packaged_dir):
    """Packages the main project folder and any extra bundled folders into a zip archive."""
    name = project["name"]
    print(f"\n--- [{name}] Packaging Addon ---")

    if not project["version_string"]:
        print("Skipped: No version specified for standalone packaging.")
        return

    packaged_dir.mkdir(parents=True, exist_ok=True)

    zip_path = packaged_dir / f"{name}_v{project['version_string']}.zip"
    folders_to_pack = [project["addon_dir"]] + project.get("also_bundle", [])

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for folder_path in folders_to_pack:
            if not folder_path.exists():
                print(f"Warning: Folder to bundle not found at {folder_path}")
                continue

            for dirpath, _, filenames in os.walk(folder_path):
                for filename in filenames:
                    abs_file = Path(dirpath) / filename
                    rel_arcname = abs_file.relative_to(folder_path.parent)
                    zf.write(abs_file, arcname=str(rel_arcname))

    print(f"Success: Packaged addon to {zip_path}")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def process_project(project, wow_addon_dirs, root_dir, packaged_dir):
    v_str = f" (v{project['version_string']})" if project['version_string'] else ""
    print(f"\n{'=' * 60}\nProject: {project['name']}{v_str}\n{'=' * 60}")

    if not project["addon_dir"].exists():
        print(f"Error: Project folder not found at {project['addon_dir']}")
        return False

    for wow_addon_dir in wow_addon_dirs:
        generate_folder_junction(wow_addon_dir, project)

    update_toc_version(project)
    update_changelog(project)
    update_readme_toc(project)
    enforce_lua_headers(project)
    package_addon(project, root_dir, packaged_dir)
    return True


def main():
    script_dir, root_dir, packaged_dir, globalvars_path = get_script_paths()

    cfg = load_globalvars(globalvars_path)
    wow_addon_dirs = cfg.get("paths", {}).get("wow_addon_directories", [])
    projects = build_projects(cfg, root_dir)

    if not projects:
        print("Error: No projects defined under 'projects' in globalvars.preph")
        return 1

    requested = sys.argv[1:]
    if requested:
        known = {p["name"].lower(): p for p in projects}
        unknown = [r for r in requested if r.lower() not in known]
        if unknown:
            print(f"Error: Unknown project(s): {', '.join(unknown)}")
            print(f"Available: {', '.join(p['name'] for p in projects)}")
            return 1
        projects = [known[r.lower()] for r in requested]

    failed = []
    for project in projects:
        try:
            if not process_project(project, wow_addon_dirs, root_dir, packaged_dir):
                failed.append(project["name"])
        except Exception as e:
            print(f"Exception while processing {project['name']}: {e}")
            failed.append(project["name"])

    if failed:
        print(f"\nProcess finished with problems in: {', '.join(failed)}")
        return 1

    print("\nProcess completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())