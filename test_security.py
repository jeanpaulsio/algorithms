"""Test script to verify security measures block malicious code."""
import sys
from app.code_executor import validate_code, execute_code_secure

# Test cases that should be BLOCKED
MALICIOUS_TESTS = [
    # File system access
    ("import os", "File system access via os import"),
    ("import os; os.system('ls')", "OS system call"),
    ("open('/etc/passwd', 'r')", "File open attempt"),
    ("import shutil; shutil.rmtree('/tmp')", "Shutil import"),
    
    # Dangerous builtins
    ("eval('1+1')", "Eval usage"),
    ("exec('print(1)')", "Exec usage"),
    ("compile('1+1', '<string>', 'eval')", "Compile usage"),
    ("__import__('os')", "Direct __import__"),
    
    # Blocked modules
    ("import subprocess", "Subprocess import"),
    ("import socket", "Socket import"),
    ("import sys; sys.exit(0)", "Sys import"),
    ("import multiprocessing", "Multiprocessing import"),
    ("import threading", "Threading import"),
    ("import ctypes", "Ctypes import"),
    
    # Builtin access attempts
    ("__builtins__.__import__('os')", "Builtins access"),
    ("getattr(__builtins__, 'eval')('1+1')", "Getattr on builtins"),
    ("vars(__builtins__)['eval']('1+1')", "Vars on builtins"),
    ("globals()['__builtins__'].__import__('os')", "Globals builtins access"),
    
    # Path manipulation
    ("import sys; sys.path.insert(0, '/'); import os", "Path manipulation"),
    
    # Indirect imports
    ("import importlib; importlib.import_module('os')", "Importlib usage"),
]

# Test cases that should be ALLOWED (legitimate code)
LEGITIMATE_TESTS = [
    ("def test_func(x): return x * 2", "Simple function"),
    ("x = [1, 2, 3]; y = x[0]", "List access"),
    ("result = sum([1, 2, 3])", "Builtin sum"),
    ("import math; math.sqrt(16)", "Math import (allowed)"),
    ("import collections; collections.Counter([1,2,2])", "Collections import (allowed)"),
    ("x = isinstance(5, int)", "Isinstance usage"),
    ("x = type(5)", "Type usage"),
    ("x = callable(len)", "Callable usage"),
]

def test_validation():
    """Test AST validation blocks malicious code."""
    print("=" * 60)
    print("Testing AST Validation (should BLOCK malicious code)")
    print("=" * 60)
    
    blocked_count = 0
    allowed_count = 0
    
    for code, description in MALICIOUS_TESTS:
        is_valid, error = validate_code(code)
        if not is_valid:
            print(f"✓ BLOCKED: {description}")
            print(f"  Error: {error}")
            blocked_count += 1
        else:
            print(f"✗ ALLOWED (SECURITY ISSUE!): {description}")
            print(f"  Code: {code[:50]}...")
            allowed_count += 1
        print()
    
    print(f"\nBlocked: {blocked_count}/{len(MALICIOUS_TESTS)}")
    print(f"Allowed (should be 0): {allowed_count}/{len(MALICIOUS_TESTS)}")
    
    if allowed_count > 0:
        print("\n⚠️  SECURITY WARNING: Some malicious code was allowed!")
        return False
    
    return True

def test_legitimate_code():
    """Test AST validation allows legitimate code."""
    print("=" * 60)
    print("Testing AST Validation (should ALLOW legitimate code)")
    print("=" * 60)
    
    blocked_count = 0
    allowed_count = 0
    
    for code, description in LEGITIMATE_TESTS:
        is_valid, error = validate_code(code)
        if is_valid:
            print(f"✓ ALLOWED: {description}")
            allowed_count += 1
        else:
            print(f"✗ BLOCKED (FALSE POSITIVE): {description}")
            print(f"  Error: {error}")
            blocked_count += 1
        print()
    
    print(f"\nAllowed: {allowed_count}/{len(LEGITIMATE_TESTS)}")
    print(f"Blocked (should be 0): {blocked_count}/{len(LEGITIMATE_TESTS)}")
    
    if blocked_count > 0:
        print("\n⚠️  WARNING: Some legitimate code was blocked!")
        return False
    
    return True

def test_execution_timeout():
    """Test that infinite loops timeout."""
    print("=" * 60)
    print("Testing Execution Timeout (should timeout infinite loops)")
    print("=" * 60)
    
    infinite_loop = """def clone_even_numbers(arr):
    while True:
        pass
    return arr
"""
    
    test_code = """from test.timeout_test import clone_even_numbers

def test_timeout():
    clone_even_numbers([1, 2, 3])
"""
    
    result = execute_code_secure(
        user_code=infinite_loop,
        test_code=test_code,
        module_path="test.timeout_test",
        timeout=2  # Short timeout for testing
    )
    
    if "timed out" in result.get("error", "").lower() or result.get("error", "").startswith("Execution timed out"):
        print("✓ Infinite loop was properly timed out")
        return True
    else:
        print("✗ Infinite loop was not timed out properly")
        print(f"  Error: {result.get('error', 'No error message')}")
        print(f"  Output: {result.get('output', 'No output')[:200]}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("SECURITY TEST SUITE")
    print("=" * 60 + "\n")
    
    results = []
    
    # Test 1: Malicious code should be blocked
    results.append(("Malicious Code Blocking", test_validation()))
    print("\n")
    
    # Test 2: Legitimate code should be allowed
    results.append(("Legitimate Code Allowing", test_legitimate_code()))
    print("\n")
    
    # Test 3: Timeout protection
    results.append(("Timeout Protection", test_execution_timeout()))
    print("\n")
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL SECURITY TESTS PASSED")
    else:
        print("✗ SOME SECURITY TESTS FAILED - REVIEW NEEDED")
    print("=" * 60 + "\n")
    
    sys.exit(0 if all_passed else 1)

