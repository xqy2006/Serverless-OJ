import sys
import os
import json
import subprocess
import base64
import psutil
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

def load_problem_config(problem_dir):
    config_path = os.path.join(problem_dir, 'problem.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

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

def run_testcase(exe_path, input_file, time_limit, memory_limit):
    try:
        proc = subprocess.Popen(
            [exe_path],
            stdin=open(input_file, 'rb'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        psutil_proc = psutil.Process(proc.pid)
        max_memory_used = 0
        
        while proc.poll() is None:
            try:
                # 获取内存使用（MB）
                memory_info = psutil_proc.memory_info()
                memory_used = memory_info.rss / 1024 / 1024  # Convert to MB
                max_memory_used = max(max_memory_used, memory_used)
                
                if max_memory_used > memory_limit:
                    proc.kill()
                    return False, None, "Memory Limit Exceeded"
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break
        
        try:
            stdout, stderr = proc.communicate(timeout=time_limit/1000)
            return proc.returncode == 0, stdout, None
        except subprocess.TimeoutExpired:
            proc.kill()
            return False, None, "Time Limit Exceeded"
            
    except Exception as e:
        return False, None, str(e)

def judge(private_key_path, problem_dir, solution_file):
    # 加载题目配置
    config = load_problem_config(problem_dir)
    time_limit = config.get('timeLimit', 1000)  # 默认1000ms
    memory_limit = config.get('memoryLimit', 256)  # 默认256MB
    
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
    
    for filename in sorted(os.listdir(problem_dir)):
        if filename.endswith('.in'):
            total_cases += 1
            testcase = filename[:-3]
            input_file = os.path.join(problem_dir, filename)
            encrypted_file = os.path.join(problem_dir, f'{testcase}.out.enc')
            
            with open(encrypted_file, 'rb') as f:
                expected_output = decrypt_data(private_key, f.read())
            
            success, actual_output, error = run_testcase(exe_path, input_file, time_limit, memory_limit)
            
            if error:
                if "Time Limit Exceeded" in error:
                    has_tle = True
                elif "Memory Limit Exceeded" in error:
                    has_mle = True
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
