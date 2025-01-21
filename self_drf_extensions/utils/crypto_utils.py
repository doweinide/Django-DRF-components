#pip install pycryptodome  安装这个包
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import hashlib
import base64

def aes_encrypt(plain_text: str, key: str) -> bytes:
    """
    AES加密
    :param plain_text: 明文
    :param key: 密钥（长度应为16、24或32字节）
    :return: 密文
    """
    # 确保密钥是16字节
    key = key.encode('utf-8')
    key = hashlib.sha256(key).digest()[:16]  # 使用SHA256哈希并取前16字节
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(plain_text.encode(), AES.block_size))
    return cipher.iv + ct_bytes  # 返回IV和密文，IV用于解密时

def aes_decrypt(cipher_text: bytes, key: str) -> str:
    """
    AES解密
    :param cipher_text: 密文
    :param key: 密钥
    :return: 明文
    """
    key = key.encode('utf-8')
    key = hashlib.sha256(key).digest()[:16]  # 使用SHA256哈希并取前16字节
    iv = cipher_text[:16]  # 获取IV
    ct = cipher_text[16:]  # 获取密文
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain_text = unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')
    return plain_text

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def generate_rsa_keys():
    """
    生成RSA公钥和私钥
    :return: 公钥和私钥
    """
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return public_key, private_key

def rsa_encrypt(plain_text: str, public_key: bytes) -> bytes:
    """
    RSA加密
    :param plain_text: 明文
    :param public_key: 公钥
    :return: 密文
    """
    public_key = RSA.import_key(public_key)
    cipher = PKCS1_OAEP.new(public_key)
    return cipher.encrypt(plain_text.encode())

def rsa_decrypt(cipher_text: bytes, private_key: bytes) -> str:
    """
    RSA解密
    :param cipher_text: 密文
    :param private_key: 私钥
    :return: 明文
    """
    private_key = RSA.import_key(private_key)
    cipher = PKCS1_OAEP.new(private_key)
    return cipher.decrypt(cipher_text).decode('utf-8')



def sha256_hash(data: str) -> str:
    """
    使用SHA-256生成哈希值
    :param data: 输入字符串
    :return: 哈希值
    """
    return hashlib.sha256(data.encode('utf-8')).hexdigest()



def base64_encode(data: bytes) -> str:
    """
    Base64 编码
    :param data: 输入字节数据
    :return: 编码后的字符串
    """
    return base64.b64encode(data).decode('utf-8')

def base64_decode(data: str) -> bytes:
    """
    Base64 解码
    :param data: 编码后的Base64字符串
    :return: 解码后的字节数据
    """
    return base64.b64decode(data)

