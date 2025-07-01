import gzip
import zlib
import bz2
import lzma
import base64
from typing import Union

class TextCompression:
    """文本壓縮類，支持多種壓縮算法"""
    
    def __init__(self):
        self.supported_algorithms = ['gzip', 'zlib', 'bz2', 'lzma']
    
    def _compress_gzip(self, data: bytes, level: int = 6) -> bytes:
        """使用 gzip 壓縮數據"""
        return gzip.compress(data, compresslevel=level)
    
    def _decompress_gzip(self, data: bytes) -> bytes:
        """使用 gzip 解壓數據"""
        return gzip.decompress(data)
    
    def _compress_zlib(self, data: bytes, level: int = 6) -> bytes:
        """使用 zlib 壓縮數據"""
        return zlib.compress(data, level=level)
    
    def _decompress_zlib(self, data: bytes) -> bytes:
        """使用 zlib 解壓數據"""
        return zlib.decompress(data)
    
    def _compress_bz2(self, data: bytes, level: int = 9) -> bytes:
        """使用 bz2 壓縮數據"""
        return bz2.compress(data, compresslevel=level)
    
    def _decompress_bz2(self, data: bytes) -> bytes:
        """使用 bz2 解壓數據"""
        return bz2.decompress(data)
    
    def _compress_lzma(self, data: bytes, level: int = 6) -> bytes:
        """使用 lzma 壓縮數據"""
        return lzma.compress(data, preset=level)
    
    def _decompress_lzma(self, data: bytes) -> bytes:
        """使用 lzma 解壓數據"""
        return lzma.decompress(data)
    
    def compress_text(self, text: str, algorithm: str = 'gzip', level: int = 6) -> str:
        """壓縮文本"""
        try:
            algorithm = algorithm.lower()
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"不支持的壓縮算法: {algorithm}")
            
            # 將文本轉換為字節
            text_bytes = text.encode('utf-8')
            
            # 根據算法壓縮
            if algorithm == 'gzip':
                compressed_data = self._compress_gzip(text_bytes, level)
            elif algorithm == 'zlib':
                compressed_data = self._compress_zlib(text_bytes, level)
            elif algorithm == 'bz2':
                compressed_data = self._compress_bz2(text_bytes, level)
            elif algorithm == 'lzma':
                compressed_data = self._compress_lzma(text_bytes, level)
            
            # 編碼為 base64
            encoded_data = base64.b64encode(compressed_data).decode('utf-8')
            
            return encoded_data
        except Exception as e:
            raise Exception(f"文本壓縮失敗: {str(e)}")
    
    def decompress_text(self, compressed_text: str, algorithm: str = 'gzip') -> str:
        """解壓文本"""
        try:
            algorithm = algorithm.lower()
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"不支持的壓縮算法: {algorithm}")
            
            # 解碼 base64
            compressed_data = base64.b64decode(compressed_text.encode('utf-8'))
            
            # 根據算法解壓
            if algorithm == 'gzip':
                decompressed_data = self._decompress_gzip(compressed_data)
            elif algorithm == 'zlib':
                decompressed_data = self._decompress_zlib(compressed_data)
            elif algorithm == 'bz2':
                decompressed_data = self._decompress_bz2(compressed_data)
            elif algorithm == 'lzma':
                decompressed_data = self._decompress_lzma(compressed_data)
            
            # 轉換為字符串
            result = decompressed_data.decode('utf-8')
            
            return result
        except Exception as e:
            raise Exception(f"文本解壓失敗: {str(e)}")
    
    def get_compression_stats(self, text: str, algorithm: str = 'gzip', level: int = 6) -> dict:
        """獲取壓縮統計信息"""
        try:
            original_size = len(text.encode('utf-8'))
            compressed_text = self.compress_text(text, algorithm, level)
            compressed_size = len(base64.b64decode(compressed_text.encode('utf-8')))
            
            compression_ratio = compressed_size / original_size if original_size > 0 else 0
            space_saved = original_size - compressed_size
            space_saved_percent = (space_saved / original_size) * 100 if original_size > 0 else 0
            
            return {
                "original_size_bytes": original_size,
                "compressed_size_bytes": compressed_size,
                "compression_ratio": round(compression_ratio, 4),
                "space_saved_bytes": space_saved,
                "space_saved_percent": round(space_saved_percent, 2),
                "algorithm": algorithm,
                "compression_level": level
            }
        except Exception as e:
            raise Exception(f"獲取壓縮統計失敗: {str(e)}")
    
    def compare_algorithms(self, text: str, level: int = 6) -> dict:
        """比較不同壓縮算法的效果"""
        try:
            results = {}
            original_size = len(text.encode('utf-8'))
            
            for algorithm in self.supported_algorithms:
                try:
                    compressed_text = self.compress_text(text, algorithm, level)
                    compressed_size = len(base64.b64decode(compressed_text.encode('utf-8')))
                    compression_ratio = compressed_size / original_size if original_size > 0 else 0
                    space_saved_percent = ((original_size - compressed_size) / original_size) * 100 if original_size > 0 else 0
                    
                    results[algorithm] = {
                        "compressed_size_bytes": compressed_size,
                        "compression_ratio": round(compression_ratio, 4),
                        "space_saved_percent": round(space_saved_percent, 2)
                    }
                except Exception as e:
                    results[algorithm] = {"error": str(e)}
            
            return {
                "original_size_bytes": original_size,
                "algorithms": results
            }
        except Exception as e:
            raise Exception(f"算法比較失敗: {str(e)}")
    
    def compress_file_content(self, file_content: bytes, algorithm: str = 'gzip', level: int = 6) -> bytes:
        """壓縮文件內容（字節數據）"""
        try:
            algorithm = algorithm.lower()
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"不支持的壓縮算法: {algorithm}")
            
            # 根據算法壓縮
            if algorithm == 'gzip':
                return self._compress_gzip(file_content, level)
            elif algorithm == 'zlib':
                return self._compress_zlib(file_content, level)
            elif algorithm == 'bz2':
                return self._compress_bz2(file_content, level)
            elif algorithm == 'lzma':
                return self._compress_lzma(file_content, level)
                
        except Exception as e:
            raise Exception(f"文件內容壓縮失敗: {str(e)}")
    
    def decompress_file_content(self, compressed_content: bytes, algorithm: str = 'gzip') -> bytes:
        """解壓文件內容（字節數據）"""
        try:
            algorithm = algorithm.lower()
            if algorithm not in self.supported_algorithms:
                raise ValueError(f"不支持的壓縮算法: {algorithm}")
            
            # 根據算法解壓
            if algorithm == 'gzip':
                return self._decompress_gzip(compressed_content)
            elif algorithm == 'zlib':
                return self._decompress_zlib(compressed_content)
            elif algorithm == 'bz2':
                return self._decompress_bz2(compressed_content)
            elif algorithm == 'lzma':
                return self._decompress_lzma(compressed_content)
                
        except Exception as e:
            raise Exception(f"文件內容解壓失敗: {str(e)}") 