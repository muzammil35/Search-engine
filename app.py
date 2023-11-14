from flask import Flask, request, jsonify
from search import search
import html
import asyncio
from filter import Filter
import time
from storage import DBStorage

app = Flask(__name__)

styles = """
<style>
.site{
    font-size: .8rem;
    color: green;
}

.snippet{
    font-size: .9rem;
    color: gray;
    margin-bottom: 30px;
}

.rel-button {
    cursor: pointer;
    color: blue;
}
</style>

<script>
const relevant = function(query, link){
    fetch("/relevant", {
        method: 'POST',
        headers: {
            'ACCEPT': 'application/json',
            'Content-Type': 'applications/json'
        },
        body: JSON.stringify({
            "query": query,
            "link": link
        })
    });
}
</script>


"""

search_template = styles + """
<form action="/" method="post">
    <input type="text" name="query">
    <input type="submit" value="Search">
</form>
"""
result_template = """
<p class="site">{rank}: {link} <span class="rel-button" onclick='relevant("{query}", "{link}");'>Relevant</span></p>
<a href="{link}">{title}</a>
<p class="snippet">{snippet}</p>
"""
def show_search_form():
    return search_template

async def run_search(query):
    results = await search(query)
    fi = Filter(results)
    results = fi.filter()
    rendered = search_template
    #make sure browser wont render random html that happens to be in the snippet
    results["snippet"] = results["snippet"].apply(lambda x: html.escape(x))
    for index,row in results.iterrows():
        rendered += result_template.format(**row)
    return rendered

@app.route("/", methods =["GET", "POST"])

    

async def search_form():
    if request.method == "POST":
        query = request.form["query"]
        result = await run_search(query)
        return result
    else:
        return show_search_form()
    
    
@app.route("/relevant", methods=["POST"])

def mark_relevant():
    data = request.get_json()
    query = data["query"]
    link = data["link"]
    storage = DBStorage()
    storage.update_relevance(query,link,10)
    return jsonify(success=True)
    
if __name__ == "__main__":
    app.run()(debug=False,host='0.0.0.0')
