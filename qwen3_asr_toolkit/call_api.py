import argparse
import os
import srt
import requests
import concurrent.futures

from tqdm import tqdm
from datetime import timedelta
from collections import Counter
from silero_vad import load_silero_vad
from qwen3_asr_toolkit.qwen3asr import QwenASR
from qwen3_asr_toolkit.audio_tools import load_audio, process_vad, save_audio_file, WAV_SAMPLE_RATE


def parse_args():
    parser = argparse.ArgumentParser(
        description="Python toolkit for the Qwen3-ASR API—parallel high‑throughput calls, robust long‑audio transcription, multi‑sample‑rate support."
    )
    parser.add_argument("--input-file", '-i', type=str, required=True, help="Input media file path")
    parser.add_argument("--context", '-c', type=str, default="None", help="Any text context content for Qwen3-ASR")
    parser.add_argument("--num-threads", '-j', type=int, default=4, help="Number of threads to use for parallel calls")
    parser.add_argument("--vad-segment-threshold", '-d', type=int, default=45, help="Segment threshold seconds for VAD")
    parser.add_argument("--tmp-dir", '-t', type=str, default=os.path.join(os.path.expanduser("~"), "qwen3-asr-cache"), help="Temp directory path")
    parser.add_argument("--silence", '-s', action="store_true", help="Reduce the output info on the terminal")
    return parser.parse_args()


def main():
    args = parse_args()
    input_file = args.input_file
    context = args.context
    num_threads = args.num_threads
    vad_segment_threshold = args.vad_segment_threshold
    tmp_dir = args.tmp_dir
    silence = args.silence

    # check if input file exists
    if input_file.startswith(("http://", "https://")):
        try:
            response = requests.head(input_file, allow_redirects=True, timeout=5)
            if response.status_code >= 400:
                raise FileNotFoundError(f"returned status code {response.status_code}")
        except Exception as e:
            raise FileNotFoundError(f"HTTP link {input_file} does not exist or is inaccessible: {str(e)}")
    elif not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file \"{input_file}\" does not exist!")

    qwen3asr = QwenASR(model="qwen3-asr")

    wav = load_audio(input_file)
    if not silence:
        print(f"Loaded wav duration: {len(wav) / WAV_SAMPLE_RATE:.2f}s")

    # Segment wav exceeding 1 minute
    if len(wav) / WAV_SAMPLE_RATE >= 60:
        if not silence:
            print(f"Wav duration is longer than 1 min, initializing Silero VAD model for segmenting...")
        worker_vad_model = load_silero_vad(onnx=True)
        wav_list = process_vad(wav, worker_vad_model, segment_threshold_s=vad_segment_threshold)
        if not silence:
            print(f"Segmenting done, total segments: {len(wav_list)}")
    else:
        wav_list = [(0, len(wav), wav)]

    # Save processed audio to tmp dir
    wav_name = os.path.basename(input_file)
    wav_dir_name = os.path.splitext(wav_name)[0]
    save_dir = os.path.join(tmp_dir, wav_dir_name)

    wav_path_list = []
    for idx, (_, _, wav_data) in enumerate(wav_list):
        wav_path = os.path.join(save_dir, f"{wav_name}_{idx}.wav")
        save_audio_file(wav_data, wav_path)
        wav_path_list.append(wav_path)

    # Sequential API call
    results = [] # (segment_index, recognized_text)
    languages = []

    for idx, wav_path in enumerate(wav_path_list):
        # Call the Qwen3‑ASR API synchronously
        language, recog_text = qwen3asr.asr(wav_path, context)
        results.append((idx, recog_text))
        languages.append(language)

    # Sort and splice in the original order
    results.sort(key=lambda x: x[0])
    full_text = " ".join(text for _, text in results)
    language = Counter(languages).most_common(1)[0][0]

    if not silence:
        print(f"Full Transcription:\n{full_text}")

    # Delete tmp save dir
    os.system(f"rm -rf {save_dir}")

    # Save full text to local file
    if os.path.exists(input_file):
        save_file = os.path.splitext(input_file)[0] + ".txt"
    else:
        raise FileNotFoundError(f"Input file \"{input_file}\" does not exist!")

    with open(save_file, 'w') as f:
        f.write(full_text + '\n')

    print(f"Full transcription of \"{input_file}\" from Qwen3-ASR API saved to \"{save_file}\"!")

if __name__ == '__main__':
    main()
