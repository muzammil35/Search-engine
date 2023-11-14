from settings import *
import requests
from requests.exceptions import RequestException
import pandas as pd 
from storage import DBStorage
from urllib.parse import quote_plus
from datetime import datetime
import asyncio
from aiohttp import ClientSession 
from concurrent.futures import ThreadPoolExecutor



async def fetch_url(session, url):
    try:
        async with session.get(url, timeout=5) as response:
            response.raise_for_status()
            return await response.json()
    except Exception as e:
        # Log the error or handle it gracefully
        print(f"Error fetching data: {e}")
        return None
    

async def search_api(query, pages=int(RESULT_COUNT/10)):
    results = []
    urls = [
        SEARCH_URL.format(
            key=SEARCH_KEY,
            cx=SEARCH_ID,
            query=quote_plus(query),
            start=i * 10 + i
        ) for i in range(pages)
    ]

    async with ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        data_list = await asyncio.gather(*tasks)

    for data in data_list:
        if data:
            results += data.get("items", [])

    res_df = pd.DataFrame.from_dict(results)
    res_df["rank"] = list(range(1, res_df.shape[0] + 1))
    res_df = res_df[["link", "rank", "snippet", "title"]]

    return res_df
    
async def scrape_page(session, links):
    async def fetch_url_async(link):
        try:
            async with session.get(link, timeout=5) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            # Log the error or handle it gracefully
            print(f"Error fetching HTML: {e}")
            return ""

    tasks = [fetch_url_async(link) for link in links]
    return await asyncio.gather(*tasks)

async def search(query):
    columns = ["query", "rank", "link", "title", "snippet", "html", "created"]
    storage = DBStorage()

    # get query results from DB
    stored_results = storage.query_results(query)
    if not stored_results.empty:
        stored_results["created"] = pd.to_datetime(stored_results["created"])
        return stored_results[columns]
    
    '''
    here asynchronous programming is used to call two I/O bound functions
    concurrently to make use of the waiting times and increase efficiency
    '''
    results = await search_api(query)
    async with ClientSession() as session:
        results["html"] = await scrape_page(session, results["link"])

    results = results[results["html"].str.len() > 0].copy()
    results["query"] = query
    results["created"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    results = results[columns]

    # maybe try to Use bulk_insert here for more efficient database insertion
    results.apply(lambda x: storage.insert_row(x), axis=1)

    return results

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search("your_query"))