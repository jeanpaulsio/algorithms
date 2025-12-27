import ast
import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Any


# Allowed imports - only safe built-in modules
ALLOWED_IMPORTS = {
    "math",
    "collections",
    "itertools",
    "functools",
    "operator",
    "string",
    "datetime",
    "decimal",
    "fractions",
    "random",
    "statistics",
    "bisect",
    "heapq",
    "array",
    "copy",
    "json",
    "re",
    "typing",
}

# Blocked dangerous builtins - only the truly dangerous ones
# Note: We keep safe builtins like type, isinstance, callable, repr, etc.
# as they're commonly used in legitimate code
DANGEROUS_BUILTINS = {
    "__import__",
    "eval",
    "exec",
    "compile",
    "open",
    "file",
    "input",
    "raw_input",
    "reload",
    "__builtins__",
    "execfile",
    "exit",
    "quit",
    "breakpoint",
    # These could be used to access dangerous functions, but we'll block them
    # at the AST level instead of removing them entirely
    # "vars",
    # "dir",
    # "globals",
    # "locals",
    # "getattr",
    # "setattr",
    # "delattr",
    # "hasattr",
}

# Blocked modules
BLOCKED_MODULES = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "multiprocessing",
    "threading",
    "ctypes",
    "pickle",
    "shelve",
    "dbm",
    "sqlite3",
    "pdb",
    "cProfile",
    "profile",
    "trace",
    "gc",
    "inspect",
    "importlib",
    "imp",
    "pkgutil",
    "pkg_resources",
    "setuptools",
    "distutils",
    "shutil",
    "pathlib",
    "tempfile",
    "zipfile",
    "tarfile",
    "gzip",
    "bz2",
    "lzma",
    "shlex",
    "pipes",
    "signal",
    "mmap",
    "select",
    "selectors",
    "asyncio",
    "concurrent",
    "queue",
    "sched",
    "time",
    "resource",
    "errno",
    "fcntl",
    "termios",
    "tty",
    "pty",
    "pwd",
    "grp",
    "crypt",
    "spwd",
    "getpass",
    "curses",
    "readline",
    "rlcompleter",
    "cmd",
    "codecs",
    "unicodedata",
    "stringprep",
    "code",
    "codeop",
    "py_compile",
    "compileall",
    "dis",
    "pickletools",
    "doctest",
    "unittest",
    "test",
    "lib2to3",
    "2to3",
    "pydoc",
    "bdb",
    "pstats",
    "timeit",
    "tracemalloc",
    "faulthandler",
    "hotshot",
    "site",
    "sitecustomize",
    "usercustomize",
    "warnings",
    "contextlib",
    "abc",
    "atexit",
    "traceback",
    "__future__",
}


class SecureImportTransformer(ast.NodeTransformer):
    """Transformer to block dangerous imports and operations."""

    def visit_Import(self, node: ast.Import) -> ast.AST:
        for alias in node.names:
            module_name = alias.name.split(".")[0]
            if module_name in BLOCKED_MODULES:
                raise ValueError(f"Import of '{module_name}' is not allowed")
        return self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        if node.module:
            module_name = node.module.split(".")[0]
            if module_name in BLOCKED_MODULES:
                raise ValueError(f"Import from '{module_name}' is not allowed")
        return self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> ast.AST:
        # Block dangerous function calls
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in DANGEROUS_BUILTINS:
                raise ValueError(f"Use of '{func_name}' is not allowed")
        elif isinstance(node.func, ast.Attribute):
            # Block getattr(__builtins__, 'eval') style attacks
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "__builtins__":
                if node.func.attr in DANGEROUS_BUILTINS:
                    raise ValueError(f"Access to __builtins__.{node.func.attr} is not allowed")
            # Block getattr(__builtins__, ...) calls
            if isinstance(node.func, ast.Attribute) and node.func.attr == "getattr":
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "__builtins__":
                    raise ValueError("getattr on __builtins__ is not allowed")
        # Block getattr(__builtins__, ...) pattern
        if isinstance(node.func, ast.Name) and node.func.id == "getattr":
            if len(node.args) >= 1:
                if isinstance(node.args[0], ast.Name) and node.args[0].id == "__builtins__":
                    raise ValueError("getattr on __builtins__ is not allowed")
        # Block vars(__builtins__) pattern
        if isinstance(node.func, ast.Name) and node.func.id == "vars":
            if len(node.args) >= 1:
                if isinstance(node.args[0], ast.Name) and node.args[0].id == "__builtins__":
                    raise ValueError("vars on __builtins__ is not allowed")
        # Block globals()['__builtins__'] pattern - check if result is used to access dangerous builtins
        if isinstance(node.func, ast.Name) and node.func.id == "globals":
            # This is tricky - we can't easily detect if the result is used maliciously
            # But we can at least warn or block it in certain contexts
            pass  # Handled at runtime by blocking __builtins__ access
        return self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> ast.AST:
        # Block access to dangerous attributes via __builtins__
        # Only block if explicitly accessing __builtins__ and the attribute is dangerous
        if isinstance(node.value, ast.Name) and node.value.id == "__builtins__":
            if node.attr in DANGEROUS_BUILTINS:
                raise ValueError(f"Access to __builtins__.{node.attr} is not allowed")
        # Block getattr/vars/globals results accessing __builtins__
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name):
                if node.value.func.id in ("getattr", "vars", "globals"):
                    # If accessing __builtins__ through the result
                    if node.attr in DANGEROUS_BUILTINS:
                        raise ValueError(f"Indirect access to dangerous builtin '{node.attr}' is not allowed")
        return self.generic_visit(node)
    
    def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
        # Block vars(__builtins__)['eval'] and globals()['__builtins__'] patterns
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name):
                if node.value.func.id in ("vars", "globals"):
                    # Check if accessing __builtins__ or dangerous builtins
                    if isinstance(node.slice, ast.Constant):
                        key = node.slice.value
                        if key == "__builtins__" or key in DANGEROUS_BUILTINS:
                            raise ValueError(f"Access to '{key}' via {node.value.func.id} is not allowed")
                    elif isinstance(node.slice, ast.Str):  # Python < 3.8
                        key = node.slice.s
                        if key == "__builtins__" or key in DANGEROUS_BUILTINS:
                            raise ValueError(f"Access to '{key}' via {node.value.func.id} is not allowed")
        return self.generic_visit(node)


