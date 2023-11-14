# Project Overview

In this project, I built a search engine that uses filtering to reorder results based on content and remove malicious/ad-heavy tracking websites. The engine will get results from the Google API, store them in an SQL-lite database, and then rank them based on the filters I defined. I found that the search engine was taking around 3-6 seconds to load results so I tried using asynchronous programming (asyncio python module) to call two I/O-bound functions concurrently instead of one after the other.

## implementation
- used sql-lite db to store search results, assign relevance scores to results
- simple html frontend with css styling to encapsulate search engine features 
- content-filtering and tracking-filtering
 
## Code

File overview:

* `app.py` - the web interface
* `filter.py` - the code to filter results
* `search.py` - code to get the search results
* `settings.py` - settings needed by the other files
* `storage.py` - code to save the results to a database


## Run
You can visit this link to try out an incomplete version of the app: https://b5cq7vfzch.execute-api.us-west-2.amazonaws.com/ 
(could not use too much memory storage for db but content filtering, tracker-filtering and search engine functionality work great)

or Run the project with:

* `pip install -r requirements.txt`
* `flask --debug run --port 5001`
