from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
import base64
import json
import os

class DigitalSignatures:
    """數字簽名類，支持RSA密鑰生成、數字簽名和驗證"""
    
    def __init__(self):
        self.key_sizes = [2048, 3072, 4096]
        self.hash_algorithms = {
            'sha256': hashes.SHA256(),
            'sha384': hashes.SHA384(),
            'sha512': hashes.SHA512(),
            'sha3_256': hashes.SHA3_256(),
            'sha3_384': hashes.SHA3_384(),
            'sha3_512': hashes.SHA3_512()
        }
    
    def generate_key_pair(self, key_size: int = 2048, password: str = None) -> dict:
        """生成RSA密鑰對"""
        try:
            if key_size not in self.key_sizes:
                raise ValueError(f"不支持的密鑰大小: {key_size}。支持的大小: {self.key_sizes}")
            
            # 生成私鑰
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
            )
            
            # 獲取公鑰
            public_key = private_key.public_key()
            
            # 序列化私鑰
            if password:
                encryption_algorithm = serialization.BestAvailableEncryption(password.encode())
            else:
                encryption_algorithm = serialization.NoEncryption()
                
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=encryption_algorithm
            )
            
            # 序列化公鑰
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return {
                "private_key": base64.b64encode(private_pem).decode('utf-8'),
                "public_key": base64.b64encode(public_pem).decode('utf-8'),
                "key_size": key_size,
                "has_password": password is not None,
                "fingerprint": self._get_key_fingerprint(public_key)
            }
            
        except Exception as e:
            raise Exception(f"密鑰對生成失敗: {str(e)}")
    
    def sign_data(self, data: str, private_key_pem: str, password: str = None, hash_algorithm: str = 'sha256') -> dict:
        """對數據進行數字簽名"""
        try:
            if hash_algorithm not in self.hash_algorithms:
                raise ValueError(f"不支持的哈希算法: {hash_algorithm}")
            
            # 解碼私鑰
            private_key_bytes = base64.b64decode(private_key_pem.encode())
            
            # 加載私鑰
            if password:
                private_key = load_pem_private_key(private_key_bytes, password.encode())
            else:
                private_key = load_pem_private_key(private_key_bytes, None)
            
            # 將數據轉換為字節
            data_bytes = data.encode('utf-8')
            
            # 創建簽名
            signature = private_key.sign(
                data_bytes,
                padding.PSS(
                    mgf=padding.MGF1(self.hash_algorithms[hash_algorithm]),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                self.hash_algorithms[hash_algorithm]
            )
            
            # 獲取公鑰用於驗證
            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return {
                "signature": base64.b64encode(signature).decode('utf-8'),
                "data": data,
                "hash_algorithm": hash_algorithm,
                "public_key": base64.b64encode(public_pem).decode('utf-8'),
                "fingerprint": self._get_key_fingerprint(public_key),
                "signature_length": len(signature)
            }
            
        except Exception as e:
            raise Exception(f"數字簽名失敗: {str(e)}")
    
    def verify_signature(self, data: str, signature: str, public_key_pem: str, hash_algorithm: str = 'sha256') -> dict:
        """驗證數字簽名"""
        try:
            if hash_algorithm not in self.hash_algorithms:
                raise ValueError(f"不支持的哈希算法: {hash_algorithm}")
            
            # 解碼公鑰和簽名
            public_key_bytes = base64.b64decode(public_key_pem.encode())
            signature_bytes = base64.b64decode(signature.encode())
            
            # 加載公鑰
            public_key = load_pem_public_key(public_key_bytes)
            
            # 將數據轉換為字節
            data_bytes = data.encode('utf-8')
            
            # 驗證簽名
            try:
                public_key.verify(
                    signature_bytes,
                    data_bytes,
                    padding.PSS(
                        mgf=padding.MGF1(self.hash_algorithms[hash_algorithm]),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    self.hash_algorithms[hash_algorithm]
                )
                is_valid = True
                error_message = None
            except Exception as verify_error:
                is_valid = False
                error_message = str(verify_error)
            
            return {
                "is_valid": is_valid,
                "data": data,
                "hash_algorithm": hash_algorithm,
                "fingerprint": self._get_key_fingerprint(public_key),
                "error_message": error_message
            }
            
        except Exception as e:
            raise Exception(f"簽名驗證失敗: {str(e)}")
    
    def sign_file(self, file_data: bytes, private_key_pem: str, password: str = None, hash_algorithm: str = 'sha256') -> dict:
        """對文件數據進行數字簽名"""
        try:
            if hash_algorithm not in self.hash_algorithms:
                raise ValueError(f"不支持的哈希算法: {hash_algorithm}")
            
            # 解碼私鑰
            private_key_bytes = base64.b64decode(private_key_pem.encode())
            
            # 加載私鑰
            if password:
                private_key = load_pem_private_key(private_key_bytes, password.encode())
            else:
                private_key = load_pem_private_key(private_key_bytes, None)
            
            # 創建簽名
            signature = private_key.sign(
                file_data,
                padding.PSS(
                    mgf=padding.MGF1(self.hash_algorithms[hash_algorithm]),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                self.hash_algorithms[hash_algorithm]
            )
            
            # 獲取公鑰
            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return {
                "signature": base64.b64encode(signature).decode('utf-8'),
                "file_size": len(file_data),
                "hash_algorithm": hash_algorithm,
                "public_key": base64.b64encode(public_pem).decode('utf-8'),
                "fingerprint": self._get_key_fingerprint(public_key)
            }
            
        except Exception as e:
            raise Exception(f"文件簽名失敗: {str(e)}")
    
    def verify_file_signature(self, file_data: bytes, signature: str, public_key_pem: str, hash_algorithm: str = 'sha256') -> dict:
        """驗證文件的數字簽名"""
        try:
            if hash_algorithm not in self.hash_algorithms:
                raise ValueError(f"不支持的哈希算法: {hash_algorithm}")
            
            # 解碼公鑰和簽名
            public_key_bytes = base64.b64decode(public_key_pem.encode())
            signature_bytes = base64.b64decode(signature.encode())
            
            # 加載公鑰
            public_key = load_pem_public_key(public_key_bytes)
            
            # 驗證簽名
            try:
                public_key.verify(
                    signature_bytes,
                    file_data,
                    padding.PSS(
                        mgf=padding.MGF1(self.hash_algorithms[hash_algorithm]),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    self.hash_algorithms[hash_algorithm]
                )
                is_valid = True
                error_message = None
            except Exception as verify_error:
                is_valid = False
                error_message = str(verify_error)
            
            return {
                "is_valid": is_valid,
                "file_size": len(file_data),
                "hash_algorithm": hash_algorithm,
                "fingerprint": self._get_key_fingerprint(public_key),
                "error_message": error_message
            }
            
        except Exception as e:
            raise Exception(f"文件簽名驗證失敗: {str(e)}")
    
    def _get_key_fingerprint(self, public_key) -> str:
        """生成公鑰指紋"""
        try:
            public_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # 使用SHA256生成指紋
            digest = hashes.Hash(hashes.SHA256())
            digest.update(public_bytes)
            fingerprint_bytes = digest.finalize()
            
            # 轉換為十六進制格式
            fingerprint = fingerprint_bytes.hex().upper()
            # 添加冒號分隔符
            return ':'.join([fingerprint[i:i+2] for i in range(0, len(fingerprint), 2)])
            
        except Exception:
            return "未知"
    
    def get_key_info(self, key_pem: str, is_private: bool = True, password: str = None) -> dict:
        """獲取密鑰信息"""
        try:
            key_bytes = base64.b64decode(key_pem.encode())
            
            if is_private:
                if password:
                    key = load_pem_private_key(key_bytes, password.encode())
                else:
                    key = load_pem_private_key(key_bytes, None)
                public_key = key.public_key()
            else:
                public_key = load_pem_public_key(key_bytes)
                key = None
            
            # 獲取密鑰大小
            key_size = public_key.key_size
            
            return {
                "is_private_key": is_private,
                "key_size": key_size,
                "fingerprint": self._get_key_fingerprint(public_key),
                "has_password": password is not None if is_private else None,
                "public_exponent": public_key.public_numbers().e if hasattr(public_key, 'public_numbers') else None
            }
            
        except Exception as e:
            raise Exception(f"獲取密鑰信息失敗: {str(e)}")
    
    def export_public_key(self, private_key_pem: str, password: str = None) -> str:
        """從私鑰中提取公鑰"""
        try:
            private_key_bytes = base64.b64decode(private_key_pem.encode())
            
            if password:
                private_key = load_pem_private_key(private_key_bytes, password.encode())
            else:
                private_key = load_pem_private_key(private_key_bytes, None)
            
            public_key = private_key.public_key()
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            return base64.b64encode(public_pem).decode('utf-8')
            
        except Exception as e:
            raise Exception(f"提取公鑰失敗: {str(e)}") 