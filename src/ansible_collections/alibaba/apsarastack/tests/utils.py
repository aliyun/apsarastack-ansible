import secrets
import string

def generate_password(length=9):
    if length < 4:
        raise ValueError("密码长度必须至少为4，以确保包含所有字符类型。")
    
    # 定义字符集
    uppercase_chars = string.ascii_uppercase
    lowercase_chars = string.ascii_lowercase
    digit_chars = string.digits
    special_chars = '!@#$'
    
    # 确保每个字符类型至少有一个
    password = [
        secrets.choice(uppercase_chars),
        secrets.choice(lowercase_chars),
        secrets.choice(digit_chars),
        secrets.choice(special_chars)
    ]
    
    # 剩余字符从所有字符中随机选取
    all_chars = uppercase_chars + lowercase_chars + digit_chars + special_chars
    remaining_length = length - 4
    for _ in range(remaining_length):
        password.append(secrets.choice(all_chars))
    
    # 打乱顺序
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)

# 示例使用
if __name__ == "__main__":
    print("生成的密码:", generate_password(12))