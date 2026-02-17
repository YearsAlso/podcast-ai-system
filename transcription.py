#!/usr/bin/env python3
"""
播客转录模块 - 支持多种转录方案
1. OpenAI Whisper API（在线）
2. faster-whisper（本地，轻量）
3. whisper.cpp（纯CPU）
4. 简化模式（仅下载）
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path
from config import (
    TRANSCRIPTION_MODE,
    OPENAI_API_KEY,
    OPENAI_WHISPER_MODEL,
    FASTER_WHISPER_MODEL_SIZE,
    FASTER_WHISPER_DEVICE,
    FASTER_WHISPER_COMPUTE_TYPE,
    TRANSCRIPT_LANGUAGE,
)


class TranscriptionError(Exception):
    """转录错误异常"""

    pass


class TranscriptionManager:
    """转录管理器 - 根据配置选择最佳转录方案"""

    def __init__(self):
        self.mode = TRANSCRIPTION_MODE
        self.language = TRANSCRIPT_LANGUAGE
        self.available_modes = self._detect_available_modes()

    def _detect_available_modes(self):
        """检测可用的转录模式"""
        available = ["simplified"]  # 简化模式总是可用

        # 检查OpenAI API
        if OPENAI_API_KEY and OPENAI_API_KEY.strip():
            available.append("openai_api")

        # 检查faster-whisper
        try:
            import faster_whisper

            available.append("faster_whisper")
        except ImportError:
            pass

        # 检查whisper.cpp
        if self._check_whisper_cpp():
            available.append("whisper_cpp")

        # 检查原始whisper（备用）
        try:
            import whisper

            available.append("whisper")
        except ImportError:
            pass

        return available

    def _check_whisper_cpp(self):
        """检查whisper.cpp是否可用"""
        try:
            # 检查是否安装了whisper-cpp
            result = subprocess.run(
                ["which", "whisper-cpp"], capture_output=True, text=True
            )
            return result.returncode == 0
        except:
            return False

    def transcribe(self, audio_path, podcast_name="", episode_title=""):
        """
        转录音频文件

        Args:
            audio_path: 音频文件路径
            podcast_name: 播客名称（用于错误信息）
            episode_title: 期数标题（用于错误信息）

        Returns:
            str: 转录文本
        """
        print(f"🎤 开始转录: {episode_title or Path(audio_path).name}")

        # 按优先级尝试可用模式
        modes_to_try = [self.mode] + [m for m in self.available_modes if m != self.mode]

        for mode in modes_to_try:
            try:
                if mode == "openai_api":
                    return self._transcribe_openai_api(audio_path)
                elif mode == "faster_whisper":
                    return self._transcribe_faster_whisper(audio_path)
                elif mode == "whisper_cpp":
                    return self._transcribe_whisper_cpp(audio_path)
                elif mode == "whisper":
                    return self._transcribe_whisper(audio_path)
                elif mode == "simplified":
                    return self._simplified_transcription(
                        audio_path, podcast_name, episode_title
                    )
            except Exception as e:
                print(f"⚠️  {mode} 模式失败: {e}")
                continue

        # 所有模式都失败
        error_msg = f"❌ 所有转录模式都失败，请检查配置"
        raise TranscriptionError(error_msg)

    def _transcribe_openai_api(self, audio_path):
        """使用OpenAI Whisper API转录音频"""
        print("🔗 使用OpenAI Whisper API转录...")

        if not OPENAI_API_KEY or not OPENAI_API_KEY.strip():
            raise TranscriptionError("OpenAI API key未配置")

        try:
            from openai import OpenAI

            client = OpenAI(api_key=OPENAI_API_KEY)

            with open(audio_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model=OPENAI_WHISPER_MODEL,
                    file=audio_file,
                    language=self.language,
                    response_format="text",
                )

            print(f"✅ OpenAI转录完成，长度: {len(transcript)} 字符")
            return transcript

        except ImportError:
            raise TranscriptionError("未安装openai库: pip install openai")
        except Exception as e:
            raise TranscriptionError(f"OpenAI API错误: {e}")

    def _transcribe_faster_whisper(self, audio_path):
        """使用faster-whisper转录音频"""
        print(f"⚡ 使用faster-whisper转录 (模型: {FASTER_WHISPER_MODEL_SIZE})...")

        try:
            from faster_whisper import WhisperModel

            # 加载模型
            model = WhisperModel(
                FASTER_WHISPER_MODEL_SIZE,
                device=FASTER_WHISPER_DEVICE,
                compute_type=FASTER_WHISPER_COMPUTE_TYPE,
            )

            # 转录音频
            segments, info = model.transcribe(
                audio_path, language=self.language, beam_size=5, vad_filter=True
            )

            # 合并所有片段
            transcript = "".join(segment.text for segment in segments)

            print(f"✅ faster-whisper转录完成，长度: {len(transcript)} 字符")
            print(
                f"   检测语言: {info.language}, 概率: {info.language_probability:.2f}"
            )

            return transcript

        except ImportError:
            raise TranscriptionError("未安装faster-whisper: pip install faster-whisper")
        except Exception as e:
            raise TranscriptionError(f"faster-whisper错误: {e}")

    def _transcribe_whisper_cpp(self, audio_path):
        """使用whisper.cpp转录音频"""
        print("🔧 使用whisper.cpp转录...")

        # 创建临时输出文件
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            output_file = f.name

        try:
            # 构建命令
            cmd = [
                "whisper-cpp",
                "-m",
                "models/ggml-base.bin",  # 需要提前下载模型
                "-f",
                audio_path,
                "-l",
                self.language,
                "-otxt",
                "-of",
                output_file.replace(".txt", ""),  # 去掉扩展名
            ]

            # 执行转录
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                raise TranscriptionError(f"whisper.cpp执行失败: {result.stderr}")

            # 读取转录结果
            with open(output_file, "r", encoding="utf-8") as f:
                transcript = f.read()

            # 清理临时文件
            os.unlink(output_file)

            print(f"✅ whisper.cpp转录完成，长度: {len(transcript)} 字符")
            return transcript

        except FileNotFoundError:
            raise TranscriptionError(
                "whisper-cpp未安装，请参考: https://github.com/ggerganov/whisper.cpp"
            )
        except Exception as e:
            # 清理临时文件
            if os.path.exists(output_file):
                os.unlink(output_file)
            raise TranscriptionError(f"whisper.cpp错误: {e}")

    def _transcribe_whisper(self, audio_path):
        """使用原始whisper转录音频（备用方案）"""
        print("🎵 使用OpenAI Whisper转录...")

        try:
            import whisper

            # 加载模型
            model = whisper.load_model("base")

            # 转录音频
            result = model.transcribe(
                audio_path, language=self.language, fp16=False  # CPU模式
            )

            transcript = result["text"]

            print(f"✅ Whisper转录完成，长度: {len(transcript)} 字符")
            return transcript

        except ImportError:
            raise TranscriptionError("未安装whisper: pip install openai-whisper")
        except Exception as e:
            raise TranscriptionError(f"Whisper错误: {e}")

    def _simplified_transcription(self, audio_path, podcast_name, episode_title):
        """简化模式 - 不实际转录，返回占位文本"""
        print("📝 使用简化模式（跳过实际转录）...")

        file_size = os.path.getsize(audio_path)
        file_size_mb = file_size / (1024 * 1024)

        transcript = f"""
