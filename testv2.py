import aiohttp
import asyncio
import os
from tqdm import tqdm
from urllib.parse import urljoin
import aiofiles

async def download_m3u8_video(url, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    async with aiohttp.ClientSession() as session:
        if await download_m3u8_recursive(session, url, output_dir):
            print('m3u8视频下载完成')
            return True
        else:
            return False

async def download_m3u8_recursive(session, url, output_dir):
    async with session.get(url) as response:
        if response.status != 200:
            print('m3u8视频下载链接无效')
            return False

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

    # 下载并行度优化
    download_tasks = [download_ts_segment(session, ts_url, output_dir) for ts_url in ts_list]
    download_results = await asyncio.gather(*download_tasks)

    download_success = all(download_results)
    return download_success


async def download_ts_segment(session, ts_url, output_dir):
    ts_filename = os.path.basename(ts_url)
    ts_filepath = os.path.join(output_dir, ts_filename)

    resume_header = {}
    if os.path.exists(ts_filepath):
        print(f"正在继续下载断点文件: {ts_filename}")
        resume_header['Range'] = f"bytes={os.path.getsize(ts_filepath)}-"

    try:
        async with session.get(ts_url, headers=resume_header) as response:
            if response.status == 200 or response.status == 206:
                total_size = int(response.headers.get('Content-Length', 0))
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=f'Downloading {ts_filename}') as pbar:
                    async with aiofiles.open(ts_filepath, 'ab') as f:
                        async for chunk in response.content.iter_chunked(1024):
                            await f.write(chunk)
                            pbar.update(len(chunk))
            elif response.status == 416:
                print(f"服务器返回范围不符合要求: {ts_url}, 状态码: {response.status}")
                if os.path.exists(ts_filepath):
                    os.remove(ts_filepath)
                    print(f"已删除出错的文件: {ts_filepath}")
                return False
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

def convert_ts_to_mp4(ts_dir, mp4_file_path):
    ts_files = [f for f in os.listdir(ts_dir) if f.endswith('.ts')]
    if not ts_files:
        print(f"目录 {ts_dir} 中没有找到TS文件.")
        return False

    ts_files.sort()

    with open(mp4_file_path, 'wb') as mp4_file:
        for ts_file in ts_files:
            ts_file_path = os.path.join(ts_dir, ts_file)
            with open(ts_file_path, 'rb') as ts:
                mp4_file.write(ts.read())

    print(f"TS文件合并完成，输出到: {mp4_file_path}")
    return True

async def main():
    url = 'https://v9.dious.cc/20231011/gSsDaQr1/index.m3u8'
    ts_output_dir = '/Users/duanqs/Downloads/m3u8/ts_files'
    mp4_file_path = '/Users/duanqs/Downloads/m3u8/video.mp4'

    if await download_m3u8_video(url, ts_output_dir):
        if convert_ts_to_mp4(ts_output_dir, mp4_file_path):
            print("MP4转换完成")
        else:
            print("转换到MP4失败，因为TS文件下载错误")
    else:
        print("下载m3u8视频失败")

if __name__ == '__main__':
    asyncio.run(main())
