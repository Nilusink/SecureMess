"""
SecretGenerator.py
Used to generate Server and Client secrets

Author:
Nilusink
"""
from core import key_func, random

while True:
    print(f"Your custom secret is:\n\"{key_func(random.randint(10, 256)).decode()}\"")
    input(f"\nPress enter to get a new one ")
