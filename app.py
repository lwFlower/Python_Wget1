import http.client
import os
import threading
import time
import urllib.parse
import sys

def download_file(url, output_file, progress_callback):
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme == "https":
        connection = http.client.HTTPSConnection(parsed_url.netloc)
    else:
        connection = http.client.HTTPConnection(parsed_url.netloc)

    connection.request("GET", parsed_url.path)
    response = connection.getresponse()

    if response.status != 200:
        raise Exception(f"Failed to download file: {response.status} {response.reason}")

    with open(output_file, "wb") as f:
        downloaded_bytes = 0
        chunk_size = 1024

        while True:
            chunk = response.read(chunk_size)
            if not chunk:
                break
            f.write(chunk)
            downloaded_bytes += len(chunk)
            progress_callback(downloaded_bytes)

    connection.close()

def progress_reporter(progress_event, total_downloaded):
    while not progress_event.is_set():
        time.sleep(1)
        print(f"Downloaded: {total_downloaded[0]} bytes")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python app.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    parsed_url = urllib.parse.urlparse(url)
    filename = os.path.basename(parsed_url.path)

    if not filename:
        print("Unable to determine file name from URL")
        sys.exit(1)

    progress_event = threading.Event()
    total_downloaded = [0]

    reporter_thread = threading.Thread(target=progress_reporter, args=(progress_event, total_downloaded))
    reporter_thread.start()

    try:
        def update_progress(downloaded):
            total_downloaded[0] = downloaded

        download_file(url, filename, update_progress)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        progress_event.set()
        reporter_thread.join()

    print("Download completed.")