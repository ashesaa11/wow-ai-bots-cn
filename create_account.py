import hashlib
import os
import struct

# SRP6 parameters for AzerothCore
N = 0x894B645E89E1535BBDAD5B8B290650530801B18EBFBF5E8FAB3C82872A3E9BB7
g = 7

def calculate_srp6(username, password):
    salt = os.urandom(32)
    h1 = hashlib.sha1(f"{username}:{password}".encode()).digest()
    h2 = hashlib.sha1(salt + h1).digest()
    h2_int = int.from_bytes(h2, 'little')
    verifier = pow(g, h2_int, N)
    verifier_bytes = verifier.to_bytes(32, 'little')
    return salt, verifier_bytes

salt, verifier = calculate_srp6("admin", "admin")
print(f"SALT: {salt.hex()}")
print(f"VERIFIER: {verifier.hex()}")
