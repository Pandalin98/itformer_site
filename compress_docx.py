#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
压缩docx文档中的图片以减小文件体积
"""

import zipfile
import os
import shutil
from PIL import Image
import io
import tempfile

def compress_image(image_data, max_size=(1920, 1080), quality=85):
    """压缩图片"""
    try:
        # 打开图片
        img = Image.open(io.BytesIO(image_data))
        
        # 转换为RGB模式（如果是RGBA）
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # 调整尺寸
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # 压缩并返回
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
    except Exception as e:
        print(f"压缩图片时出错: {e}")
        return image_data

def compress_docx(input_file, output_file, max_image_size=(1920, 1080), image_quality=85):
    """压缩docx文档"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 解压docx文件
        with zipfile.ZipFile(input_file, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # 压缩word/media目录中的图片
        media_dir = os.path.join(temp_dir, 'word', 'media')
        if os.path.exists(media_dir):
            for filename in os.listdir(media_dir):
                file_path = os.path.join(media_dir, filename)
                if os.path.isfile(file_path):
                    # 检查是否为图片文件
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                        print(f"正在压缩: {filename}")
                        
                        # 读取原图片
                        with open(file_path, 'rb') as f:
                            original_data = f.read()
                        
                        # 压缩图片
                        compressed_data = compress_image(original_data, max_image_size, image_quality)
                        
                        # 保存压缩后的图片
                        with open(file_path, 'wb') as f:
                            f.write(compressed_data)
                        
                        # 显示压缩效果
                        original_size = len(original_data)
                        compressed_size = len(compressed_data)
                        reduction = (original_size - compressed_size) / original_size * 100
                        print(f"  {filename}: {original_size/1024/1024:.2f}MB -> {compressed_size/1024/1024:.2f}MB (减少 {reduction:.1f}%)")
        
        # 重新打包为docx文件
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zip_ref.write(file_path, arcname)
        
        # 显示最终结果
        original_size = os.path.getsize(input_file) / 1024 / 1024
        final_size = os.path.getsize(output_file) / 1024 / 1024
        total_reduction = (original_size - final_size) / original_size * 100
        
        print(f"\n压缩完成!")
        print(f"原始文件: {original_size:.2f}MB")
        print(f"压缩后: {final_size:.2f}MB")
        print(f"总体减少: {total_reduction:.1f}%")
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

def main():
    """主函数"""
    # 要压缩的文件列表
    files_to_compress = [
        "公众号投稿v1.5.docx",
        "weixin.docx"
    ]
    
    for filename in files_to_compress:
        if os.path.exists(filename):
            print(f"\n正在处理: {filename}")
            output_filename = filename.replace('.docx', '_compressed.docx')
            
            try:
                compress_docx(filename, output_filename)
                print(f"压缩后的文件保存为: {output_filename}")
            except Exception as e:
                print(f"处理 {filename} 时出错: {e}")
        else:
            print(f"文件不存在: {filename}")

if __name__ == "__main__":
    main() 