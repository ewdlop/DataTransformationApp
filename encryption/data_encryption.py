from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import json

class DataEncryption:
    """通用數據加密類，支持多種加密算法"""
    
    def __init__(self):
        self.supported_algorithms = ['AES', 'Fernet']
    
    def _derive_key(self, password: str, salt: bytes, key_length: int = 32) -> bytes:
        """從密碼和鹽值生成加密密鑰"""
        password_bytes = password.encode('utf-8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=key_length,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password_bytes)
    
    def _encrypt_aes(self, data: bytes, password: str) -> bytes:
        """使用 AES 加密數據"""
        # 生成隨機鹽值和 IV
        salt = os.urandom(16)
        iv = os.urandom(16)
        
        # 生成密鑰
        key = self._derive_key(password, salt)
        
        # 填充數據
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data)
        padded_data += padder.finalize()
        
        # 創建加密器
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        
        # 加密數據
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        # 組合鹽值、IV 和加密數據
        result = salt + iv + encrypted_data
        return result
    
    def _decrypt_aes(self, encrypted_data: bytes, password: str) -> bytes:
        """使用 AES 解密數據"""
        # 提取鹽值、IV 和加密數據
        salt = encrypted_data[:16]
        iv = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]
        
        # 生成密鑰
        key = self._derive_key(password, salt)
        
        # 創建解密器
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        
        # 解密數據
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        # 移除填充
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data)
        data += unpadder.finalize()
        
        return data
    
    def _encrypt_fernet(self, data: bytes, password: str) -> bytes:
        """使用 Fernet 加密數據"""
        # 生成隨機鹽值
        salt = os.urandom(16)
        
        # 生成密鑰
        key = base64.urlsafe_b64encode(self._derive_key(password, salt))
        
        # 創建 Fernet 實例
        f = Fernet(key)
        
        # 加密數據
        encrypted_data = f.encrypt(data)
        
        # 組合鹽值和加密數據
        result = salt + encrypted_data
        return result
    
    def _decrypt_fernet(self, encrypted_data: bytes, password: str) -> bytes:
        """使用 Fernet 解密數據"""
        # 提取鹽值和加密數據
        salt = encrypted_data[:16]
        ciphertext = encrypted_data[16:]
        
        # 生成密鑰
        key = base64.urlsafe_b64encode(self._derive_key(password, salt))
        
        # 創建 Fernet 實例
        f = Fernet(key)
        
        # 解密數據
        decrypted_data = f.decrypt(ciphertext)
        return decrypted_data
    
    def encrypt(self, data: str, password: str, algorithm: str = 'AES') -> str:
        """加密數據"""
        try:
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"不支持的算法: {algorithm}")
            
            # 將字符串轉換為字節
            data_bytes = data.encode('utf-8')
            
            # 根據算法選擇加密方法
            if algorithm == 'AES':
                encrypted_data = self._encrypt_aes(data_bytes, password)
            elif algorithm == 'Fernet':
                encrypted_data = self._encrypt_fernet(data_bytes, password)
            
            # 編碼為 base64
            result = base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
            return result
        except Exception as e:
            raise Exception(f"數據加密失敗: {str(e)}")
    
    def decrypt(self, encrypted_data: str, password: str, algorithm: str = 'AES') -> str:
        """解密數據"""
        try:
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"不支持的算法: {algorithm}")
            
            # 解碼 base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
            
            # 根據算法選擇解密方法
            if algorithm == 'AES':
                decrypted_data = self._decrypt_aes(encrypted_bytes, password)
            elif algorithm == 'Fernet':
                decrypted_data = self._decrypt_fernet(encrypted_bytes, password)
            
            # 轉換為字符串
            result = decrypted_data.decode('utf-8')
            return result
        except Exception as e:
            raise Exception(f"數據解密失敗: {str(e)}") 