import math
import multiprocessing
import os
import argparse
from random import shuffle
import torchaudio
import torchaudio.transforms as T

import torch
from glob import glob
from tqdm import tqdm

from audiolm_pytorch import SoundStream, EncodecWrapper
import utils
import logging

logging.getLogger("numba").setLevel(logging.WARNING)
import librosa
import numpy as np

hps = utils.get_hparams_from_file("config.json")
sampling_rate = hps.data.sampling_rate
hop_length = hps.data.hop_length
in_dir = ""

def process_one(filename, hmodel, codec):
    wav, sr = torchaudio.load(filename)
    if wav.shape[0] > 1:  # mix to mono
        wav = wav.mean(dim=0, keepdim=True)
    wav16k = T.Resample(sr, 16000)(wav)
    wav24k = T.Resample(sr, 24000)(wav)
    filename = filename.replace(in_dir, in_dir+"_processed")
    wav24k_path = filename
    if not os.path.exists(os.path.dirname(wav24k_path)):
        os.makedirs(os.path.dirname(wav24k_path))
    torchaudio.save(wav24k_path, wav24k, 24000)
    soft_path = filename + ".soft.pt"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    wav16k = wav16k.to(device)
    c = utils.get_hubert_content(hmodel, wav_16k_tensor=wav16k[0])
    torch.save(c.cpu(), soft_path)

    f0_path = filename + ".f0.npy"
    f0 = utils.compute_f0_dio(
        wav24k.cpu().numpy()[0], sampling_rate=24000, hop_length=hop_length
    )
    np.save(f0_path, f0)

    spec_path = filename.replace(".wav", ".spec.pt")
    spec_process = torchaudio.transforms.MelSpectrogram(
        sample_rate=24000,
        n_fft=1024,
        hop_length=256,
        n_mels=100,
        center=True,
        power=1,
    )
    spec = spec_process(wav24k)# 1 100 T
    spec = torch.log(torch.clip(spec, min=1e-7))
    torch.save(spec, spec_path)


def process_batch(filenames):
    print("Loading hubert for content...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    hmodel = utils.get_hubert_model().to(device)
    codec = EncodecWrapper()
    print("Loaded hubert.")
    for filename in tqdm(filenames):
        process_one(filename, hmodel, codec)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--in_dir", type=str, default="dataset", help="path to input dir"
    )

    args = parser.parse_args()
    filenames = glob(f"{args.in_dir}/**/*.wav", recursive=True)  # [:10]
    in_dir = args.in_dir
    shuffle(filenames)
    process_batch(filenames)
