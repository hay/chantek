from pyquery import PyQuery as pq
from urllib import quote_plus as encode

SEARCH_ENDPOINT = "http://www.amazon.com/s/?field-keywords=%s"

def get_searchitem_data(element):
    item = pq(element)

    return {
        "title" : item.find("h3.newaps span").text(),
        "href" : item.find("h3.newaps a").attr('href'),
        "price" : item.find(".newp .bld").text(),
        "rating" : item.find(".rvw .a-declarative a").attr('alt'),
        "reviews" : item.find(".rvwCnt a").text()
    }

def search(query):
    url = SEARCH_ENDPOINT % encode(query)
    d = pq(url)

    # No results?
    if d("#noResultsTitle").length == 1:
        return { "error" : "No results" }

    results = d("#resultsCol .prod")

    return map(get_searchitem_data, results)

def run(args):
    if "method" in args and "q" in args:
        if args["method"] == "search":
            return search(args["q"])
        else:
            return ( {"error" : "Invalid method"} )
    else:
        return ( { "error" : "No valid method or url" })
