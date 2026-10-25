#!/usr/bin/env python3
"""
create_snapshot.py
==================
Creates comprehensive JSON snapshot of project state for context persistence.

Usage:
    python tools/create_snapshot.py [--phase PHASE] [--message MESSAGE]
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def get_git_info() -> Dict[str, str]:
    """Extract Git repository information."""
    try:
        git_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], 
            text=True, 
            stderr=subprocess.DEVNULL
        ).strip()
        
        git_branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
        
        git_status = subprocess.check_output(
            ["git", "status", "--short"],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
        
        git_tags = subprocess.check_output(
            ["git", "tag", "--points-at", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()
        
        return {
            "commit_hash": git_hash,
            "branch": git_branch or "unknown",
            "status": git_status or "clean",
            "tags": git_tags.split("\n") if git_tags else []
        }
    except Exception as e:
        return {
            "commit_hash": "N/A",
            "branch": "N/A",
            "status": f"Error: {e}",
            "tags": []
        }


def get_file_stats() -> Dict[str, int]:
    """Count files by type."""
    project_root = Path.cwd()
    
    py_files = list(project_root.rglob("*.py"))
    md_files = list(project_root.rglob("*.md"))
    ps1_files = list(project_root.rglob("*.ps1"))
    
    return {
        "python_files": len(py_files),
        "markdown_files": len(md_files),
        "powershell_files": len(ps1_files),
        "total_files": len(py_files) + len(md_files) + len(ps1_files)
    }


def get_dependencies() -> List[str]:
    """Read requirements.txt."""
    req_file = Path("requirements.txt")
    if req_file.exists():
        return [line.strip() for line in req_file.read_text().splitlines() 
                if line.strip() and not line.startswith("#")]
    return []


def get_memory_state() -> Dict[str, str]:
    """Read PROJECT_MEMORY files."""
    memory_files = {
        "current_state": "PROJECT_MEMORY/00_CURRENT_STATE.md",
        "architecture": "PROJECT_MEMORY/01_ARCHITECTURE.md",
        "changes_log": "PROJECT_MEMORY/02_CHANGES_LOG.md",
        "decisions": "PROJECT_MEMORY/03_DECISIONS.md",
        "file_registry": "PROJECT_MEMORY/04_FILE_REGISTRY.md"
    }
    
    memory_state = {}
    for key, path in memory_files.items():
        file_path = Path(path)
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            # Store first 500 chars for overview
            memory_state[key] = content[:500] + "..." if len(content) > 500 else content
        else:
            memory_state[key] = "NOT_FOUND"
    
    return memory_state


def create_snapshot(phase: str = "unknown", message: str = "") -> Path:
    """Create comprehensive snapshot."""
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    
    snapshot = {
        "metadata": {
            "timestamp": timestamp.isoformat(),
            "phase": phase,
            "message": message,
            "python_version": sys.version,
        },
        "git": get_git_info(),
        "files": get_file_stats(),
        "dependencies": get_dependencies(),
        "memory": get_memory_state()
    }
    
    # Create snapshots directory if not exists
    snapshots_dir = Path("PROJECT_MEMORY/snapshots")
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    
    # Write snapshot
    snapshot_path = snapshots_dir / f"snapshot_{timestamp_str}.json"
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    
    # Also append to session log (JSONL)
    session_log_path = snapshots_dir / "session_log.jsonl"
    with open(session_log_path, "a", encoding="utf-8") as f:
        json.dump({
            "timestamp": timestamp_str,
            "type": "snapshot",
            "phase": phase,
            "message": message,
            "git_hash": snapshot["git"]["commit_hash"]
        }, f, ensure_ascii=False)
        f.write("\n")
    
    return snapshot_path


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Create project snapshot")
    parser.add_argument("--phase", default="unknown", help="Current phase (e.g., '2', '3')")
    parser.add_argument("--message", default="", help="Snapshot message")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("CREATING PROJECT SNAPSHOT")
    print("=" * 60)
    print(f"Phase: {args.phase}")
    print(f"Message: {args.message or '(none)'}")
    print()
    
    snapshot_path = create_snapshot(phase=args.phase, message=args.message)
    
    print(f"✓ Snapshot created: {snapshot_path}")
    print(f"✓ Size: {snapshot_path.stat().st_size / 1024:.2f} KB")
    print()
    print("=" * 60)
    print("SNAPSHOT COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
