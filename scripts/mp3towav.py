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


def convert(source_dir, dst_dir):
    for file in scandir(source_dir):
        if file.is_dir():
            convert(file.path, dst_dir)
            continue

        if not file.is_file() or not file.name.lower().endswith(".mp3"):
            continue
        try:
            print("processing " + file.name)
        except Exception as e:
            print(e)

        sound = AudioSegment.from_mp3(file.path)
        sound.export(dst_dir + "/" + file.name + ".wav", format="wav")


def main():
    if len(sys.argv) != 3:
        usage()
        return

    source_dir = path.abspath(sys.argv[1])
    dst_dir = path.abspath(sys.argv[2])
    convert(source_dir, dst_dir)


if __name__ == '__main__':
    main()
