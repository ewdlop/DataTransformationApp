import io
import base64
from PIL import Image
import json

class QRCodeGenerator:
    """QR碼生成器類，支持生成和讀取QR碼"""
    
    def __init__(self):
        self.error_corrections = {
            'L': 'low',      # 約7%的錯誤修正能力
            'M': 'medium',   # 約15%的錯誤修正能力（默認）
            'Q': 'quartile', # 約25%的錯誤修正能力
            'H': 'high'      # 約30%的錯誤修正能力
        }
    
    def generate_qr_code(self, 
                        data: str, 
                        error_correction: str = 'M',
                        box_size: int = 10,
                        border: int = 4,
                        fill_color: str = 'black',
                        back_color: str = 'white') -> bytes:
        """生成QR碼圖像"""
        try:
            import qrcode
            from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
            
            # 設置錯誤修正級別
            error_correct_map = {
                'L': ERROR_CORRECT_L,
                'M': ERROR_CORRECT_M,
                'Q': ERROR_CORRECT_Q,
                'H': ERROR_CORRECT_H
            }
            
            if error_correction not in error_correct_map:
                raise ValueError(f"不支持的錯誤修正級別: {error_correction}")
            
            # 創建QR碼實例
            qr = qrcode.QRCode(
                version=1,  # 控制QR碼的大小，1是最小的
                error_correction=error_correct_map[error_correction],
                box_size=box_size,
                border=border,
            )
            
            # 添加數據
            qr.add_data(data)
            qr.make(fit=True)
            
            # 創建圖像
            qr_image = qr.make_image(fill_color=fill_color, back_color=back_color)
            
            # 轉換為字節
            buffer = io.BytesIO()
            qr_image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except ImportError:
            raise Exception("需要安裝 qrcode 庫: pip install qrcode[pil]")
        except Exception as e:
            raise Exception(f"QR碼生成失敗: {str(e)}")
    
    def generate_qr_with_logo(self, 
                             data: str, 
                             logo_data: bytes,
                             error_correction: str = 'H',
                             box_size: int = 10,
                             border: int = 4) -> bytes:
        """生成帶Logo的QR碼"""
        try:
            import qrcode
            from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
            
            error_correct_map = {
                'L': ERROR_CORRECT_L,
                'M': ERROR_CORRECT_M,
                'Q': ERROR_CORRECT_Q,
                'H': ERROR_CORRECT_H
            }
            
            # 創建QR碼
            qr = qrcode.QRCode(
                version=1,
                error_correction=error_correct_map[error_correction],
                box_size=box_size,
                border=border,
            )
            
            qr.add_data(data)
            qr.make(fit=True)
            
            # 創建QR碼圖像
            qr_image = qr.make_image(fill_color="black", back_color="white").convert('RGBA')
            
            # 載入Logo
            logo = Image.open(io.BytesIO(logo_data)).convert('RGBA')
            
            # 計算Logo大小（不超過QR碼的1/5）
            qr_width, qr_height = qr_image.size
            logo_size = min(qr_width, qr_height) // 5
            
            # 調整Logo大小
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # 計算Logo位置（居中）
            logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
            
            # 在Logo背景添加白色圓形背景
            background = Image.new('RGBA', (logo_size + 20, logo_size + 20), (255, 255, 255, 255))
            background_pos = ((qr_width - logo_size - 20) // 2, (qr_height - logo_size - 20) // 2)
            
            # 合成圖像
            qr_image.paste(background, background_pos, background)
            qr_image.paste(logo, logo_pos, logo)
            
            # 轉換為字節
            buffer = io.BytesIO()
            qr_image.save(buffer, format='PNG')
            return buffer.getvalue()
            
        except ImportError:
            raise Exception("需要安裝 qrcode 庫: pip install qrcode[pil]")
        except Exception as e:
            raise Exception(f"帶Logo的QR碼生成失敗: {str(e)}")
    
    def read_qr_code(self, image_data: bytes) -> dict:
        """讀取QR碼內容"""
        try:
            from pyzbar import pyzbar
            import numpy as np
            
            # 載入圖像
            image = Image.open(io.BytesIO(image_data))
            
            # 轉換為RGB模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 轉換為numpy數組
            image_array = np.array(image)
            
            # 解碼QR碼
            decoded_objects = pyzbar.decode(image_array)
            
            if not decoded_objects:
                return {
                    "success": False,
                    "message": "未檢測到QR碼",
                    "qr_codes": []
                }
            
            qr_codes = []
            for obj in decoded_objects:
                qr_info = {
                    "data": obj.data.decode('utf-8'),
                    "type": obj.type,
                    "quality": obj.quality if hasattr(obj, 'quality') else None,
                    "rect": {
                        "left": obj.rect.left,
                        "top": obj.rect.top,
                        "width": obj.rect.width,
                        "height": obj.rect.height
                    },
                    "polygon": [(point.x, point.y) for point in obj.polygon]
                }
                qr_codes.append(qr_info)
            
            return {
                "success": True,
                "message": f"成功解碼 {len(qr_codes)} 個QR碼",
                "qr_codes": qr_codes
            }
            
        except ImportError:
            raise Exception("需要安裝 pyzbar 庫: pip install pyzbar")
        except Exception as e:
            raise Exception(f"QR碼讀取失敗: {str(e)}")
    
    def generate_wifi_qr(self, ssid: str, password: str, security: str = 'WPA', hidden: bool = False) -> bytes:
        """生成WiFi連接QR碼"""
        try:
            # WiFi QR碼格式: WIFI:T:WPA;S:mynetwork;P:mypass;H:false;;
            wifi_string = f"WIFI:T:{security};S:{ssid};P:{password};H:{'true' if hidden else 'false'};;"
            
            return self.generate_qr_code(wifi_string, error_correction='M')
            
        except Exception as e:
            raise Exception(f"WiFi QR碼生成失敗: {str(e)}")
    
    def generate_contact_qr(self, contact_info: dict) -> bytes:
        """生成聯絡人QR碼"""
        try:
            # vCard格式
            vcard = "BEGIN:VCARD\nVERSION:3.0\n"
            
            if 'name' in contact_info:
                vcard += f"FN:{contact_info['name']}\n"
            
            if 'phone' in contact_info:
                vcard += f"TEL:{contact_info['phone']}\n"
            
            if 'email' in contact_info:
                vcard += f"EMAIL:{contact_info['email']}\n"
            
            if 'org' in contact_info:
                vcard += f"ORG:{contact_info['org']}\n"
            
            if 'url' in contact_info:
                vcard += f"URL:{contact_info['url']}\n"
            
            vcard += "END:VCARD"
            
            return self.generate_qr_code(vcard, error_correction='M')
            
        except Exception as e:
            raise Exception(f"聯絡人QR碼生成失敗: {str(e)}")
    
    def generate_url_qr(self, url: str) -> bytes:
        """生成URL QR碼"""
        try:
            return self.generate_qr_code(url, error_correction='M')
        except Exception as e:
            raise Exception(f"URL QR碼生成失敗: {str(e)}")
    
    def generate_text_qr(self, text: str) -> bytes:
        """生成純文本QR碼"""
        try:
            return self.generate_qr_code(text, error_correction='M')
        except Exception as e:
            raise Exception(f"文本QR碼生成失敗: {str(e)}")
    
    def get_qr_info(self, data: str) -> dict:
        """分析QR碼數據並返回信息"""
        try:
            import qrcode
            
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M)
            qr.add_data(data)
            qr.make(fit=True)
            
            return {
                "data_length": len(data),
                "version": qr.version,
                "error_correction": "M",
                "estimated_capacity": {
                    "numeric": qr.data_list[0].get_length() if qr.data_list else 0,
                    "alphanumeric": qr.data_list[0].get_length() if qr.data_list else 0,
                    "byte": qr.data_list[0].get_length() if qr.data_list else 0
                },
                "modules_count": qr.modules_count,
                "data_type": self._detect_data_type(data)
            }
            
        except ImportError:
            raise Exception("需要安裝 qrcode 庫")
        except Exception as e:
            raise Exception(f"QR碼信息分析失敗: {str(e)}")
    
    def _detect_data_type(self, data: str) -> str:
        """檢測數據類型"""
        data_lower = data.lower()
        
        if data_lower.startswith('http://') or data_lower.startswith('https://'):
            return 'URL'
        elif data_lower.startswith('mailto:'):
            return 'Email'
        elif data_lower.startswith('tel:'):
            return 'Phone'
        elif data_lower.startswith('wifi:'):
            return 'WiFi'
        elif data_lower.startswith('begin:vcard'):
            return 'Contact'
        elif data_lower.startswith('geo:'):
            return 'Location'
        elif data.isdigit():
            return 'Numeric'
        else:
            return 'Text'
    
    def batch_generate_qr_codes(self, data_list: list) -> list:
        """批量生成QR碼"""
        try:
            results = []
            
            for i, data in enumerate(data_list):
                try:
                    qr_image = self.generate_qr_code(data)
                    results.append({
                        "index": i,
                        "success": True,
                        "data": data,
                        "qr_code": base64.b64encode(qr_image).decode('utf-8'),
                        "size": len(qr_image)
                    })
                except Exception as e:
                    results.append({
                        "index": i,
                        "success": False,
                        "data": data,
                        "error": str(e)
                    })
            
            return results
            
        except Exception as e:
            raise Exception(f"批量生成QR碼失敗: {str(e)}") 