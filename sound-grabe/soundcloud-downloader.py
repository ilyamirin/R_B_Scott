import os.path
from urllib.request import urlopen
import requests
import soundcloud


class SoundCloudDownloader:
    def __init__(self):
        self.client_id = "LHzSAKe8eP9Yy3FgBugfBapRPLncO6Ng"
        self.success_downloads = 0

    def get_stream_url(self, sid):
        stream_url = "https://api.soundcloud.com/i1/tracks/{0}/streams?client_id={1}".format(sid, self.client_id)
        json_stream = requests.get(stream_url)
        if json_stream.status_code == 200:
            return json_stream.json()['http_mp3_128_url']
        else:
            return False

    def download(self, url, title='mem'):
        if url:
            print('Check: %s' % title)
            if not os.path.exists("downloads/%s.mp3" % clean_title(title)):
                print('Downloading: %s' % title)
                html = requests.get(url)
                if download_file(url, "%s.mp3" % clean_title(title)):
                    self.success_downloads += 1

                    return True
            else:
                print('Skip: %s' % title)

        return False


def download_file(url, filename):
    try:
        f = urlopen(url)
        with open('downloads/%s' % filename, "wb") as song:
            song.write(f.read())

        return True
    finally:
        f = urlopen(url)
        print("Error occured while downloading file %s" % url)

        return False


def clean_title(title):
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789-_()$"

    return ''.join(c for c in title if c in allowed)


def main():
    tracks_count = int(input("Enter tracks count for download: "))
    genre = input("Enter genre: ")

    client = soundcloud.Client(client_id='NmW1FlPaiL94ueEu7oziOWjYEzZzQDcK')
    sc_downloader = SoundCloudDownloader()

    def download():
        tracks = client.get('/tracks', genres=genre, limit=100, linked_partitioning=1)
        current_track_index = 0
        while current_track_index <= tracks_count:
            for track in tracks.collection.data:
                if sc_downloader.download(sc_downloader.get_stream_url(track.id), track.title):
                    current_track_index += 1
                if current_track_index == tracks_count:
                    return
            next_href = tracks.obj['next_href']
            tracks = client.get(next_href)

    download()

    print("Success downloads: {0}/{1}".format(sc_downloader.success_downloads, tracks_count))


if __name__ == "__main__":
    main()
