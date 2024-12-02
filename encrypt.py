import os
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def generate_aes_key():
    return os.urandom(32)  # 256位AES密钥


def encrypt_file(public_key, input_file, output_file):
    # 读取需要加密的数据
    with open(input_file, 'rb') as f:
        data = f.read()

    # 生成AES密钥和IV
    aes_key = generate_aes_key()
    iv = os.urandom(16)

    # 使用RSA加密AES密钥
    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # 使用AES加密数据
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # PKCS7 padding
    pad_length = 16 - (len(data) % 16)
    padded_data = data + bytes([pad_length] * pad_length)

    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # 组合加密后的密钥、IV和数据，并进行Base64编码
    final_data = encrypted_key + iv + encrypted_data
    encrypted_b64 = base64.b64encode(final_data)

    with open(output_file, 'wb') as f:
        f.write(encrypted_b64)


def process_directory(problem_dir):
    with open('public_key.pem', 'rb') as f:
        public_key = serialization.load_pem_public_key(
            f.read(),
        )
    for filename in os.listdir(problem_dir):
        if filename.endswith('.out') or filename.endswith('.in'):
            input_file = os.path.join(problem_dir, filename)
            output_file = input_file + '.enc'
            print(f'Encrypting {input_file}...')
            encrypt_file(public_key, input_file, output_file)


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print("Usage: python encrypt.py <problem_directory>")
        sys.exit(1)
    process_directory(sys.argv[1])