"""Migrate existing Benutzer_Archive_Start from flat to hierarchical layout.

OLD: Benutzer_Archive_Start/Client_Slug_Synergy/...
NEW: Benutzer_Archive_Start/Synergy/Client_Slug/...

Usage:
    python -m tools.migrate_archive_hierarchy [--dry-run] [--archive-root PATH]
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ARCHIVE_ROOT = Path(r"C:\Benutzer_Archive_Start")

REPORT_SUFFIXES = {
    "_Synergy": "Synergy",
    "_Remedies": "Remedies",
    "_Deutung": "Deutung",
    "_Trends": "Trends",
}


def migrate(archive_root: Path, dry_run: bool = False) -> int:
    """Move flat client_suffix folders to type/client hierarchy."""
    if not archive_root.exists():
        print(f"Archive root not found: {archive_root}")
        return 1

    moved = 0
    skipped = 0

    for item in sorted(archive_root.iterdir()):
        if not item.is_dir():
            continue

        for suffix, type_folder in REPORT_SUFFIXES.items():
            if not item.name.endswith(suffix):
                continue

            client_slug = item.name[: -len(suffix)]
            target_type_dir = archive_root / type_folder
            target_client_dir = target_type_dir / client_slug

            if target_client_dir.exists():
                # Merge: move files from old to new
                print(f"  [MERGE] {item.name} -> {type_folder}/{client_slug}/")
                if not dry_run:
                    target_type_dir.mkdir(parents=True, exist_ok=True)
                    for child in item.iterdir():
                        dest = target_client_dir / child.name
                        if dest.exists():
                            if child.is_dir():
                                # Merge subdirectories
                                for sub in child.rglob("*"):
                                    if sub.is_file():
                                        rel = sub.relative_to(child)
                                        dest_sub = target_client_dir / child.name / rel
                                        dest_sub.parent.mkdir(parents=True, exist_ok=True)
                                        shutil.move(str(sub), str(dest_sub))
                            else:
                                shutil.move(str(child), str(dest))
                        else:
                            shutil.move(str(child), str(dest))
                    # Remove empty old dir
                    try:
                        item.rmdir()
                    except OSError:
                        pass
                moved += 1
            else:
                print(f"  [MOVE]  {item.name} -> {type_folder}/{client_slug}/")
                if not dry_run:
                    target_type_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(item), str(target_client_dir))
                moved += 1
            break
        else:
            # Check if it's a Resonanz client folder (no suffix)
            # These should be moved under Resonanz/
            if not any(item.name.endswith(s) for s in REPORT_SUFFIXES):
                # Check if it looks like a client folder (has SESSION subdirs)
                has_session = any(
                    "SESSION" in child.name
                    for child in item.iterdir()
                    if child.is_dir()
                )
                if has_session:
                    target = archive_root / "Resonanz" / item.name
                    if target.exists():
                        print(f"  [SKIP]  {item.name} (already in Resonanz/)")
                        skipped += 1
                    else:
                        print(f"  [MOVE]  {item.name} -> Resonanz/{item.name}/")
                        if not dry_run:
                            (archive_root / "Resonanz").mkdir(parents=True, exist_ok=True)
                            shutil.move(str(item), str(target))
                        moved += 1

    print(f"\nMigration complete: {moved} moved, {skipped} skipped")
    if dry_run:
        print("(DRY RUN - no changes made)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Migrate archive from flat to hierarchical layout."
    )
    parser.add_argument(
        "--archive-root",
        default=str(ARCHIVE_ROOT),
        help="Root directory of the archive",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without actually moving",
    )
    args = parser.parse_args()

    return migrate(Path(args.archive_root), dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
