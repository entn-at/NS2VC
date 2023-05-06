import torch
import torch.nn as nn
import torch.nn.functional as F
import json
from model import NaturalSpeech2, TextEncoder, F0Predictor, Diffusion_Encoder
from audiolm_pytorch import SoundStream, EncodecWrapper
from dataset import NS2VCDataset,TextAudioCollate
from torch.utils.data import Dataset, DataLoader
from multiprocessing import cpu_count



if __name__ == '__main__':
    cfg = json.load(open('config.json'))


    collate_fn = TextAudioCollate()
    codec = EncodecWrapper()
    ds = NS2VCDataset(cfg, codec)
    dl = DataLoader(ds, batch_size = cfg['train']['train_batch_size'], shuffle = True, pin_memory = True, num_workers = 0, collate_fn = collate_fn)
    # c, f0, codes, audio, uv = ds[0]
    # print(c.shape, f0.shape, codes.shape, audio.shape, uv.shape)
    # c_padded, refer_padded, f0_padded, codes_padded, wav_padded, lengths, refer_lengths, uv_padded = next(iter(dl))
    # print(c_padded.shape, refer_padded.shape, f0_padded.shape, codes_padded.shape, wav_padded.shape, lengths.shape, refer_lengths.shape, uv_padded.shape)
    data = next(iter(dl))
    model = NaturalSpeech2(cfg)
    out = model(data)
    out.backward()
    # print(lengths)
    # print(refer_lengths)
    


    # phoneme_encoder = TextEncoder(**cfg['phoneme_encoder'])
    # f0_predictor = F0Predictor(**cfg['f0_predictor'])
    # prompt_encoder = TextEncoder(**cfg['prompt_encoder'])
    # diff_model = Diffusion_Encoder(**cfg['diffusion_encoder'])
    # audio_prompt = torch.randn(3, 256, 80)
    # contentvec = torch.randn(3, 256, 200)
    # f0 = torch.randint(1,100,(3, 200))
    # noised_audio = torch.randn(3, 512, 200)
    # times = torch.randn(3)
    # audio_prompt_length = torch.tensor([3, 4, 5])
    # contentvec_length = torch.tensor([3, 4, 5])
    # #ok
    # audio_prompt = prompt_encoder(audio_prompt,audio_prompt_length)
    # #ok
    # f0_pred = f0_predictor(contentvec, audio_prompt, contentvec_length, audio_prompt_length)
    # #ok
    # content = phoneme_encoder(contentvec, contentvec_length,f0)
    # #ok
    # pred = diff_model(
    #     noised_audio,
    #     content, audio_prompt, 
    #     contentvec_length, audio_prompt_length,
    #     times)






