import argparse
from model import logger
from model.gena import GenaModel

SAMPLING_RATE = 44100              #TODO: убрать копипасту
SAMPLE_SIZE = SAMPLING_RATE//100


def parse_arguments():
    parser = argparse.ArgumentParser(description="Generation")
    parser.add_argument('checkpoint_path', type=str)
    parser.add_argument('--duration', type=int, default=5)
    return parser.parse_known_args()


def main():
    known_args, unknown_args = parse_arguments()
    logger.configure_logger()
    model = GenaModel(SAMPLE_SIZE)
    model.load_weights(known_args.checkpoint_path)
    generate_samples_seconds = SAMPLING_RATE * known_args.duration
    model.generate_wav(generate_samples_seconds, "gen.wav")
    print('generated')


if __name__ == '__main__':
    main()
