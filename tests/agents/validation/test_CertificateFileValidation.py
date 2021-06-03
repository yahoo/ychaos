#  Copyright 2021, Verizon Media
#  Licensed under the terms of the Apache 2.0 license. See the LICENSE file in the project root for terms
from datetime import datetime, timedelta, timezone
from tempfile import NamedTemporaryFile
from unittest import TestCase

from ychaos.agents.validation.certificate import (
    CertificateFileValidation,
    CertificateFileValidationConfig,
)


class TestCertificateFileValidation(TestCase):
    def setUp(self) -> None:
        self.test_cert_valid = NamedTemporaryFile("wb", delete=False)
        self.test_key_valid = NamedTemporaryFile("wb", delete=False)

        self.test_cert_expired = NamedTemporaryFile("wb", delete=False)
        self.test_key_expired = NamedTemporaryFile("wb", delete=False)

        self.test_cert_invalid = NamedTemporaryFile("wb", delete=False)

        generate_selfsigned_cert(
            "test.principal.valid",
            cert_fp=self.test_cert_valid,
            key_fp=self.test_key_valid,
        )
        generate_selfsigned_cert(
            "test.principal.expired",
            not_after=datetime.now(tz=timezone.utc),
            cert_fp=self.test_cert_expired,
            key_fp=self.test_key_expired,
        )

        self.test_cert_valid.close()
        self.test_key_valid.close()

        self.test_cert_expired.close()
        self.test_key_expired.close()

    def test_cert_file_validation(self):
        config = CertificateFileValidationConfig(
            paths=[
                self.test_cert_valid.name,
                self.test_cert_expired.name,
                {"path": self.test_cert_invalid.name},
            ]
        )

        agent = CertificateFileValidation(config)

        agent.setup()
        agent.run()
        agent.teardown()

        datapoint1 = agent.monitor().get()
        self.assertIsNotNone(datapoint1.data["error"])

        datapoint2 = agent.monitor().get()
        self.assertTrue(datapoint2.data["is_expired"])
        self.assertTrue(datapoint2.data["is_critical"])

        datapoint3 = agent.monitor().get()
        self.assertFalse(datapoint3.data["is_expired"])
        self.assertFalse(datapoint3.data["is_critical"])


# Copyright 2018 Simon Davy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
def generate_selfsigned_cert(
    hostname,
    not_before: datetime = datetime.now(tz=timezone.utc),
    not_after: datetime = datetime.now(tz=timezone.utc) + timedelta(days=10),
    cert_fp=None,
    key_fp=None,
):
    """
    Generate Self signed certificates for testing purpose

    Args:
        hostname: Subject of Certificate
        not_before: Certificate not valid before this date
        not_after: Certificate not valid before this date
        cert_fp: Certificate File Pointer to save the certificates
        key_fp: Key File Pointer to save the certificates

    Returns:
        Tuple of bytes containing Cert, Key
    """
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend(),
    )

    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, hostname)])

    # best practice seem to be to include the hostname in the SAN, which *SHOULD* mean COMMON_NAME is ignored.
    alt_names = [x509.DNSName(hostname)]

    san = x509.SubjectAlternativeName(alt_names)

    # path_len=0 means this cert can only sign itself, not other certs.
    basic_contraints = x509.BasicConstraints(ca=True, path_length=0)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(1000)
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .add_extension(basic_contraints, False)
        .add_extension(san, False)
        .sign(key, hashes.SHA256(), default_backend())
    )
    cert_pem = cert.public_bytes(encoding=serialization.Encoding.PEM)
    key_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    if cert_fp:
        cert_fp.write(cert_pem)

    if key_fp:
        key_fp.write(key_pem)

    return cert_pem, key_pem
