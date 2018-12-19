import json
import requests 
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from bs4 import BeautifulSoup
app = Flask(__name__)
import re
from urllib.parse import urlparse

from videos import Videos

gethub = Videos()

page = 1
qty = 30

# videos = []
# for video in gethub.getVideos(page, qty):
    
#     print(json.dumps(video, indent=4, sort_keys=True))
#     videos.append(json.dumps(video, indent=4, sort_keys=True))

@app.route('/', defaults={'page':1}, methods=['GET', 'POST'])
@app.route('/<int:page>')
def home(page):
    videos = []
    
    for video in gethub.getVideos(page, qty):
        # print(json.dumps(video, indent=4, sort_keys=True))
        # print("\n")
        #videos.append(json.dumps(video, indent=4, sort_keys=True))
        videos.append(video)

 
    return render_template("videos.html", videos=videos, page=page)


@app.route('/play', methods=['GET', 'POST'])
def playvideo():

    viewkey = request.args.get('viewkey')
    top_comment = gethub.getComment(gethub.getSingleVideoPage("https://www.pornhub.com/view_video.php?viewkey=" + viewkey))
    

    return render_template("playvideo.html", viewkey=viewkey, top_comment=top_comment)

# if __name__ == '__main__':
#     # This is used when running locally. Gunicorn is used to run the
#     # application on Google App Engine. See entrypoint in app.yaml.
#     app.run(host='127.0.0.1', port=8080, debug=True)