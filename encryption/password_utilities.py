import random
import string
import secrets
import re
import math
from typing import List, Dict
import unicodedata

class PasswordUtilities:
    """密碼工具類，提供密碼生成、強度檢查等功能"""
    
    def __init__(self):
        self.common_passwords = {
            '123456', 'password', '123456789', '12345678', '12345', '1234567',
            'qwerty', 'abc123', 'password123', 'admin', '1234567890', 'welcome',
            'monkey', 'login', 'admin123', 'princess', 'solo', 'master', 'hello',
            'charlie', 'aa123456', 'donald', 'password1', 'qwerty123'
        }
        
        self.keyboard_patterns = [
            'qwerty', 'asdfgh', 'zxcvbn', '123456', '654321', 'qwertyuiop',
            'asdfghjkl', 'zxcvbnm', '1qaz2wsx', '1q2w3e4r', 'qweasd'
        ]
        
    def generate_password(self, 
                         length: int = 12, 
                         include_uppercase: bool = True,
                         include_lowercase: bool = True, 
                         include_numbers: bool = True,
                         include_symbols: bool = True,
                         exclude_ambiguous: bool = False,
                         exclude_similar: bool = False,
                         custom_symbols: str = None) -> dict:
        """生成安全密碼"""
        try:
            if length < 4:
                raise ValueError("密碼長度至少需要4個字符")
            
            if length > 128:
                raise ValueError("密碼長度不能超過128個字符")
            
            # 構建字符集
            charset = ""
            categories = []
            
            if include_lowercase:
                chars = string.ascii_lowercase
                if exclude_similar:
                    chars = chars.replace('l', '').replace('o', '')
                charset += chars
                categories.append(('lowercase', chars))
            
            if include_uppercase:
                chars = string.ascii_uppercase
                if exclude_similar:
                    chars = chars.replace('I', '').replace('O', '')
                charset += chars
                categories.append(('uppercase', chars))
            
            if include_numbers:
                chars = string.digits
                if exclude_ambiguous:
                    chars = chars.replace('0', '').replace('1', '')
                if exclude_similar:
                    chars = chars.replace('0', '').replace('1', '')
                charset += chars
                categories.append(('numbers', chars))
            
            if include_symbols:
                if custom_symbols:
                    chars = custom_symbols
                else:
                    chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
                    if exclude_ambiguous:
                        chars = chars.replace('|', '').replace('l', '').replace('1', '').replace('I', '')
                charset += chars
                categories.append(('symbols', chars))
            
            if not charset:
                raise ValueError("至少需要選擇一種字符類型")
            
            # 生成密碼，確保每個類別至少有一個字符
            password = []
            
            # 首先從每個類別中選一個字符
            for category_name, category_chars in categories:
                password.append(secrets.choice(category_chars))
            
            # 填充剩餘長度
            for _ in range(length - len(categories)):
                password.append(secrets.choice(charset))
            
            # 隨機打亂順序
            secrets.SystemRandom().shuffle(password)
            
            password_str = ''.join(password)
            
            # 分析生成的密碼
            analysis = self.analyze_password_strength(password_str)
            
            return {
                "password": password_str,
                "length": len(password_str),
                "charset_size": len(charset),
                "entropy_bits": analysis["entropy_bits"],
                "strength_score": analysis["strength_score"],
                "strength_level": analysis["strength_level"],
                "composition": {
                    "uppercase": sum(1 for c in password_str if c.isupper()),
                    "lowercase": sum(1 for c in password_str if c.islower()),
                    "numbers": sum(1 for c in password_str if c.isdigit()),
                    "symbols": sum(1 for c in password_str if not c.isalnum())
                }
            }
            
        except Exception as e:
            raise Exception(f"密碼生成失敗: {str(e)}")
    
    def analyze_password_strength(self, password: str) -> dict:
        """分析密碼強度"""
        try:
            analysis = {
                "password_length": len(password),
                "entropy_bits": 0,
                "strength_score": 0,
                "strength_level": "極弱",
                "issues": [],
                "suggestions": [],
                "composition": {},
                "patterns": {},
                "time_to_crack": {}
            }
            
            if not password:
                analysis["issues"].append("密碼為空")
                return analysis
            
            # 字符組成分析
            has_upper = bool(re.search(r'[A-Z]', password))
            has_lower = bool(re.search(r'[a-z]', password))
            has_digit = bool(re.search(r'\d', password))
            has_symbol = bool(re.search(r'[^A-Za-z0-9]', password))
            
            analysis["composition"] = {
                "uppercase_count": sum(1 for c in password if c.isupper()),
                "lowercase_count": sum(1 for c in password if c.islower()),
                "number_count": sum(1 for c in password if c.isdigit()),
                "symbol_count": sum(1 for c in password if not c.isalnum()),
                "has_uppercase": has_upper,
                "has_lowercase": has_lower,
                "has_numbers": has_digit,
                "has_symbols": has_symbol
            }
            
            # 計算字符集大小
            charset_size = 0
            if has_lower:
                charset_size += 26
            if has_upper:
                charset_size += 26
            if has_digit:
                charset_size += 10
            if has_symbol:
                charset_size += 32  # 估計符號數量
            
            # 計算熵值
            if charset_size > 0:
                analysis["entropy_bits"] = len(password) * math.log2(charset_size)
            
            # 強度評分計算
            score = 0
            
            # 長度分數
            length = len(password)
            if length >= 12:
                score += 25
            elif length >= 8:
                score += 20
            elif length >= 6:
                score += 10
            elif length >= 4:
                score += 5
            
            # 字符多樣性分數
            diversity_score = 0
            if has_upper:
                diversity_score += 5
            if has_lower:
                diversity_score += 5
            if has_digit:
                diversity_score += 5
            if has_symbol:
                diversity_score += 10
            score += diversity_score
            
            # 檢查常見密碼
            if password.lower() in self.common_passwords:
                score -= 30
                analysis["issues"].append("這是一個常見的弱密碼")
            
            # 檢查鍵盤模式
            password_lower = password.lower()
            for pattern in self.keyboard_patterns:
                if pattern in password_lower or pattern[::-1] in password_lower:
                    score -= 15
                    analysis["issues"].append(f"包含鍵盤模式: {pattern}")
                    break
            
            # 檢查重複字符
            char_counts = {}
            for char in password:
                char_counts[char] = char_counts.get(char, 0) + 1
            
            max_repeat = max(char_counts.values())
            repeat_ratio = max_repeat / len(password)
            
            if repeat_ratio > 0.5:
                score -= 20
                analysis["issues"].append("包含過多重複字符")
            elif repeat_ratio > 0.3:
                score -= 10
                analysis["issues"].append("包含較多重複字符")
            
            # 檢查順序字符（如123, abc）
            sequential_count = 0
            for i in range(len(password) - 2):
                if (ord(password[i+1]) == ord(password[i]) + 1 and 
                    ord(password[i+2]) == ord(password[i]) + 2):
                    sequential_count += 1
            
            if sequential_count > 0:
                score -= sequential_count * 5
                analysis["issues"].append("包含順序字符")
            
            # 檢查年份模式
            if re.search(r'(19|20)\d{2}', password):
                score -= 5
                analysis["issues"].append("包含年份模式")
            
            # 確保分數在0-100範圍內
            score = max(0, min(100, score))
            analysis["strength_score"] = score
            
            # 確定強度等級
            if score >= 80:
                analysis["strength_level"] = "非常強"
            elif score >= 60:
                analysis["strength_level"] = "強"
            elif score >= 40:
                analysis["strength_level"] = "中等"
            elif score >= 20:
                analysis["strength_level"] = "弱"
            else:
                analysis["strength_level"] = "極弱"
            
            # 生成建議
            if length < 8:
                analysis["suggestions"].append("增加密碼長度至少8個字符")
            if length < 12:
                analysis["suggestions"].append("建議密碼長度至少12個字符")
            
            if not has_upper:
                analysis["suggestions"].append("添加大寫字母")
            if not has_lower:
                analysis["suggestions"].append("添加小寫字母")
            if not has_digit:
                analysis["suggestions"].append("添加數字")
            if not has_symbol:
                analysis["suggestions"].append("添加特殊符號")
            
            if repeat_ratio > 0.3:
                analysis["suggestions"].append("減少重複字符的使用")
            
            # 計算破解時間估計
            if charset_size > 0:
                total_combinations = charset_size ** len(password)
                # 假設每秒10億次嘗試
                attempts_per_second = 1_000_000_000
                seconds_to_crack = total_combinations / (2 * attempts_per_second)  # 平均需要一半時間
                
                analysis["time_to_crack"] = self._format_crack_time(seconds_to_crack)
            
            analysis["patterns"] = {
                "max_repeat_char": max_repeat,
                "repeat_ratio": repeat_ratio,
                "sequential_patterns": sequential_count,
                "charset_size": charset_size
            }
            
            return analysis
            
        except Exception as e:
            raise Exception(f"密碼強度分析失敗: {str(e)}")
    
    def _format_crack_time(self, seconds: float) -> dict:
        """格式化破解時間"""
        if seconds < 1:
            return {"time": "瞬間", "value": seconds, "unit": "秒"}
        elif seconds < 60:
            return {"time": f"{seconds:.1f} 秒", "value": seconds, "unit": "秒"}
        elif seconds < 3600:
            minutes = seconds / 60
            return {"time": f"{minutes:.1f} 分鐘", "value": minutes, "unit": "分鐘"}
        elif seconds < 86400:
            hours = seconds / 3600
            return {"time": f"{hours:.1f} 小時", "value": hours, "unit": "小時"}
        elif seconds < 31536000:
            days = seconds / 86400
            return {"time": f"{days:.1f} 天", "value": days, "unit": "天"}
        elif seconds < 31536000 * 100:
            years = seconds / 31536000
            return {"time": f"{years:.1f} 年", "value": years, "unit": "年"}
        else:
            return {"time": "幾個世紀", "value": float('inf'), "unit": "世紀"}
    
    def generate_passphrase(self, word_count: int = 4, separator: str = "-", 
                           capitalize: bool = True, add_numbers: bool = False) -> dict:
        """生成密碼短語（基於詞典）"""
        try:
            # 簡單的詞典（實際應用中應該使用更大的詞典）
            words = [
                'apple', 'banana', 'cherry', 'dragon', 'eagle', 'forest', 'garden', 'happy',
                'island', 'jungle', 'kitten', 'lemon', 'mountain', 'nature', 'ocean', 'planet',
                'quiet', 'river', 'sunset', 'turtle', 'unique', 'valley', 'water', 'yellow',
                'zebra', 'bridge', 'castle', 'dream', 'energy', 'flower', 'guitar', 'harmony',
                'imagine', 'journey', 'kitchen', 'library', 'melody', 'notebook', 'orange', 'piano',
                'rainbow', 'silver', 'thunder', 'umbrella', 'violin', 'winter', 'crystal', 'butterfly'
            ]
            
            if word_count < 2:
                raise ValueError("詞語數量至少需要2個")
            if word_count > 10:
                raise ValueError("詞語數量不能超過10個")
            
            # 隨機選擇詞語
            selected_words = [secrets.choice(words) for _ in range(word_count)]
            
            # 處理大小寫
            if capitalize:
                selected_words = [word.capitalize() for word in selected_words]
            
            # 添加數字
            if add_numbers:
                # 在隨機位置插入數字
                number = secrets.randbelow(9999)
                insert_pos = secrets.randbelow(len(selected_words) + 1)
                selected_words.insert(insert_pos, str(number))
            
            # 組合密碼短語
            passphrase = separator.join(selected_words)
            
            # 分析強度
            analysis = self.analyze_password_strength(passphrase)
            
            return {
                "passphrase": passphrase,
                "words": selected_words,
                "word_count": word_count,
                "separator": separator,
                "length": len(passphrase),
                "entropy_bits": analysis["entropy_bits"],
                "strength_score": analysis["strength_score"],
                "strength_level": analysis["strength_level"]
            }
            
        except Exception as e:
            raise Exception(f"密碼短語生成失敗: {str(e)}")
    
    def generate_pin(self, length: int = 4, exclude_patterns: bool = True) -> dict:
        """生成PIN碼"""
        try:
            if length < 3:
                raise ValueError("PIN長度至少需要3位")
            if length > 20:
                raise ValueError("PIN長度不能超過20位")
            
            max_attempts = 1000
            attempts = 0
            
            while attempts < max_attempts:
                pin = ''.join([str(secrets.randbelow(10)) for _ in range(length)])
                
                if exclude_patterns:
                    # 檢查是否有問題模式
                    if self._has_pin_patterns(pin):
                        attempts += 1
                        continue
                
                # PIN生成成功
                return {
                    "pin": pin,
                    "length": length,
                    "entropy_bits": length * math.log2(10),
                    "total_combinations": 10 ** length,
                    "patterns_excluded": exclude_patterns
                }
            
            # 如果無法生成無模式的PIN，返回隨機PIN
            pin = ''.join([str(secrets.randbelow(10)) for _ in range(length)])
            return {
                "pin": pin,
                "length": length,
                "entropy_bits": length * math.log2(10),
                "total_combinations": 10 ** length,
                "patterns_excluded": False,
                "warning": "無法生成無模式PIN，返回隨機PIN"
            }
            
        except Exception as e:
            raise Exception(f"PIN生成失敗: {str(e)}")
    
    def _has_pin_patterns(self, pin: str) -> bool:
        """檢查PIN是否包含常見模式"""
        # 檢查重複數字
        if len(set(pin)) == 1:
            return True
        
        # 檢查順序模式（如1234, 4321）
        if len(pin) >= 3:
            ascending = True
            descending = True
            
            for i in range(1, len(pin)):
                if int(pin[i]) != int(pin[i-1]) + 1:
                    ascending = False
                if int(pin[i]) != int(pin[i-1]) - 1:
                    descending = False
            
            if ascending or descending:
                return True
        
        # 檢查常見PIN
        common_pins = ['1234', '0000', '1111', '1212', '7777', '1004', '2000', '4444', '2222', '6969', '9999', '3333', '5555', '6666', '1122', '1313', '8888', '4321', '2001', '1010']
        if pin in common_pins:
            return True
        
        return False
    
    def check_breach(self, password: str) -> dict:
        """檢查密碼是否在已知洩露數據庫中（模擬）"""
        # 注意：這是一個模擬功能。實際應用中應該使用真實的洩露密碼數據庫
        # 如 HaveIBeenPwned API 或本地數據庫
        
        # 模擬檢查
        is_breached = password.lower() in self.common_passwords
        
        return {
            "is_breached": is_breached,
            "breach_count": 1000000 if is_breached else 0,
            "recommendation": "立即更換密碼" if is_breached else "密碼未發現在已知洩露中",
            "note": "這是模擬檢查，實際應用建議使用真實的洩露密碼數據庫"
        } 