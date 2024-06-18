# !brew install ffmpeg
# !python3 -m pip install requests ffmpeg-python
# 运行 python3 2mp4.py

import os
import requests
import ffmpeg

# 下载 m3u8 文件并获取 ts 文件列表
def download_m3u8(url, save_path):
    response = requests.get(url)
    with open(save_path, 'wb') as file:
        file.write(response.content)

# 下载 ts 文件并保存
def download_ts_files(m3u8_path, base_url, output_folder):
    with open(m3u8_path, 'r') as file:
        lines = file.readlines()
    
    ts_files = [line.strip() for line in lines if line.strip().endswith('.ts')]
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for ts_file in ts_files:
        ts_url = os.path.join(base_url, ts_file)
        ts_path = os.path.join(output_folder, ts_file)
        response = requests.get(ts_url)
        with open(ts_path, 'wb') as file:
            file.write(response.content)

    return [os.path.join(output_folder, ts_file) for ts_file in ts_files]

# 合并 ts 文件并转换为 mp4
# 合并 ts 文件并转换为 mp4
# 合并 ts 文件并转换为 mp4
def convert_ts_to_mp4(ts_files, output_file):
    input_files = '|'.join([os.path.basename(ts_file) for ts_file in ts_files])
    print(f"Input files: {input_files}")  # 打印以便调试
    ffmpeg.input(f"concat:{input_files}", format='mpegts').output(output_file).run(overwrite_output=True, quiet=False)



# 定义主函数
def main(m3u8_url, output_mp4):
    m3u8_file = 'video.m3u8'
    output_folder = 'ts_files'
    
    download_m3u8(m3u8_url, m3u8_file)
    base_url = os.path.dirname(m3u8_url)
    ts_files = download_ts_files(m3u8_file, base_url, output_folder)
    convert_ts_to_mp4(ts_files, output_mp4)

    # 清理临时文件
    os.remove(m3u8_file)
    for ts_file in ts_files:
        os.remove(ts_file)
    os.rmdir(output_folder)

# 示例使用
m3u8_url = 'https://v9.dious.cc/20231011/gSsDaQr1/index.m3u8'
output_mp4 = 'output_video.mp4'
main(m3u8_url, output_mp4)
