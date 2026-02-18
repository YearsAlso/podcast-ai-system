#!/usr/bin/env python3
"""
Markdown文件生成器 - 将播客信息保存为Markdown文件
"""

import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

from config import PODCASTS_DIR


class MarkdownGeneratorError(Exception):
    """Markdown生成错误异常"""
    pass


class MarkdownGenerator:
    """Markdown文件生成器"""
    
    def __init__(self, base_dir: str = PODCASTS_DIR):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
    
    def generate_episode_markdown(self, feed_info: Dict[str, Any], episode: Dict[str, Any]) -> str:
        """生成单期播客的Markdown内容"""
        
        # 提取基本信息
        podcast_title = feed_info.get("title", "未知播客")
        episode_title = episode.get("title", "未知标题")
        episode_number = episode.get("episode_number")
        published = episode.get("published", "")
        description = episode.get("description", "")
        audio_url = episode.get("audio_url", "")
        duration = episode.get("duration", "")
        author = episode.get("author", feed_info.get("author", ""))
        
        # 生成YAML frontmatter
        frontmatter = self._generate_frontmatter(
            podcast_title=podcast_title,
            episode_title=episode_title,
            episode_number=episode_number,
            published=published,
            audio_url=audio_url,
            duration=duration,
            author=author,
            feed_info=feed_info,
            episode=episode,
        )
        
        # 生成Markdown内容
        content = self._generate_content(
            podcast_title=podcast_title,
            episode_title=episode_title,
            episode_number=episode_number,
            published=published,
            description=description,
            audio_url=audio_url,
            duration=duration,
            author=author,
            feed_info=feed_info,
            episode=episode,
        )
        
        return frontmatter + content
    
    def _generate_frontmatter(self, **kwargs) -> str:
        """生成YAML frontmatter"""
        podcast_title = kwargs.get("podcast_title", "")
        episode_title = kwargs.get("episode_title", "")
        episode_number = kwargs.get("episode_number")
        published = kwargs.get("published", "")
        audio_url = kwargs.get("audio_url", "")
        duration = kwargs.get("duration", "")
        author = kwargs.get("author", "")
        
        frontmatter_lines = [
            "---",
            f"title: \"{episode_title}\"",
            f"podcast: \"{podcast_title}\"",
        ]
        
        if episode_number:
            frontmatter_lines.append(f"episode_number: {episode_number}")
        
        if published:
            # 尝试解析日期
            try:
                from dateutil import parser
                pub_date = parser.parse(published)
                frontmatter_lines.append(f"published_date: \"{pub_date.date().isoformat()}\"")
                frontmatter_lines.append(f"published_time: \"{pub_date.time().isoformat()}\"")
            except:
                frontmatter_lines.append(f"published: \"{published}\"")
        
        if audio_url:
            frontmatter_lines.append(f"audio_url: \"{audio_url}\"")
        
        if duration:
            frontmatter_lines.append(f"duration: \"{duration}\"")
        
        if author:
            frontmatter_lines.append(f"author: \"{author}\"")
        
        # 添加标签
        tags = ["播客", podcast_title]
        if episode_number:
            tags.append(f"第{episode_number}期")
        
        frontmatter_lines.append(f"tags: {json.dumps(tags, ensure_ascii=False)}")
        
        # 添加处理信息
        frontmatter_lines.append(f"processed_date: \"{datetime.now().isoformat()}\"")
        
        frontmatter_lines.append("---\n")
        
        return "\n".join(frontmatter_lines)
    
    def _generate_content(self, **kwargs) -> str:
        """生成Markdown内容"""
        podcast_title = kwargs.get("podcast_title", "")
        episode_title = kwargs.get("episode_title", "")
        episode_number = kwargs.get("episode_number")
        published = kwargs.get("published", "")
        description = kwargs.get("description", "")
        audio_url = kwargs.get("audio_url", "")
        duration = kwargs.get("duration", "")
        author = kwargs.get("author", "")
        
        content_lines = []
        
        # 标题
        if episode_number:
            content_lines.append(f"# 第{episode_number}期：{episode_title}")
        else:
            content_lines.append(f"# {episode_title}")
        
        content_lines.append("")
        
        # 元信息表格
        content_lines.append("## 📋 播客信息")
        content_lines.append("")
        content_lines.append("| 项目 | 内容 |")
        content_lines.append("|------|------|")
        content_lines.append(f"| 播客 | {podcast_title} |")
        
        if episode_number:
            content_lines.append(f"| 期号 | 第{episode_number}期 |")
        
        if published:
            content_lines.append(f"| 发布日期 | {published} |")
        
        if duration:
            content_lines.append(f"| 时长 | {duration} |")
        
        if author:
            content_lines.append(f"| 作者/主播 | {author} |")
        
        if audio_url:
            content_lines.append(f"| 音频链接 | [{audio_url[:50]}...]({audio_url}) |")
        
        content_lines.append("")
        
        # 描述
        if description:
            content_lines.append("## 📝 内容描述")
            content_lines.append("")
            content_lines.append(description)
            content_lines.append("")
        
        # 音频播放（如果支持）
        if audio_url:
            content_lines.append("## 🎵 音频播放")
            content_lines.append("")
            content_lines.append(f"音频链接: [{audio_url}]({audio_url})")
            content_lines.append("")
            
            # 添加HTML音频播放器（如果平台支持）
            if audio_url.endswith(('.mp3', '.m4a', '.wav', '.ogg')):
                content_lines.append("```html")
                content_lines.append(f'<audio controls src="{audio_url}">')
                content_lines.append('  您的浏览器不支持音频播放')
                content_lines.append('</audio>')
                content_lines.append("```")
                content_lines.append("")
        
        # 处理信息
        content_lines.append("## 🔧 处理信息")
        content_lines.append("")
        content_lines.append(f"- 处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content_lines.append("- 来源: RSS解析")
        content_lines.append("")
        
        return "\n".join(content_lines)
    
    def save_episode_markdown(self, feed_info: Dict[str, Any], episode: Dict[str, Any], 
                             output_dir: Optional[str] = None) -> str:
        """保存单期播客为Markdown文件"""
        
        podcast_title = feed_info.get("title", "未知播客")
        episode_title = episode.get("title", "未知标题")
        episode_number = episode.get("episode_number")
        
        # 确定输出目录
        if output_dir:
            save_dir = output_dir
        else:
            # 使用播客名称作为子目录
            safe_podcast_name = self._safe_filename(podcast_title)
            save_dir = os.path.join(self.base_dir, safe_podcast_name)
        
        os.makedirs(save_dir, exist_ok=True)
        
        # 生成文件名
        filename = self._generate_filename(feed_info, episode)
        filepath = os.path.join(save_dir, filename)
        
        # 生成Markdown内容
        markdown_content = self.generate_episode_markdown(feed_info, episode)
        
        # 保存文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        return filepath
    
    def save_feed_summary(self, feed_data: Dict[str, Any], output_dir: Optional[str] = None) -> str:
        """保存feed摘要为Markdown文件"""
        
        feed_info = feed_data["feed_info"]
        episodes = feed_data["episodes"]
        podcast_title = feed_info.get("title", "未知播客")
        
        # 确定输出目录
        if output_dir:
            save_dir = output_dir
        else:
            safe_podcast_name = self._safe_filename(podcast_title)
            save_dir = os.path.join(self.base_dir, safe_podcast_name)
        
        os.makedirs(save_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = self._safe_filename(podcast_title)
        filename = f"{safe_title}_feed_summary_{timestamp}.md"
        filepath = os.path.join(save_dir, filename)
        
        # 生成摘要内容
        content = self._generate_feed_summary(feed_data)
        
        # 保存文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return filepath
    
    def _generate_feed_summary(self, feed_data: Dict[str, Any]) -> str:
        """生成feed摘要内容"""
        feed_info = feed_data["feed_info"]
        episodes = feed_data["episodes"]
        
        podcast_title = feed_info.get("title", "未知播客")
        description = feed_info.get("description", "")
        platform = feed_info.get("platform", "unknown")
        language = feed_info.get("language", "zh")
        total_episodes = len(episodes)
        
        content_lines = [
            f"# {podcast_title} - RSS Feed摘要",
            "",
            "## 📊 Feed信息",
            "",
            f"- **标题**: {podcast_title}",
            f"- **描述**: {description[:200]}..." if len(description) > 200 else f"- **描述**: {description}",
            f"- **平台**: {platform}",
            f"- **语言**: {language}",
            f"- **总期数**: {total_episodes}",
            f"- **RSS URL**: {feed_info.get('rss_url', '')}",
            f"- **解析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 📋 最新剧集",
            "",
        ]
        
        # 添加最新10期
        for i, episode in enumerate(episodes[:10], 1):
            episode_title = episode.get("title", "未知标题")
            episode_number = episode.get("episode_number")
            published = episode.get("published", "")
            duration = episode.get("duration", "")
            
            if episode_number:
                content_lines.append(f"{i}. **第{episode_number}期**: {episode_title}")
            else:
                content_lines.append(f"{i}. {episode_title}")
            
            if published:
                content_lines.append(f"   - 发布日期: {published}")
            if duration:
                content_lines.append(f"   - 时长: {duration}")
            
            content_lines.append("")
        
        # 添加统计信息
        content_lines.append("## 📈 统计信息")
        content_lines.append("")
        
        # 计算有音频URL的剧集数量
        episodes_with_audio = sum(1 for ep in episodes if ep.get("audio_url"))
        content_lines.append(f"- 有音频链接的剧集: {episodes_with_audio}/{total_episodes}")
        
        # 计算有期号的剧集数量
        episodes_with_number = sum(1 for ep in episodes if ep.get("episode_number"))
        content_lines.append(f"- 有期号的剧集: {episodes_with_number}/{total_episodes}")
        
        # 计算有时长的剧集数量
        episodes_with_duration = sum(1 for ep in episodes if ep.get("duration"))
        content_lines.append(f"- 有时长的剧集: {episodes_with_duration}/{total_episodes}")
        
        content_lines.append("")
        content_lines.append("---")
        content_lines.append(f"*生成时间: {datetime.now().isoformat()}*")
        
        return "\n".join(content_lines)
    
    def _generate_filename(self, feed_info: Dict[str, Any], episode: Dict[str, Any]) -> str:
        """生成文件名"""
        podcast_title = feed_info.get("title", "未知播客")
        episode_title = episode.get("title", "未知标题")
        episode_number = episode.get("episode_number")
        published = episode.get("published", "")
        
        # 安全化文件名
        safe_podcast = self._safe_filename(podcast_title)[:30]
        safe_episode = self._safe_filename(episode_title)[:50]
        
        # 尝试从发布日期提取日期
        date_part = ""
        if published:
            try:
                from dateutil import parser
                pub_date = parser.parse(published)
                date_part = pub_date.strftime("%Y-%m-%d")
            except:
                pass
        
        if not date_part:
            date_part = datetime.now().strftime("%Y-%m-%d")
        
        # 构建文件名
        if episode_number:
            filename = f"{date_part}_{safe_podcast}_第{episode_number}期_{safe_episode}.md"
        else:
            filename = f"{date_part}_{safe_podcast}_{safe_episode}.md"
        
        # 限制文件名长度
        if len(filename) > 150:
            # 缩短剧集标题部分
            max_episode_len = 150 - len(f"{date_part}_{safe_podcast}_...md")
            safe_episode = safe_episode[:max_episode_len]
            
            if episode_number:
                filename = f"{date_part}_{safe_podcast}_第{episode_number}期_{safe_episode}.md"
            else:
                filename = f"{date_part}_{safe_podcast}_{safe_episode}.md"
        
        return filename
    
    def _safe_filename(self, text: str) -> str:
        """将文本转换为安全的文件名"""
        if not text:
            return ""
        
        # 替换不安全字符
        unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\n', '\r', '\t']
        for char in unsafe_chars:
            text = text.replace(char, '_')
        
        # 移除多余空格和下划线
        text = ' '.join(text.split())
        text = text.replace(' ', '_')
        
        return text


# 便捷函数
def save_episode_to_markdown(feed_info: Dict[str, Any], episode: Dict[str, Any], 
                           output_dir: Optional[str] = None) -> str:
    """保存单期播客为Markdown文件的便捷函数"""
    generator = MarkdownGenerator()
    return generator.save_episode_markdown(feed_info, episode, output_dir)


def save_feed_summary_to_markdown(feed_data: Dict[str, Any], output_dir: Optional[str] = None) -> str:
    """保存feed摘要为Markdown文件的便捷函数"""
    generator = MarkdownGenerator()
    return generator.save_feed_summary(feed_data, output_dir)


if __name__ == "__main__":
    # 测试代码
    import argparse
    
    parser = argparse.ArgumentParser(description="Markdown生成测试")
    parser.add_argument("--json", required=True, help="包含feed数据的JSON文件")
    parser.add_argument("--episode", type=int, default=0, help="要保存的剧集索引（0表示最新）")
    parser.add_argument("--output", help="输出目录（默认使用配置的PODCASTS_DIR）")
    parser.add_argument("--summary", action="store_true", help="生成feed摘要")
    
    args = parser.parse_args()
    
    try:
        print("=" * 60)
        print("📝 Markdown生成测试")
        print("=" * 60)
        
        # 加载feed数据
        import json
        with open(args.json, "r", encoding="utf-8") as f:
            feed_data = json.load(f)
        
        feed_info = feed_data["feed_info"]
        episodes = feed_data["episodes"]
        
        print(f"\n🎙️  播客: {feed_info['title']}")
        print(f"📋 总期数: {len(episodes)}")
        
        if args.summary:
            # 生成feed摘要
            print("\n📊 生成feed摘要...")
            filepath = save_feed_summary_to_markdown(feed_data, args.output)
            print(f"✅ 已保存摘要到: {filepath}")
        
        else:
            # 生成单期播客
            if args.episode < 0 or args.episode >= len(episodes):
                print(f"⚠️  剧集索引 {args.episode} 无效，使用最新一期")
                episode_idx = 0
            else:
                episode_idx = args.episode
            
            episode = episodes[episode_idx]
            print(f"\n📄 生成剧集: {episode['title']}")
            
            filepath = save_episode_to_markdown(feed_info, episode, args.output)
            print(f"✅ 已保存到: {filepath}")
            
            # 显示文件大小
            file_size = os.path.getsize(filepath)
            print(f"📏 文件大小: {file_size} 字节")
        
        print("\n" + "=" * 60)
        print("✅ Markdown生成测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Markdown生成失败: {e}")
        import traceback
        traceback.print_exc()