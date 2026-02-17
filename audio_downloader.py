#!/usr/bin/env python3
"""
音频下载模块
支持多种下载方式和格式处理
"""

import os
import sys
import time
import hashlib
import mimetypes
from pathlib import Path
from urllib.parse import urlparse
import requests
from config import TEMP_DIR


class AudioDownloadError(Exception):
    """音频下载错误异常"""

    pass


class AudioDownloader:
    """音频下载器 - 支持多种下载方式"""

    def __init__(self, temp_dir=TEMP_DIR):
        self.temp_dir = temp_dir
        os.makedirs(self.temp_dir, exist_ok=True)

        # 支持的音频格式
        self.supported_formats = {
            ".mp3": "audio/mpeg",
            ".m4a": "audio/mp4",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".flac": "audio/flac",
            ".aac": "audio/aac",
            ".mp4": "video/mp4",  # 可能包含音频
            ".mov": "video/quicktime",
        }

        # User-Agent 伪装
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "audio/*, video/*, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }

    def download(self, url, podcast_name="", episode_title="", timeout=30):
        """
        下载音频文件

        Args:
            url: 音频文件URL
            podcast_name: 播客名称（用于文件名）
            episode_title: 期数标题（用于文件名）
            timeout: 超时时间（秒）

        Returns:
            str: 下载的音频文件路径
        """
        print(f"📥 下载音频: {episode_title or '未知期数'}")
        print(f"   🔗 URL: {url[:80]}..." if len(url) > 80 else f"   🔗 URL: {url}")

        # 验证URL
        if not self._validate_url(url):
            raise AudioDownloadError(f"无效的URL: {url}")

        try:
            # 方法1: 直接下载
            return self._download_direct(url, podcast_name, episode_title, timeout)
        except Exception as e1:
            print(f"   ⚠️  直接下载失败: {e1}")
            try:
                # 方法2: 使用流式下载
                return self._download_streaming(
                    url, podcast_name, episode_title, timeout
                )
            except Exception as e2:
                print(f"   ⚠️  流式下载失败: {e2}")
                raise AudioDownloadError(f"所有下载方法都失败: {e1}, {e2}")

    def _validate_url(self, url):
        """验证URL是否有效"""
        try:
            result = urlparse(url)
            return all([result.scheme in ["http", "https"], result.netloc])
        except:
            return False

    def _download_direct(self, url, podcast_name, episode_title, timeout):
        """直接下载音频文件"""
        print("   🚀 使用直接下载...")

        # 发送HEAD请求获取文件信息
        try:
            head_response = requests.head(
                url, headers=self.headers, timeout=10, allow_redirects=True
            )
            head_response.raise_for_status()

            # 获取文件大小
            content_length = head_response.headers.get("Content-Length")
            file_size = int(content_length) if content_length else None

            # 获取内容类型
            content_type = head_response.headers.get("Content-Type", "")
            print(
                f"   📊 文件信息: {content_type}, 大小: {self._format_size(file_size) if file_size else '未知'}"
            )

        except Exception as e:
            print(f"   ℹ️  无法获取文件信息: {e}")
            file_size = None
            content_type = ""

        # 生成文件名
        filename = self._generate_filename(
            url, podcast_name, episode_title, content_type
        )
        filepath = os.path.join(self.temp_dir, filename)

        # 下载文件
        print(f"   💾 保存到: {filename}")

        response = requests.get(
            url, headers=self.headers, timeout=timeout, stream=False
        )
        response.raise_for_status()

        # 保存文件
        with open(filepath, "wb") as f:
            f.write(response.content)

        # 验证文件
        actual_size = os.path.getsize(filepath)
        if file_size and actual_size != file_size:
            print(
                f"   ⚠️  文件大小不匹配: 期望 {self._format_size(file_size)}, 实际 {self._format_size(actual_size)}"
            )

        print(f"   ✅ 下载完成: {self._format_size(actual_size)}")
        return filepath

    def _download_streaming(self, url, podcast_name, episode_title, timeout):
        """流式下载大文件"""
        print("   🌊 使用流式下载...")

        # 生成文件名
        filename = self._generate_filename(url, podcast_name, episode_title)
        filepath = os.path.join(self.temp_dir, filename)

        # 流式下载
        response = requests.get(url, headers=self.headers, timeout=timeout, stream=True)
        response.raise_for_status()

        # 获取文件大小
        total_size = int(response.headers.get("content-length", 0))
        block_size = 8192  # 8KB

        downloaded = 0
        start_time = time.time()

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)

                    # 显示进度
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        speed = downloaded / (time.time() - start_time) / 1024  # KB/s
                        print(
                            f"   📈 进度: {percent:.1f}% ({self._format_size(downloaded)}/{self._format_size(total_size)}) - {speed:.1f} KB/s",
                            end="\r",
                        )

        print()  # 换行
        actual_size = os.path.getsize(filepath)
        print(f"   ✅ 流式下载完成: {self._format_size(actual_size)}")

        return filepath

    def _generate_filename(self, url, podcast_name, episode_title, content_type=""):
        """生成文件名"""
        # 从URL提取基础信息
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        timestamp = int(time.time())

        # 清理播客名称和期数标题
        safe_podcast = (
            self._safe_filename(podcast_name)[:20] if podcast_name else "podcast"
        )
        safe_episode = (
            self._safe_filename(episode_title)[:30] if episode_title else "episode"
        )

        # 确定文件扩展名
        extension = self._get_extension_from_url(url, content_type)

        # 构建文件名
        if podcast_name and episode_title:
            filename = (
                f"{safe_podcast}_{safe_episode}_{url_hash}_{timestamp}{extension}"
            )
        else:
            filename = f"audio_{url_hash}_{timestamp}{extension}"

        return filename

    def _safe_filename(self, text):
        """将文本转换为安全的文件名"""
        if not text:
            return ""

        # 替换不安全字符
        unsafe_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|", "\n", "\r", "\t"]
        for char in unsafe_chars:
            text = text.replace(char, "_")

        # 移除多余空格和下划线
        text = " ".join(text.split())
        text = text.replace(" ", "_")

        # 限制长度
        return text[:50]

    def _get_extension_from_url(self, url, content_type=""):
        """从URL或内容类型获取文件扩展名"""
        # 从URL路径获取扩展名
        path = urlparse(url).path
        _, ext = os.path.splitext(path.lower())

        if ext in self.supported_formats:
            return ext

        # 从内容类型获取扩展名
        if content_type:
            for ext, mime_type in self.supported_formats.items():
                if mime_type in content_type:
                    return ext

        # 默认使用.mp3
        return ".mp3"

    def _format_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes is None:
            return "未知大小"

        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def get_file_info(self, filepath):
        """获取音频文件信息"""
        if not os.path.exists(filepath):
            return None

        info = {
            "path": filepath,
            "filename": os.path.basename(filepath),
            "size": os.path.getsize(filepath),
            "size_formatted": self._format_size(os.path.getsize(filepath)),
            "extension": os.path.splitext(filepath)[1].lower(),
            "created": time.ctime(os.path.getctime(filepath)),
            "modified": time.ctime(os.path.getmtime(filepath)),
        }

        # 检查是否为支持的格式
        info["supported"] = info["extension"] in self.supported_formats

        return info

    def cleanup_old_files(self, max_age_hours=24):
        """清理旧的临时文件"""
        print(f"🧹 清理 {self.temp_dir} 中的旧文件...")

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        deleted_count = 0
        total_size = 0

        for filename in os.listdir(self.temp_dir):
            filepath = os.path.join(self.temp_dir, filename)

            try:
                # 检查文件年龄
                file_age = current_time - os.path.getmtime(filepath)

                if file_age > max_age_seconds:
                    file_size = os.path.getsize(filepath)
                    os.remove(filepath)
                    deleted_count += 1
                    total_size += file_size

            except Exception as e:
                print(f"   ⚠️  无法删除 {filename}: {e}")

        if deleted_count > 0:
            print(
                f"   ✅ 清理完成: 删除 {deleted_count} 个文件, 释放 {self._format_size(total_size)}"
            )
        else:
            print("   ℹ️  没有需要清理的旧文件")

        return deleted_count, total_size


