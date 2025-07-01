from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class TextEncryption:
    """文本加密類，使用 Fernet 對稱加密"""
    
    def __init__(self):
        pass
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """從密碼和鹽值生成加密密鑰"""
        password_bytes = password.encode('utf-8')
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        return key
    
    def encrypt(self, text: str, password: str) -> str:
        """加密文本"""
        try:
            # 生成隨機鹽值
            salt = os.urandom(16)
            
            # 生成密鑰
            key = self._derive_key(password, salt)
            
            # 創建 Fernet 實例
            f = Fernet(key)
            
            # 加密文本
            text_bytes = text.encode('utf-8')
            encrypted_text = f.encrypt(text_bytes)
            
            # 組合鹽值和加密文本
            result = base64.urlsafe_b64encode(salt + encrypted_text).decode('utf-8')
            
            return result
        except Exception as e:
            raise Exception(f"文本加密失敗: {str(e)}")
    
    def decrypt(self, encrypted_text: str, password: str) -> str:
        """解密文本"""
        try:
            # 解碼 base64
            encrypted_data = base64.urlsafe_b64decode(encrypted_text.encode('utf-8'))
            
            # 提取鹽值和加密文本
            salt = encrypted_data[:16]
            encrypted_content = encrypted_data[16:]
            
            # 生成密鑰
            key = self._derive_key(password, salt)
            
            # 創建 Fernet 實例
            f = Fernet(key)
            
            # 解密文本
            decrypted_bytes = f.decrypt(encrypted_content)
            decrypted_text = decrypted_bytes.decode('utf-8')
            
            return decrypted_text
        except Exception as e:
            raise Exception(f"文本解密失敗: {str(e)}") 