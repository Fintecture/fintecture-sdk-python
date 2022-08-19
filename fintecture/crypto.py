# -*- coding: utf-8 -*-

import json
import uuid
import base64

from cryptography.hazmat.primitives.asymmetric import dsa, rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.exceptions import UnsupportedAlgorithm

from hashlib import sha256


def generate_uuid():
    return str(uuid.uuid4()).replace('-', '')


def generate_uuidv4():
    return str(uuid.uuid4())


def hash_base64(plain_text):
    m = sha256()
    m.update(plain_text.encode('utf-8'))
    b_digest = m.digest()
    b_b64 = base64.b64encode(b_digest)
    plain_b64_hash = b_b64.decode('ascii')
    return plain_b64_hash


def create_signature_header(headers, app_id, private_key, signed_headers):
    signing_string = build_signing_string(headers, signed_headers)
    header_string = build_header_string(headers, signed_headers)

    signature = sign_payload(signing_string, private_key)
    return (
            'keyId="' + app_id +
            '",algorithm="rsa-sha256",headers="' + header_string +
            '",signature="' + signature + '"'
    )


def build_signing_string(headers, signed_headers):
    signing_string = ''

    for param in signed_headers:
        if param in headers:
            p = param.lower()
            signing_string = signing_string + '\n' if signing_string else signing_string
            signing_string = signing_string + p + ': ' + headers[param]

    return signing_string


def build_header_string(headers, signed_headers):
    header_string = ''

    for param in signed_headers:
        if param in headers:
            p = param.lower()
            header_string = header_string + ' ' + p if header_string else p

    return header_string


def sign_payload(payload, private_key, algorithm=None):
    if isinstance(payload, dict):
        payload = json.dumps(payload, separators=(',', ':'))

    bytes_payload = str.encode(payload)

    if not algorithm or algorithm == 'rsa-sha256':
        try:
            bytes_private_key = str.encode(private_key)
            private_key = load_pem_private_key(bytes_private_key, password=None)

            signature = private_key.sign(bytes_payload, padding.PKCS1v15(), hashes.SHA256())

            base64_bytes = base64.b64encode(signature)
            plain_b64_signature = base64_bytes.decode('ascii')

            return plain_b64_signature

        except ValueError as error:
            raise ValueError(
                'the PEM data could not be decrypted or '
                'if its structure could not be decoded successfully'
            )
        except TypeError as error:
            raise ValueError(
                'password was given and the private key was not encrypted; '
                'or the key was encrypted but no password was supplied'
            )
        except UnsupportedAlgorithm as error:
            raise ValueError(
                'the serialized key type is not supported by the OpenSSL version cryptography is using'
            )

    raise ValueError('invalid signature algorithm')
