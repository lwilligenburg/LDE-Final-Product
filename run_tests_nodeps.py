import sys, types, traceback, contextlib

# Minimal pytest shim so we can execute the standard test file without the package installed.
pytest = types.ModuleType("pytest")
class _Raises:
    def __init__(self, exc): self.exc = exc
    def __enter__(self): return self
    def __exit__(self, et, ev, tb):
        assert et is not None, f"DID NOT RAISE {self.exc}"
        return issubclass(et, self.exc)
pytest.raises = lambda exc: _Raises(exc)
sys.modules["pytest"] = pytest

import test_engine as T
tests = [getattr(T, n) for n in dir(T) if n.startswith("test_")]
passed = failed = 0
for t in tests:
    try:
        t(); passed += 1; print(f"PASS {t.__name__}")
    except Exception:
        failed += 1; print(f"FAIL {t.__name__}"); traceback.print_exc()
print(f"\n{passed} passed, {failed} failed, {len(tests)} total")
sys.exit(1 if failed else 0)
