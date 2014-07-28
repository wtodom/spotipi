from collections import deque
from ConfigParser import SafeConfigParser
import threading

from flask import Flask, request, render_template
import spotify


config = SafeConfigParser()
config.read("spotipi.cfg")

app = Flask(__name__)
app.debug = True

song_queue = deque()

session = spotify.Session()
loop = spotify.EventLoop(session)
loop.start()

audio = spotify.AlsaSink(session)

## Events
logged_in = threading.Event()
end_of_track = threading.Event()

def on_connection_state_updated(session):
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in.set()

def on_end_of_track(self):
    end_of_track.set()

## Handlers
session.on(
    spotify.SessionEvent.CONNECTION_STATE_UPDATED,
    on_connection_state_updated
    )

session.on(
    spotify.SessionEvent.END_OF_TRACK,
    on_end_of_track
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
    return str(song_queue)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/queue/add", methods=["POST"])
def add_to_queue():
    track = request.args.get("track", '')
    if track is not '':
        song_queue.append(track)

@app.route("/queue/clear", methods=["POST"])
def clear_queue():
    song_queue.clear()

@app.route("/pause", methods=["POST"])
def pause():
    pass

@app.route("/skip", methods=["POST"])
def skip():
    pass

@app.route("/search", methods=["POST"])
def search():
    query = get_query(request.form)
    res = session.search(query).load()
    while not res.is_loaded:
        res.load()
    res = res.tracks
    print(res[0].name)
    return render_template("search.html", tracks=res)

@app.route("/play", methods=["POST"])
def play_track():
    track_uri = request.form["track_uri"]
    track = session.get_track(track_uri).load()
    session.player.load(track)
    session.player.play()
    return render_template("index.html")

if __name__ == '__main__':
    app.run('0.0.0.0')
