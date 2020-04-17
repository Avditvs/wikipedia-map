import urllib.parse as urlparse
import re


def get_page_title(parser):
    return parser.title.text.split("—")[0].strip().replace(" ", "_")


def get_page_links(parser, duplicate=False):
    content = parser.select_one(".mw-parser-output")
    links = [] if duplicate is True else set()
    for a in content.find_all("a"):
        h = a.get("href")
        if h is not None:
            h = urlparse.unquote(h)
            if "#" not in h and ":" not in h and re.match("^/wiki/.*", h):
                links.append(
                    h.split("/")[2]
                ) if duplicate is True else links.add(h.split("/")[2])
    return links


def make_request_url(page_title, locale):
    return "https://{}.wikipedia.org/wiki/{}".format(locale, page_title)
