"""Run all tests with coverage report.

Usage:
    python run_tests.py
"""

import subprocess
import sys

if __name__ == "__main__":
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html:coverage_html",
        ],
        check=False,
    )
    sys.exit(result.returncode)
