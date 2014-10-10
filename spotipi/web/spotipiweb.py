from __future__ import print_function

from ConfigParser import SafeConfigParser
import threading

from flask import Flask, request, render_template
import requests
import spotify


config = SafeConfigParser()
config.read("spotipi.cfg")

app = Flask(__name__)
app.debug = True

session = spotify.Session()
loop = spotify.EventLoop(session)
loop.start()

## Events
logged_in = threading.Event()

def on_connection_state_updated(session):
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in.set()

## Handlers
session.on(
    spotify.SessionEvent.CONNECTION_STATE_UPDATED,
    on_connection_state_updated
    )

username = config.get("credentials", "username")
password = config.get("credentials", "password")
session.login(username, password, remember_me=True)

## Helpers
def get_query(form):
    return ' '.join(form[key] for key in form.keys())

## API
@app.route("/queue", methods=["GET"])
def get_queue():
    # TODO: send command to retrieve current queue
    pass

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/queue/add/<link>", methods=["GET", "POST"])
def add_to_queue(link):
    r = requests.get("http://192.168.1.118:5001/queue/add/{0}".format(link))
    return r.text

@app.route("/queue/clear", methods=["POST"])
def clear_queue():
    # TODO: send command to clear queue
    pass

@app.route("/pause", methods=["POST"])
def pause():
    # TODO: send command to pause
    pass

@app.route("/skip", methods=["POST"])
def skip():
    # TODO: send command to skip current track
    pass

@app.route("/search", methods=["POST"])
def search():
    query = get_query(request.form)
    res = session.search(query).load()
    while not res.is_loaded:
        res = res.load()
    tracks = res.tracks
    # artists = res.artists
    # albums = res.albums
    playlists = [p.playlist for p in res.playlists]
    # TODO: parse out other things besides tracks
    return render_template(
        "search.html",
        tracks=tracks,
        # artists=artists,
        # albums=albums,
        playlists=playlists
        )

@app.route("/play/<link>", methods=["GET", "POST"])
def play_track(link):
    r = requests.get("http://192.168.1.118:5001/play/{0}".format(link))
    return r.text

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000)
