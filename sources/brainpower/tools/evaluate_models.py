"""Explicit synthetic router benchmark. Run from the project root."""
import argparse
import json
from pathlib import Path
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from governor_workbench.llm import RouterClient, model_check


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://127.0.0.1:3000/v1')
    parser.add_argument('--output', default='artifacts/model_evaluation.json')
    parser.add_argument('--codex-auth-path', help='Optional existing Codex auth.json; loopback port 3000 only')
    args = parser.parse_args()
    report = model_check(RouterClient(args.base_url, codex_auth_path=args.codex_auth_path), on_event=lambda event: print(event['model'] + ': ' + event['message'], flush=True))
    report['evaluated_at'] = datetime.now(timezone.utc).isoformat()
    target = Path(args.output).resolve()
    root = Path(__file__).resolve().parents[1]
    if not target.is_relative_to(root):
        parser.error('Output must be inside the workspace.')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report['comparisons'], indent=2))


if __name__ == '__main__':
    main()
