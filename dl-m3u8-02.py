#使用多线程来优化下载速度
# 运行 python3 dl-m3u8-01.py
#EXTM3U
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=2000000,RESOLUTION=1920x1040
#/20231011/gSsDaQr1/2000kb/hls/index.m3u8
#https://v9.dious.cc/20231011/gSsDaQr1/2000kb/hls/index.m3u8
import requests
import os
import threading

class Downloader(threading.Thread):
    def __init__(self, url, ts_url, file_path):
        threading.Thread.__init__(self)
        self.url = url
        self.ts_url = ts_url
        self.file_path = file_path

    def run(self):
        r = requests.get(self.ts_url, stream=True)
        if r.status_code == 200:
            with open(self.file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

def download_m3u8_video(url, file_path):
    r = requests.get(url)
    if r.status_code != 200:
        print('m3u8视频下载链接无效')
        return False

    m3u8_list = r.text.split('\n')
    m3u8_list = [i for i in m3u8_list if i and i[0] != '#']

    ts_list = []
    for ts_url in m3u8_list:
        ts_url = url.rsplit('/', 1)[0] + '/' + ts_url
        ts_list.append(ts_url)

    threads = []
    for i, ts_url in enumerate(ts_list):
        ts_file_path = file_path.rsplit('.', 1)[0] + f'_{i}.ts'
        thread = Downloader(url, ts_url, ts_file_path)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print('m3u8视频下载完成')
    return True

def convert_ts_to_mp4(ts_file_path, mp4_file_path):
    os.system(f'ffmpeg -i {ts_file_path} -c copy {mp4_file_path}')

if __name__ == '__main__':
    url = '输入m3u8流媒体播放列表文件下载链接'
    ts_file_path = '输入ts文件保存路径'
    mp4_file_path = '输入mp4文件保存路径'

    download_m3u8_video(url, ts_file_path)
    convert_ts_to_mp4(ts_file_path, mp4_file_path)


#在这个示例中，定义了一个 Downloader 类，用于下载每个 ts 文件。在 Downloader 类中，使用 requests 库的 stream 参数将下载进度分块，每次下载 1024 个字节，然后写入到文件中。在 download_m3u8_video 函数中，使用多线程的方式同时下载多个 ts 文件，并等待所有线程下载完成后再将其合并成一个 mp4 文件。这样可以大大缩短下载时间。

# 需要注意的是，多线程下载可能会导致网络瓶颈，从而降低下载速度。因此，在实际应用中，需要根据具体情况选择合适的下载方式，并进行调整和优化。例如，可以使用异步 IO、协程等技术来优化下载速度。另外，为了提高下载速度，还可以使用 CDN、负载均衡、网络加速等技术来优化下载环节。