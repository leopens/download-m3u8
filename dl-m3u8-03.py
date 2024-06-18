#使用异步 IO 和协程来优化下载速度
# 运行 python3 dl-m3u8-01.py
#EXTM3U
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2000000,RESOLUTION=1920x1040
#/20231011/gSsDaQr1/2000kb/hls/index.m3u8
#https://v9.dious.cc/20231011/gSsDaQr1/2000kb/hls/index.m3u8
import aiohttp
import asyncio
import os

async def download_ts_file(ts_url, ts_file_path):
    # 防止ssl报错：
    # aiohttp.client_exceptions.ClientConnectorCertificateError: Cannot connect to host ***.****.com:443 ssl:True
    # [SSLCertVerificationError: (1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local
    # issuer certificate (_ssl.c:1123)')]
    conn = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(ts_url) as response:
            if response.status != 200:
                print(f'{ts_url} 下载失败')
                return False
            with open(ts_file_path, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
    print(f'{ts_url} 下载完成')
    return True

async def download_m3u8_video(url, file_path):
    # 防止ssl报错
    conn = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=conn) as session:
        async with session.get(url) as response:
            if response.status != 200:
                print('m3u8视频下载链接无效')
                return False

            m3u8_text = await response.text()
            m3u8_list = m3u8_text.split('\n')
            m3u8_list = [i for i in m3u8_list if i and i[0] != '#']

            tasks = []
            for i, ts_url in enumerate(m3u8_list):
                ts_url = url.rsplit('/', 1)[0] + '/' + ts_url
                ts_file_path = file_path.rsplit('.', 1)[0] + f'_{i}.ts'
                task = asyncio.ensure_future(
                    download_ts_file(ts_url, ts_file_path))
                tasks.append(task)

            await asyncio.gather(*tasks)

    print('m3u8视频下载完成')
    return True

def convert_ts_to_mp4(ts_file_path, mp4_file_path):
    os.system(f'ffmpeg -i {ts_file_path} -c copy {mp4_file_path}')

if __name__ == '__main__':
    url = '输入m3u8流媒体播放列表文件下载链接'
    ts_file_path = '输入ts文件保存路径'
    mp4_file_path = '输入mp4文件保存路径'

    loop = asyncio.get_event_loop()
    loop.run_until_complete(download_m3u8_video(url, ts_file_path))
    convert_ts_to_mp4(ts_file_path, mp4_file_path)

# 协程（Coroutine）是一种轻量级的线程，可以在单线程中实现多个任务的并发执行，从而提高程序的效率和性能。Python 中的协程是通过 async/await 关键字来实现的，可以使用 asyncio 库来进行协程编程。

# 异步 IO（Asynchronous IO）是一种非阻塞式 IO 模型，可以在进行 IO 操作时不会阻塞程序的执行，从而提高程序的效率和响应速度。Python 中的异步 IO 是通过 asyncio 库来实现的，可以使用 async/await 关键字和协程来实现异步 IO 操作。

# 异步 IO 和协程的结合可以实现高效的并发编程，通过异步 IO 可以充分利用 CPU 和网络带宽等资源，提高程序的效率和性能；而通过协程可以在单线程中实现多个任务的并发执行，避免了线程切换的开销，从而提高程序的响应速度和并发性能。在实际应用中，我们可以根据具体情况选择和优化异步 IO 和协程的使用方式，以达到最佳的效果和性能。

# 为了使用异步 IO 和协程来优化下载速度，可以使用 aiohttp 和 asyncio 库来实现。以下是使用异步 IO 和协程下载 m3u8 视频的示例代码：

# 在这个示例中，使用了 aiohttp 和 asyncio 库来实现异步 IO 和协程。定义了两个协程函数：download_m3u8_video 和 download_ts_file。在 download_m3u8_video 函数中，使用 aiohttp 库的 ClientSession 类异步获取 m3u8 文件，并解析出其中的 ts 文件链接。然后，使用协程和异步 IO 的方式异步下载每个 ts 文件，并将其写入到本地文件中。在下载过程中，使用了异步 IO 和协程的方式，可以充分利用网络带宽，提高下载速度。

# 在 download_m3u8_video 函数中，使用了 async for 循环来遍历 m3u8 文件中的 ts 文件链接，并创建了一个任务列表 tasks，用于存储异步下载的任务。然后，使用 asyncio.ensure_future 方法将每个任务添加到任务列表中。最后，使用 asyncio.gather 方法同时运行所有异步任务，等待所有任务完成后，即可完成整个 m3u8 视频的下载。

# 最后，使用 ffmpeg 工具将下载的 ts 文件转换为 mp4 格式的视频文件。这个步骤并不涉及异步 IO 和协程，只是为了将下载的 ts 文件转换为可用的视频文件格式。

# 使用协程可以充分利用网络带宽，提高下载速度。需要注意的是，在使用协程时，需要考虑到 CPU 和内存等资源的占用，避免出现资源耗尽或者死锁等问题。同时，协程的使用需要掌握一定的异步编程技巧，例如使用 async/await 关键字、协程调度等。因此，在实际应用中，需要根据具体情况进行调整和优化，以获取最佳的性能和效果。
