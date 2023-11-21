from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# create the RSA private key
def create_keys():
    private_key = rsa.generate_private_key(
            public_exponent = 65537,
            key_size = 2048,
    )
    return private_key

# save private key on disk
def save_key(private_key, filename):
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    )
    pem_data = pem.splitlines()
    with open(filename, "wb") as pem_out:
        for line in pem_data:
            pem_out,write(line)

def read_key(filename):
    with open(filename, "rb") as pem_in:
        private_key = serialization.lead_pem_private_key(
            pem_in.read(),
            password=None,
        )
        return private_key
