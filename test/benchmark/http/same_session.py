import time
import asyncio
import requests
import httpx
import aiohttp
import urllib.request
import http.client

HOST = "127.0.0.1"
PORT = 8080
URL = f"http://{HOST}:{PORT}"


def benchmark_http_client_sync():
    start_time = time.time()
    for _ in range(1000):
        conn = http.client.HTTPConnection(HOST, port=PORT)
        conn.request("GET", "/")
        conn.close()
    end_time = time.time()
    return end_time - start_time


def benchmark_requests():
    start_time = time.time()
    with requests.Session() as session:
        for _ in range(1000):
            session.get(URL)
    end_time = time.time()
    return end_time - start_time


async def benchmark_aiohttp():
    start_time = time.time()
    async with aiohttp.ClientSession() as session:
        for _ in range(1000):
            await session.get(URL)
    end_time = time.time()
    return end_time - start_time


def benchmark_httpx():
    start_time = time.time()
    with httpx.Client() as client:
        for _ in range(1000):
            client.get(URL)
    end_time = time.time()
    return end_time - start_time


def benchmark_urllib():
    start_time = time.time()
    opener = urllib.request.build_opener()
    for _ in range(1000):
        opener.open(URL)
    opener.close()
    end_time = time.time()
    return end_time - start_time


if __name__ == "__main__":
    sync_time = benchmark_requests()
    async_time = asyncio.run(benchmark_aiohttp())
    httpx_time = benchmark_httpx()
    urllib_time = benchmark_urllib()
    http_client_sync_time = benchmark_http_client_sync()

    print(f"HTTP:     {http_client_sync_time} seconds")
    print(f"Requests: {sync_time} seconds")
    print(f"Aiohttp:  {async_time} seconds")
    print(f"HTTPX:    {httpx_time} seconds")
    print(f"Urllib:   {urllib_time} seconds")
