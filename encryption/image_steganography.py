from PIL import Image
import io
import os

class ImageSteganography:
    """圖像隱寫術類，用於在圖像中隱藏和提取文本信息"""
    
    def __init__(self):
        self.delimiter = "###END###"  # 用於標記隱藏文本的結束
        
    def _text_to_binary(self, text: str) -> str:
        """將文本轉換為二進制字符串"""
        binary = ''.join(format(ord(char), '08b') for char in text)
        return binary
    
    def _binary_to_text(self, binary: str) -> str:
        """將二進制字符串轉換為文本"""
        text = ''
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                text += chr(int(byte, 2))
        return text
    
    def _bytes_to_image(self, image_bytes: bytes) -> Image.Image:
        """將字節數據轉換為 PIL Image 對象"""
        return Image.open(io.BytesIO(image_bytes))
    
    def _image_to_bytes(self, image: Image.Image, format: str = 'PNG') -> bytes:
        """將 PIL Image 對象轉換為字節數據"""
        buffer = io.BytesIO()
        # 確保使用 PNG 格式以保持質量
        if format.upper() != 'PNG':
            format = 'PNG'
        image.save(buffer, format=format)
        return buffer.getvalue()
    
    def hide_text_lsb(self, image_bytes: bytes, secret_text: str, encrypt_text: bool = False, password: str = None) -> bytes:
        """使用 LSB (Least Significant Bit) 方法在圖像中隱藏文本"""
        try:
            # 如果選擇加密，先加密文本
            if encrypt_text and password:
                from .text_encryption import TextEncryption
                text_crypto = TextEncryption()
                secret_text = text_crypto.encrypt(secret_text, password)
                secret_text = f"ENCRYPTED:{secret_text}"
            
            # 添加結束標記
            secret_text += self.delimiter
            
            # 轉換為二進制
            binary_secret = self._text_to_binary(secret_text)
            
            # 載入圖像
            image = self._bytes_to_image(image_bytes)
            
            # 確保圖像是 RGB 模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 獲取圖像尺寸
            width, height = image.size
            
            # 檢查圖像是否足夠大來隱藏文本
            max_bits = width * height * 3  # 每個像素3個通道 (R, G, B)
            if len(binary_secret) > max_bits:
                raise ValueError(f"圖像太小，無法隱藏 {len(binary_secret)} 位數據。最大容量: {max_bits} 位")
            
            # 載入像素數據
            pixels = list(image.getdata())
            
            binary_index = 0
            modified_pixels = []
            
            for pixel in pixels:
                r, g, b = pixel
                
                # 修改紅色通道的 LSB
                if binary_index < len(binary_secret):
                    r = (r & 0xFE) | int(binary_secret[binary_index]) # 0xFE 是 11111110，保留其他位，只修改最低 
                    binary_index += 1
                
                # 修改綠色通道的 LSB
                if binary_index < len(binary_secret):
                    g = (g & 0xFE) | int(binary_secret[binary_index]) # 0xFE 是 11111110，保留其他位，只修改最低 
                    binary_index += 1
                
                # 修改藍色通道的 LSB
                if binary_index < len(binary_secret):
                    b = (b & 0xFE) | int(binary_secret[binary_index]) # 0xFE 是 11111110，保留其他位，只修改最低 
                    binary_index += 1
                
                modified_pixels.append((r, g, b))
                
                # 如果所有位都已隱藏，可以提前結束
                if binary_index >= len(binary_secret):
                    # 添加剩餘未修改的像素
                    remaining_pixels = pixels[len(modified_pixels):]
                    modified_pixels.extend(remaining_pixels)
                    break
            
            # 創建新圖像
            new_image = Image.new('RGB', (width, height))
            new_image.putdata(modified_pixels)
            
            return self._image_to_bytes(new_image, 'PNG')
            
        except Exception as e:
            raise Exception(f"隱藏文本失敗: {str(e)}")
    
    def extract_text_lsb(self, image_bytes: bytes, is_encrypted: bool = False, password: str = None) -> str:
        """使用 LSB 方法從圖像中提取隱藏的文本"""
        try:
            # 載入圖像
            image = self._bytes_to_image(image_bytes)
            
            # 確保圖像是 RGB 模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 載入像素數據
            pixels = list(image.getdata())
            
            binary_secret = ""
            
            for pixel in pixels:
                r, g, b = pixel
                
                # 提取每個通道的 LSB
                binary_secret += str(r & 1)
                binary_secret += str(g & 1)
                binary_secret += str(b & 1)
            
            # 轉換為文本
            extracted_text = self._binary_to_text(binary_secret)
            
            # 查找結束標記
            if self.delimiter in extracted_text:
                extracted_text = extracted_text.split(self.delimiter)[0]
            else:
                raise ValueError("未找到有效的隱藏文本或文本已損壞")
            
            # 如果文本是加密的，進行解密
            if extracted_text.startswith("ENCRYPTED:"):
                if not is_encrypted or not password:
                    raise ValueError("檢測到加密文本，但未提供密碼")
                
                encrypted_text = extracted_text[10:]  # 移除 "ENCRYPTED:" 前綴
                from .text_encryption import TextEncryption
                text_crypto = TextEncryption()
                extracted_text = text_crypto.decrypt(encrypted_text, password)
            
            return extracted_text
            
        except Exception as e:
            raise Exception(f"提取文本失敗: {str(e)}")
    
    def hide_text_dct(self, image_bytes: bytes, secret_text: str, strength: float = 10.0) -> bytes:
        """使用改進的 DCT (Discrete Cosine Transform) 方法隱藏文本"""
        try:
            import numpy as np
            from scipy import fftpack
            
            # 添加結束標記
            secret_text += self.delimiter
            binary_secret = self._text_to_binary(secret_text)
            
            # 載入圖像
            image = self._bytes_to_image(image_bytes)
            
            # 轉換為灰度圖像以簡化處理
            if image.mode != 'L':
                image = image.convert('L')
            
            # 轉換為 numpy 數組
            img_array = np.array(image, dtype=np.float64)  # 使用 float64 提高精度
            
            # 獲取圖像尺寸
            height, width = img_array.shape
            
            # 檢查是否有足夠空間
            max_capacity = (height // 8) * (width // 8)
            if len(binary_secret) > max_capacity:
                raise ValueError(f"文本太長，無法隱藏。最大容量: {max_capacity} 位")
            
            # 處理 8x8 塊
            binary_index = 0
            
            for i in range(0, height - 7, 8):  # 確保不越界
                for j in range(0, width - 7, 8):
                    if binary_index >= len(binary_secret):
                        break
                    
                    # 提取 8x8 塊
                    block = img_array[i:i+8, j:j+8].copy()
                    
                    # 應用 DCT
                    dct_block = fftpack.dctn(block, norm='ortho')
                    
                    # 在低頻區域的特定位置隱藏數據（避免 DC 分量）
                    coeff_pos = (2, 3)  # 選擇低頻但非 DC 的位置
                    original_coeff = dct_block[coeff_pos]
                    
                    # 量化嵌入：將係數量化到特定範圍
                    quantization_step = strength * 2
                    
                    if binary_secret[binary_index] == '1':
                        # 嵌入 1：使係數在奇數量化區間
                        quantized = np.round(original_coeff / quantization_step)
                        if quantized % 2 == 0:
                            quantized += 1
                    else:
                        # 嵌入 0：使係數在偶數量化區間
                        quantized = np.round(original_coeff / quantization_step)
                        if quantized % 2 == 1:
                            quantized += 1 if quantized >= 0 else -1
                    
                    dct_block[coeff_pos] = quantized * quantization_step
                    
                    # 應用逆 DCT
                    idct_block = fftpack.idctn(dct_block, norm='ortho')
                    
                    # 確保值在有效範圍內
                    idct_block = np.clip(idct_block, 0, 255)
                    
                    # 更新圖像塊
                    img_array[i:i+8, j:j+8] = idct_block
                    
                    binary_index += 1
                
                if binary_index >= len(binary_secret):
                    break
            
            # 轉換回圖像
            new_image = Image.fromarray(img_array.astype(np.uint8), 'L')
            
            return self._image_to_bytes(new_image, 'PNG')
            
        except ImportError:
            raise Exception("DCT 方法需要安裝 numpy 和 scipy 庫")
        except Exception as e:
            raise Exception(f"DCT 隱藏文本失敗: {str(e)}")
    
    def extract_text_dct(self, image_bytes: bytes, strength: float = 10.0) -> str:
        """使用改進的 DCT 方法提取隱藏的文本"""
        try:
            import numpy as np
            from scipy import fftpack
            
            # 載入圖像
            image = self._bytes_to_image(image_bytes)
            
            # 轉換為灰度圖像
            if image.mode != 'L':
                image = image.convert('L')
            
            # 轉換為 numpy 數組
            img_array = np.array(image, dtype=np.float64)  # 使用 float64 提高精度
            
            # 獲取圖像尺寸
            height, width = img_array.shape
            
            binary_secret = ""
            
            # 處理 8x8 塊
            for i in range(0, height - 7, 8):  # 確保不越界
                for j in range(0, width - 7, 8):
                    # 提取 8x8 塊
                    block = img_array[i:i+8, j:j+8]
                    
                    # 應用 DCT
                    dct_block = fftpack.dctn(block, norm='ortho')
                    
                    # 從相同位置提取數據
                    coeff_pos = (2, 3)
                    coeff_value = dct_block[coeff_pos]
                    
                    # 量化解析
                    quantization_step = strength * 2
                    quantized = np.round(coeff_value / quantization_step)
                    
                    # 根據奇偶性判斷隱藏的位
                    if quantized % 2 == 1:
                        binary_secret += '1'
                    else:
                        binary_secret += '0'
            
            # 轉換為文本
            extracted_text = self._binary_to_text(binary_secret)
            
            # 查找結束標記
            if self.delimiter in extracted_text:
                extracted_text = extracted_text.split(self.delimiter)[0]
            else:
                # 如果沒有找到完整的結束標記，嘗試找到可讀的文本部分
                # 移除不可打印字符
                clean_text = ''.join(char for char in extracted_text if ord(char) >= 32 and ord(char) <= 126 or ord(char) >= 19968)
                if len(clean_text) > 0:
                    return clean_text
                raise ValueError("未找到有效的隱藏文本或文本已損壞")
            
            return extracted_text
            
        except ImportError:
            raise Exception("DCT 方法需要安裝 numpy 和 scipy 庫")
        except Exception as e:
            raise Exception(f"DCT 提取文本失敗: {str(e)}")
    
    def check_capacity(self, image_bytes: bytes, method: str = 'lsb') -> dict:
        """檢查圖像的隱藏容量"""
        try:
            image = self._bytes_to_image(image_bytes)
            width, height = image.size
            
            if method.lower() == 'lsb':
                # LSB 方法：每個像素的每個通道可以隱藏 1 位
                if image.mode == 'RGB':
                    max_bits = width * height * 3
                elif image.mode == 'RGBA':
                    max_bits = width * height * 4
                else:
                    max_bits = width * height
            elif method.lower() == 'dct':
                # DCT 方法：每個 8x8 塊可以隱藏 1 位
                max_bits = (height // 8) * (width // 8)
            else:
                raise ValueError(f"不支持的方法: {method}")
            
            max_chars = max_bits // 8  # 每個字符需要 8 位
            
            return {
                "image_size": f"{width}x{height}",
                "method": method,
                "max_bits": max_bits,
                "max_characters": max_chars,
                "max_text_length": max_chars - len(self.delimiter)  # 減去結束標記的長度
            }
            
        except Exception as e:
            raise Exception(f"檢查容量失敗: {str(e)}")
    
    def detect_hidden_text(self, image_bytes: bytes, method: str = 'lsb') -> dict:
        """檢測圖像中是否隱藏有文本"""
        try:
            if method.lower() == 'lsb':
                try:
                    text = self.extract_text_lsb(image_bytes)
                    return {
                        "has_hidden_text": True,
                        "method": "lsb",
                        "text_length": len(text),
                        "preview": text[:50] + "..." if len(text) > 50 else text
                    }
                except:
                    return {
                        "has_hidden_text": False,
                        "method": "lsb",
                        "message": "未檢測到隱藏文本"
                    }
            elif method.lower() == 'dct':
                try:
                    text = self.extract_text_dct(image_bytes)
                    return {
                        "has_hidden_text": True,
                        "method": "dct",
                        "text_length": len(text),
                        "preview": text[:50] + "..." if len(text) > 50 else text
                    }
                except:
                    return {
                        "has_hidden_text": False,
                        "method": "dct",
                        "message": "未檢測到隱藏文本"
                    }
            else:
                raise ValueError(f"不支持的檢測方法: {method}")
                
        except Exception as e:
            raise Exception(f"檢測隱藏文本失敗: {str(e)}") 