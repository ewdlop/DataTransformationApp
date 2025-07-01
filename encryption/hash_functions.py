import hashlib
import hmac
import secrets
from typing import Union, Optional

class HashFunctions:
    """哈希函數類，提供多種哈希算法和相關功能"""
    
    def __init__(self):
        self.supported_algorithms = [
            'md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
            'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512',
            'blake2b', 'blake2s'
        ]
    
    def hash_text(self, text: str, algorithm: str = 'sha256', encoding: str = 'utf-8') -> str:
        """對文本進行哈希計算"""
        try:
            algorithm = algorithm.lower()
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"不支持的哈希算法: {algorithm}")
            
            # 將文本轉換為字節
            text_bytes = text.encode(encoding)
            
            # 創建哈希對象
            hash_obj = hashlib.new(algorithm)
            hash_obj.update(text_bytes)
            
            # 返回十六進制哈希值
            return hash_obj.hexdigest()
        except Exception as e:
            raise Exception(f"文本哈希計算失敗: {str(e)}")
    
    def hash_file_content(self, file_content: bytes, algorithm: str = 'sha256') -> str:
        """對文件內容進行哈希計算"""
        try:
            algorithm = algorithm.lower()
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"不支持的哈希算法: {algorithm}")
            
            # 創建哈希對象
            hash_obj = hashlib.new(algorithm)
            hash_obj.update(file_content)
            
            # 返回十六進制哈希值
            return hash_obj.hexdigest()
        except Exception as e:
            raise Exception(f"文件內容哈希計算失敗: {str(e)}")
    
    def verify_hash(self, text: str, expected_hash: str, algorithm: str = 'sha256', encoding: str = 'utf-8') -> bool:
        """驗證文本的哈希值"""
        try:
            calculated_hash = self.hash_text(text, algorithm, encoding)
            return calculated_hash.lower() == expected_hash.lower()
        except Exception as e:
            raise Exception(f"哈希驗證失敗: {str(e)}")
    
    def hmac_hash(self, message: str, key: str, algorithm: str = 'sha256', encoding: str = 'utf-8') -> str:
        """使用 HMAC 生成認證哈希"""
        try:
            algorithm = algorithm.lower()
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"不支持的哈希算法: {algorithm}")
            
            # 將消息和密鑰轉換為字節
            message_bytes = message.encode(encoding)
            key_bytes = key.encode(encoding)
            
            # 生成 HMAC
            hmac_obj = hmac.new(key_bytes, message_bytes, algorithm)
            
            return hmac_obj.hexdigest()
        except Exception as e:
            raise Exception(f"HMAC 生成失敗: {str(e)}")
    
    def verify_hmac(self, message: str, key: str, expected_hmac: str, algorithm: str = 'sha256', encoding: str = 'utf-8') -> bool:
        """驗證 HMAC"""
        try:
            calculated_hmac = self.hmac_hash(message, key, algorithm, encoding)
            return hmac.compare_digest(calculated_hmac, expected_hmac)
        except Exception as e:
            raise Exception(f"HMAC 驗證失敗: {str(e)}")
    
    def generate_salt(self, length: int = 32) -> str:
        """生成隨機鹽值"""
        try:
            return secrets.token_hex(length)
        except Exception as e:
            raise Exception(f"鹽值生成失敗: {str(e)}")
    
    def hash_with_salt(self, text: str, salt: Optional[str] = None, algorithm: str = 'sha256', encoding: str = 'utf-8') -> dict:
        """使用鹽值進行哈希計算"""
        try:
            if salt is None:
                salt = self.generate_salt()
            
            # 組合文本和鹽值
            salted_text = text + salt
            
            # 計算哈希
            hash_value = self.hash_text(salted_text, algorithm, encoding)
            
            return {
                "hash": hash_value,
                "salt": salt,
                "algorithm": algorithm
            }
        except Exception as e:
            raise Exception(f"鹽值哈希計算失敗: {str(e)}")
    
    def verify_salted_hash(self, text: str, salt: str, expected_hash: str, algorithm: str = 'sha256', encoding: str = 'utf-8') -> bool:
        """驗證帶鹽值的哈希"""
        try:
            salted_text = text + salt
            calculated_hash = self.hash_text(salted_text, algorithm, encoding)
            return calculated_hash.lower() == expected_hash.lower()
        except Exception as e:
            raise Exception(f"鹽值哈希驗證失敗: {str(e)}")
    
    def multi_hash(self, text: str, algorithms: list = None, encoding: str = 'utf-8') -> dict:
        """使用多種算法同時計算哈希"""
        try:
            if algorithms is None:
                algorithms = ['md5', 'sha1', 'sha256', 'sha512']
            
            results = {}
            for algorithm in algorithms:
                if algorithm.lower() in self.supported_algorithms:
                    try:
                        results[algorithm] = self.hash_text(text, algorithm, encoding)
                    except Exception as e:
                        results[algorithm] = f"錯誤: {str(e)}"
                else:
                    results[algorithm] = f"不支持的算法: {algorithm}"
            
            return results
        except Exception as e:
            raise Exception(f"多重哈希計算失敗: {str(e)}")
    
    def hash_iterations(self, text: str, iterations: int = 1000, algorithm: str = 'sha256', encoding: str = 'utf-8') -> str:
        """進行多次迭代哈希計算（用於密碼存儲等安全場景）"""
        try:
            if iterations < 1:
                raise ValueError("迭代次數必須大於 0")
            
            algorithm = algorithm.lower()
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"不支持的哈希算法: {algorithm}")
            
            result = text.encode(encoding)
            
            for _ in range(iterations):
                hash_obj = hashlib.new(algorithm)
                hash_obj.update(result)
                result = hash_obj.digest()
            
            return result.hex()
        except Exception as e:
            raise Exception(f"迭代哈希計算失敗: {str(e)}")
    
    def get_hash_info(self, algorithm: str) -> dict:
        """獲取哈希算法信息"""
        try:
            algorithm = algorithm.lower()
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"不支持的哈希算法: {algorithm}")
            
            hash_obj = hashlib.new(algorithm)
            
            return {
                "algorithm": algorithm,
                "digest_size": hash_obj.digest_size,
                "digest_size_bits": hash_obj.digest_size * 8,
                "block_size": hash_obj.block_size if hasattr(hash_obj, 'block_size') else None,
                "name": hash_obj.name
            }
        except Exception as e:
            raise Exception(f"獲取哈希算法信息失敗: {str(e)}")
    
    def crunch_hash(self, data: Union[str, bytes], salt: Optional[str] = None, iterations: int = 10000, algorithm: str = 'sha256') -> dict:
        """Crunch Hash - 高強度哈希處理，結合鹽值和多次迭代"""
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            if salt is None:
                salt = self.generate_salt(32)
            
            # 組合數據和鹽值
            salted_data = data + salt.encode('utf-8')
            
            # 多次迭代哈希
            result = salted_data
            for _ in range(iterations):
                hash_obj = hashlib.new(algorithm)
                hash_obj.update(result)
                result = hash_obj.digest()
            
            final_hash = result.hex()
            
            return {
                "hash": final_hash,
                "salt": salt,
                "iterations": iterations,
                "algorithm": algorithm,
                "strength": "high"
            }
        except Exception as e:
            raise Exception(f"Crunch Hash 計算失敗: {str(e)}")
    
    def verify_crunch_hash(self, data: Union[str, bytes], stored_hash: str, salt: str, iterations: int = 10000, algorithm: str = 'sha256') -> bool:
        """驗證 Crunch Hash"""
        try:
            result = self.crunch_hash(data, salt, iterations, algorithm)
            return result["hash"].lower() == stored_hash.lower()
        except Exception as e:
            raise Exception(f"Crunch Hash 驗證失敗: {str(e)}") 