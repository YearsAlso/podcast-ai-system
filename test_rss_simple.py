#!/usr/bin/env python3
"""
简单的RSS解析测试
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rss_parser import RSSParser

def main():
    print("🧪 简单RSS解析测试")
    print("=" * 60)
    
    # 创建一个简单的测试RSS内容
    test_rss_content = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
<title>测试播客</title>
<description>这是一个测试播客</description>
<language>zh</language>
<item>
<title>测试期1: RSS解析功能</title>
<description>本期讨论RSS解析功能的实现</description>
<pubDate>Mon, 15 Jan 2024 10:30:00 GMT</pubDate>
<enclosure url="https://example.com/audio1.mp3" type="audio/mpeg" length="1234567"/>
</item>
<item>
<title>测试期2: Markdown生成</title>
<description>本期讨论Markdown文件生成</description>
<pubDate>Tue, 16 Jan 2024 11:00:00 GMT</pubDate>
<enclosure url="https://example.com/audio2.mp3" type="audio/mpeg" length="2345678"/>
</item>
</channel>
</rss>'''
    
    # 保存到临时文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(test_rss_content)
        temp_file = f.name
    
    try:
        # 使用文件URL测试
        file_url = f"file://{temp_file}"
        print(f"📁 测试文件: {temp_file}")
        
        parser = RSSParser()
        
        # 测试解析
        print("\n📡 解析测试RSS...")
        feed_data = parser.parse_feed(file_url)
        
        print(f"✅ 解析成功!")
        print(f"🎙️  播客: {feed_data['feed_info']['title']}")
        print(f"📝 描述: {feed_data['feed_info']['description']}")
        print(f"📊 期数: {feed_data['total_episodes']}")
        
        # 显示剧集
        print("\n📋 剧集列表:")
        for i, episode in enumerate(feed_data['episodes'], 1):
            print(f"  {i}. {episode['title']}")
            print(f"     音频URL: {episode.get('audio_url', '无')}")
            print(f"     发布日期: {episode.get('published', '未知')}")
        
        print("\n" + "=" * 60)
        print("✅ 简单测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理临时文件
        if os.path.exists(temp_file):
            os.unlink(temp_file)

if __name__ == "__main__":
    main()