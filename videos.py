import re
import json
import requests 
from bs4 import BeautifulSoup
from flask import request
from urllib.parse import urlparse

# Adapted from https://github.com/sskender/pornhub-api

class Videos():

    def __init__(self):
        self.data = []

    def craftVideoURL(self, page_num):
        payload = {"page": page_num}
        return payload

    def loadVideosPage(self, page_num):
        #loadvideospage
        r = requests.get("https://pornhub.com/sfw", params={"page" : page_num}, headers={ "Content-Type" : "text/html; charset=UTF-8" })
        html = r.text 
        return BeautifulSoup(html, "lxml")

    def scrapeLiveVideos(self, soup_data):
        try:
            true_soup = soup_data.select_one("ul#videoCategory")
            return true_soup.find_all("li", { "class" : re.compile(".*videoblock videoBox.*") } )
        except Exception as e:
            pass

    def getSingleVideoPage(self, url):
        r = requests.get(url)
        html = r.text
        return BeautifulSoup(html, "lxml")

    def getComment(self, video_page):
        try: 
            soup = video_page.select_one("div.topCommentBlock")
            username = soup.select_one("a.usernameLink")
            date = soup.select_one("div.date")
            message = soup.select_one("div.commentMessage")
            img = soup.select_one("img.avatarTrigger")
            comment = {
                "username": username.get_text(),
                "date": date.get_text(),
                "message": message.span.get_text(),
                "img": img.get('data-src')
            }
            return comment
        except Exception as e:
            pass 
        
    def scrapeVideoInfo(self, div_el):
        data = {
            "name": None,
            "url": None,
            "rating": None,
            "duration": None,
            "background": None,
            "viewkey": None
        }
        
        # scrape url and name from title html element
        for a_tag in div_el.find_all("a", href=True):
            try:
                url = a_tag.attrs["href"]
                data["url"] = "https://pornhub.com" + url 
                data["name"] = a_tag.attrs["title"]
                vid_url = urlparse(data['url'])
                viewkey = vid_url.query[8:]
                data["viewkey"] = viewkey
                break 
            except Exception as e:
                pass

        for img_tag in div_el.find_all("img", src=True):
            try:
                url = img_tag.attrs["data-thumb_url"]
                data["background"] = url
                break
            except Exception as e:
                pass

        #duration
        for var_tag in div_el.find_all("var", {"class": "duration"} ):
            try:
                data["duration"] = str(var_tag).split(">")[-2].split("<")[-2]
                break 
            except Exception as e:
                pass
        
        # rating
        for div_tag in div_el.find_all("div", { "class" : "value" } ):
            try:
                data["rating"] = int( str(div_tag).split(">")[1].split("%")[0] )
                break
            except Exception as e:
                pass

        return data

    def getVideos(self, page = 1, quantity = 1, infinity = False):
        quantity = quantity if quantity >=1 else 1 
        page = page if page >= 1 else 1
        found = 0

        while True:
            if self.scrapeLiveVideos(self.loadVideosPage(page)) is not None:
                for possible_video in self.scrapeLiveVideos(self.loadVideosPage(page)):
                    data_dict = self.scrapeVideoInfo(possible_video)
                    
                    if data_dict:
                        yield data_dict

                        if not infinity:
                            found += 1
                            if found >= quantity: return

                page += 1
            else:
                pass
