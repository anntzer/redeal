from argparse import ArgumentParser
from pathlib import Path
import subprocess
import sys


def main():
    parser = ArgumentParser()
    parser.add_argument("--cov", action="store_true")
    args = parser.parse_args()
    extra_argv = (
        ["-mcoverage", "run", "--source=redeal", "--branch", "--append"]
        if args.cov else [])
    for path in Path(__file__).parent.glob("*.py"):
        if path.stem.startswith("__"):
            continue
        print(path)
        subprocess.run(
            [sys.executable, *extra_argv, "-m", "redeal", str(path)],
            check=True)
    if args.cov:
        subprocess.run([sys.executable, "-mcoverage", "report"])


if __name__ == "__main__":
    main()
