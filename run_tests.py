#!/usr/bin/env python3
"""
Test runner for the Codecomprehender project.
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all tests with appropriate configuration."""
    project_root = Path(__file__).parent

    # Basic pytest command
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--capture=no",  # Don't capture stdout/stderr
    ]

    print("Running Codecomprehender tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)

    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def run_integration_tests_only():
    """Run only integration tests."""
    project_root = Path(__file__).parent

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/integration/",
        "-v",
        "--tb=short",
        "--capture=no",
    ]

    print("Running integration tests only...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)

    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error running integration tests: {e}")
        return 1


def run_unit_tests_only():
    """Run only unit tests."""
    project_root = Path(__file__).parent

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit/",
        "-v",
        "--tb=short",
        "--capture=no",
    ]

    print("Running unit tests only...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)

    try:
        result = subprocess.run(cmd, cwd=project_root, check=False)
        return result.returncode
    except Exception as e:
        print(f"Error running unit tests: {e}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == "integration":
            exit_code = run_integration_tests_only()
        elif test_type == "unit":
            exit_code = run_unit_tests_only()
        else:
            print(f"Unknown test type: {test_type}")
            print("Usage: python run_tests.py [integration|unit]")
            exit_code = 1
    else:
        exit_code = run_tests()

    sys.exit(exit_code)