# 便捷函数
def download_audio(url, podcast_name="", episode_title="", timeout=30):
    """下载音频文件的便捷函数"""
    downloader = AudioDownloader()
    return downloader.download(url, podcast_name, episode_title, timeout)


def get_audio_info(filepath):
    """获取音频文件信息的便捷函数"""
    downloader = AudioDownloader()
    return downloader.get_file_info(filepath)


def cleanup_temp_files(max_age_hours=24):
    """清理临时文件的便捷函数"""
    downloader = AudioDownloader()
    return downloader.cleanup_old_files(max_age_hours)


if __name__ == "__main__":
    # 测试代码
    import argparse

    parser = argparse.ArgumentParser(description="音频下载测试")
    parser.add_argument("--url", help="音频文件URL")
    parser.add_argument("--podcast", default="测试播客", help="播客名称")
    parser.add_argument("--episode", default="测试期数", help="期数标题")
    parser.add_argument("--cleanup", action="store_true", help="清理临时文件")
    parser.add_argument("--info", help="获取文件信息")

    args = parser.parse_args()

    if args.cleanup:
        # 清理临时文件
        deleted, size = cleanup_temp_files()
        print(f"清理结果: 删除 {deleted} 个文件, 释放 {size} 字节")

    elif args.info:
        # 获取文件信息
        info = get_audio_info(args.info)
        if info:
            print("📁 文件信息:")
            for key, value in info.items():
                print(f"  {key}: {value}")
        else:
            print("❌ 文件不存在")

    elif args.url:
        # 下载测试
        try:
            print("=" * 60)
            print("🎵 音频下载测试")
            print("=" * 60)

            filepath = download_audio(args.url, args.podcast, args.episode)

            print("\n✅ 下载成功!")
            print(f"📁 文件路径: {filepath}")

            # 显示文件信息
            info = get_audio_info(filepath)
            if info:
                print("\n📊 文件详情:")
                print(f"  大小: {info['size_formatted']}")
                print(f"  格式: {info['extension']}")
                print(f"  支持: {'✅' if info['supported'] else '❌'}")
                print(f"  创建: {info['created']}")

        except Exception as e:
            print(f"\n❌ 下载失败: {e}")
            print("\n💡 故障排除:")
            print("1. 检查URL是否有效")
            print("2. 检查网络连接")
            print("3. 尝试使用代理")
            print("4. 检查文件权限")

    else:
        print("💡 使用方法:")
        print(
            "  下载音频: python audio_downloader.py --url <音频URL> --podcast '播客名' --episode '期数标题'"
        )
        print("  获取信息: python audio_downloader.py --info <文件路径>")
        print("  清理文件: python audio_downloader.py --cleanup")
        print("\n💡 示例:")
        print(
            "  python audio_downloader.py --url https://example.com/audio.mp3 --podcast '得到' --episode 'AI如何改变工作'"
        )
