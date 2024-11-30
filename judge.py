import sys
import os
import subprocess
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

def decrypt_data(private_key, encrypted_b64):
    encrypted = base64.b64decode(encrypted_b64)
    decrypted = private_key.decrypt(
        encrypted,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return decrypted

def normalize_text(text):
    lines = text.decode().strip().split('\n')
    return '\n'.join(line.rstrip() for line in lines)

def run_testcase(exe_path, input_file, time_limit=1000):
    try:
        proc = subprocess.run(
            [exe_path],
            input=open(input_file, 'rb').read(),
            capture_output=True,
            timeout=time_limit/1000
        )
        return proc.returncode == 0, proc.stdout, None
    except subprocess.TimeoutExpired:
        return False, None, "Time Limit Exceeded"
    except Exception as e:
        return False, None, str(e)

def judge(private_key_path, problem_dir, solution_file):
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    exe_path = './solution'
    compile_result = subprocess.run(['g++', solution_file, '-o', exe_path, '-O2'])
    if compile_result.returncode != 0:
        return "Compilation Error", "CE"
    
    results = []
    total_cases = 0
    ac_cases = 0
    has_tle = False
    
    for filename in sorted(os.listdir(problem_dir)):
        if filename.endswith('.in'):
            total_cases += 1
            testcase = filename[:-3]
            input_file = os.path.join(problem_dir, filename)
            encrypted_file = os.path.join(problem_dir, f'{testcase}.out.enc')
            with open(encrypted_file, 'rb') as f:
                expected_output = decrypt_data(private_key, f.read())
            success, actual_output, error = run_testcase(exe_path, input_file)
            if error:
                if "Time Limit Exceeded" in error:
                    has_tle = True
                results.append(f'测试点 {testcase}: {error}')
                continue
            expected = normalize_text(expected_output)
            actual = normalize_text(actual_output)
            
            if expected == actual:
                results.append(f'测试点 {testcase}: AC')
                ac_cases += 1
            else:
                results.append(f'测试点 {testcase}: WA')
    
    if ac_cases == total_cases:
        status = "AC"
    elif ac_cases > 0:
        #status = "Partially AC"
        status = "WA"
    elif has_tle:
        status = "TLE"
    else:
        status = "WA"
    
    return '\n'.join(results), status

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python judge.py <private_key_file> <problem_dir> <solution_file>")
        sys.exit(1)
    
    result, status = judge(sys.argv[1], sys.argv[2], sys.argv[3])
    print(result)
    with open('judge_status.txt', 'w') as f:
        f.write(status)
