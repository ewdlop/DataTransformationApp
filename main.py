from fastapi import FastAPI, HTTPException, UploadFile, File, Query, Form
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import uvicorn
import os
import io
import tempfile
import base64
from encryption.text_encryption import TextEncryption
from encryption.data_encryption import DataEncryption
from encryption.image_encryption import ImageEncryption
from encryption.image_transformation import ImageTransformation
from encryption.text_compression import TextCompression
from encryption.hash_functions import HashFunctions
from encryption.image_steganography import ImageSteganography
from encryption.file_encryption import FileEncryption
from encryption.digital_signatures import DigitalSignatures
from encryption.qr_code_generator import QRCodeGenerator

app = FastAPI(
    title="加密與處理 API 服務",
    description="提供文本、數據和圖像加密/解密、圖像變換、文本壓縮、哈希服務、數字簽名和QR碼生成的綜合 FastAPI 應用程式",
    version="3.0.0"
)

# 請求模型
class TextEncryptRequest(BaseModel):
    text: str
    password: str

class TextDecryptRequest(BaseModel):
    encrypted_text: str
    password: str

class DataEncryptRequest(BaseModel):
    data: str
    password: str
    algorithm: Optional[str] = "AES"

class DataDecryptRequest(BaseModel):
    encrypted_data: str
    password: str
    algorithm: Optional[str] = "AES"

# 文本壓縮請求模型
class TextCompressRequest(BaseModel):
    text: str
    algorithm: Optional[str] = "gzip"
    level: Optional[int] = 6

class TextDecompressRequest(BaseModel):
    compressed_text: str
    algorithm: Optional[str] = "gzip"

# 哈希請求模型
class HashRequest(BaseModel):
    text: str
    algorithm: Optional[str] = "sha256"

class HashVerifyRequest(BaseModel):
    text: str
    expected_hash: str
    algorithm: Optional[str] = "sha256"

class CrunchHashRequest(BaseModel):
    data: str
    salt: Optional[str] = None
    iterations: Optional[int] = 10000
    algorithm: Optional[str] = "sha256"

# 數字簽名請求模型
class KeyPairRequest(BaseModel):
    key_size: Optional[int] = 2048
    password: Optional[str] = None

class SignDataRequest(BaseModel):
    data: str
    private_key: str
    password: Optional[str] = None
    hash_algorithm: Optional[str] = "sha256"

class VerifySignatureRequest(BaseModel):
    data: str
    signature: str
    public_key: str
    hash_algorithm: Optional[str] = "sha256"



# QR碼請求模型
class QRGenerateRequest(BaseModel):
    data: str
    error_correction: Optional[str] = "M"
    box_size: Optional[int] = 10
    border: Optional[int] = 4

class QRWifiRequest(BaseModel):
    ssid: str
    password: str
    security: Optional[str] = "WPA"
    hidden: Optional[bool] = False

class QRContactRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    org: Optional[str] = None
    url: Optional[str] = None

# 初始化加密和處理類
text_crypto = TextEncryption()
data_crypto = DataEncryption()
image_crypto = ImageEncryption()
image_transform = ImageTransformation()
text_compressor = TextCompression()
hash_functions = HashFunctions()
image_stego = ImageSteganography()
file_crypto = FileEncryption()
digital_signer = DigitalSignatures()
qr_generator = QRCodeGenerator()

