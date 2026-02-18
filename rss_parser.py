#!/usr/bin/env python3
"""
RSS解析模块 - 支持多种播客RSS格式
"""

import feedparser
import time
import hashlib
from datetime import datetime
from urllib.parse import urlparse
import requests
from typing import Dict, List, Optional, Any
import json

from config import DOWNLOAD_TIMEOUT


class RSSParserError(Exception):
    """RSS解析错误异常"""
    pass


class RSSParser:
    """RSS解析器 - 支持多种播客格式"""
    
    def __init__(self, timeout: int = DOWNLOAD_TIMEOUT):
        self.timeout = timeout
        self.user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # 支持的播客平台识别
        self.platform_patterns = {
            "apple": ["apple.com", "podcasts.apple.com", "itunes.apple.com"],
            "spotify": ["spotify.com", "open.spotify.com"],
            "google": ["google.com", "podcasts.google.com"],
            "xiaoyuzhou": ["xiaoyuzhoufm.com"],
            "getpodcast": ["getpodcast.xyz"],
            "dedao": ["dedao.cn", "igetget.com"],
        }
    
    def parse_feed(self, rss_url: str) -> Dict[str, Any]:
        """
        解析RSS feed
        
        Args:
            rss_url: RSS feed URL
            
        Returns:
            Dict containing feed metadata and episodes
        """
        print(f"📡 解析RSS feed: {rss_url[:80]}..." if len(rss_url) > 80 else f"📡 解析RSS feed: {rss_url}")
        
        try:
            # 解析feed
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                # 尝试使用自定义User-Agent
                headers = {"User-Agent": self.user_agent}
                response = requests.get(rss_url, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                feed = feedparser.parse(response.content)
            
            # 检查feed是否有效
            if not feed.entries:
                raise RSSParserError(f"RSS feed没有内容或无法解析: {rss_url}")
            
            # 提取feed信息
            feed_info = self._extract_feed_info(feed, rss_url)
            
            # 提取剧集信息
            episodes = self._extract_episodes(feed)
            
            return {
                "feed_info": feed_info,
                "episodes": episodes,
                "total_episodes": len(episodes),
                "parse_time": datetime.now().isoformat(),
                "source_url": rss_url,
            }
            
        except Exception as e:
            raise RSSParserError(f"解析RSS失败: {e}")
    
    def _extract_feed_info(self, feed: feedparser.FeedParserDict, rss_url: str) -> Dict[str, Any]:
        """提取feed元数据"""
        feed_info = {
            "title": feed.feed.get("title", "未知播客"),
            "description": feed.feed.get("description", ""),
            "link": feed.feed.get("link", rss_url),
            "language": feed.feed.get("language", "zh"),
            "updated": feed.feed.get("updated", ""),
            "generator": feed.feed.get("generator", ""),
            "image_url": self._get_feed_image(feed),
            "author": feed.feed.get("author", ""),
            "rss_url": rss_url,
            "platform": self._detect_platform(rss_url),
        }
        
        # 清理和标准化数据
        feed_info["title"] = self._clean_text(feed_info["title"])
        feed_info["description"] = self._clean_text(feed_info["description"])
        
        return feed_info
    
    def _extract_episodes(self, feed: feedparser.FeedParserDict) -> List[Dict[str, Any]]:
        """提取剧集信息"""
        episodes = []
        
        for entry in feed.entries:
            try:
                episode = self._extract_single_episode(entry)
                if episode:
                    episodes.append(episode)
            except Exception as e:
                print(f"⚠️  跳过无法解析的剧集: {e}")
                continue
        
        # 按发布日期排序（最新的在前）
        episodes.sort(key=lambda x: x.get("published_parsed", (1970, 1, 1)), reverse=True)
        
        return episodes
    
    def _extract_single_episode(self, entry: feedparser.FeedParserDict) -> Optional[Dict[str, Any]]:
        """提取单个剧集信息"""
        # 获取标题
        title = entry.get("title", "未知标题")
        title = self._clean_text(title)
        
        if not title:
            return None
        
        # 获取发布日期
        published = entry.get("published", "")
        published_parsed = entry.get("published_parsed")
        
        # 获取描述
        description = ""
        if "summary" in entry:
            description = entry.summary
        elif "description" in entry:
            description = entry.description
        elif "content" in entry:
            # 尝试从content中提取
            for content in entry.content:
                if hasattr(content, "value"):
                    description = content.value
                    break
        
        description = self._clean_text(description)
        
        # 获取音频URL
        audio_url = self._find_audio_url(entry)
        
        # 获取剧集时长
        duration = self._extract_duration(entry)
        
        # 获取剧集编号
        episode_number = self._extract_episode_number(entry, title)
        
        # 生成唯一ID
        episode_id = self._generate_episode_id(entry, title, audio_url)
        
        return {
            "id": episode_id,
            "title": title,
            "description": description,
            "published": published,
            "published_parsed": published_parsed,
            "audio_url": audio_url,
            "duration": duration,
            "episode_number": episode_number,
            "link": entry.get("link", ""),
            "author": entry.get("author", ""),
            "guid": entry.get("id", ""),
            "enclosures": self._get_enclosures(entry),
        }
    
    def _find_audio_url(self, entry: feedparser.FeedParserDict) -> Optional[str]:
        """查找音频URL"""
        # 检查enclosures
        if hasattr(entry, "enclosures"):
            for enclosure in entry.enclosures:
                if enclosure.type.startswith("audio/"):
                    return enclosure.href
                elif enclosure.type.startswith("video/"):
                    # 有些播客使用video格式但实际上是音频
                    return enclosure.href
        
        # 检查links
        if hasattr(entry, "links"):
            for link in entry.links:
                if link.type.startswith("audio/"):
                    return link.href
        
        # 检查itunes扩展
        if hasattr(entry, "itunes_duration"):
            # 如果有itunes_duration，可能在其他字段中
            pass
        
        # 尝试从description中提取
        if hasattr(entry, "description"):
            import re
            desc = entry.description
            # 查找常见的音频URL模式
            audio_patterns = [
                r'https?://[^\s<>"\']+\.(mp3|m4a|wav|ogg|flac|aac)[^\s<>"\']*',
                r'src=["\']([^"\']+\.(mp3|m4a|wav|ogg|flac|aac))["\']',
            ]
            
            for pattern in audio_patterns:
                matches = re.findall(pattern, desc, re.IGNORECASE)
                if matches:
                    if isinstance(matches[0], tuple):
                        return matches[0][0]
                    else:
                        return matches[0]
        
        return None
    
    def _extract_duration(self, entry: feedparser.FeedParserDict) -> Optional[str]:
        """提取剧集时长"""
        # 检查itunes扩展
        if hasattr(entry, "itunes_duration"):
            duration = entry.itunes_duration
            if duration:
                # 标准化时长格式 (HH:MM:SS 或 MM:SS)
                parts = duration.split(":")
                if len(parts) == 3:
                    return duration  # HH:MM:SS
                elif len(parts) == 2:
                    # 可能是MM:SS，检查是否超过60分钟
                    minutes, seconds = map(int, parts)
                    if minutes >= 60:
                        hours = minutes // 60
                        minutes = minutes % 60
                        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        return f"00:{minutes:02d}:{seconds:02d}"
        
        return None
    
    def _extract_episode_number(self, entry: feedparser.FeedParserDict, title: str) -> Optional[int]:
        """提取剧集编号"""
        # 检查itunes扩展
        if hasattr(entry, "itunes_episode"):
            try:
                return int(entry.itunes_episode)
            except (ValueError, TypeError):
                pass
        
        # 从标题中提取
        import re
        patterns = [
            r'第\s*(\d+)\s*[期集回]',
            r'Episode\s*(\d+)',
            r'EP\.?\s*(\d+)',
            r'#\s*(\d+)',
            r'(\d+)\s*[\.\-\s]',  # 以数字开头
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _generate_episode_id(self, entry: feedparser.FeedParserDict, title: str, audio_url: str) -> str:
        """生成剧集唯一ID"""
        # 使用guid如果存在
        if hasattr(entry, "id") and entry.id:
            guid_hash = hashlib.md5(entry.id.encode()).hexdigest()[:12]
            return f"ep_{guid_hash}"
        
        # 使用标题和音频URL的组合
        id_string = f"{title}_{audio_url}" if audio_url else title
        title_hash = hashlib.md5(id_string.encode()).hexdigest()[:12]
        
        # 添加时间戳确保唯一性
        timestamp = int(time.time())
        
        return f"ep_{title_hash}_{timestamp}"
    
    def _get_enclosures(self, entry: feedparser.FeedParserDict) -> List[Dict[str, str]]:
        """获取所有附件信息"""
        enclosures = []
        
        if hasattr(entry, "enclosures"):
            for enc in entry.enclosures:
                enclosures.append({
                    "url": enc.href,
                    "type": enc.type,
                    "length": getattr(enc, "length", None),
                })
        
        return enclosures
    
    def _get_feed_image(self, feed: feedparser.FeedParserDict) -> Optional[str]:
        """获取feed图片URL"""
        # 检查itunes扩展
        if hasattr(feed.feed, "image"):
            if hasattr(feed.feed.image, "href"):
                return feed.feed.image.href
        
        # 检查其他图片字段
        image_fields = ["image", "logo", "icon"]
        for field in image_fields:
            if hasattr(feed.feed, field):
                value = getattr(feed.feed, field)
                if isinstance(value, str) and value.startswith("http"):
                    return value
        
        return None
    
    def _detect_platform(self, rss_url: str) -> str:
        """检测播客平台"""
        parsed_url = urlparse(rss_url)
        domain = parsed_url.netloc.lower()
        
        for platform, patterns in self.platform_patterns.items():
            for pattern in patterns:
                if pattern in domain:
                    return platform
        
        return "unknown"
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        if not text:
            return ""
        
        # 移除HTML标签
        import re
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # 移除多余空白
        text = ' '.join(text.split())
        
        # 限制长度
        if len(text) > 1000:
            text = text[:1000] + "..."
        
        return text.strip()
    
    def get_latest_episodes(self, rss_url: str, limit: int = 5) -> List[Dict[str, Any]]:
        """获取最新剧集"""
        feed_data = self.parse_feed(rss_url)
        return feed_data["episodes"][:limit]
    
    def check_for_new_episodes(self, rss_url: str, last_check_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """检查新剧集"""
        feed_data = self.parse_feed(rss_url)
        
        if not last_check_time:
            return feed_data["episodes"][:5]  # 返回最新的5个
        
        new_episodes = []
        for episode in feed_data["episodes"]:
            published = episode.get("published_parsed")
            if published:
                # 将published_parsed转换为datetime
                from time import mktime
                from datetime import datetime as dt
                episode_time = dt.fromtimestamp(mktime(published))
                
                if episode_time > last_check_time:
                    new_episodes.append(episode)
        
        return new_episodes


# 便捷函数
def parse_rss_feed(rss_url: str) -> Dict[str, Any]:
    """解析RSS feed的便捷函数"""
    parser = RSSParser()
    return parser.parse_feed(rss_url)


def get_latest_episodes(rss_url: str, limit: int = 5) -> List[Dict[str, Any]]:
    """获取最新剧集的便捷函数"""
    parser = RSSParser()
    return parser.get_latest_episodes(rss_url, limit)


def save_feed_to_json(feed_data: Dict[str, Any], filepath: str) -> None:
    """保存feed数据到JSON文件"""
    import json
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(feed_data, f, ensure_ascii=False, indent=2, default=str)


def load_feed_from_json(filepath: str) -> Dict[str, Any]:
    """从JSON文件加载feed数据"""
    import json
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    # 测试代码
    import argparse
    
    parser = argparse.ArgumentParser(description="RSS解析测试")
    parser.add_argument("--url", required=True, help="RSS feed URL")
    parser.add_argument("--limit", type=int, default=3, help="显示最新几期")
    parser.add_argument("--save", help="保存到JSON文件")
    
    args = parser.parse_args()
    
    try:
        print("=" * 60)
        print("📡 RSS解析测试")
        print("=" * 60)
        
        # 解析feed
        feed_data = parse_rss_feed(args.url)
        
        # 显示feed信息
        feed_info = feed_data["feed_info"]
        print(f"\n🎙️  播客信息:")
        print(f"  标题: {feed_info['title']}")
        print(f"  描述: {feed_info['description'][:100]}..." if len(feed_info['description']) > 100 else f"  描述: {feed_info['description']}")
        print(f"  平台: {feed_info['platform']}")
        print(f"  语言: {feed_info['language']}")
        print(f"  总期数: {feed_data['total_episodes']}")
        
        # 显示最新剧集
        print(f"\n📋 最新 {args.limit} 期:")
        for i, episode in enumerate(feed_data["episodes"][:args.limit], 1):
            print(f"\n  {i}. {episode['title']}")
            print(f"     发布日期: {episode['published']}")
            if episode['duration']:
                print(f"     时长: {episode['duration']}")
            if episode['episode_number']:
                print(f"     期号: {episode['episode_number']}")
            if episode['audio_url']:
                print(f"     音频: {episode['audio_url'][:80]}..." if len(episode['audio_url']) > 80 else f"     音频: {episode['audio_url']}")
        
        # 保存到文件
        if args.save:
            save_feed_to_json(feed_data, args.save)
            print(f"\n💾 已保存到: {args.save}")
        
        print("\n" + "=" * 60)
        print("✅ RSS解析测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ RSS解析失败: {e}")
        print("\n💡 故障排除:")
        print("1. 检查URL是否正确")
        print("2. 检查网络连接")
        print("3. 尝试使用代理")
        print("4. 确认RSS feed可公开访问")