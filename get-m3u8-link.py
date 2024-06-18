# 从网页中获取视频播放地址
# python3 -m pip install requests beautifulsoup4 lxml
# 运行 python3 index.py

import requests
from bs4 import BeautifulSoup
import re

# 测试网址
url = 'https://91mjw.tv/vplay/MDkxMDcyMS0yLWhk.html'
url = 'https://91mjw.tv/vplay/MTYxMDcwNy0xMy1oZA==.html'
# 获取网页内容
response = requests.get(url)
html_content = response.text

# 解析HTML内容
soup = BeautifulSoup(html_content, 'lxml')

# 提取视频链接
video_links = []

# 查找<video>标签中的视频链接
for video in soup.find_all('video'):
    if video.has_attr('src'):
        video_links.append(video['src'])
    for source in video.find_all('source'):
        if source.has_attr('src'):
            video_links.append(source['src'])

# 使用正则表达式匹配常见的视频链接格式
video_links += re.findall(r'(https?://\S+\.(?:mp4|webm|ogg|m3u8))', html_content)

# 去重
video_links = list(set(video_links))

# 输出视频链接
print("找到的视频链接：")
for link in video_links:
    print(link)
