# Preload easyocr models for faster container runtime
import easyocr
import logging
import os

MODEL_DIR = "/opt/easyocr"

os.makedirs(MODEL_DIR, exist_ok=True)

logging.getLogger("easyocr").setLevel(logging.ERROR)

easyocr.Reader(
    ['en'],
    model_storage_directory=MODEL_DIR,
    download_enabled=True,   # allow download at build time
    gpu=False,
    verbose=False
)

print("EasyOCR models preloaded into", MODEL_DIR)