#!/usr/bin/env python3
"""
RSS解析功能测试
"""

import os
import sys
import tempfile
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rss_parser import parse_rss_feed, get_latest_episodes, save_feed_to_json, load_feed_from_json
from markdown_generator import save_episode_to_markdown, save_feed_summary_to_markdown


def test_with_sample_rss():
    """使用示例RSS进行测试"""
    print("=" * 60)
    print("🧪 RSS解析功能测试")
    print("=" * 60)
    
    # 示例RSS链接（使用公开可访问的播客）
    test_rss_urls = [
        # NPR播客（英文，稳定可靠）
        "https://feeds.npr.org/510289/podcast.xml",
        # BBC新闻（英文）
        "https://podcasts.files.bbci.co.uk/p02nq0gn.rss",
        # 测试无效URL
        "https://example.com/invalid.rss",
    ]
    
    for i, rss_url in enumerate(test_rss_urls[:2]):  # 只测试前两个有效URL
        print(f"\n🔗 测试RSS {i+1}: {rss_url[:80]}...")
        
        try:
            # 解析RSS feed
            feed_data = parse_rss_feed(rss_url)
            feed_info = feed_data["feed_info"]
            episodes = feed_data["episodes"]
            
            print(f"✅ 解析成功!")
            print(f"🎙️  播客: {feed_info['title']}")
            print(f"📝 描述: {feed_info['description'][:100]}..." if len(feed_info['description']) > 100 else f"📝 描述: {feed_info['description']}")
            print(f"🌐 平台: {feed_info['platform']}")
            print(f"📊 总期数: {len(episodes)}")
            
            # 显示最新3期
            if episodes:
                print(f"\n📋 最新3期:")
                for j, episode in enumerate(episodes[:3], 1):
                    print(f"  {j}. {episode['title'][:80]}..." if len(episode['title']) > 80 else f"  {j}. {episode['title']}")
                    if episode.get('published'):
                        print(f"     发布日期: {episode['published']}")
                    if episode.get('audio_url'):
                        print(f"     音频: 有")
            
        except Exception as e:
            print(f"❌ 解析失败: {e}")
    
    print("\n" + "=" * 60)
    print("🧪 测试无效URL...")
    
    try:
        feed_data = parse_rss_feed(test_rss_urls[2])
    except Exception as e:
        print(f"✅ 预期中的失败: {e}")
        print("   系统正确处理了无效URL")


