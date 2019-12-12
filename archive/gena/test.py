import argparse
import librosa

def parse_arguments():
    parser = argparse.ArgumentParser(description="Description")
    parser.add_argument('--data_dir', '-D', type=str, required=True)
    return parser.parse_args()


def main():
    l = librosa.load("./data_dir/01. Breeze.mp3")
    arguments = parse_arguments()


if __name__ == '__main__':
    main()
