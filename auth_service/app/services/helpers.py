import hashlib
import os
import random


def hash_password(password: str) -> str:
    algorithm = 'sha256'
    iterations = random.randint(100000, 150000)
    salt = os.urandom(32)  # Новая соль для данного пользователя
    key = hashlib.pbkdf2_hmac(algorithm, password.encode('utf-8'), salt, iterations)

    return f'{algorithm}${iterations}${salt.hex()}${key.hex()}'
