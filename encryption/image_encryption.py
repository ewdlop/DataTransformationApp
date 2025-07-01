from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import os

class ImageEncryption:
    """圖像加密類，使用 AES 加密圖像數據"""
    
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
        return kdf.derive(password_bytes)
    
    def encrypt(self, image_data: bytes, password: str) -> bytes:
        """加密圖像數據"""
        try:
            # 生成隨機鹽值和 IV
            salt = os.urandom(16)
            iv = os.urandom(16)
            
            # 生成密鑰
            key = self._derive_key(password, salt)
            
            # 填充圖像數據
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(image_data)
            padded_data += padder.finalize()
            
            # 創建加密器
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            encryptor = cipher.encryptor()
            
            # 加密數據
            encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
            
            # 添加標識頭和元數據
            header = b'IMGENC01'  # 8字節標識頭
            original_size = len(image_data).to_bytes(8, byteorder='big')
            
            # 組合所有數據：標識頭 + 原始大小 + 鹽值 + IV + 加密數據
            result = header + original_size + salt + iv + encrypted_data
            
            return result
        except Exception as e:
            raise Exception(f"圖像加密失敗: {str(e)}")
    
    def decrypt(self, encrypted_data: bytes, password: str) -> bytes:
        """解密圖像數據"""
        try:
            # 檢查標識頭
            if len(encrypted_data) < 8 or encrypted_data[:8] != b'IMGENC01':
                raise ValueError("無效的加密圖像文件格式")
            
            # 提取元數據
            original_size = int.from_bytes(encrypted_data[8:16], byteorder='big')
            salt = encrypted_data[16:32]
            iv = encrypted_data[32:48]
            ciphertext = encrypted_data[48:]
            
            # 生成密鑰
            key = self._derive_key(password, salt)
            
            # 創建解密器
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
            decryptor = cipher.decryptor()
            
            # 解密數據
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # 移除填充
            unpadder = padding.PKCS7(128).unpadder()
            decrypted_data = unpadder.update(padded_data)
            decrypted_data += unpadder.finalize()
            
            # 確保數據大小正確
            if len(decrypted_data) >= original_size:
                decrypted_data = decrypted_data[:original_size]
            
            return decrypted_data
        except Exception as e:
            raise Exception(f"圖像解密失敗: {str(e)}")
    
    def is_encrypted_image(self, data: bytes) -> bool:
        """檢查數據是否為加密的圖像"""
        return len(data) >= 8 and data[:8] == b'IMGENC01' 