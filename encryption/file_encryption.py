from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import mimetypes
import json

class FileEncryption:
    """通用文件加密類，支持任意文件類型的加密和解密"""
    
    def __init__(self):
        self.file_header = b"ENCRYPTED_FILE_V1"
        
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
    
    def encrypt_file(self, file_data: bytes, password: str, filename: str = None, preserve_metadata: bool = True) -> bytes:
        """加密文件數據"""
        try:
            # 生成隨機鹽值
            salt = os.urandom(16)
            
            # 生成密鑰
            key = self._derive_key(password, salt)
            
            # 創建 Fernet 實例
            f = Fernet(key)
            
            # 準備元數據
            metadata = {}
            if filename:
                metadata['filename'] = filename
                metadata['mime_type'] = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            else:
                metadata['mime_type'] = 'application/octet-stream'
            
            metadata['original_size'] = len(file_data)
            
            if preserve_metadata:
                metadata_json = json.dumps(metadata).encode('utf-8')
                metadata_size = len(metadata_json).to_bytes(4, byteorder='big')
            else:
                metadata_json = b''
                metadata_size = (0).to_bytes(4, byteorder='big')
            
            # 加密文件數據
            encrypted_data = f.encrypt(file_data)
            
            # 如果有元數據，也加密元數據
            if metadata_json:
                encrypted_metadata = f.encrypt(metadata_json)
            else:
                encrypted_metadata = b''
            
            # 組合最終結果：文件頭 + 鹽值 + 元數據大小 + 加密的元數據 + 加密的文件數據
            result = (self.file_header + 
                     salt + 
                     metadata_size + 
                     encrypted_metadata + 
                     encrypted_data)
            
            return result
            
        except Exception as e:
            raise Exception(f"文件加密失敗: {str(e)}")
    
    def decrypt_file(self, encrypted_data: bytes, password: str) -> tuple:
        """解密文件數據，返回 (文件數據, 元數據)"""
        try:
            # 檢查文件頭
            header_size = len(self.file_header)
            if encrypted_data[:header_size] != self.file_header:
                raise ValueError("無效的加密文件格式")
            
            # 提取鹽值
            salt = encrypted_data[header_size:header_size + 16]
            
            # 提取元數據大小
            metadata_size_bytes = encrypted_data[header_size + 16:header_size + 20]
            metadata_size = int.from_bytes(metadata_size_bytes, byteorder='big')
            
            # 生成密鑰
            key = self._derive_key(password, salt)
            
            # 創建 Fernet 實例
            f = Fernet(key)
            
            # 提取加密的元數據和文件數據
            offset = header_size + 20
            
            if metadata_size > 0:
                encrypted_metadata = encrypted_data[offset:offset + metadata_size]
                encrypted_file_data = encrypted_data[offset + metadata_size:]
                
                # 解密元數據
                metadata_json = f.decrypt(encrypted_metadata)
                metadata = json.loads(metadata_json.decode('utf-8'))
            else:
                metadata = {}
                encrypted_file_data = encrypted_data[offset:]
            
            # 解密文件數據
            decrypted_file_data = f.decrypt(encrypted_file_data)
            
            return decrypted_file_data, metadata
            
        except Exception as e:
            raise Exception(f"文件解密失敗: {str(e)}")
    
    def get_file_info(self, encrypted_data: bytes, password: str) -> dict:
        """獲取加密文件的信息（不解密文件內容）"""
        try:
            # 檢查文件頭
            header_size = len(self.file_header)
            if encrypted_data[:header_size] != self.file_header:
                raise ValueError("無效的加密文件格式")
            
            # 提取鹽值
            salt = encrypted_data[header_size:header_size + 16]
            
            # 提取元數據大小
            metadata_size_bytes = encrypted_data[header_size + 16:header_size + 20]
            metadata_size = int.from_bytes(metadata_size_bytes, byteorder='big')
            
            info = {
                "is_encrypted_file": True,
                "file_format_version": "V1",
                "total_size": len(encrypted_data),
                "has_metadata": metadata_size > 0,
                "metadata_size": metadata_size
            }
            
            if metadata_size > 0:
                try:
                    # 生成密鑰並嘗試解密元數據
                    key = self._derive_key(password, salt)
                    f = Fernet(key)
                    
                    offset = header_size + 20
                    encrypted_metadata = encrypted_data[offset:offset + metadata_size]
                    metadata_json = f.decrypt(encrypted_metadata)
                    metadata = json.loads(metadata_json.decode('utf-8'))
                    
                    info.update({
                        "filename": metadata.get('filename'),
                        "mime_type": metadata.get('mime_type'),
                        "original_size": metadata.get('original_size')
                    })
                except:
                    info["metadata_error"] = "無法解密元數據（密碼可能錯誤）"
            
            return info
            
        except Exception as e:
            raise Exception(f"獲取文件信息失敗: {str(e)}")
    
    def is_encrypted_file(self, data: bytes) -> bool:
        """檢查數據是否為此格式的加密文件"""
        try:
            header_size = len(self.file_header)
            return len(data) >= header_size and data[:header_size] == self.file_header
        except:
            return False 