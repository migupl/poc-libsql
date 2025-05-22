# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "cryptography",
#     "pyjwt",
# ]
# ///

from cryptography.hazmat import backends
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from datetime import timedelta, datetime, timezone
from typing import Dict

import base64
import jwt
import time


def create_pem_keys() -> [str, str]:
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_key_pem = private_key.private_bytes(encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    return public_key_pem, private_key_pem


def create_jwt_token(secret, expire_seconds = 0) -> str:
    payload = {
        "sub": "access",
    }

    if expire_seconds:
        payload["exp"] = datetime.now(timezone.utc) + timedelta(seconds=expire_seconds)

    token = jwt.encode(payload, secret, algorithm='EdDSA')
    return token


def decode_jwt_token(token, secret) -> Dict:
    encoded = jwt.decode(token, secret, algorithms='EdDSA')
    return encoded


def main() -> None:
    public_key_pem, private_key_pem = create_pem_keys()

    print("Public Key:", base64.urlsafe_b64encode(public_key_pem))

    for seconds in [0, 2]:
        message = f"Should raise an exception when token expire after {seconds} seconds" if seconds \
            else "Should get the payload (no expiration time)"

        print("-"*5, message)

        token = create_jwt_token(private_key_pem, seconds)
        print("JWT:", token)

        if seconds:
            print(f"Sleep for {seconds} seconds")
            time.sleep(seconds)

        decode = decode_jwt_token(token, public_key_pem)
        print("payload:", decode)


if __name__ == "__main__":
    main()
