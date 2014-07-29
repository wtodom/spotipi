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
playback_in_progress = threading.Event()

def on_connection_state_updated(session):
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in.set()

def on_end_of_track(self):
    if len(song_queue) > 0:
        play_track(song_queue.pop())
    else:
        end_of_track.set()

def on_playback_in_progress():
    print("started.")
    playback_in_progress.set()

## Handlers
session.on(
    spotify.SessionEvent.CONNECTION_STATE_UPDATED,
    on_connection_state_updated
    )

session.on(
    spotify.SessionEvent.END_OF_TRACK,
    on_end_of_track
    )

session.on(
    spotify.SessionEvent.START_PLAYBACK,
    on_playback_in_progress
    )

username = config.get("credentials", "username")
password = config.get("credentials", "password")
session.login(username, password, remember_me=True)

## API
@app.route("/queue", methods=["GET"])
def get_queue():
    return str(song_queue)

@app.route("/queue/add/<link>", methods=["GET", "POST"])
def add_to_queue(link):
    song_queue.append(link)
    if len(song_queue) == 1 and not playback_in_progress.is_set():
        play_track(song_queue.pop())
    return "added"

@app.route("/queue/clear", methods=["POST"])
def clear_queue():
    song_queue.clear()
    return "cleared"

@app.route("/pause", methods=["POST"])
def pause():
    pass

@app.route("/skip", methods=["POST"])
def skip():
    pass

@app.route("/play/<link>", methods=["GET", "POST"])
def play_track(link):
    session.emit(spotify.SessionEvent.START_PLAYBACK)
    track = session.get_track(link).load()
    session.player.load(track)
    session.player.play()

    return "playing..."

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001)
