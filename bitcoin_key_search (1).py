import binascii
import random
from bitcoin import *
import os
import threading
import multiprocessing

# 指定存储路径
home_dir = "D:/比特币离线破解"

# 确保指定目录存在，如果不存在则创建
if not os.path.exists(home_dir):
    try:
        os.makedirs(home_dir)
    except PermissionError:
        print(f"没有权限创建目录 {home_dir}，请检查 D 盘的权限设置。")
        exit(1)
    except Exception as e:
        print(f"创建目录 {home_dir} 时出错: {e}")
        exit(1)

# 起始私钥
start_hex = "20000000000000000000"
end_hex = "3fffffffffffffffffff"

start_int = int(start_hex, 16)
end_int = int(end_hex, 16)

# 目标地址
target_address = "1K3x5L6G57Y494fDqBfrojD28UJv4s5JcK"

# 已生成私钥文件路径
generated_keys_file = os.path.join(home_dir, 'generated_private_keys.txt')

# 私钥保存文件路径
private_key_save_file = os.path.join(home_dir, 'private_key.txt')

# 读取已生成的私钥
generated_keys = set()
if os.path.exists(generated_keys_file):
    try:
        with open(generated_keys_file, 'r') as file:
            for line in file:
                generated_keys.add(int(line.strip(), 16))
    except FileNotFoundError:
        print(f"文件 {generated_keys_file} 未找到。")
    except PermissionError:
        print(f"没有权限读取文件 {generated_keys_file}，请检查 D 盘的权限设置。")
    except ValueError:
        print(f"文件 {generated_keys_file} 中的数据格式错误。")
    except Exception as e:
        print(f"读取已生成私钥文件时出错: {e}")

# 线程锁，用于线程安全
lock = threading.Lock()
found = False


def check_keys():
    global found
    while not found:
        # 随机生成一个在区间内的私钥
        current_key = random.randint(start_int, end_int)
        with lock:
            if current_key in generated_keys:
                continue

        private_key_hex = '{:064x}'.format(current_key)
        print(f"正在检查私钥: {private_key_hex}")

        try:
            private_key_bytes = binascii.unhexlify(private_key_hex)
            public_key = privtopub(private_key_bytes)
            address = pubtoaddr(public_key)
            if address == target_address:
                with lock:
                    found = True
                print(f"找到目标地址: {target_address}，私钥 (十六进制): {private_key_hex}")
                try:
                    with open(private_key_save_file, 'w') as file:
                        file.write(private_key_hex)
                    print(f"私钥已保存到 {private_key_save_file}")
                except FileNotFoundError:
                    print(f"无法创建文件 {private_key_save_file}。")
                except PermissionError:
                    print(f"没有权限写入文件 {private_key_save_file}，请检查 D 盘的权限设置。")
                except Exception as e:
                    print(f"保存私钥到文件时出错: {e}")
                break
        except binascii.Error:
            print(f"私钥 {private_key_hex} 格式错误。")
        except Exception as e:
            print(f"处理私钥 {private_key_hex} 时出错: {e}")

        try:
            with lock:
                with open(generated_keys_file, 'a') as file:
                    file.write(private_key_hex + '\n')
                generated_keys.add(current_key)
        except FileNotFoundError:
            print(f"无法创建文件 {generated_keys_file}。")
        except PermissionError:
            print(f"没有权限写入文件 {generated_keys_file}，请检查 D 盘的权限设置。")
        except Exception as e:
            print(f"保存已生成私钥到文件时出错: {e}")


# 根据 CPU 核心数动态设置线程数量
num_threads = multiprocessing.cpu_count()
threads = []
for _ in range(num_threads):
    thread = threading.Thread(target=check_keys)
    threads.append(thread)
    thread.start()

# 等待所有线程完成
for thread in threads:
    thread.join()
    