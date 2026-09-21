#!/usr/bin/env python3
import os
from pathlib import Path

print("Debug Environment Variables")
print("=" * 80)
print()

print(f"Current Working Directory: {os.getcwd()}")
print()

# Check if .env exists in various locations
env_paths = [
    ".env",
    "../.env",
    "../../.env",
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent / ".env",
    Path(__file__).parent.parent.parent / ".env",
]

print("Checking for .env file:")
for path in env_paths:
    full_path = Path(path).resolve()
    exists = full_path.exists()
    print(f"  {path:40} -> {full_path} [{('✓' if exists else '✗')}]")

print()
print("Environment Variables:")
print(f"  SMTP_USER: {os.getenv('SMTP_USER', '(not set)')}")
print(f"  SMTP_PASSWORD: {os.getenv('SMTP_PASSWORD', '(not set)')}")
print(f"  SMTP_HOST: {os.getenv('SMTP_HOST', '(not set)')}")
print(f"  SMTP_PORT: {os.getenv('SMTP_PORT', '(not set)')}")

print()
print("Testing load_dotenv()...")
from dotenv import load_dotenv

# Try loading from specific path
env_path = Path(__file__).parent.parent.parent / ".env"
print(f"Loading from: {env_path}")
print(f"File exists: {env_path.exists()}")

result = load_dotenv(dotenv_path=env_path)
print(f"load_dotenv() returned: {result}")

print()
print("After load_dotenv():")
print(f"  SMTP_USER: {os.getenv('SMTP_USER', '(not set)')}")
print(f"  SMTP_PASSWORD: {os.getenv('SMTP_PASSWORD', '(not set)')}")
