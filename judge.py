import sys
import os
import json
import subprocess
import base64
import psutil
import time
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import tempfile
import threading
from queue import Queue, Empty

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
        #print(lines)
    return '\n'.join(line.rstrip() for line in lines)

class ProcessMonitor:
    def __init__(self, time_limit, memory_limit, max_output_size):
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.max_output_size = max_output_size
        self.start_time = None
        self.output_size = 0
        self.max_memory_used = 0
        self.error = None
        self.stop_flag = False
        
    def check_limits(self, proc, psutil_proc):
        if not self.start_time:
            self.start_time = time.time()
        elapsed = (time.time() - self.start_time) * 1000
        if elapsed > self.time_limit:
            self.error = "Time Limit Exceeded"
            return False
        try:
            memory_info = psutil_proc.memory_info()
            memory_used = memory_info.rss / 1024 / 1024
            self.max_memory_used = max(self.max_memory_used, memory_used)
            
            if self.max_memory_used > self.memory_limit:
                self.error = "Memory Limit Exceeded"
                return False
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
            
        return True

    def update_output_size(self, size):
        self.output_size += size
        if self.output_size > self.max_output_size:
            self.error = "Output Limit Exceeded"
            return False
        return True

def output_reader(proc, output_file, queue, monitor):
    try:
        while not monitor.stop_flag:
            chunk = proc.stdout.read(8192)
            if not chunk:
                break
            queue.put(('output', chunk))
            proc.stdout.flush()
    except Exception as e:
        queue.put(('error', str(e)))
    finally:
        queue.put(('done', None))

def run_testcase(exe_path, input_path, output_path, time_limit, memory_limit):
    MAX_OUTPUT_SIZE = 50 * 1024 * 1024
    monitor = ProcessMonitor(time_limit, memory_limit, MAX_OUTPUT_SIZE)
    
    try:
        with open(input_path, 'rb') as input_file:
            proc = subprocess.Popen(
                [exe_path],
                stdin=input_file,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0
            )
            
        psutil_proc = psutil.Process(proc.pid)
        queue = Queue()
        reader_thread = threading.Thread(
            target=output_reader,
            args=(proc, output_path, queue, monitor)
        )
        reader_thread.daemon = True
        reader_thread.start()
        
        with open(output_path, 'wb') as output_file:
            while True:
                if proc.poll() is not None:
                    if proc.returncode < 0:
                        return False, "Runtime Error: Program terminated by signal"
                    elif proc.returncode > 0:
                        stderr_output = proc.stderr.read().decode('utf-8', errors='ignore')
                        return False, f"Runtime Error: Program exited with code {proc.returncode}"
                    break
                    
                try:
                    msg_type, data = queue.get(timeout=2.0)
                    if msg_type == 'output':
                        if not monitor.update_output_size(len(data)):
                            proc.kill()
                            return False, monitor.error
                        output_file.write(data)
                    elif msg_type == 'error':
                        proc.kill()
                        return False, f"Runtime Error: {data}"
                    elif msg_type == 'done':
                        break
                except Empty:
                    pass
                
                if not monitor.check_limits(proc, psutil_proc):
                    proc.kill()
                    return False, monitor.error
                
        monitor.stop_flag = True
        reader_thread.join(timeout=1.0)
        
        try:
            proc.wait(timeout=1.0)
        except subprocess.TimeoutExpired:
            proc.kill()
            return False, "Time Limit Exceeded"
            
        return True, None
            
    except Exception as e:
        return False, f"Runtime Error: {str(e)}"

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
    compile_result = subprocess.run(['gcc', solution_file, '-o', exe_path, '-O2','-Wall','-fno-asm','-lm','-march=native''-D_IONBF','-Wno-unused-result'])
    if compile_result.returncode != 0:
        return "Compilation Error", "CE"
    
    results = []
    total_cases = 0
    ac_cases = 0
    has_tle = False
    has_mle = False
    has_re = False
    with tempfile.TemporaryDirectory() as temp_dir:
        for filename in sorted(os.listdir(problem_dir)):
            if filename.endswith('.in.enc'):
                total_cases += 1
                testcase = filename[:-7]
                input_file = os.path.join(problem_dir, filename)
                output_file = os.path.join(problem_dir, f'{testcase}.out.enc')
                with open(input_file, 'rb') as f:
                    input_data = decrypt_data(private_key, f.read())
                temp_input = os.path.join(temp_dir, f'{testcase}.in')
                with open(temp_input, 'wb') as f:
                    f.write(input_data)
                with open(output_file, 'rb') as f:
                    expected_output = decrypt_data(private_key, f.read())
                temp_expected = os.path.join(temp_dir, f'{testcase}.expected')
                with open(temp_expected, 'wb') as f:
                    f.write(expected_output)
                temp_output = os.path.join(temp_dir, f'{testcase}.out')
                
                success, error = run_testcase(exe_path, temp_input, temp_output, time_limit, memory_limit)
                
                if error:
                    if "Time Limit Exceeded" in error:
                        has_tle = True
                    elif "Memory Limit Exceeded" in error:
                        has_mle = True
                    elif "Runtime Error" in error:
                        has_re = True
                    results.append(f'测试点 {testcase}: {error}')
                    continue
                
                expected = normalize_text(temp_expected)
                actual = normalize_text(temp_output)
                #print(expected)
                #print(actual)
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
    elif has_re:
        status = "RE"
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
