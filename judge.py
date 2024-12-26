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
def natural_sort_key(s):
    import re
    def atoi(text):
        return int(text) if text.isdigit() else text
    return [atoi(c) for c in re.split(r'(\d+)', s)]
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
def output_reader(proc, output_file, queue, monitor):
    try:
        while not monitor.stop_flag:
            chunk = proc.stdout.read1(8192)
            if not chunk and proc.poll() is not None:
                break
            if chunk:
                queue.put(('output', chunk))
        remaining = proc.stdout.read()
        if remaining:
            queue.put(('output', remaining))
    except Exception as e:
        queue.put(('error', str(e)))
    finally:
        queue.put(('done', None))

def normalize_text(text_path):
    with open(text_path, 'r') as f:
        lines = f.read().strip().split('\n')
    return '\n'.join(line.rstrip() for line in lines)

class ProcessMonitor:
    def __init__(self, time_limit, memory_limit, max_output_size):
        self.time_limit = time_limit
        self.memory_limit = memory_limit
        self.max_output_size = max_output_size
        self.output_size = 0
        self.max_memory_used = 0
        self.error = None
        self.stop_flag = False
        
    def check_limits(self, proc, psutil_proc, elapsed_time):
        if elapsed_time > self.time_limit:
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
def run_spj(spj_path, input_path, output_path, answer_path, time_limit, memory_limit):
    monitor = ProcessMonitor(time_limit, memory_limit, MAX_OUTPUT_SIZE)
    start_time = time.time()
    
    try:
        proc = subprocess.Popen(
            [spj_path, input_path, output_path, answer_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        psutil_proc = psutil.Process(proc.pid)
        
        while proc.poll() is None:
            current_time = time.time()
            elapsed_time = (current_time - start_time) * 1000
            
            if not monitor.check_limits(proc, psutil_proc, elapsed_time):
                proc.kill()
                return False, monitor.error, elapsed_time
                
            time.sleep(0.001)
            
        final_time = (time.time() - start_time) * 1000
        
        if proc.returncode == 0:
            return True, None, final_time
        elif proc.returncode == 1:
            return False, "Wrong Answer", final_time
        else:
            stderr = proc.stderr.read()
            return False, f"Special Judge Error: {stderr}", final_time
            
    except Exception as e:
        final_time = (time.time() - start_time) * 1000
        return False, f"Special Judge Error: {str(e)}", final_time
def run_testcase(exe_path, input_path, output_path, time_limit, memory_limit):
    MAX_OUTPUT_SIZE = 50 * 1024 * 1024
    monitor = ProcessMonitor(time_limit, memory_limit, MAX_OUTPUT_SIZE)
    start_time = time.time()  # 时间计算移到这里
    
    try:
        with open(input_path, 'rb') as input_file:
            proc = subprocess.Popen(
                [exe_path],
                stdin=input_file,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=1,
                universal_newlines=False
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
            output_buffer = []
            while True:
                current_time = time.time()
                elapsed_time = (current_time - start_time) * 1000  # 计算经过的时间
                
                if proc.poll() is not None:
                    if elapsed_time > time_limit:
                        proc.kill()
                        return False, "Time Limit Exceeded", elapsed_time
                    time.sleep(0.001)
                    while True:
                        try:
                            msg_type, data = queue.get_nowait()
                            if msg_type == 'output':
                                output_buffer.append(data)
                            elif msg_type == 'error':
                                proc.kill()
                                return False, f"Runtime Error: {data}", elapsed_time
                            elif msg_type == 'done':
                                break
                        except Empty:
                            break
                            
                    if proc.returncode < 0:
                        return False, "Runtime Error: Program terminated by signal", elapsed_time
                    elif proc.returncode > 0:
                        stderr_output = proc.stderr.read().decode('utf-8', errors='ignore')
                        return False, f"Runtime Error: Program exited with code {proc.returncode}", elapsed_time
                    break
                    
                try:
                    msg_type, data = queue.get(timeout=0.1)
                    if msg_type == 'output':
                        output_buffer.append(data)
                        if not monitor.update_output_size(len(data)):
                            proc.kill()
                            return False, monitor.error, elapsed_time
                    elif msg_type == 'error':
                        proc.kill()
                        return False, f"Runtime Error: {data}", elapsed_time
                    elif msg_type == 'done':
                        break
                except Empty:
                    pass
                
                if not monitor.check_limits(proc, psutil_proc, elapsed_time):
                    proc.kill()
                    return False, monitor.error, elapsed_time
            
            if output_buffer:
                all_output = b''.join(output_buffer)
                output_file.write(all_output)
                
        monitor.stop_flag = True
        reader_thread.join(timeout=1.0)
        
        final_time = (time.time() - start_time) * 1000
        if final_time > time_limit:
            return False, "Time Limit Exceeded", final_time
        return True, None, final_time
            
    except Exception as e:
        final_time = (time.time() - start_time) * 1000
        return False, f"Runtime Error: {str(e)}", final_time
        
def judge(private_key_path, problem_dir, solution_file):
    config = load_problem_config(problem_dir)
    time_limit = config.get('timeLimit', 1000)
    memory_limit = config.get('memoryLimit', 256)
    spj_config = config.get('specialJudge', 0)
    with open(private_key_path, 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    
    # Compile solution
    exe_path = './solution'
    compile_result = subprocess.run(['gcc', solution_file, '-o', exe_path, '-O2', '-Wall', '-fno-asm', '-lstdc++', '-lm', '-march=native', '-D_IONBF', '-Wno-unused-result'])
    if compile_result.returncode != 0:
        return "Compilation Error", "CE"
    
    # Compile special judge if needed
    spj_path = None
    if spj_config==1:
        spj_source = os.path.join(problem_dir, 'spj.cpp')
        spj_path = './spj'
        spj_compile = subprocess.run(['g++', spj_source, '-o', spj_path, '-O2'])
        if spj_compile.returncode != 0:
            return "Special Judge Compilation Error", "SE"
    
    results = []
    total_cases = 0
    ac_cases = 0
    has_tle = False
    has_mle = False
    has_re = False
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 找到第一个测试样例进行预热
        first_testcase = None
        for filename in sorted(os.listdir(problem_dir), key=natural_sort_key):
            if filename.endswith('.in.enc'):
                first_testcase = filename[:-7]
                break
                
        if first_testcase:
            # 预热运行
            input_file = os.path.join(problem_dir, f'{first_testcase}.in.enc')
            with open(input_file, 'rb') as f:
                input_data = decrypt_data(private_key, f.read())
            temp_input = os.path.join(temp_dir, f'{first_testcase}.in')
            with open(temp_input, 'wb') as f:
                f.write(input_data)
            temp_output = os.path.join(temp_dir, f'{first_testcase}.out')
            run_testcase(exe_path, temp_input, temp_output, time_limit, memory_limit)

        # 正式评测
        for filename in sorted(os.listdir(problem_dir), key=natural_sort_key):
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
                
                success, error, execution_time = run_testcase(exe_path, temp_input, temp_output, time_limit, memory_limit)
                
                if error:
                    if "Time Limit Exceeded" in error:
                        has_tle = True
                    elif "Memory Limit Exceeded" in error:
                        has_mle = True
                    elif "Runtime Error" in error:
                        has_re = True
                    results.append(f'测试点 {testcase}: {error} ({execution_time:.0f}ms)')
                    continue
                
                if spj_path:
                    # 使用special judge
                    spj_success, spj_error, spj_time = run_spj(
                        spj_path,
                        temp_input,
                        temp_output,
                        temp_expected,
                        60000,
                        1024
                    )
                    
                    if spj_error:
                        results.append(f'测试点 {testcase}: {spj_error} ({execution_time:.0f}ms)')
                        if "Special Judge Error" in spj_error:
                            return '\n'.join(results), "SE"
                        continue
                    
                    if spj_success:
                        results.append(f'测试点 {testcase}: AC ({execution_time:.0f}ms)')
                        ac_cases += 1
                    else:
                        results.append(f'测试点 {testcase}: WA ({execution_time:.0f}ms)')
                else:
                    # 普通判题
                    expected = normalize_text(temp_expected)
                    actual = normalize_text(temp_output)
                    
                    if expected == actual:
                        results.append(f'测试点 {testcase}: AC ({execution_time:.0f}ms)')
                        ac_cases += 1
                    else:
                        results.append(f'测试点 {testcase}: WA ({execution_time:.0f}ms)')
    
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