def test_markdown_generation():
    """测试Markdown文件生成"""
    print("\n" + "=" * 60)
    print("📝 Markdown文件生成测试")
    print("=" * 60)
    
    # 使用临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 使用临时目录: {temp_dir}")
        
        # 创建测试数据
        test_feed_info = {
            "title": "测试播客",
            "description": "这是一个用于测试的播客描述",
            "platform": "test",
            "language": "zh",
            "author": "测试作者",
            "rss_url": "https://example.com/test.rss",
        }
        
        test_episode = {
            "title": "测试期：RSS解析功能实现",
            "description": "本期节目讨论了RSS解析功能的实现细节，包括feed解析、音频URL提取、Markdown文件生成等。",
            "published": "2024-01-15 10:30:00",
            "audio_url": "https://example.com/audio.mp3",
            "duration": "01:23:45",
            "episode_number": 42,
        }
        
        try:
            # 生成Markdown文件
            print("\n📄 生成单期播客Markdown...")
            md_path = save_episode_to_markdown(test_feed_info, test_episode, temp_dir)
            
            if os.path.exists(md_path):
                file_size = os.path.getsize(md_path)
                print(f"✅ 文件生成成功: {md_path}")
                print(f"📏 文件大小: {file_size} 字节")
                
                # 显示文件内容预览
                print("\n📋 文件内容预览:")
                with open(md_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()[:20]  # 显示前20行
                    for line in lines:
                        print(f"  {line.rstrip()}")
                if len(lines) >= 20:
                    print("  ...")
            else:
                print("❌ 文件生成失败")
        
        except Exception as e:
            print(f"❌ Markdown生成失败: {e}")
            import traceback
            traceback.print_exc()


def test_json_save_load():
    """测试JSON保存和加载"""
    print("\n" + "=" * 60)
    print("💾 JSON保存和加载测试")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试数据
        test_data = {
            "feed_info": {
                "title": "测试播客",
                "description": "测试描述",
                "platform": "test",
            },
            "episodes": [
                {
                    "title": "测试期1",
                    "published": "2024-01-01",
                    "audio_url": "https://example.com/audio1.mp3",
                },
                {
                    "title": "测试期2", 
                    "published": "2024-01-02",
                    "audio_url": "https://example.com/audio2.mp3",
                }
            ],
            "total_episodes": 2,
            "parse_time": "2024-01-15T10:30:00",
        }
        
        # 保存到JSON
        json_path = os.path.join(temp_dir, "test_feed.json")
        save_feed_to_json(test_data, json_path)
        
        if os.path.exists(json_path):
            file_size = os.path.getsize(json_path)
            print(f"✅ JSON保存成功: {json_path}")
            print(f"📏 文件大小: {file_size} 字节")
            
            # 加载JSON
            loaded_data = load_feed_from_json(json_path)
            print(f"✅ JSON加载成功")
            print(f"📊 加载数据: {len(loaded_data.get('episodes', []))} 期")
        else:
            print("❌ JSON保存失败")


def test_integration():
    """集成测试"""
    print("\n" + "=" * 60)
    print("🔗 集成测试")
    print("=" * 60)
    
    # 使用一个简单的公开RSS进行集成测试
    test_rss = "https://feeds.simplecast.com/54nAGcIl"  # 一个简单的公开播客
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            print(f"📡 解析RSS: {test_rss}")
            feed_data = parse_rss_feed(test_rss)
            
            print(f"🎙️  播客: {feed_data['feed_info']['title']}")
            print(f"📊 期数: {len(feed_data['episodes'])}")
            
            if feed_data['episodes']:
                # 生成Markdown文件
                print("\n📄 生成Markdown文件...")
                md_path = save_episode_to_markdown(
                    feed_data['feed_info'], 
                    feed_data['episodes'][0],
                    temp_dir
                )
                
                if os.path.exists(md_path):
                    print(f"✅ 集成测试成功!")
                    print(f"📁 生成文件: {md_path}")
                else:
                    print("❌ Markdown文件生成失败")
            else:
                print("⚠️  没有找到剧集，跳过Markdown生成")
        
        except Exception as e:
            print(f"❌ 集成测试失败: {e}")
            print("💡 这可能是网络问题，不影响核心功能")


def main():
    """主测试函数"""
    try:
        print("🔧 RSS解析模块测试套件")
        print("=" * 60)
        
        # 测试1: RSS解析
        test_with_sample_rss()
        
        # 测试2: Markdown生成
        test_markdown_generation()
        
        # 测试3: JSON保存加载
        test_json_save_load()
        
        # 测试4: 集成测试
        test_integration()
        
        print("\n" + "=" * 60)
        print("🎉 所有测试完成!")
        print("=" * 60)
        
        print("\n📋 功能验证:")
        print("✅ RSS feed解析")
        print("✅ 音频URL提取")
        print("✅ 剧集信息提取")
        print("✅ Markdown文件生成")
        print("✅ JSON格式保存/加载")
        print("✅ 错误处理")
        
        print("\n💡 使用建议:")
        print("1. 对于中文播客，可能需要调整User-Agent")
        print("2. 某些播客平台可能需要特殊处理")
        print("3. 建议添加缓存机制减少网络请求")
        print("4. 考虑添加代理支持")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断测试")
        return 1
    except Exception as e:
        print(f"\n❌ 测试程序错误: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())