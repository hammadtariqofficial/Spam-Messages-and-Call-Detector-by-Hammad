# -*- mode: python ; coding: utf-8 -*-
"""Focused PyInstaller spec for Spam Messages and Call Detector.

The previous build recursively collected large third-party package trees.
That pulled optional test/development modules and produced missing-submodule
warnings. This spec keeps the runtime dependency set explicit.
"""
from PyInstaller.utils.hooks import collect_data_files

APP_NAME = "Spam Messages and Call Detector"

datas = [
    ("models", "models"),
    ("data", "data"),
]
# Runtime package data only; do not recursively collect google.genai tests.
datas += collect_data_files("google.genai", includes=["*.json", "*.txt"])

hiddenimports = [
    "joblib",
    "numpy",
    "sklearn",
    "sklearn.base",
    "sklearn.pipeline",
    "sklearn.feature_extraction",
    "sklearn.feature_extraction.text",
    "sklearn.linear_model",
    "sklearn.preprocessing",
    "scipy",
    "scipy.sparse",
    "speech_recognition",
    "soundcard",
    "google.genai",
    "google.genai.interactions",
]

excludes = [
    "pytest",
    "_pytest",
    "google.genai.tests",
    "google.genai.test_api_client",
    "google.genai._test_api_client",
    "sklearn.external.array_api_compat.torch",
    "pycparser",
    "pycparser.c_parser",
    "pycparser.yacc",
    "pycparser.lextab",
    "pycparser.yacctab",
    "tzdata",
    "scipy.special._cdflib",
]

a = Analysis(
    ["spam_detector_desktop.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=APP_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
)