@app.get("/")
async def root():
    return {
        "message": "歡迎使用加密與處理 API 服務",
        "version": "3.0.0",
        "categories": {
            "encryption": {
                "text_encrypt": "/encrypt/text",
                "text_decrypt": "/decrypt/text",
                "data_encrypt": "/encrypt/data",
                "data_decrypt": "/decrypt/data",
                "image_encrypt": "/encrypt/image",
                "image_decrypt": "/decrypt/image"
            },
            "compression": {
                "compress_text": "/compress/text",
                "decompress_text": "/decompress/text",
                "compression_stats": "/compress/stats",
                "compare_algorithms": "/compress/compare"
            },
            "image_transformation": {
                "resize": "/transform/image/resize",
                "rotate": "/transform/image/rotate",
                "crop": "/transform/image/crop",
                "filter": "/transform/image/filter",
                "brightness": "/transform/image/brightness",
                "contrast": "/transform/image/contrast",
                "convert_format": "/transform/image/convert",
                "thumbnail": "/transform/image/thumbnail",
                "info": "/transform/image/info"
            },
            "hash": {
                "hash_text": "/hash/text",
                "verify_hash": "/hash/verify",
                "multi_hash": "/hash/multi",
                "crunch_hash": "/hash/crunch",
                "verify_crunch": "/hash/crunch/verify"
            },
            "steganography": {
                "hide_text": "/stego/hide",
                "extract_text": "/stego/extract",
                "check_capacity": "/stego/capacity",
                "detect_hidden": "/stego/detect"
            },
            "file_encryption": {
                "encrypt_file": "/encrypt/file",
                "decrypt_file": "/decrypt/file",
                "file_info": "/file/info"
            },
            "digital_signatures": {
                "generate_keypair": "/signature/generate-keypair",
                "sign_data": "/signature/sign",
                "verify_signature": "/signature/verify",
                "sign_file": "/signature/sign-file",
                "verify_file": "/signature/verify-file"
            },
            "qr_codes": {
                "generate_qr": "/qr/generate",
                "read_qr": "/qr/read",
                "generate_wifi": "/qr/wifi",
                "generate_contact": "/qr/contact",
                "generate_url": "/qr/url"
            }
        }
    }

