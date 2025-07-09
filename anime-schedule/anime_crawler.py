import os
import re
import json
import requests
from bs4 import BeautifulSoup

WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
FILENAME = "A2025_7_animes"
url = "https://yuc.wiki/202507"


def find_weekday_for_block(block):
    """向前查找最近的星期标识"""
    current = block

    # 向前查找前面的兄弟元素，寻找包含星期信息的div
    while current:
        # 查找前一个兄弟元素
        prev_sibling = current.find_previous_sibling()
        if prev_sibling:
            # 在前一个元素中查找 td.date2
            date_td = prev_sibling.find('td', class_='date2')
            if date_td:
                date_text = date_td.get_text(strip=True)
                weekday = parse_weekday_text(date_text)
                if weekday != "unknown":
                    return weekday
            current = prev_sibling
        else:
            # 如果没有前一个兄弟元素，向上查找父元素
            parent = current.find_parent()
            if parent and parent.name != 'html':
                current = parent
            else:
                break

    return "unknown"


def parse_weekday_text(text):
    """从文本中解析星期几"""
    weekday_map = {
        '周一': 'monday', '月': 'monday',
        '周二': 'tuesday', '火': 'tuesday',
        '周三': 'wednesday', '水': 'wednesday',
        '周四': 'thursday', '木': 'thursday',
        '周五': 'friday', '金': 'friday',
        '周六': 'saturday', '土': 'saturday',
        '周日': 'sunday', '周天': 'sunday', '日': 'sunday'
    }

    for key, value in weekday_map.items():
        if key in text:
            return value

    return "unknown"


def crawl_yuc_online(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    weekly_data = {day: [] for day in WEEKDAYS}
    anime_blocks = soup.find_all('div', class_='div_date')

    for block in anime_blocks:
        try:
            # 时间 & 集数 - 添加空值检查
            time_elem = block.find('p', class_='imgtext4')
            time_text = time_elem.get_text(strip=True) if time_elem else "未知时间"

            episode_elem = block.find('p', class_='imgep')
            episode_info = episode_elem.get_text(strip=True) if episode_elem else "未知集数"

            # 图片链接 - 添加空值检查
            img_tag = block.find('img')
            image_url = ""
            if img_tag:
                image_url = img_tag.get('data-src') or img_tag.get('src') or ""
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url

            # 动画信息在后面div - 添加空值检查
            next_div = block.find_next_sibling('div')
            if not next_div:
                print(f"⚠️ 未找到后续div，跳过此条目")
                continue

            # 根据你提供的结构，标题在table->tr->td中
            title_td = next_div.find('td', class_=re.compile(r'date_title'))
            if not title_td:
                # 如果没找到，尝试其他可能的class名称
                title_td = next_div.find('td', class_='date_title_')

            if not title_td:
                print(f"⚠️ 未找到标题元素，跳过此条目")
                continue

            # 动画标题（可能有链接）
            link_tag = title_td.find('a')
            title = link_tag.get_text(strip=True) if link_tag else title_td.get_text(strip=True)
            title = title.replace('\n', ' ').replace('<br>', ' ').strip()  # 处理换行

            if not title:
                print(f"⚠️ 标题为空，跳过此条目")
                continue

            # 星期判断 - 向前查找最近的星期标识
            weekday = find_weekday_for_block(block)
            if weekday == "unknown":
                print(f"⚠️ 未能确定星期信息: {title}")

            # 图片保存
            local_image = download_image(image_url, title) if image_url else ""

            # 构造条目
            entry = {
                "title": title,
                "time": time_text,
                "episodes": episode_info,
                "image": local_image,
                "god": "字幕组:",
                "ladder": "no",
                "url": "",
                "isWatch":"no"
            }

            if weekday in WEEKDAYS:
                weekly_data[weekday].append(entry)
            else:
                # 如果无法确定星期，放入一个默认分类
                if 'unknown' not in weekly_data:
                    weekly_data['unknown'] = []
                weekly_data['unknown'].append(entry)

            print(f"✅ 成功解析: {title} - {weekday}")

        except Exception as e:
            print(f"❌ 动画解析失败：{e}")
            # 打印更详细的错误信息用于调试
            import traceback
            traceback.print_exc()

    return weekly_data


def download_image(url, title):
    try:
        if not url:
            return ""
        os.makedirs(f'data/{FILENAME}/images', exist_ok=True)
        # 更安全的文件名处理
        safe_title = re.sub(r'[^\w\s-]', '', title.replace(' ', '_'))[:30]
        if not safe_title:  # 如果处理后文件名为空
            safe_title = "untitled"
        filepath = f"data/{FILENAME}/images/{safe_title}.jpg"

        if os.path.exists(filepath):
            return filepath

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            f.write(response.content)

        print(f"✅ 已保存图片: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ 下载图片失败：{url} - {e}")
        return ""


def save_json(data, filename=f"data/{FILENAME}/{FILENAME}.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"✅ 已保存信息到 {filename}")


def main():
    data = crawl_yuc_online(url)
    save_json(data)

    # 打印统计信息
    total_count = sum(len(animes) for animes in data.values())
    print(f"\n📊 爬取统计:")
    for day, animes in data.items():
        if animes:
            print(f"  {day}: {len(animes)} 部动画")
    print(f"  总计: {total_count} 部动画")


if __name__ == '__main__':
    main()
