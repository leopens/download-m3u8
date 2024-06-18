import requests
import os
from tqdm import tqdm
from urllib.parse import urljoin

def download_m3u8_video(url, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

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
    for index, ts_url in enumerate(ts_list, start=1):
        ts_filename = f"video_{index}.ts"
        ts_filepath = os.path.join(output_dir, ts_filename)
        if os.path.exists(ts_filepath):
            print(f"文件已存在: {ts_filepath}")
            continue
        
        print(f"正在下载: {index} of {len(ts_list)}, {ts_url}")
        download_ts_segment(ts_url, ts_filepath)
            
    print('m3u8视频下载完成')
    return True

def download_ts_segment(ts_url, ts_filepath):
    with requests.get(ts_url, stream=True) as r:
        if r.status_code == 200:
            with open(ts_filepath, 'wb') as f:
                for chunk in tqdm(r.iter_content(chunk_size=1024), desc="Downloading", unit="B", leave=False):
                    f.write(chunk)
        else:
            print(f"下载失败: {ts_url}")

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

def convert_ts_to_mp4(ts_dir, mp4_file_path):
    ts_files = [f for f in os.listdir(ts_dir) if f.endswith('.ts')]
    if not ts_files:
        print(f"目录 {ts_dir} 中没有找到TS文件.")
        return False

    ts_files.sort()  # 确保文件按顺序合并

    with open(mp4_file_path, 'wb') as mp4_file:
        for ts_file in ts_files:
            ts_file_path = os.path.join(ts_dir, ts_file)
            with open(ts_file_path, 'rb') as ts:
                mp4_file.write(ts.read())

    print(f"TS文件合并完成，输出到: {mp4_file_path}")
    return True

if __name__ == '__main__':
    url = 'https://v9.dious.cc/20231011/gSsDaQr1/index.m3u8'
    ts_output_dir = '/Users/duanqs/Downloads/m3u8/ts_files'
    mp4_file_path = '/Users/duanqs/Downloads/m3u8/video.mp4'

    download_m3u8_video(url, ts_output_dir)
    convert_ts_to_mp4(ts_output_dir, mp4_file_path)
