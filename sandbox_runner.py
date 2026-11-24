import ast
import io
import contextlib
import multiprocessing

FORBIDDEN_MODULES = {"os", "sys", "subprocess", "socket", "shutil", "pathlib"}

class SecurityViolation(Exception):
    pass

def validate_ast(source_code: str):
    tree = ast.parse(source_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in FORBIDDEN_MODULES:
                    raise SecurityViolation(f"Blocked import: {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0] in FORBIDDEN_MODULES:
                raise SecurityViolation(f"Blocked import from: {node.module}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {"eval", "exec", "open", "__import__"}:
                raise SecurityViolation(f"Blocked builtin: {node.func.id}")

def _worker(code: str, queue: multiprocessing.Queue):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(code, {"__builtins__": {"print": print, "range": range, "len": len, "sum": sum, "sorted": sorted}})
        queue.put({"status": "ok", "output": buf.getvalue()})
    except Exception as exc:
        queue.put({"status": "runtime_error", "error": str(exc)})

def run_safe(code: str, timeout: float = 2.0) -> dict:
    validate_ast(code)
    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=_worker, args=(code, q))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.terminate()
        return {"status": "timeout", "error": "Execution exceeded 2.0s limit"}
    return q.get() if not q.empty() else {"status": "error", "error": "No output"}

if __name__ == "__main__":
    print(run_safe("print([x**2 for x in range(6)])"))
