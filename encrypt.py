import os
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

def encrypt_file(public_key, input_file, output_file):
    with open(input_file, 'rb') as f:
        data = f.read()
    encrypted = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    encrypted_b64 = base64.b64encode(encrypted)
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
