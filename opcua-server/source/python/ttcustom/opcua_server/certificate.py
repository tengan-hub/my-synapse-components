from pathlib import Path

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from datetime import datetime, timedelta, timezone
import socket

# =========================
# 鍵生成
# =========================
key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
)

def create_cert(cert_dir: Path) -> tuple[Path, Path]:
    key_path = cert_dir / 'client_key.pem'
    cert_path = cert_dir / 'client_cert.pem'
    if key_path.exists() and cert_path.exists():
        return key_path, cert_path

    # =========================
    # Subject / Issuer
    # （自己署名）
    # =========================
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "JP"),                     # subject countryName
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Nagano"),       # subject stateOrProvinceName
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Shiojiri"),              # subject localityName
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "SALTYSTER Inc."),    # subject organizationName
        x509.NameAttribute(NameOID.COMMON_NAME, "SynapseOpcUaClient"),      # subject commonName
    ])

    # =========================
    # 証明書構築
    # =========================
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))                       # 証明書の有効開始日時
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=3650)) # 証明書の有効期限（10年）
    )

    # ---- Extensions ----
    builder = builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None),                  # req_ext basicConstraints = CA:FALSE
        critical=True
    )

    builder = builder.add_extension(
        x509.KeyUsage(
            digital_signature=True,                                         # req_ext keyUsage = digitalSignature
            content_commitment=True,                                        # req_ext keyUsage = nonRepudiation
            key_encipherment=True,                                          # req_ext keyUsage = keyEncipherment
            data_encipherment=True,                                         # req_ext keyUsage = dataEncipherment
            key_agreement=False,
            key_cert_sign=True,                                             # req_ext keyUsage = keyCertSign
            crl_sign=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True
    )

    builder = builder.add_extension(
        x509.ExtendedKeyUsage([
            ExtendedKeyUsageOID.SERVER_AUTH,                                # req_ext extendedKeyUsage = serverAuth
            ExtendedKeyUsageOID.CLIENT_AUTH,                                # req_ext extendedKeyUsage = clientAuth
        ]),
        critical=False
    )

    builder = builder.add_extension(
        x509.SubjectKeyIdentifier.from_public_key(key.public_key()),        # req_ext subjectKeyIdentifier
        critical=False
    )

    builder = builder.add_extension(
        x509.AuthorityKeyIdentifier.from_issuer_public_key(key.public_key()),   # req_ext authorityKeyIdentifier
        critical=False
    )

    hostname = socket.gethostname()
    uri = f"urn:{hostname}:Saltyster:SpeeDBeeSynapse"
    builder = builder.add_extension(
        x509.SubjectAlternativeName([
            x509.UniformResourceIdentifier(uri),                            # req_ext subjectAltName = URI:urn:...
            x509.DNSName(hostname),                                         # req_ext subjectAltName = DNS:...
        ]),
        critical=False
    )

    # =========================
    # 署名
    # =========================
    cert = builder.sign(
        private_key=key,
        algorithm=hashes.SHA256(),
    )

    # =========================
    # 保存
    # =========================
    with open(key_path, "wb") as f:
        f.write(key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption()
        ))

    with open(cert_path, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))

    return key_path, cert_path
