from __future__ import absolute_import, division, print_function

import datetime
import hmac
import json
import time
import base64

from email.utils import parsedate_tz, parsedate

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import dsa, rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.exceptions import UnsupportedAlgorithm

from collections import OrderedDict
from hashlib import sha256

import fintecture

from fintecture import crypto
from fintecture import error, util
from fintecture.six.moves.urllib.parse import urlencode
from fintecture.api_requestor import _api_encode


class Webhook(object):
    DEFAULT_TOLERANCE = 300

    @staticmethod
    def construct_event(
        payload,
        digest_header,
        signature_header,
        request_id_header,
        private_key=None,
        tolerance=DEFAULT_TOLERANCE,
        app_id=None
    ):
        if hasattr(payload, "decode"):
            payload = payload.decode("utf-8")

        pkey = private_key or fintecture.private_key
        if pkey is None:
            raise error.AuthenticationError(
                "No private key provided. (HINT: set your private_key using fintecture.private_key = <PRIVATE-KEY>)"
                "You can find your application values in your Fintecture developer console at "
                "https://console.fintecture.com/developers, after registering your account as a platform. "
                "See https://docs.fintecture.com/ for details, or email contact@fintecture.com "
                "if you have any questions."
            )

        encoded_payload = urlencode(list(_api_encode(payload or {})))

        WebhookSignature.verify_header(encoded_payload, digest_header, signature_header, request_id_header, pkey, tolerance)

        event = util.convert_to_fintecture_object(payload, app_id or fintecture.app_id)

        return event


class WebhookSignature(object):
    EXPECTED_SCHEME = "v2"

    @staticmethod
    def _get_timestamp_and_signatures(header, scheme):
        list_items = [i.split("=", 2) for i in header.split(",")]
        timestamp = int([i[1] for i in list_items if i[0] == "t"][0])
        signatures = [i[1] for i in list_items if i[0] == scheme]
        return timestamp, signatures

    @staticmethod
    def _extract_signature(signature):
        if hasattr(signature, "decode"):
            signature.decode('ascii')
        sign_items = signature.split(',')  # 0: keyId, 1: algorithm, 2: headers, 3: signature
        signature_chunk = sign_items[3]
        # now just keep the part after "signature="
        signature_chunk = signature_chunk.replace('"', '')
        signature_value = signature_chunk[10:]  # exclude 'signature=' from begin of string
        return signature_value

    @classmethod
    def verify_header(cls, payload, digest_header, signature_header, request_id_header, private_key, tolerance=None):
        try:
            extracted_signature = cls._extract_signature(signature_header)
        except Exception as e:
            raise error.SignatureVerificationError(
                "Unable to extract signatures from header",
                signature_header,
                digest_header,
                request_id_header,
                payload,
            )

        try:
            bytes_decoded_signature = base64.b64decode(extracted_signature)
        except Exception as e:
            raise error.SignatureVerificationError(
                "Unable to decode signatures",
                signature_header,
                digest_header,
                request_id_header,
                payload,
            )

        try:
            bytes_private_key = str.encode(private_key)
            private_key_obj = load_pem_private_key(
                data=bytes_private_key,
                password=None,
                backend=default_backend(),
            )
        except ValueError as e:
            raise error.SignatureVerificationError(
                'the PEM data could not be decrypted or if its structure could not be decoded successfully',
                signature_header,
                digest_header,
                request_id_header,
                payload,
            )

        signature_lines = []
        signature_items = {
            'date': None,
            'digest': None,
            'x-request-id': None,
        }

        try:
            signature = private_key_obj.decrypt(
                ciphertext=bytes_decoded_signature,
                padding=padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA1()),
                    algorithm=hashes.SHA1(),
                    label=None
                ))

            if hasattr(signature, "decode"):
                signature = signature.decode('utf-8')
                signature_lines = signature.split('\n')
                for sign_item in signature_lines:
                    pair = sign_item.split(': ')
                    signature_items[pair[0]] = pair[1].lstrip()

        except UnsupportedAlgorithm as e:
            raise ValueError(
                'the serialized key type is not supported by the OpenSSL version cryptography is using'
            )
        except Exception as e:
            raise error.SignatureVerificationError(
                "Unable to decode signatures",
                signature_header,
                digest_header,
                request_id_header,
                payload,
            )

        if not signature_lines or len(signature_lines) == 0:
            raise error.SignatureVerificationError(
                "No signatures found with expected scheme "
                "%s" % cls.EXPECTED_SCHEME,
                signature_header,
                digest_header,
                request_id_header,
                payload,
            )

        digest = 'SHA-256=' + crypto.hash_base64(payload)

        match_digests = util.secure_compare(digest, signature_items['digest'])
        match_request_ids = util.secure_compare(request_id_header, signature_items['x-request-id'])

        if match_digests is False or match_request_ids is False:
            raise error.SignatureVerificationError(
                "No signatures found matching the expected signature for payload and request identifier",
                signature_header,
                digest_header,
                request_id_header,
                payload,
            )

        # date_sign = parsedate_tz(signature_items['date'])
        date_sign = parsedate(signature_items['date'])
        timestamp = time.mktime(date_sign)
        time_diff = time.time() - tolerance
        if tolerance and timestamp < time_diff:
            raise error.SignatureVerificationError(
                "Timestamp outside the tolerance (%d) zone (%d)" % (tolerance, timestamp),
                signature,
                digest_header,
                request_id_header,
                payload,
            )

        return True
