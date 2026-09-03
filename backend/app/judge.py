import ast
import os
import sys
import json
import time
import tempfile
import subprocess
import traceback
import textwrap
import logging
import shutil
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Security: forbidden modules
FORBIDDEN_MODULES = {
    "os",
    "subprocess",
    "sys",
    "pathlib",
    "shutil",
    "socket",
    "urllib",
    "http",
    "ftplib",
    "pickle",
    "marshal",
    "ctypes",
    "multiprocessing",
    "threading",
    "pty",
    "fcntl",
    "resource",
    "signal",
    "requests",
    "telnetlib",
    "smtplib",
    "importlib",
    "inspect",
    "ast",
    "platform",
    "glob",
    "tempfile",
    "webbrowser",
}

FORBIDDEN_BUILTINS = {
    "eval",
    "exec",
    "compile",
    "__import__",
    "open",
    "input",
    "exit",
    "quit",
    "help",
    "memoryview",
}

# Allow list explicitly?
# We'll forbid only clearly dangerous; allow torch, math, numpy, typing, etc.
# Also deny any import that starts with forbidden name.
def _check_ast_security(code: str) -> tuple[bool, str]:
    """
    Basic AST check to forbid dangerous imports and builtins.
    Returns (is_allowed, error_message)
    """
    try:
        tree = ast.parse(code, filename="<user_code>")
    except SyntaxError as e:
        return False, f"SyntaxError: {e.msg} at line {e.lineno}, column {e.offset}: {e.text or ''}"

    for node in ast.walk(tree):
        # Check imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root in FORBIDDEN_MODULES:
                    return False, f"Forbidden import: '{alias.name}'. Importing '{root}' is not allowed for security reasons."
                # also block importlib which can be used to bypass
                if root == "importlib":
                    return False, f"Forbidden import: '{alias.name}' not allowed."
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root = node.module.split(".")[0]
                if root in FORBIDDEN_MODULES:
                    return False, f"Forbidden import: 'from {node.module} import ...' not allowed."
        elif isinstance(node, ast.Call):
            # Check for forbidden builtins like eval, exec, __import__, open
            # ast.Call func can be Name or Attribute
            if isinstance(node.func, ast.Name):
                if node.func.id in FORBIDDEN_BUILTINS:
                    # Allow 'open' only if we want strict? For MVP forbid open
                    return False, f"Forbidden builtin call: '{node.func.id}()' is not allowed."
            elif isinstance(node.func, ast.Attribute):
                # e.g., os.system, subprocess.Popen - already blocked via imports but also check attribute
                if isinstance(node.func.value, ast.Name):
                    if node.func.value.id in FORBIDDEN_MODULES:
                        return False, f"Forbidden call: '{node.func.value.id}.{node.func.attr}' not allowed."
    return True, ""

