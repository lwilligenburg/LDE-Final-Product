"""
Thin wrapper kept for backward compatibility — the runnable demo now lives in
final-product.py. Run either:  python demo.py   |   python final-product.py
"""

from importlib import import_module

# 'final-product' isn't a valid identifier, so import by file-safe module name.
_fp = import_module("final-product") if False else None

if __name__ == "__main__":
    # Load and run final-product.py's main() regardless of the hyphenated name.
    import runpy

    runpy.run_path("final-product.py", run_name="__main__")
