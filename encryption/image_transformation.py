from PIL import Image, ImageFilter, ImageEnhance
import io
import base64
from typing import Tuple, Optional

class ImageTransformation:
    """圖像變換類，提供各種圖像處理功能"""
    
    def __init__(self):
        self.supported_formats = ['JPEG', 'PNG', 'BMP', 'TIFF', 'WEBP']
        self.supported_filters = ['BLUR', 'CONTOUR', 'DETAIL', 'EDGE_ENHANCE', 'EMBOSS', 'SMOOTH']
    
    def _bytes_to_image(self, image_bytes: bytes) -> Image.Image:
        """將字節數據轉換為 PIL Image 對象"""
        return Image.open(io.BytesIO(image_bytes))
    
    def _image_to_bytes(self, image: Image.Image, format: str = 'PNG') -> bytes:
        """將 PIL Image 對象轉換為字節數據"""
        buffer = io.BytesIO()
        # 確保 RGB 模式用於 JPEG
        if format.upper() == 'JPEG' and image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        image.save(buffer, format=format.upper())
        return buffer.getvalue()
    
    def resize_image(self, image_bytes: bytes, width: int, height: int, maintain_aspect: bool = True) -> bytes:
        """調整圖像大小"""
        try:
            image = self._bytes_to_image(image_bytes)
            original_format = image.format or 'PNG'
            
            if maintain_aspect:
                # 保持縱橫比
                image.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                # 強制調整到指定尺寸
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            return self._image_to_bytes(image, original_format)
        except Exception as e:
            raise Exception(f"圖像大小調整失敗: {str(e)}")
    
    def rotate_image(self, image_bytes: bytes, angle: float, expand: bool = True) -> bytes:
        """旋轉圖像"""
        try:
            image = self._bytes_to_image(image_bytes)
            original_format = image.format or 'PNG'
            
            # 旋轉圖像
            rotated = image.rotate(angle, expand=expand, fillcolor='white')
            
            return self._image_to_bytes(rotated, original_format)
        except Exception as e:
            raise Exception(f"圖像旋轉失敗: {str(e)}")
    
    def crop_image(self, image_bytes: bytes, left: int, top: int, right: int, bottom: int) -> bytes:
        """裁剪圖像"""
        try:
            image = self._bytes_to_image(image_bytes)
            original_format = image.format or 'PNG'
            
            # 裁剪圖像
            cropped = image.crop((left, top, right, bottom))
            
            return self._image_to_bytes(cropped, original_format)
        except Exception as e:
            raise Exception(f"圖像裁剪失敗: {str(e)}")
    
    def apply_filter(self, image_bytes: bytes, filter_name: str) -> bytes:
        """應用圖像濾鏡"""
        try:
            image = self._bytes_to_image(image_bytes)
            original_format = image.format or 'PNG'
            
            filter_name = filter_name.upper()
            if filter_name not in self.supported_filters:
                raise ValueError(f"不支持的濾鏡: {filter_name}")
            
            # 應用濾鏡
            filter_map = {
                'BLUR': ImageFilter.BLUR,
                'CONTOUR': ImageFilter.CONTOUR,
                'DETAIL': ImageFilter.DETAIL,
                'EDGE_ENHANCE': ImageFilter.EDGE_ENHANCE,
                'EMBOSS': ImageFilter.EMBOSS,
                'SMOOTH': ImageFilter.SMOOTH
            }
            
            filtered = image.filter(filter_map[filter_name])
            
            return self._image_to_bytes(filtered, original_format)
        except Exception as e:
            raise Exception(f"濾鏡應用失敗: {str(e)}")
    
    def adjust_brightness(self, image_bytes: bytes, factor: float) -> bytes:
        """調整圖像亮度"""
        try:
            image = self._bytes_to_image(image_bytes)
            original_format = image.format or 'PNG'
            
            # 調整亮度 (1.0 = 原始亮度, >1.0 = 更亮, <1.0 = 更暗)
            enhancer = ImageEnhance.Brightness(image)
            enhanced = enhancer.enhance(factor)
            
            return self._image_to_bytes(enhanced, original_format)
        except Exception as e:
            raise Exception(f"亮度調整失敗: {str(e)}")
    
    def adjust_contrast(self, image_bytes: bytes, factor: float) -> bytes:
        """調整圖像對比度"""
        try:
            image = self._bytes_to_image(image_bytes)
            original_format = image.format or 'PNG'
            
            # 調整對比度 (1.0 = 原始對比度, >1.0 = 更高對比度, <1.0 = 更低對比度)
            enhancer = ImageEnhance.Contrast(image)
            enhanced = enhancer.enhance(factor)
            
            return self._image_to_bytes(enhanced, original_format)
        except Exception as e:
            raise Exception(f"對比度調整失敗: {str(e)}")
    
    def convert_format(self, image_bytes: bytes, target_format: str) -> bytes:
        """轉換圖像格式"""
        try:
            image = self._bytes_to_image(image_bytes)
            target_format = target_format.upper()
            
            if target_format not in self.supported_formats:
                raise ValueError(f"不支持的格式: {target_format}")
            
            return self._image_to_bytes(image, target_format)
        except Exception as e:
            raise Exception(f"格式轉換失敗: {str(e)}")
    
    def get_image_info(self, image_bytes: bytes) -> dict:
        """獲取圖像信息"""
        try:
            image = self._bytes_to_image(image_bytes)
            
            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "size_bytes": len(image_bytes),
                "has_transparency": image.mode in ('RGBA', 'LA', 'P')
            }
        except Exception as e:
            raise Exception(f"獲取圖像信息失敗: {str(e)}")
    
    def create_thumbnail(self, image_bytes: bytes, size: Tuple[int, int] = (128, 128)) -> bytes:
        """創建縮略圖"""
        try:
            image = self._bytes_to_image(image_bytes)
            original_format = image.format or 'PNG'
            
            # 創建縮略圖
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            return self._image_to_bytes(image, original_format)
        except Exception as e:
            raise Exception(f"縮略圖創建失敗: {str(e)}") 