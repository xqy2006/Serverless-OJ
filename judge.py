import sys
import os
import json
import subprocess
import base64
import psutil
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import tempfile

def load_problem_config(problem_dir):
    config_path = os.path.join(problem_dir, 'problem.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def decrypt_data(private_key, encrypted_b64):
    encrypted_data = base64.b64decode(encrypted_b64)
    
    encrypted_key = encrypted_data[:256]
    iv = encrypted_data[256:272]
    encrypted_content = encrypted_data[272:]
    
    aes_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(encrypted_content) + decryptor.finalize()
    
    pad_length = decrypted_padded[-1]
    return decrypted_padded[:-pad_length]

def normalize_text(text_path):
    with open(text_path, 'r') as f:
        lines = f.read().strip().split('\n')
    return '\n'.join(line.rstrip() for line in lines)

def run_testcase(exe_path, input_path, output_path, time_limit, memory_limit):
    try:
        proc = subprocess.Popen(
            [exe_path],
            stdin=open(input_path, 'r'),
            stdout=open(output_path, 'w'),
            stderr=subprocess.PIPE
        )
        
        psutil_proc = psutil.Process(proc.pid)
        max_memory_used = 0
        
        while proc.poll() is None:
            try:
                memory_info = psutil_proc.memory_info()
                memory_used = memory_info.rss / 1024 / 1024
                max_memory_used = max(max_memory_used, memory_used)
                
                if max_memory_used > memory_limit:
                    proc.kill()
                    return False, "Memory Limit Exceeded"
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
        
        try:
            _, stderr = proc.communicate(timeout=time_limit/1000)
            return proc.returncode == 0, None
        except subprocess.TimeoutExpired:
            proc.kill()
            return False, "Time Limit Exceeded"
            
    except Exception as e:
        return False, str(e)

def judge(private_key_path, problem_dir, solution_file):
    config = load_problem_config(problem_dir)
    time_limit = config.get('timeLimit', 1000)
    memory_limit = config.get('memoryLimit', 256)
    
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
    has_mle = False
    
    # 创建临时目录存放解密后的输入输出文件
    with tempfile.TemporaryDirectory() as temp_dir:
        for filename in sorted(os.listdir(problem_dir)):
            if filename.endswith('.in.enc'):
                total_cases += 1
                testcase = filename[:-7]
                input_file = os.path.join(problem_dir, filename)
                output_file = os.path.join(problem_dir, f'{testcase}.out.enc')
                
                # 解密并保存输入文件
                with open(input_file, 'rb') as f:
                    input_data = decrypt_data(private_key, f.read())
                temp_input = os.path.join(temp_dir, f'{testcase}.in')
                with open(temp_input, 'wb') as f:
                    f.write(input_data)
                
                # 解密并保存预期输出文件
                with open(output_file, 'rb') as f:
                    expected_output = decrypt_data(private_key, f.read())
                temp_expected = os.path.join(temp_dir, f'{testcase}.expected')
                with open(temp_expected, 'wb') as f:
                    f.write(expected_output)
                
                # 创建实际输出文件路径
                temp_output = os.path.join(temp_dir, f'{testcase}.out')
                
                success, error = run_testcase(exe_path, temp_input, temp_output, time_limit, memory_limit)
                
                if error:
                    if "Time Limit Exceeded" in error:
                        has_tle = True
                    elif "Memory Limit Exceeded" in error:
                        has_mle = True
                    results.append(f'测试点 {testcase}: {error}')
                    continue
                
                expected = normalize_text(temp_expected)
                actual = normalize_text(temp_output)
                
                if expected == actual:
                    results.append(f'测试点 {testcase}: AC')
                    ac_cases += 1
                else:
                    results.append(f'测试点 {testcase}: WA')
    
    if ac_cases == total_cases:
        status = "AC"
    elif has_mle:
        status = "MLE"
    elif has_tle:
        status = "TLE"
    elif ac_cases > 0:
        status = "WA"
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
