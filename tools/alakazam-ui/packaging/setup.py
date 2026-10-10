"""py2app build script.

Lives in its own subdirectory, deliberately apart from the project's pyproject.toml:
setuptools auto-reads a pyproject.toml's [project] table (even for a plain
`python setup.py` invocation) and populates install_requires from it, which py2app
refuses to build against ("install_requires is no longer supported" - it wants
dependencies expressed only through its own packages/includes options). Running from
a directory with no pyproject.toml of its own avoids that entirely.

Build with: ../.venv/bin/python setup.py py2app
"""

from pathlib import Path

from setuptools import setup

PROJECT_ROOT = Path(__file__).resolve().parent.parent

APP = [str(PROJECT_ROOT / "main.py")]
DATA_FILES = []
OPTIONS = {
    "argv_emulation": False,
    "iconfile": str(PROJECT_ROOT / "resources" / "alakazam.icns"),
    "plist": {
        "CFBundleName": "Alakazam",
        "CFBundleDisplayName": "Alakazam",
        "CFBundleIdentifier": "com.andrewli.alakazam-ui",
        "CFBundleShortVersionString": "0.1.0",
        "CFBundleVersion": "0.1.0",
        "LSUIElement": True,
    },
    "packages": ["rumps", "alakazam", "alakazam_ui"],
    "includes": ["AppKit", "Foundation", "PyObjCTools.AppHelper", "objc"],
    "dist_dir": str(PROJECT_ROOT / "dist"),
    "bdist_base": str(Path(__file__).resolve().parent / "build"),
}

setup(
    app=APP,
    data_files=DATA_FILES,
    # pyrefly: ignore [bad-assignment]
    options={"py2app": OPTIONS},
)