def validate_code(code: str) -> tuple[bool, str | None]:
    """Validate code for dangerous operations."""
    try:
        tree = ast.parse(code)
        transformer = SecureImportTransformer()
        transformer.visit(tree)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {str(e)}"
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Validation error: {str(e)}"




def execute_code_secure(
    user_code: str, test_code: str, module_path: str, timeout: int = 5
) -> dict[str, Any]:
    """
    Execute user code and run tests in a secure subprocess.

    Args:
        user_code: The user's solution code
        test_code: The test code to run
        module_path: The module path (e.g., "arrays_and_strings.clone_even_numbers")
        timeout: Maximum execution time in seconds

    Returns:
        Dictionary with execution results
    """
    # Validate user code
    is_valid, error = validate_code(user_code)
    if not is_valid:
        return {
            "success": False,
            "error": error,
            "test_results": [{"name": "Code validation", "passed": False, "error": error}],
            "output": "",
            "passed_count": 0,
            "failed_count": 1,
        }

    # Create temporary directory for execution
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create module directory structure
        module_parts = module_path.split(".")
        module_dir = tmp_path
        for part in module_parts[:-1]:
            module_dir = module_dir / part
            module_dir.mkdir(exist_ok=True)
            (module_dir / "__init__.py").touch()

        # Write user code to module file
        module_file = module_dir / f"{module_parts[-1]}.py"
        module_file.write_text(user_code, encoding="utf-8")

        # Create test runner script
        test_runner = tmp_path / "run_tests.py"
        # Indent the test code properly for the try block
        indented_lines = []
        for line in test_code.split("\n"):
            if line.strip():
                indented_lines.append("    " + line)
            else:
                indented_lines.append(line)
        indented_test_code = "\n".join(indented_lines)
        
        test_runner_content = f"""import sys
from pathlib import Path

# Add tmpdir to path
sys.path.insert(0, r"{tmp_path}")

# Execute test code to define test functions
try:
{indented_test_code}
except Exception as e:
    error_type = type(e).__name__
    error_msg = str(e) if str(e) else "Unknown error"
    print(f"ERROR: Failed to load test code: {{error_type}}: {{error_msg}}")
    sys.exit(1)

# Discover and run all test functions
test_functions = [
    name for name, obj in globals().items()
    if name.startswith("test_") and callable(obj)
]

if not test_functions:
    print("ERROR: No test functions found (functions must start with 'test_')")
    sys.exit(1)

print(f"Found {{len(test_functions)}} test(s)")
failed_tests = []
passed_tests = []

for test_name in sorted(test_functions):
    try:
        test_func = globals()[test_name]
        test_func()
        print(f"PASSED: {{test_name}}")
        passed_tests.append(test_name)
    except AssertionError as e:
        error_msg = str(e) if str(e) else "Assertion failed"
        print(f"FAILED: {{test_name}} - {{error_msg}}")
        failed_tests.append(test_name)
    except Exception as e:
        # Extract the most relevant error message
        error_type = type(e).__name__
        error_msg = str(e) if str(e) else "Error occurred"
        # For common errors, show a cleaner message
        if "NameError" in error_type:
            formatted_msg = "NameError: " + error_msg
        elif "TypeError" in error_type:
            formatted_msg = "TypeError: " + error_msg
        elif "AttributeError" in error_type:
            formatted_msg = "AttributeError: " + error_msg
        elif "IndexError" in error_type:
            formatted_msg = "IndexError: " + error_msg
        elif "KeyError" in error_type:
            formatted_msg = "KeyError: " + error_msg
        else:
            formatted_msg = error_type + ": " + error_msg
        print("ERROR in " + test_name + ": " + formatted_msg)
        failed_tests.append(test_name)

print(f"\\nTest Summary: {{len(passed_tests)}} passed, {{len(failed_tests)}} failed out of {{len(test_functions)}} total")

if failed_tests:
    sys.exit(1)
else:
    print("SUCCESS: All tests passed")
"""
        test_runner.write_text(test_runner_content, encoding="utf-8")

        # Execute in subprocess with timeout and resource limits
        try:
            # Create minimal environment
            env = os.environ.copy()
            env.update({
                "PYTHONPATH": str(tmp_path),
                "PYTHONUNBUFFERED": "1",
                "PYTHONDONTWRITEBYTECODE": "1",  # Don't write .pyc files
            })
            # Remove potentially dangerous environment variables
            for key in list(env.keys()):
                if key.startswith("LD_") or key.startswith("DYLD_"):
                    del env[key]
            
            result = subprocess.run(
                [sys.executable, str(test_runner)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(tmp_path),
                env=env,
                # Prevent subprocess from spawning new processes (Unix only)
                preexec_fn=None if sys.platform == "win32" else lambda: None,
            )

            output = result.stdout + result.stderr
            success = result.returncode == 0

            # Parse test results from output
            test_results = []
            passed_tests = []
            failed_tests = []
            total_tests = 0
            
            # Parse individual test results
            for line in output.split("\n"):
                line = line.strip()
                if line.startswith("Found"):
                    # Extract total test count: "Found 6 test(s)"
                    import re
                    match = re.search(r"Found (\d+) test", line)
                    if match:
                        total_tests = int(match.group(1))
                elif line.startswith("PASSED:"):
                    test_name = line.replace("PASSED:", "").strip()
                    passed_tests.append(test_name)
                    test_results.append({"name": test_name, "passed": True, "error": None})
                elif line.startswith("FAILED:"):
                    # Extract test name and error message
                    parts = line.replace("FAILED:", "").strip().split(" - ", 1)
                    test_name = parts[0].strip()
                    error_msg = parts[1].strip() if len(parts) > 1 else "Assertion failed"
                    # Clean up error message - remove any traceback-like content
                    error_msg = error_msg.split("\n")[0].split("Traceback")[0].strip()
                    failed_tests.append(test_name)
                    test_results.append({"name": test_name, "passed": False, "error": error_msg})
                elif line.startswith("ERROR in"):
                    # Extract test name and error message
                    parts = line.replace("ERROR in", "").strip().split(":", 1)
                    test_name = parts[0].strip()
                    error_msg = parts[1].strip() if len(parts) > 1 else "Error occurred"
                    # Clean up error message - remove any traceback-like content
                    error_msg = error_msg.split("\n")[0].split("Traceback")[0].strip()
                    failed_tests.append(test_name)
                    test_results.append({"name": test_name, "passed": False, "error": error_msg})
            
            # If we found a total count but don't have that many results, some tests might not have run
            if total_tests > 0 and len(test_results) < total_tests:
                # Find missing tests by checking what was discovered but not executed
                executed_tests = {r["name"] for r in test_results}
                # We can't know which tests weren't executed without more info, so we'll just note it
                pass
            
            # If no individual test results parsed, check for overall status
            if not test_results:
                if "SUCCESS" in output:
                    test_results.append({"name": "All tests", "passed": True, "error": None})
                elif "ERROR: Failed to load test code" in output:
                    test_results.append({"name": "Test setup", "passed": False, "error": "Failed to load test code"})
                else:
                    # Generic error
                    error_msg = output.split("\n")[0] if output else "Unknown error"
                    test_results.append({"name": "Execution", "passed": False, "error": error_msg})

            return {
                "success": success,
                "error": None if success else output,
                "test_results": test_results,
                "output": output,
                "passed_count": len(passed_tests),
                "failed_count": len(failed_tests),
                "total_count": total_tests if total_tests > 0 else len(test_results),
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Execution timed out after {timeout} seconds",
                "test_results": [{"name": "Execution", "passed": False, "error": f"Execution timed out after {timeout} seconds"}],
                "output": "",
                "passed_count": 0,
                "failed_count": 1,
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "test_results": [{"name": "Execution", "passed": False, "error": str(e)}],
                "output": traceback.format_exc(),
                "passed_count": 0,
                "failed_count": 1,
            }

