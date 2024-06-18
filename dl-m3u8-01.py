# 代码来自: https://www.cnblogs.com/yuzhihui/p/17443299.html
# 基础实现
# 运行 python3 dl-m3u8-01.py
#EXTM3U
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2000000,RESOLUTION=1920x1040
#/20231011/gSsDaQr1/2000kb/hls/index.m3u8
#https://v9.dious.cc/20231011/gSsDaQr1/2000kb/hls/index.m3u8
import requests
import os
from tqdm import tqdm
from urllib.parse import urljoin

def download_m3u8_video(url, file_path):
    r = requests.get(url)
    if r.status_code != 200:
        print('m3u8视频下载链接无效')
        return False

    m3u8_list = r.text.split('\n')
    m3u8_list = [i for i in m3u8_list if i and i[0] != '#']
    ts_list = []

    for line in m3u8_list:
        if line.endswith('.m3u8'):
            print(f"正在重定向解析: {line}")
            nested_url = urljoin(url, line)
            nested_ts_list = download_nested_m3u8(nested_url)
            ts_list.extend(nested_ts_list)
        else:
            ts_url = urljoin(url, line)
            ts_list.append(ts_url)

    print(f"解析到 {len(ts_list)} 个ts文件,准备下载.")
    with open(file_path, 'wb') as f:
        index=0
        for ts_url in tqdm(ts_list, desc="Downloading", unit="file"):
            index=index+1
            #print(f"准备下载: {index} of {len(ts_list)}, {ts_url}")
            r = requests.get(ts_url,stream=True)
            if r.status_code == 200:
                #print(f"内容长度: {len(r.content)}")  
                #f.write(r.content)
                #print(f"写入文件完成")
                total_length = int(r.headers.get('content-length'))
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            else:
                print(f"下载失败: {ts_url}")   
    print('m3u8视频下载完成')
    return True

def download_nested_m3u8(url):
    r = requests.get(url)
    if r.status_code != 200:
        print(f'嵌套m3u8视频下载链接无效: {url}')
        return []

    m3u8_list = r.text.split('\n')
    m3u8_list = [i for i in m3u8_list if i and i[0] != '#']
    ts_list = []

    for line in m3u8_list:
        ts_url = urljoin(url, line)
        ts_list.append(ts_url)

    return ts_list

def convert_ts_to_mp4(ts_file_path, mp4_file_path):
    os.system(f'ffmpeg -i {ts_file_path} -c copy {mp4_file_path}')

if __name__ == '__main__':
    #url = 'https://v9.dious.cc/20231011/gSsDaQr1/2000kb/hls/index.m3u8'
    url = 'https://v9.dious.cc/20231011/gSsDaQr1/index.m3u8'
    ts_file_path = '/Users/duanqs/Downloads/m3u8/video.ts'
    mp4_file_path = '/Users/duanqs/Downloads/m3u8/video.mp4'

    download_m3u8_video(url, ts_file_path)
    #convert_ts_to_mp4(ts_file_path, mp4_file_path)