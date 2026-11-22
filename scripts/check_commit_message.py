import argparse
import re
import subprocess
import sys
from pathlib import Path


HEADER_PATTERN = re.compile(
    r"^[a-z][a-z0-9-]*(?:\([^()\r\n]+\))?!?: \S.*$"
)
MERGE_HEADER_PATTERN = re.compile(
    r"^Merge (?:branch|remote-tracking branch|tag|pull request)\b"
)


def valid_header(header: str) -> bool:
    return HEADER_PATTERN.fullmatch(header) is not None


def first_message_header(message: str) -> str:
    for line in message.splitlines():
        if line.strip() and not line.startswith("#"):
            return line
    return ""


def validate_file(path: Path) -> int:
    header = first_message_header(path.read_text(encoding="utf-8"))
    if valid_header(header) or MERGE_HEADER_PATTERN.match(header):
        return 0

    print(
        "Invalid commit message. Use "
        "'type(scope): description', for example "
        "'feat(auth): add login endpoint'.",
        file=sys.stderr,
    )
    if header:
        print(f"Found: {header}", file=sys.stderr)
    return 1


def validate_range(commit_range: str) -> int:
    result = subprocess.run(
        [
            "git",
            "log",
            "--no-merges",
            "--format=%H%x09%s",
            commit_range,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    invalid = []
    for line in result.stdout.splitlines():
        commit_hash, subject = line.split("\t", maxsplit=1)
        if not valid_header(subject):
            invalid.append((commit_hash, subject))

    if not invalid:
        print("All commit messages follow Conventional Commits.")
        return 0

    print("These commits do not follow Conventional Commits:", file=sys.stderr)
    for commit_hash, subject in invalid:
        print(f"  {commit_hash[:12]} {subject}", file=sys.stderr)
    print(
        "Use 'type(scope): description', for example "
        "'feat(auth): add login endpoint'.",
        file=sys.stderr,
    )
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Conventional Commit message headers."
    )
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--file", type=Path, help="Path to a commit message file")
    target.add_argument("--range", help="Git revision range to validate")
    args = parser.parse_args()

    if args.file is not None:
        return validate_file(args.file)
    return validate_range(args.range)


if __name__ == "__main__":
    raise SystemExit(main())
