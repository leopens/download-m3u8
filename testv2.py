import asyncio
import os
from urllib.parse import urljoin
import aiofiles
import aiohttp
from tqdm import tqdm
import subprocess
import time

# 设置显示模式变量
progress_display_mode = 1  # 0: 显示单个文件的进度条, 1: 显示整体进度条和每秒下载的数据量

async def download_m3u8_video(url, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    async with aiohttp.ClientSession() as session:
        success, ts_list = await download_m3u8_recursive(session, url, output_dir)
        if success:
            print('m3u8视频下载完成')
            return True, ts_list
        else:
            return False, []

async def download_m3u8_recursive(session, url, output_dir):
    async with session.get(url) as response:
        if response.status != 200:
            print('m3u8视频下载链接无效')
            return False, []

        m3u8_content = await response.text()

    m3u8_list = m3u8_content.split('\n')
    m3u8_list = [i for i in m3u8_list if i and i[0] != '#']
    ts_list = []

    for line in m3u8_list:
        if line.endswith('.m3u8'):
            print(f"正在重定向解析: {line}")
            nested_url = urljoin(url, line)
            nested_ts_list = await download_nested_m3u8(session, nested_url)
            ts_list.extend(nested_ts_list)
        else:
            ts_url = urljoin(url, line)
            ts_list.append(ts_url)

    print(f"解析到 {len(ts_list)} 个ts文件,准备下载.")

    progress_bar = None
    if progress_display_mode == 1:
        progress_bar = tqdm(total=len(ts_list), unit='file', desc='Downloading', ncols=100)

    download_tasks = [download_ts_segment(session, ts_url, output_dir, progress_bar) for ts_url in ts_list]
    download_results = await asyncio.gather(*download_tasks)

    if progress_bar:
        progress_bar.close()

    download_success = all(download_results)
    return download_success, ts_list

async def download_ts_segment(session, ts_url, output_dir, progress_bar=None):
    ts_filename = os.path.basename(ts_url)
    ts_filepath = os.path.join(output_dir, ts_filename)

    resume_header = {}
    if os.path.exists(ts_filepath):
        resume_header['Range'] = f"bytes={os.path.getsize(ts_filepath)}-"
        if progress_display_mode == 1 and progress_bar:
            progress_bar.update(1)
        return True  # Skip downloading if the file already exists

    try:
        async with session.get(ts_url, headers=resume_header) as response:
            #print(f"请求URL: {ts_url}")
            #print(f"请求头部Range: {resume_header.get('Range')}")

            if response.status == 200 or response.status == 206:
                total_size = int(response.headers.get('Content-Length', 0))

                if progress_display_mode == 0:
                    pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc=f'Downloading {ts_filename}')

                async with aiofiles.open(ts_filepath, 'ab') as f:
                    start_time = time.time()
                    total_downloaded = 0
                    async for chunk in response.content.iter_chunked(1024):
                        await f.write(chunk)
                        total_downloaded += len(chunk)
                        if progress_display_mode == 0:
                            pbar.update(len(chunk))

                    elapsed_time = time.time() - start_time
                    if progress_display_mode == 1 and progress_bar:
                        speed = total_downloaded / elapsed_time / (1024 * 1024)  # MB/s
                        bandwidth = speed * 8  # Mbps
                        progress_bar.set_postfix(speed=f'{speed:.2f} MB/s', bandwidth=f'{bandwidth:.2f} Mbps')

                if progress_display_mode == 0:
                    pbar.close()
                if progress_display_mode == 1 and progress_bar:
                    progress_bar.update(1)

            elif response.status == 416:
                local_file_size = os.path.getsize(ts_filepath)
                #print(f"本地文件大小: {local_file_size}")
                expected_size = int(response.headers.get('Content-Length', 0))
                #if expected_size==206:
                #    content206 = await response.text()
                #    print(f"部分内容为:\n{content206}")
                
                #print(f"服务器返回Content-Length: {expected_size}")
                if local_file_size < expected_size:
                    #print(f"服务器返回范围不符合要求: {ts_url}, 状态码: {response.status}")
                    if os.path.exists(ts_filepath):
                        os.remove(ts_filepath)
                        #print(f"已删除出错的文件: {ts_filepath}")
                    return False
                else:
                    #print(f"下载成功: {ts_url}, 状态码: {response.status}")
                    return True
            else:
                print(f"下载失败: {ts_url}, 状态码: {response.status}")
                return False
    except aiohttp.ClientError as e:
        print(f"发生网络错误: {e}")
        return False
    except aiohttp.ServerDisconnectedError as e:
        print(f"服务器断开连接: {e}")
        return False
    except aiohttp.ClientResponseError as e:
        print(f"客户端响应错误: {e}")
        return False
    except aiohttp.ContentTypeError as e:
        print(f"内容类型错误: {e}")
        return False
    except Exception as e:
        print(f"发生未知异常: {e}")
        return False

    return True

async def download_nested_m3u8(session, url):
    async with session.get(url) as response:
        if response.status != 200:
            print(f'嵌套m3u8视频下载链接无效: {url}')
            return []

        m3u8_content = await response.text()

    m3u8_list = m3u8_content.split('\n')
    m3u8_list = [i for i in m3u8_list if i and i[0] != '#']
    ts_list = [urljoin(url, line) for line in m3u8_list]

    return ts_list

async def convert_ts_to_mp4(ts_dir, mp4_file_path, ts_list):
    if not ts_list:
        print("播放列表为空，无法生成 MP4 文件")
        return False

    # 构建 FFmpeg 命令
    ffmpeg_cmd = [
        'ffmpeg', '-loglevel', 'error',  # Suppress logs
        '-i', 'concat:' + '|'.join([os.path.join(ts_dir, os.path.basename(ts_url)) for ts_url in ts_list]),
        '-c', 'copy', mp4_file_path
    ]

    try:
        # 执行 FFmpeg 命令
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"MP4 转换完成，输出到: {mp4_file_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"转换到 MP4 失败: {e}")
        return False

async def main():
    url = 'https://v9.dious.cc/20231011/gSsDaQr1/index.m3u8'
    ts_output_dir = '/Users/duanqs/Downloads/m3u8/ts_files'
    mp4_file_path = '/Users/duanqs/Downloads/m3u8/video.mp4'

    success, ts_list = await download_m3u8_video(url, ts_output_dir)
    if success:
        if await convert_ts_to_mp4(ts_output_dir, mp4_file_path, ts_list):
            print("MP4转换完成")
        else:
            print("转换到MP4失败，因为TS文件下载错误")
    else:
        print("下载m3u8视频失败")

if __name__ == '__main__':
    asyncio.run(main())
