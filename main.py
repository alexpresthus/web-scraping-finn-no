#!/usr/bin/env python

import asyncio # asyncio-3.4.3
import aiohttp # aiohttp-3-7-4
import time
import re
import requests as req

baseurl = "https://www.finn.no" # global variable for base url


async def get(url, session):
    """
    Asyncronously make http get requests to a url and return the stringified response body
    """
    try:
        async with session.get(url=url) as response:
            resp = await response.read()
            print("Successfully got url {} with resp of length {}.".format(url, len(resp)))
            return str(resp)
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))
        return ''

def get_page_urls(first_page_url):
    """
    Get full urls to all available pages for a search.
    """
    url = first_page_url
    curPage = 1
    while True:
        text = req.get(url).text
        page_numbers = [int(number) for number in re.findall(r"\"Side (\d*)\"", text)]          # find all page numbers present on current page (shows max 7 new pages)
        if curPage == page_numbers[-1]:                                                         # check if last page (current page is highest)
            break                                                                                   # break loop if last page
        else:
            curPage = page_numbers[-1]                                                              # update curPage and url with highest page number and iterate if not last page
            url = f'{first_page_url}&page={str(curPage)}'
    
    return [f'{first_page_url}&page={str(i+1)}' for i in range(curPage)]                        # return list of urls to all pages



def format_and_save_results(keywords, no_ads):
    """
    Format keywords, sort results and save to file
    """
    # TODO filter out unwanted / unrelevant keywords

    keywords_formatted_1 = [re.sub(r"(^ )|( $)", '', keyword).lower() for keyword in keywords]                                                                                                          # remove whitespace at start and end of string, and make all characters lowercase
    keywords_formatted_2 = [re.sub(r"(\\xc3\\xb8)|(ø)", 'o', re.sub(r"(\\xc3\\xa6)|(æ)", 'ae', re.sub(r"(\\xc3\\xa5)|(\\xc3\\x85)|(å)", 'aa', keyword))).lower() for keyword in keywords_formatted_1]   # replace unicode (æ, ø, å) with (ae, o, aa)

    results = {}

    # Fill results dict with structure { keyword: count }
    for keyword in keywords_formatted_2:
        if keyword in results.keys():
            results[str(keyword)] += 1
        else:
            results[str(keyword)] = 1
    
    results_sorted = dict(sorted(results.items(), key=lambda item: item[1]))                                                                # sort results dict

    with open (f'./output/results.txt', 'w', encoding='utf-8') as f:                                                                        # save to file
        f.write(f'Showing number of appearances for keywords across {no_ads} ads for IT positions on Finn.no.\n\nKEYWORD :: COUNT\n\n')
        for keyword, count in results_sorted.items():
            f.write(f'{keyword}  ::  {count}\n')

async def main(async_loop, urls):
    async with aiohttp.ClientSession(loop=async_loop) as session:
        # get number of pages
        ret = await asyncio.gather(*[get(url, session) for url in urls])                                                                    # get content from all pages
        print("Finalized requesting all pages. Got len {} outputs.".format(len(ret)))

        regex_ad_urls = r"<a id=\"\d*\" href=\"([^\"]*)"                                                                                    # regex for finding ad urls on a page
        ad_urls_lists = [re.findall(regex_ad_urls, html) for html in ret]                                                                   # find ad urls on all pages
        ad_urls = [re.sub(r"^/", baseurl+'/', url, flags=re.MULTILINE | re.VERBOSE) for url_list in ad_urls_lists for url in url_list]      # format relative links to full urls and flatten 2d to 1d list

        ret2 = await asyncio.gather(*[get(url, session) for url in ad_urls])                                                                # get content from all ads
        print("Finalized requesting all ads. Got len {} outputs.".format(len(ret2)))

    regex_keywords = r"N\\xc3\\xb8kkelord</h2>[\\n\s]*<p>[\\n\s]*([^<]*)"                                                               # regex for finding keywords in an ad
    keywords_string_lists = [re.findall(regex_keywords, html, flags=re.VERBOSE | re.MULTILINE) for html in ret2]                        # find keywords
    keywords_lists = [keywords_string[0].split(',') if len(keywords_string) else [] for keywords_string in keywords_string_lists]       # split string of keywords sequences into list of strings
    keywords = [keyword for keyword_list in keywords_lists for keyword in keyword_list]                                                 # flatten 2d to 1d list

    try:
        format_and_save_results(keywords, len(ad_urls))
        print("Finalized all and saved to file.")
    except Exception as e:
        print("Unable to format and save results due to {}.".format(e.__class__))
    finally:
        print("Program finished.")

if __name__ == '__main__':
    start = time.time()

    first_url = "https://www.finn.no/job/fulltime/search.html?abTestKey=rerank&location=0.20001&occupation=0.23&sort=RELEVANCE"

    event_loop = asyncio.get_event_loop()                   # get event loop
    urls = get_page_urls(first_url)                         # get urls to all pages
    event_loop.run_until_complete(main(event_loop, urls))   # run eventloop with async wrapper function until complete
    
    end = time.time()

    print("Took {} seconds.".format(end - start))