def _build_harness_code(function_name: str, user_file: str, tests_file: str) -> str:
    """
    Build harness.py content as a string.
    This harness will import user_code and tests, run them, capture stdout, and output JSON.
    """
    # Use textwrap to avoid indentation issues; harness must be robust
    harness = f'''
import os
import sys
import json
import traceback
import io
import contextlib

# Enforce CPU thread limits
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
os.environ["OPENBLAS_NUM_THREADS"] = "2"
os.environ["NUMEXPR_NUM_THREADS"] = "2"

# Try to set torch deterministic and threads
try:
    import torch
    torch.set_num_threads(2)
    torch.set_num_interop_threads(2)
    try:
        torch.use_deterministic_algorithms(True)
    except Exception:
        pass
    # Disable cudnn if present
    try:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    except Exception:
        pass
except Exception as e:
    print(json.dumps({{"harness_error": f"Failed to configure torch: {{e}}", "traceback": traceback.format_exc()}}))
    sys.exit(1)

import importlib.util

USER_FILE = r"{user_file}"
TESTS_FILE = r"{tests_file}"
FUNC_NAME = r"{function_name}"

stdout_capture = io.StringIO()
stderr_capture = io.StringIO()

# Helper to output result and exit
def emit_result(payload):
    # Ensure payload is JSON serializable; attach stdout
    payload["stdout"] = stdout_capture.getvalue() + stderr_capture.getvalue()
    print("___RESULT_JSON___")
    print(json.dumps(payload))
    sys.exit(0)

# Load user module
try:
    with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
        spec = importlib.util.spec_from_file_location("user_code", USER_FILE)
        if spec is None or spec.loader is None:
            emit_result({{"error": "Failed to create spec for user_code", "passed": 0, "total": 0, "results": []}})
        user_mod = importlib.util.module_from_spec(spec)
        sys.modules["user_code"] = user_mod
        spec.loader.exec_module(user_mod)
except SyntaxError as e:
    emit_result({{"error": f"SyntaxError in user code: {{e.msg}} at line {{e.lineno}}", "traceback": traceback.format_exc(), "passed": 0, "total": 0, "results": [{{"name": "syntax_check", "passed": False, "error": str(e)}}]}})
except Exception as e:
    emit_result({{"error": f"Error importing user code: {{e}}", "traceback": traceback.format_exc(), "passed": 0, "total": 0, "results": [{{"name": "import", "passed": False, "error": str(e)}}]}})

# Check function exists
if not hasattr(user_mod, FUNC_NAME):
    emit_result({{"error": f"Function '{{FUNC_NAME}}' not found in submission. Ensure you define def {{FUNC_NAME}}(...)", "passed": 0, "total": 0, "results": [{{"name": "function_exists", "passed": False, "error": f"Function '{{FUNC_NAME}}' not defined"}}]}})

solve_fn = getattr(user_mod, FUNC_NAME)
if not callable(solve_fn):
    emit_result({{"error": f"'{{FUNC_NAME}}' is not callable", "passed": 0, "total": 0, "results": [{{"name": "function_callable", "passed": False, "error": f"{{FUNC_NAME}} not callable"}}]}})

# Load tests module
try:
    with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
        spec_t = importlib.util.spec_from_file_location("problem_tests", TESTS_FILE)
        tests_mod = importlib.util.module_from_spec(spec_t)
        sys.modules["problem_tests"] = tests_mod
        spec_t.loader.exec_module(tests_mod)
except Exception as e:
    emit_result({{"error": f"Failed to load tests: {{e}}", "traceback": traceback.format_exc(), "passed": 0, "total": 0, "results": []}})

# Discover and run tests
results = []

# Strategy: if tests_mod has TESTS list, use it. Else discover test_ functions. Else if run_tests exists fallback.

tests_to_run = []

if hasattr(tests_mod, "TESTS") and isinstance(getattr(tests_mod, "TESTS"), (list, tuple)):
    tests_to_run = getattr(tests_mod, "TESTS")
    # They are functions expecting solve param
    for t in tests_to_run:
        name = getattr(t, "__name__", str(t))
        try:
            # Capture per-test output
            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                # Tests are defined as def test_X(solve): -> they raise AssertionError on failure
                # But spec says return (passed, error). In our problems, they raise on fail.
                # So we call and interpret: if no exception => passed
                ret = t(solve_fn)
                # If test returns something explicit? Ignore for problems that use TESTS style with exceptions
                # Check if ret is tuple (passed, err)
                if isinstance(ret, tuple) and len(ret) == 2 and isinstance(ret[0], bool):
                    passed, err = ret
                    results.append({{"name": name, "passed": bool(passed), "error": str(err) if err else ""}})
                else:
                    results.append({{"name": name, "passed": True, "error": ""}})
        except AssertionError as e:
            err_msg = str(e) if str(e) else "Assertion failed"
            results.append({{"name": name, "passed": False, "error": err_msg, "traceback": traceback.format_exc()}})
        except Exception as e:
            results.append({{"name": name, "passed": False, "error": f"{{type(e).__name__}}: {{e}}", "traceback": traceback.format_exc()}})
elif hasattr(tests_mod, "run_tests") or hasattr(tests_mod, "run_all") or hasattr(tests_mod, "check"):
    # Try generic runner: but we prefer granular; fallback to inspecting TESTS already done.
    # If no TESTS, try to discover test_ functions
    discovered = []
    for attr in dir(tests_mod):
        if attr.startswith("test_"):
            fn = getattr(tests_mod, attr)
            if callable(fn):
                discovered.append((attr, fn))
    if discovered:
        for name, fn in discovered:
            try:
                with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                    ret = fn(solve_fn)
                    if isinstance(ret, tuple) and len(ret) == 2 and isinstance(ret[0], bool):
                        passed, err = ret
                        results.append({{"name": name, "passed": bool(passed), "error": str(err) if err else ""}})
                    else:
                        results.append({{"name": name, "passed": True, "error": ""}})
            except AssertionError as e:
                err_msg = str(e) if str(e) else "Assertion failed"
                results.append({{"name": name, "passed": False, "error": err_msg, "traceback": traceback.format_exc()}})
            except Exception as e:
                results.append({{"name": name, "passed": False, "error": f"{{type(e).__name__}}: {{e}}", "traceback": traceback.format_exc()}})
    else:
        # Last resort: try calling run_tests if it exists
        try:
            runner = getattr(tests_mod, "run_tests", None) or getattr(tests_mod, "run_all", None) or getattr(tests_mod, "check", None)
            if runner and callable(runner):
                with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                    runner(solve_fn)
                results.append({{"name": "run_tests", "passed": True, "error": ""}})
            else:
                emit_result({{"error": "No tests found in tests.py", "passed": 0, "total": 0, "results": []}})
        except AssertionError as e:
            results.append({{"name": "run_tests", "passed": False, "error": str(e), "traceback": traceback.format_exc()}})
        except Exception as e:
            results.append({{"name": "run_tests", "passed": False, "error": f"{{type(e).__name__}}: {{e}}", "traceback": traceback.format_exc()}})
else:
    # Discover test_*
    discovered = []
    for attr in dir(tests_mod):
        if attr.startswith("test_"):
            fn = getattr(tests_mod, attr)
            if callable(fn):
                discovered.append((attr, fn))
    if not discovered:
        emit_result({{"error": "No test cases found", "passed": 0, "total": 0, "results": []}})
    for name, fn in discovered:
        try:
            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                ret = fn(solve_fn)
                if isinstance(ret, tuple) and len(ret) == 2 and isinstance(ret[0], bool):
                    passed, err = ret
                    results.append({{"name": name, "passed": bool(passed), "error": str(err) if err else ""}})
                else:
                    results.append({{"name": name, "passed": True, "error": ""}})
        except AssertionError as e:
            err_msg = str(e) if str(e) else "Assertion failed"
            results.append({{"name": name, "passed": False, "error": err_msg, "traceback": traceback.format_exc()}})
        except Exception as e:
            results.append({{"name": name, "passed": False, "error": f"{{type(e).__name__}}: {{e}}", "traceback": traceback.format_exc()}})

# Compute summary
passed = sum(1 for r in results if r.get("passed"))
total = len(results)

emit_result({{"passed": passed, "total": total, "results": results}})
'''
    return harness