# 播客音频文件信息

**播客名称**: {podcast_name}
**期数标题**: {episode_title}
**音频文件**: {Path(audio_path).name}
**文件大小**: {file_size_mb:.2f} MB
**处理时间**: 已下载，等待转录

## 📋 转录状态
当前使用简化模式，未进行实际音频转录。

## 🔧 启用完整转录的方法

### 方案一：使用OpenAI Whisper API（推荐）
1. 获取OpenAI API key: https://platform.openai.com/api-keys
2. 在 `config.py` 中设置 `OPENAI_API_KEY = "你的API key"`
3. 设置 `TRANSCRIPTION_MODE = "openai_api"`

### 方案二：使用本地faster-whisper
```bash
pip install faster-whisper
# 然后在 config.py 中设置:
# TRANSCRIPTION_MODE = "faster_whisper"
```

### 方案三：使用whisper.cpp
```bash
# 安装whisper.cpp
git clone https://github.com/ggerganov/whisper.cpp
cd whisper.cpp
make
# 下载模型
./models/download-ggml-model.sh base
# 然后在 config.py 中设置:
# TRANSCRIPTION_MODE = "whisper_cpp"
```

## 🎯 当前文件
音频文件已保存，可以使用上述任一方案进行转录。

---
*简化模式 - 需要配置转录功能以获取完整文字稿*
"""

        print("✅ 简化模式完成（音频已保存，未转录）")
        return transcript

    def get_mode_info(self):
        """获取当前转录模式信息"""
        info = {
            "current_mode": self.mode,
            "available_modes": self.available_modes,
            "language": self.language,
        }

        if self.mode == "openai_api":
            info["api_configured"] = bool(OPENAI_API_KEY and OPENAI_API_KEY.strip())
            info["model"] = OPENAI_WHISPER_MODEL
        elif self.mode == "faster_whisper":
            info["model_size"] = FASTER_WHISPER_MODEL_SIZE
            info["device"] = FASTER_WHISPER_DEVICE

        return info


# 便捷函数
def transcribe_audio(audio_path, podcast_name="", episode_title=""):
    """转录音频文件的便捷函数"""
    manager = TranscriptionManager()
    return manager.transcribe(audio_path, podcast_name, episode_title)


def get_transcription_info():
    """获取转录配置信息"""
    manager = TranscriptionManager()
    return manager.get_mode_info()


if __name__ == "__main__":
    # 测试代码
    import argparse

    parser = argparse.ArgumentParser(description="测试转录模块")
    parser.add_argument("--audio", help="音频文件路径")
    parser.add_argument("--podcast", default="测试播客", help="播客名称")
    parser.add_argument("--episode", default="测试期数", help="期数标题")

    args = parser.parse_args()

    # 显示配置信息
    print("📋 转录配置信息:")
    info = get_transcription_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    print("\n" + "=" * 60)

    if args.audio and os.path.exists(args.audio):
        try:
            transcript = transcribe_audio(args.audio, args.podcast, args.episode)
            print("\n📝 转录结果预览（前500字符）:")
            print("=" * 60)
            print(transcript[:500] + ("..." if len(transcript) > 500 else ""))
            print("=" * 60)
            print(f"总长度: {len(transcript)} 字符")
        except Exception as e:
            print(f"❌ 转录失败: {e}")
    else:
        print("💡 使用方法:")
        print(
            "  python transcription.py --audio /path/to/audio.mp3 --podcast '播客名' --episode '期数标题'"
        )
        print("\n💡 测试简化模式:")
        print("  echo '测试音频' > test_audio.txt")
        print("  python transcription.py --audio test_audio.txt")
