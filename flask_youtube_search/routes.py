from flask.helpers import total_seconds, url_for
import requests
from isodate import parse_duration

from flask import Blueprint, render_template, current_app, request, redirect

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def index():
    search_url = "https://www.googleapis.com/youtube/v3/search"
    videos_url = "https://www.googleapis.com/youtube/v3/videos"

    videos = []

    if request.method == "POST" and request.form.get("query"):
        search_query = request.form.get("query")
        if not search_query:
            return 
        search_parameters = {
            "key": current_app.config["YOUTUBE_API_KEY"],
            "q": search_query, # search query
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
            "part": "snippet, contentDetails, statistics",
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
                    "likes": result["statistics"]["likeCount"],
                    "dislikes": result["statistics"]["dislikeCount"],
                }
                video_data["route"] = f"{url_for('main.video_page', video_data=video_data)}"
                videos.append(video_data)

    return render_template("index.html", videos=videos)

@main.route("/video", methods=["GET", "POST"])
def video_page():
    video_data = eval(request.args.get("video_data", None))

    if not video_data:
        return "<h2>Error while loading video data.</h2>"

    video_response = requests.get(f"https://www.youtube.com/embed/{video_data['id']}")
    if video_response.status_code != 200: # 200 means ok
        return "<h2>Video can't be loaded.</h2>"

    return render_template("video.html", video_data=video_data)