# 文本加密端點
@app.post("/encrypt/text")
async def encrypt_text(request: TextEncryptRequest):
    try:
        encrypted_text = text_crypto.encrypt(request.text, request.password)
        return {
            "status": "success",
            "encrypted_text": encrypted_text,
            "message": "文本加密成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"加密失敗: {str(e)}")

@app.post("/decrypt/text")
async def decrypt_text(request: TextDecryptRequest):
    try:
        decrypted_text = text_crypto.decrypt(request.encrypted_text, request.password)
        return {
            "status": "success",
            "decrypted_text": decrypted_text,
            "message": "文本解密成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"解密失敗: {str(e)}")

# 數據加密端點
@app.post("/encrypt/data")
async def encrypt_data(request: DataEncryptRequest):
    try:
        encrypted_data = data_crypto.encrypt(request.data, request.password, request.algorithm)
        return {
            "status": "success",
            "encrypted_data": encrypted_data,
            "algorithm": request.algorithm,
            "message": "數據加密成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"數據加密失敗: {str(e)}")

@app.post("/decrypt/data")
async def decrypt_data(request: DataDecryptRequest):
    try:
        decrypted_data = data_crypto.decrypt(request.encrypted_data, request.password, request.algorithm)
        return {
            "status": "success",
            "decrypted_data": decrypted_data,
            "algorithm": request.algorithm,
            "message": "數據解密成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"數據解密失敗: {str(e)}")

# 圖像加密端點
@app.post("/encrypt/image")
async def encrypt_image(password: str, file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        # 讀取上傳的圖像
        image_data = await file.read()
        
        # 加密圖像
        encrypted_data = image_crypto.encrypt(image_data, password)
        
        # 保存加密文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.enc') as temp_file:
            temp_file.write(encrypted_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='application/octet-stream',
            filename=f"encrypted_{file.filename}.enc"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"圖像加密失敗: {str(e)}")

@app.post("/decrypt/image")
async def decrypt_image(password: str, file: UploadFile = File(...)):
    try:
        # 讀取加密文件
        encrypted_data = await file.read()
        
        # 解密圖像
        decrypted_data = image_crypto.decrypt(encrypted_data, password)
        
        # 保存解密文件
        original_filename = file.filename.replace('.enc', '') if file.filename.endswith('.enc') else file.filename
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(decrypted_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/jpeg',
            filename=f"decrypted_{original_filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"圖像解密失敗: {str(e)}")

# 文本壓縮端點
@app.post("/compress/text")
async def compress_text(request: TextCompressRequest):
    try:
        compressed_text = text_compressor.compress_text(request.text, request.algorithm, request.level)
        return {
            "status": "success",
            "compressed_text": compressed_text,
            "algorithm": request.algorithm,
            "compression_level": request.level,
            "message": "文本壓縮成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文本壓縮失敗: {str(e)}")

@app.post("/decompress/text")
async def decompress_text(request: TextDecompressRequest):
    try:
        decompressed_text = text_compressor.decompress_text(request.compressed_text, request.algorithm)
        return {
            "status": "success",
            "decompressed_text": decompressed_text,
            "algorithm": request.algorithm,
            "message": "文本解壓成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文本解壓失敗: {str(e)}")

@app.post("/compress/stats")
async def get_compression_stats(request: TextCompressRequest):
    try:
        stats = text_compressor.get_compression_stats(request.text, request.algorithm, request.level)
        return {
            "status": "success",
            "stats": stats,
            "message": "壓縮統計獲取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"壓縮統計獲取失敗: {str(e)}")

@app.post("/compress/compare")
async def compare_compression_algorithms(text: str = Form(...), level: int = Form(6)):
    try:
        comparison = text_compressor.compare_algorithms(text, level)
        return {
            "status": "success",
            "comparison": comparison,
            "message": "算法比較完成"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"算法比較失敗: {str(e)}")

# 圖像變換端點
@app.post("/transform/image/resize")
async def resize_image(
    width: int = Form(...),
    height: int = Form(...),
    maintain_aspect: bool = Form(True),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        resized_data = image_transform.resize_image(image_data, width, height, maintain_aspect)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(resized_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/png',
            filename=f"resized_{file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"圖像大小調整失敗: {str(e)}")

@app.post("/transform/image/rotate")
async def rotate_image(
    angle: float = Form(...),
    expand: bool = Form(True),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        rotated_data = image_transform.rotate_image(image_data, angle, expand)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(rotated_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/png',
            filename=f"rotated_{file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"圖像旋轉失敗: {str(e)}")

@app.post("/transform/image/crop")
async def crop_image(
    left: int = Form(...),
    top: int = Form(...),
    right: int = Form(...),
    bottom: int = Form(...),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        cropped_data = image_transform.crop_image(image_data, left, top, right, bottom)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(cropped_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/png',
            filename=f"cropped_{file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"圖像裁剪失敗: {str(e)}")

@app.post("/transform/image/filter")
async def apply_image_filter(
    filter_name: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        filtered_data = image_transform.apply_filter(image_data, filter_name)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(filtered_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/png',
            filename=f"filtered_{file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"濾鏡應用失敗: {str(e)}")

@app.post("/transform/image/brightness")
async def adjust_brightness(
    factor: float = Form(...),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        adjusted_data = image_transform.adjust_brightness(image_data, factor)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(adjusted_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/png',
            filename=f"brightness_{file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"亮度調整失敗: {str(e)}")

@app.post("/transform/image/contrast")
async def adjust_contrast(
    factor: float = Form(...),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        adjusted_data = image_transform.adjust_contrast(image_data, factor)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(adjusted_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/png',
            filename=f"contrast_{file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"對比度調整失敗: {str(e)}")

@app.post("/transform/image/convert")
async def convert_image_format(
    target_format: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        converted_data = image_transform.convert_format(image_data, target_format)
        
        ext = target_format.lower()
        mime_type = f'image/{ext}'
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{ext}') as temp_file:
            temp_file.write(converted_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type=mime_type,
            filename=f"converted_{file.filename}.{ext}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"格式轉換失敗: {str(e)}")

@app.post("/transform/image/thumbnail")
async def create_thumbnail(
    width: int = Form(128),
    height: int = Form(128),
    file: UploadFile = File(...)
):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        thumbnail_data = image_transform.create_thumbnail(image_data, (width, height))
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
            temp_file.write(thumbnail_data)
            temp_file_path = temp_file.name
        
        return FileResponse(
            temp_file_path,
            media_type='image/png',
            filename=f"thumbnail_{file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"縮略圖創建失敗: {str(e)}")

@app.post("/transform/image/info")
async def get_image_info(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="文件必須是圖像格式")
        
        image_data = await file.read()
        info = image_transform.get_image_info(image_data)
        
        return {
            "status": "success",
            "image_info": info,
            "message": "圖像信息獲取成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"圖像信息獲取失敗: {str(e)}")

# 圖像隱寫術端點
@app.post("/stego/hide")
async def hide_text_in_image(
    image: UploadFile = File(...),
    secret_text: str = Form(...),
    method: str = Form("lsb", description="隱藏方法: lsb 或 dct"),
    encrypt_text: bool = Form(False, description="是否加密隱藏的文本"),
    password: str = Form(None, description="加密密碼（如果 encrypt_text 為 True）"),
    strength: float = Form(10.0, description="DCT 方法的強度（僅適用於 DCT）")
):
    """在圖像中隱藏文本"""
    try:
        # 讀取圖像文件
        image_bytes = await image.read()
        
        method = method.lower()
        if method == "lsb":
            result_image = image_stego.hide_text_lsb(
                image_bytes, 
                secret_text, 
                encrypt_text=encrypt_text, 
                password=password
            )
        elif method == "dct":
            if encrypt_text:
                # DCT 方法目前不支持加密，先手動加密
                if password:
                    encrypted_text = text_crypto.encrypt(secret_text, password)
                    secret_text = f"ENCRYPTED:{encrypted_text}"
            result_image = image_stego.hide_text_dct(image_bytes, secret_text, strength)
        else:
            raise ValueError(f"不支持的隱藏方法: {method}")
        
        # 返回處理後的圖像
        return StreamingResponse(
            io.BytesIO(result_image),
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=hidden_{image.filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/stego/extract")
async def extract_text_from_image(
    image: UploadFile = File(...),
    method: str = Form("lsb", description="提取方法: lsb 或 dct"),
    is_encrypted: bool = Form(False, description="隱藏的文本是否加密"),
    password: str = Form(None, description="解密密碼（如果 is_encrypted 為 True）"),
    strength: float = Form(10.0, description="DCT 方法的強度（僅適用於 DCT）")
):
    """從圖像中提取隱藏的文本"""
    try:
        # 讀取圖像文件
        image_bytes = await image.read()
        
        method = method.lower()
        if method == "lsb":
            extracted_text = image_stego.extract_text_lsb(
                image_bytes,
                is_encrypted=is_encrypted,
                password=password
            )
        elif method == "dct":
            extracted_text = image_stego.extract_text_dct(image_bytes, strength)
            # DCT 方法的解密處理
            if extracted_text.startswith("ENCRYPTED:"):
                if not is_encrypted or not password:
                    raise ValueError("檢測到加密文本，但未提供密碼")
                encrypted_text = extracted_text[10:]  # 移除 "ENCRYPTED:" 前綴
                extracted_text = text_crypto.decrypt(encrypted_text, password)
        else:
            raise ValueError(f"不支持的提取方法: {method}")
        
        return {
            "extracted_text": extracted_text,
            "method": method,
            "text_length": len(extracted_text),
            "is_encrypted": is_encrypted
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/stego/capacity")
async def check_image_capacity(
    image: UploadFile = File(...),
    method: str = Form("lsb", description="檢查方法: lsb 或 dct")
):
    """檢查圖像的隱藏容量"""
    try:
        # 讀取圖像文件
        image_bytes = await image.read()
        
        capacity_info = image_stego.check_capacity(image_bytes, method)
        
        return {
            "image_name": image.filename,
            "capacity": capacity_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/stego/detect")
async def detect_hidden_text(
    image: UploadFile = File(...),
    method: str = Form("lsb", description="檢測方法: lsb 或 dct")
):
    """檢測圖像中是否隱藏有文本"""
    try:
        # 讀取圖像文件
        image_bytes = await image.read()
        
        detection_result = image_stego.detect_hidden_text(image_bytes, method)
        
        return {
            "image_name": image.filename,
            "detection": detection_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 哈希函數端點
@app.post("/hash/text")
async def hash_text(request: HashRequest):
    try:
        hash_value = hash_functions.hash_text(request.text, request.algorithm)
        return {
            "status": "success",
            "hash": hash_value,
            "algorithm": request.algorithm,
            "message": "文本哈希計算成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文本哈希計算失敗: {str(e)}")

@app.post("/hash/verify")
async def verify_hash(request: HashVerifyRequest):
    try:
        is_valid = hash_functions.verify_hash(request.text, request.expected_hash, request.algorithm)
        return {
            "status": "success",
            "is_valid": is_valid,
            "algorithm": request.algorithm,
            "message": "哈希驗證完成"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"哈希驗證失敗: {str(e)}")

@app.post("/hash/multi")
async def multi_hash(text: str = Form(...), algorithms: str = Form("md5,sha1,sha256,sha512")):
    try:
        algorithm_list = [alg.strip() for alg in algorithms.split(',')]
        hashes = hash_functions.multi_hash(text, algorithm_list)
        return {
            "status": "success",
            "hashes": hashes,
            "message": "多重哈希計算成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"多重哈希計算失敗: {str(e)}")

@app.post("/hash/crunch")
async def crunch_hash(request: CrunchHashRequest):
    try:
        result = hash_functions.crunch_hash(
            request.data, 
            request.salt, 
            request.iterations, 
            request.algorithm
        )
        return {
            "status": "success",
            "crunch_hash": result,
            "message": "Crunch Hash 計算成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Crunch Hash 計算失敗: {str(e)}")

@app.post("/hash/crunch/verify")
async def verify_crunch_hash(
    data: str = Form(...),
    stored_hash: str = Form(...),
    salt: str = Form(...),
    iterations: int = Form(10000),
    algorithm: str = Form("sha256")
):
    try:
        is_valid = hash_functions.verify_crunch_hash(data, stored_hash, salt, iterations, algorithm)
        return {
            "status": "success",
            "is_valid": is_valid,
            "algorithm": algorithm,
            "iterations": iterations,
            "message": "Crunch Hash 驗證完成"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Crunch Hash 驗證失敗: {str(e)}")

@app.post("/hash/file")
async def hash_file(algorithm: str = Form("sha256"), file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        hash_value = hash_functions.hash_file_content(file_content, algorithm)
        return {
            "status": "success",
            "file_hash": hash_value,
            "algorithm": algorithm,
            "filename": file.filename,
            "file_size": len(file_content),
            "message": "文件哈希計算成功"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件哈希計算失敗: {str(e)}")

# 文件加密端點
@app.post("/encrypt/file")
async def encrypt_file_endpoint(
    file: UploadFile = File(...),
    password: str = Form(...),
    preserve_metadata: bool = Form(True)
):
    """加密文件"""
    try:
        contents = await file.read()
        encrypted_data = file_crypto.encrypt_file(
            contents, password, file.filename, preserve_metadata
        )
        
        return {
            "message": "文件加密成功",
            "encrypted_data": base64.b64encode(encrypted_data).decode(),
            "original_filename": file.filename,
            "encrypted_size": len(encrypted_data)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/decrypt/file")
async def decrypt_file_endpoint(
    encrypted_file: UploadFile = File(...),
    password: str = Form(...)
):
    """解密文件"""
    try:
        encrypted_data = await encrypted_file.read()
        # 如果是base64編碼的數據，嘗試解碼
        try:
            if len(encrypted_data) % 4 == 0:
                test_decode = base64.b64decode(encrypted_data)
                if file_crypto.is_encrypted_file(test_decode):
                    encrypted_data = test_decode
        except:
            pass
        
        decrypted_data, metadata = file_crypto.decrypt_file(encrypted_data, password)
        
        return {
            "message": "文件解密成功",
            "decrypted_data": base64.b64encode(decrypted_data).decode(),
            "metadata": metadata,
            "decrypted_size": len(decrypted_data)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/file/info")
async def get_file_info_endpoint(
    encrypted_file: UploadFile = File(...),
    password: str = Form(...)
):
    """獲取加密文件信息"""
    try:
        encrypted_data = await encrypted_file.read()
        info = file_crypto.get_file_info(encrypted_data, password)
        
        return {
            "message": "獲取文件信息成功",
            "file_info": info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 數字簽名端點
@app.post("/signature/generate-keypair")
def generate_keypair_endpoint(request: KeyPairRequest):
    """生成RSA密鑰對"""
    try:
        result = digital_signer.generate_key_pair(
            key_size=request.key_size,
            password=request.password
        )
        
        return {
            "message": "密鑰對生成成功",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/signature/sign")
def sign_data_endpoint(request: SignDataRequest):
    """對數據進行數字簽名"""
    try:
        result = digital_signer.sign_data(
            data=request.data,
            private_key_pem=request.private_key,
            password=request.password,
            hash_algorithm=request.hash_algorithm
        )
        
        return {
            "message": "數字簽名成功",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/signature/verify")
def verify_signature_endpoint(request: VerifySignatureRequest):
    """驗證數字簽名"""
    try:
        result = digital_signer.verify_signature(
            data=request.data,
            signature=request.signature,
            public_key_pem=request.public_key,
            hash_algorithm=request.hash_algorithm
        )
        
        return {
            "message": "簽名驗證完成",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/signature/sign-file")
async def sign_file_endpoint(
    file: UploadFile = File(...),
    private_key: str = Form(...),
    password: str = Form(None),
    hash_algorithm: str = Form("sha256")
):
    """對文件進行數字簽名"""
    try:
        file_data = await file.read()
        result = digital_signer.sign_file(
            file_data=file_data,
            private_key_pem=private_key,
            password=password,
            hash_algorithm=hash_algorithm
        )
        
        return {
            "message": "文件簽名成功",
            "filename": file.filename,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/signature/verify-file")
async def verify_file_signature_endpoint(
    file: UploadFile = File(...),
    signature: str = Form(...),
    public_key: str = Form(...),
    hash_algorithm: str = Form("sha256")
):
    """驗證文件數字簽名"""
    try:
        file_data = await file.read()
        result = digital_signer.verify_file_signature(
            file_data=file_data,
            signature=signature,
            public_key_pem=public_key,
            hash_algorithm=hash_algorithm
        )
        
        return {
            "message": "文件簽名驗證完成",
            "filename": file.filename,
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# QR碼生成端點
@app.post("/qr/generate")
def generate_qr_endpoint(request: QRGenerateRequest):
    """生成QR碼"""
    try:
        qr_image = qr_generator.generate_qr_code(
            data=request.data,
            error_correction=request.error_correction,
            box_size=request.box_size,
            border=request.border
        )
        
        return {
            "message": "QR碼生成成功",
            "qr_code": base64.b64encode(qr_image).decode(),
            "data": request.data,
            "size": len(qr_image)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/qr/read")
async def read_qr_endpoint(qr_image: UploadFile = File(...)):
    """讀取QR碼"""
    try:
        image_data = await qr_image.read()
        result = qr_generator.read_qr_code(image_data)
        
        return {
            "message": "QR碼讀取完成",
            **result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/qr/wifi")
def generate_wifi_qr_endpoint(request: QRWifiRequest):
    """生成WiFi QR碼"""
    try:
        qr_image = qr_generator.generate_wifi_qr(
            ssid=request.ssid,
            password=request.password,
            security=request.security,
            hidden=request.hidden
        )
        
        return {
            "message": "WiFi QR碼生成成功",
            "qr_code": base64.b64encode(qr_image).decode(),
            "wifi_info": {
                "ssid": request.ssid,
                "security": request.security,
                "hidden": request.hidden
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/qr/contact")
def generate_contact_qr_endpoint(request: QRContactRequest):
    """生成聯絡人QR碼"""
    try:
        contact_info = {k: v for k, v in request.dict().items() if v is not None}
        qr_image = qr_generator.generate_contact_qr(contact_info)
        
        return {
            "message": "聯絡人QR碼生成成功",
            "qr_code": base64.b64encode(qr_image).decode(),
            "contact_info": contact_info
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/qr/url")
def generate_url_qr_endpoint(url: str = Form(...)):
    """生成URL QR碼"""
    try:
        qr_image = qr_generator.generate_url_qr(url)
        
        return {
            "message": "URL QR碼生成成功",
            "qr_code": base64.b64encode(qr_image).decode(),
            "url": url
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 