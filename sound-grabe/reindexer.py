import os

from models import *

directory = 'downloads/'


def reindex_exist_tracks():
    try:
        Track.create_table()
    except InternalError as px:
        print(str(px))

    for filename in os.listdir(directory):
        add_track(filename.split('.')[0])

    return [track.title for track in Track.select()]
