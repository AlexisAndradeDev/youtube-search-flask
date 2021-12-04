from flask.helpers import total_seconds
import requests
from isodate import parse_duration

from flask import Blueprint, render_template, current_app, request, redirect

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def index():
    search_url = "https://www.googleapis.com/youtube/v3/search"
    videos_url = "https://www.googleapis.com/youtube/v3/videos"

    videos = []

    if request.method == "POST":
        search_parameters = {
            "key": current_app.config["YOUTUBE_API_KEY"],
            "q": request.form.get("query"), # search query
            "part": "snippet",
            "maxResults": 12,
            "type": "video",
        }

        req = requests.get(search_url, params=search_parameters)
        
        results = req.json()["items"]

        video_ids = []
        for result in results:
            video_ids.append(result["id"]["videoId"])


        videos_parameters = {
            "key": current_app.config["YOUTUBE_API_KEY"],
            "id": ",".join(video_ids),
            "part": "snippet, contentDetails",
            "maxResults": 12,
        }

        req = requests.get(videos_url, params=videos_parameters)
        results = req.json()["items"]

        if request.form.get("submit") == "lucky":
            url = f"https://www.youtube.com/watch?v={results[0]['id']}"
            return redirect(url)

        elif request.form.get("submit") == "search":
            for result in results:
                video_data = {
                    "id": result["id"],
                    "url": f"https://www.youtube.com/watch?v={ result['id'] }",
                    "thumbnail": result["snippet"]["thumbnails"]["high"]["url"],
                    "duration": int(parse_duration(result["contentDetails"]["duration"]).total_seconds() / 60),
                    "title": result["snippet"]["title"],
                }
                videos.append(video_data)


    return render_template("index.html", videos=videos)
