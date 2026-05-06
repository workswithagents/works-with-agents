#!/usr/bin/env python3.11
"""ASFS Converter — Hermes SKILL.md ↔ ASFS format.

No dependencies. Converts between Hermes skill format and the
Agent Skill Format Standard (ASFS).

Usage:
    python3.11 asfs-convert.py ~/.hermes/skills/*/SKILL.md --output-dir ./asfs/
    python3.11 asfs-convert.py my-skill.asfs.md --to-hermes
"""

import argparse
import os
import re
import sys
from pathlib import Path

# Hermes-specific frontmatter keys to strip when converting to ASFS
HERMES_ONLY_KEYS = {
    "hermes", "metadata", "related_skills", "category",
    "prerequisites", "author", "required_environment_variables",
    "required_commands", "missing_required_environment_variables",
    "missing_credential_files", "missing_required_commands",
    "setup_needed", "setup_skipped", "readiness_status",
    "required_mcp_connections", "mcp_config", "plugin_required",
}

# ASFS required frontmatter keys
ASFS_REQUIRED = {"name", "version", "description"}


def parse_frontmatter(text: str) -> tuple[dict, str, str]:
    """Parse YAML frontmatter and return (metadata, body, raw_fm)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, text, ""

    fm_lines = []
    body_start = 0
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            body_start = i + 1
            break
        fm_lines.append(line)

    body = "\n".join(lines[body_start:])
    raw_fm = "\n".join(lines[: body_start + 1] if body_start > 0 else lines[:2])

    # Simple YAML parser (stdlib only, no pyyaml dependency)
    meta = {}
    current_key = None
    current_list = None
    current_dict = None
    indent_level = 0

    for line in fm_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Detect indent level
        indent = len(line) - len(line.lstrip())

        # Key: value
        if ":" in stripped and not stripped.startswith("-"):
            parts = stripped.split(":", 1)
            key = parts[0].strip()
            value = parts[1].strip()

            if value in ("true", "false"):
                meta[key] = value == "true"
            elif value.replace(".", "").isdigit():
                meta[key] = float(value) if "." in value else int(value)
            elif value:
                meta[key] = value
            else:
                # Value is on next line(s) — dict or list
                current_key = key
                current_list = []
                current_dict = {}
                indent_level = indent
        elif stripped.startswith("- ") and current_key:
            item = stripped[2:].strip().strip('"').strip("'")
            current_list.append(item)
            meta[current_key] = current_list
        elif current_key and ":" in stripped:
            k, v = stripped.split(":", 1)
            current_dict[k.strip()] = v.strip().strip('"').strip("'")
            meta[current_key] = current_dict

    return meta, body, raw_fm


def hermes_to_asfs(content: str) -> str:
    """Convert Hermes SKILL.md to ASFS format."""
    meta, body, raw_fm = parse_frontmatter(content)

    # Build clean ASFS frontmatter
    asfs_lines = ["---"]
    for key in ["name", "version", "description", "tags", "triggers", "os", "deps"]:
        if key in meta:
            val = meta[key]
            if isinstance(val, list):
                asfs_lines.append(f"{key}:")
                for item in val:
                    asfs_lines.append(f"  - {item}")
            elif isinstance(val, dict):
                asfs_lines.append(f"{key}:")
                for k, v in val.items():
                    asfs_lines.append(f"  {k}: {v}")
            elif isinstance(val, bool):
                asfs_lines.append(f"{key}: {'true' if val else 'false'}")
            else:
                asfs_lines.append(f"{key}: {val}")

    # Add ASFS-specific fields if missing
    if "tags" not in meta:
        asfs_lines.append("tags: []")
    if "triggers" not in meta:
        asfs_lines.append("triggers: []")
    if "os" not in meta:
        asfs_lines.append("os: [linux, macos]")

    asfs_lines.append("---")
    asfs_lines.append("")
    asfs_lines.append(body.strip())

    return "\n".join(asfs_lines) + "\n"


def asfs_to_hermes(content: str) -> str:
    """Convert ASFS to Hermes SKILL.md format (minimal)."""
    meta, body, _ = parse_frontmatter(content)
    name = meta.get("name", "unnamed")

    lines = [
        "---",
        f"name: {name}",
        f"version: {meta.get('version', '1.0.0')}",
        f"description: {meta.get('description', '')}",
        f"tags: {meta.get('tags', [])}",
        "---",
        "",
        body.strip(),
        "",
    ]
    return "\n".join(lines)


def convert_file(input_path: str, output_dir: str, to_hermes: bool = False):
    """Convert a single file."""
    content = Path(input_path).read_text()

    if to_hermes:
        output = asfs_to_hermes(content)
        suffix = ".hermes.md"
    else:
        output = hermes_to_asfs(content)
        suffix = ".asfs.md"

    # Generate output filename
    stem = Path(input_path).stem
    if stem == "SKILL":
        # Use parent directory name for skills
        name = Path(input_path).parent.name
    else:
        name = stem

    out_path = Path(output_dir) / f"{name}{suffix}"
    os.makedirs(output_dir, exist_ok=True)
    Path(out_path).write_text(output)
    return out_path


def main():
    parser = argparse.ArgumentParser(description="ASFS Converter")
    parser.add_argument("inputs", nargs="+", help="Input SKILL.md or .asfs.md files")
    parser.add_argument("--output-dir", "-o", default="./asfs/",
                        help="Output directory (default: ./asfs/)")
    parser.add_argument("--to-hermes", action="store_true",
                        help="Convert ASFS → Hermes (default: Hermes → ASFS)")
    args = parser.parse_args()

    converted = 0
    for pattern in args.inputs:
        for path in Path().glob(pattern) if "*" in pattern else [Path(pattern)]:
            if not path.exists():
                print(f"✗ Not found: {path}", file=sys.stderr)
                continue
            if path.is_dir():
                skill_md = path / "SKILL.md"
                if skill_md.exists():
                    path = skill_md
                else:
                    continue

            try:
                out = convert_file(str(path), args.output_dir, args.to_hermes)
                print(f"✓ {path} → {out}")
                converted += 1
            except Exception as e:
                print(f"✗ {path}: {e}", file=sys.stderr)

    print(f"\n{converted} file(s) converted.")
    sys.exit(0 if converted > 0 else 1)


if __name__ == "__main__":
    main()
