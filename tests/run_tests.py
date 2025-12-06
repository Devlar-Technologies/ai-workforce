#!/usr/bin/env python3
"""
Test runner script for Devlar AI Workforce
Provides various test execution options and reporting
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path


def run_command(command, capture_output=True):
    """Run command and return result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=capture_output,
            text=True,
            check=False
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_dependencies():
    """Check if required testing dependencies are installed"""
    print("🔍 Checking test dependencies...")

    required_packages = [
        ('pytest', 'pytest'),
        ('pytest-cov', 'pytest-cov'),
        ('pytest-mock', 'pytest-mock'),
        ('pytest-xdist', 'pytest-xdist')
    ]

    missing_packages = []

    for package_name, import_name in required_packages:
        success, _, _ = run_command(f"python -c 'import {import_name}'")
        if not success:
            missing_packages.append(package_name)

    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install pytest pytest-cov pytest-mock pytest-xdist")
        return False

    print("✅ All test dependencies are installed")
    return True


def run_unit_tests(verbose=False, coverage=False):
    """Run unit tests"""
    print("🧪 Running unit tests...")

    cmd = ["python", "-m", "pytest", "tests/"]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])

    # Add markers to focus on unit tests
    cmd.extend(["-m", "unit"])

    # Run tests
    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start_time

    print(f"⏱️  Unit tests completed in {duration:.2f} seconds")

    if result.returncode == 0:
        print("✅ All unit tests passed!")
    else:
        print("❌ Some unit tests failed:")
        print(result.stdout)
        if result.stderr:
            print(result.stderr)

    return result.returncode == 0


def run_integration_tests(verbose=False):
    """Run integration tests"""
    print("🔗 Running integration tests...")

    cmd = ["python", "-m", "pytest", "tests/", "-m", "integration"]

    if verbose:
        cmd.append("-v")

    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start_time

    print(f"⏱️  Integration tests completed in {duration:.2f} seconds")

    if result.returncode == 0:
        print("✅ All integration tests passed!")
    else:
        print("❌ Some integration tests failed:")
        print(result.stdout)

    return result.returncode == 0


def run_specific_test(test_path, verbose=False):
    """Run a specific test file or test function"""
    print(f"🎯 Running specific test: {test_path}")

    cmd = ["python", "-m", "pytest", test_path]

    if verbose:
        cmd.append("-v")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Test passed!")
    else:
        print("❌ Test failed:")
        print(result.stdout)
        if result.stderr:
            print(result.stderr)

    return result.returncode == 0


def run_quick_tests():
    """Run a quick subset of tests for fast feedback"""
    print("⚡ Running quick test suite...")

    cmd = [
        "python", "-m", "pytest", "tests/",
        "-m", "not slow",  # Exclude slow tests
        "--tb=short",      # Short traceback format
        "-q"               # Quiet mode
    ]

    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True)
    duration = time.time() - start_time

    print(f"⏱️  Quick tests completed in {duration:.2f} seconds")

    if result.returncode == 0:
        print("✅ Quick tests passed!")
    else:
        print("❌ Some quick tests failed:")
        print(result.stdout)

    return result.returncode == 0


def generate_coverage_report():
    """Generate detailed coverage report"""
    print("📊 Generating coverage report...")

    # Run tests with coverage
    cmd = [
        "python", "-m", "pytest", "tests/",
        "--cov=.",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Coverage report generated!")
        print("📁 HTML report available at: htmlcov/index.html")
        print("📁 XML report available at: coverage.xml")
    else:
        print("❌ Coverage report generation failed:")
        print(result.stdout)

    return result.returncode == 0


def run_lint_checks():
    """Run code quality checks"""
    print("🔍 Running code quality checks...")

    checks = [
        ("flake8", "flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics"),
        ("pycodestyle", "pycodestyle . --count --statistics"),
        ("pylint", "pylint --errors-only *.py")
    ]

    all_passed = True

    for check_name, command in checks:
        print(f"Running {check_name}...")
        success, stdout, stderr = run_command(command)

        if success:
            print(f"✅ {check_name} passed")
        else:
            print(f"❌ {check_name} found issues:")
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
            all_passed = False

    return all_passed


def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Devlar AI Workforce Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--quick", action="store_true", help="Run quick test suite")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--lint", action="store_true", help="Run code quality checks")
    parser.add_argument("--specific", type=str, help="Run specific test file or function")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--all", action="store_true", help="Run all tests and checks")

    args = parser.parse_args()

    # Change to project directory
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    os.chdir(project_dir)

    print("🚀 Devlar AI Workforce Test Runner")
    print(f"📁 Working directory: {os.getcwd()}")
    print()

    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)

    success = True

    if args.quick:
        success = run_quick_tests()
    elif args.unit:
        success = run_unit_tests(args.verbose, args.coverage)
    elif args.integration:
        success = run_integration_tests(args.verbose)
    elif args.coverage:
        success = generate_coverage_report()
    elif args.lint:
        success = run_lint_checks()
    elif args.specific:
        success = run_specific_test(args.specific, args.verbose)
    elif args.all:
        print("🏃 Running comprehensive test suite...")
        success = True

        # Run unit tests
        if success:
            success = run_unit_tests(args.verbose, False)

        # Run integration tests
        if success:
            success = run_integration_tests(args.verbose)

        # Generate coverage report
        if success:
            success = generate_coverage_report()

        # Run lint checks
        if success:
            success = run_lint_checks()

        if success:
            print("🎉 All tests and checks passed!")
        else:
            print("💥 Some tests or checks failed!")

    else:
        # Default: run unit tests
        success = run_unit_tests(args.verbose, args.coverage)

    if success:
        print("\n✨ Test execution completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test execution failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()