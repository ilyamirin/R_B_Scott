from os import path
from pydub import AudioSegment
from os import path, scandir
import sys

# # files
# src = "transcript.mp3"
# dst = "test.wav"
#
# # convert wav to mp3
# sound = AudioSegment.from_mp3(src)
# sound.export(dst, format="wav")


def usage():
    print(path.basename(__file__) + " source_dir dst_dir")


def main():
    if len(sys.argv) != 3:
        usage()
        return

    source_dir = path.abspath(sys.argv[1])
    dst_dir = path.abspath(sys.argv[2])

    for file in scandir(source_dir):
        if not file.is_file():
            continue
        print(file.name)
        sound = AudioSegment.from_mp3(file.path)
        sound.export(dst_dir + "/" + file.name, format="wav")


if __name__ == '__main__':
    main()