def evaluate(slug: str, code: str, timeout: int = 5) -> Dict[str, Any]:
    """
    Evaluate user code for given problem slug.
    Returns dict: {passed, total, results, stdout, latency_ms, error?}
    """
    start_time = time.time()
    from app.problems import get_problem

    problem = get_problem(slug)
    if not problem:
        return {
            "passed": 0,
            "total": 0,
            "results": [{"name": "slug_check", "passed": False, "error": f"Problem '{slug}' not found"}],
            "stdout": "",
            "latency_ms": 0,
            "error": f"Problem '{slug}' not found"
        }

    function_name = problem.function_name or "solve"
    tests_path = problem.tests_path

    # Step 1: AST security check
    allowed, err_msg = _check_ast_security(code)
    if not allowed:
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "passed": 0,
            "total": 1,
            "results": [{"name": "security_check", "passed": False, "error": err_msg}],
            "stdout": "",
            "latency_ms": latency_ms,
            "error": err_msg
        }

    # Step 2: Syntax check (compile)
    try:
        compile(code, "<user_code>", "exec")
    except SyntaxError as e:
        latency_ms = int((time.time() - start_time) * 1000)
        msg = f"SyntaxError: {e.msg} at line {e.lineno}"
        return {
            "passed": 0,
            "total": 1,
            "results": [{"name": "syntax_check", "passed": False, "error": msg}],
            "stdout": "",
            "latency_ms": latency_ms,
            "error": msg,
            "traceback": traceback.format_exc() if False else ""
        }

    # Step 3: Create temp dir and write files
    tmpdir = tempfile.mkdtemp(prefix="rictrlab_judge_")
    user_file = os.path.join(tmpdir, "user_code.py")
    harness_file = os.path.join(tmpdir, "harness.py")

    try:
        # Write user code
        with open(user_file, "w") as f:
            f.write(code)
            # Ensure trailing newline
            if not code.endswith("\n"):
                f.write("\n")

        # Build harness
        harness_code = _build_harness_code(function_name, user_file, tests_path)
        with open(harness_file, "w") as f:
            f.write(harness_code)

        # Prepare environment
        env = os.environ.copy()
        env["OMP_NUM_THREADS"] = "2"
        env["MKL_NUM_THREADS"] = "2"
        env["OPENBLAS_NUM_THREADS"] = "2"
        env["NUMEXPR_NUM_THREADS"] = "2"
        env["PYTHONUNBUFFERED"] = "1"
        # Ensure no GPU
        env["CUDA_VISIBLE_DEVICES"] = ""

        # Run subprocess with timeout
        judge_start = time.time()
        try:
            result = subprocess.run(
                [sys.executable, harness_file],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
            )
            latency_ms = int((time.time() - judge_start) * 1000)
            # Also include overall start offset? Use judge_start latency for consistency
            # But spec latency_ms should be total execution time.
            # We'll compute total from start_time
            total_latency = int((time.time() - start_time) * 1000)
            # Use max for visible? Prefer total
            latency_ms = total_latency

            stdout = result.stdout or ""
            stderr = result.stderr or ""

            # Harness prints ___RESULT_JSON___ marker
            # Parse results
            if "___RESULT_JSON___" in stdout:
                try:
                    # Split after marker
                    json_part = stdout.split("___RESULT_JSON___")[-1].strip()
                    # json_part may contain multiple lines; first valid JSON object is result
                    # Find first { and last } ; but easier: json.loads on stripped lines
                    # There might be extra output after JSON? Harness only prints JSON after marker, so take first line after marker that is JSON
                    # Attempt to parse the whole remainder as JSON (should be one object)
                    # If multiple JSON prints, take first
                    lines = json_part.strip().splitlines()
                    # Filter empty
                    json_str = ""
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        # Try to parse incrementally
                        try:
                            # accumulating lines until valid JSON
                            json_str += line
                            parsed = json.loads(json_str)
                            # success
                            break
                        except json.JSONDecodeError:
                            json_str += line
                            continue
                    else:
                        # fallback: try entire json_part
                        parsed = json.loads(json_part)

                    # parsed is dict with passed, total, results, stdout, error, etc.
                    passed = parsed.get("passed", 0)
                    total = parsed.get("total", 0)
                    results = parsed.get("results", [])
                    harness_stdout = parsed.get("stdout", "")
                    # combine stderr + harness_stdout + any pre-marker stdout?
                    # stdout before marker is not harness stdout capture; but we should include harness_stdout
                    combined_stdout = harness_stdout
                    # If stderr not empty and not already in stdout, append
                    if stderr and stderr not in combined_stdout:
                        combined_stdout += "\\n[stderr]\\n" + stderr
                    # Also if there's output before marker (like torch warnings) not captured, include?
                    # For now return harness captured

                    # Ensure results shape
                    normalized_results = []
                    for r in results:
                        normalized_results.append({
                            "name": r.get("name", "test"),
                            "passed": bool(r.get("passed", False)),
                            "error": r.get("error", "") + (f"\\n{ r.get('traceback','') }" if r.get("traceback") else "")
                        })

                    # If parsed has top-level error and results empty, ensure at least one result
                    if not normalized_results and parsed.get("error"):
                        normalized_results = [{"name": "harness", "passed": False, "error": parsed.get("error") + ("\\n" + parsed.get("traceback","") if parsed.get("traceback") else "")}]

                    return {
                        "passed": passed,
                        "total": total,
                        "results": normalized_results,
                        "stdout": combined_stdout,
                        "latency_ms": latency_ms,
                        "error": parsed.get("error")
                    }
                except json.JSONDecodeError as e:
                    logger.exception(f"Failed to parse harness JSON: {e}, stdout: {stdout}, stderr: {stderr}")
                    return {
                        "passed": 0,
                        "total": 0,
                        "results": [{"name": "harness", "passed": False, "error": f"Failed to parse judge output: {e}"}],
                        "stdout": stdout + "\\n" + stderr,
                        "latency_ms": latency_ms,
                        "error": f"JSON parse error: {e}"
                    }
            else:
                # No marker found, maybe harness crashed before emitting
                # Check stderr and stdout for clues
                # If process returned non-zero, show error
                err_msg = f"Harness did not produce output. stdout: {stdout[:1000]} stderr: {stderr[:1000]} returncode: {result.returncode}"
                # Try to see if stdout contains JSON directly without marker (fallback)
                try:
                    parsed = json.loads(stdout.strip().splitlines()[-1])
                    if "passed" in parsed:
                        return {
                            "passed": parsed.get("passed",0),
                            "total": parsed.get("total",0),
                            "results": parsed.get("results",[]),
                            "stdout": parsed.get("stdout","") + "\\n" + stderr,
                            "latency_ms": latency_ms
                        }
                except:
                    pass

                return {
                    "passed": 0,
                    "total": 0,
                    "results": [{"name": "harness", "passed": False, "error": err_msg}],
                    "stdout": stdout + "\\n" + stderr,
                    "latency_ms": latency_ms,
                    "error": err_msg
                }

        except subprocess.TimeoutExpired:
            latency_ms = int((time.time() - start_time) * 1000)
            return {
                "passed": 0,
                "total": 0,
                "results": [{"name": "timeout", "passed": False, "error": f"Execution timed out after {timeout}s"}],
                "stdout": "",
                "latency_ms": latency_ms,
                "error": f"Timeout after {timeout}s"
            }
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.exception(f"Subprocess failed: {e}")
            return {
                "passed": 0,
                "total": 0,
                "results": [{"name": "harness", "passed": False, "error": str(e)}],
                "stdout": "",
                "latency_ms": latency_ms,
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    finally:
        # Cleanup temp dir
        try:
            shutil.rmtree(tmpdir, ignore_errors=True)
        except Exception:
            pass
