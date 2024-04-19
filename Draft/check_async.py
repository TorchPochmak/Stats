# SlingAcademy.com
# This example uses Python 3.11.4

# import the modules
import asyncio
import aiohttp
from pprint import pprint

# list of urls to request
urls = [
    "https://api.slingacademy.com/v1/sample-data/products",
    "https://api.slingacademy.com/v1/sample-data/users",
    "https://api.slingacademy.com/v1/sample-data/photos",
]


# async function to make a single request
async def fetch(url, session):
    async with session.get(url, ssl=False) as response:
        status = response.status
        data = await response.json()
        data_length = len(data)
        return {"url": url, "status": status, "data_length": data_length}


# async function to make multiple requests
async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(url, session) for url in urls]
        results = await asyncio.gather(*tasks)
        return results


# run the async functions
results = asyncio.run(fetch_all(urls))

# print the results
pprint(results)