import os
import time
import random

from pydub import AudioSegment
from openai import OpenAI
import base64

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="EMPTY"
)

MAX_API_RETRY = 1
API_RETRY_SLEEP = (1, 2)


language_code_mapping = {
    "ar": "Arabic",
    "zh": "Chinese",
    "en": "English",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "pt": "Portuguese",
    "ru": "Russian",
    "es": "Spanish"
}


class QwenASR:
    def __init__(self, model: str = "qwen3-asr"):
        self.model = model

    def post_text_process(self, text, threshold=20):
        def fix_char_repeats(s, thresh):
            res = []
            i = 0
            n = len(s)
            while i < n:
                count = 1
                while i + count < n and s[i + count] == s[i]:
                    count += 1

                if count > thresh:
                    res.append(s[i])
                    i += count
                else:
                    res.append(s[i:i + count])
                    i += count
            return ''.join(res)

        def fix_pattern_repeats(s, thresh, max_len=20):
            n = len(s)
            min_repeat_chars = thresh * 2
            if n < min_repeat_chars:
                return s

            i = 0
            result = []
            while i <= n - min_repeat_chars:
                found = False
                for k in range(1, max_len + 1):
                    if i + k * thresh > n:
                        break

                    pattern = s[i:i + k]

                    valid = True
                    for rep in range(1, thresh):
                        start_idx = i + rep * k
                        if s[start_idx:start_idx + k] != pattern:
                            valid = False
                            break

                    if valid:
                        total_rep = thresh
                        end_index = i + thresh * k
                        while end_index + k <= n and s[end_index:end_index + k] == pattern:
                            total_rep += 1
                            end_index += k

                        result.append(pattern)
                        result.append(fix_pattern_repeats(s[end_index:], thresh, max_len))
                        i = n
                        found = True
                        break

                if found:
                    break
                else:
                    result.append(s[i])
                    i += 1

            if not found:
                result.append(s[i:])
            return ''.join(result)

        text = fix_char_repeats(text, threshold)
        return fix_pattern_repeats(text, threshold)

    def asr(self, wav_url: str, context: str = ""):
        my_lang = context
        prefix = "language"
        suffix = "<asr_text>"
        combined_text = f"{prefix} {my_lang}{suffix}"

        if not wav_url.startswith("http"):
            assert os.path.exists(wav_url), f"{wav_url} not exists!"
            file_path = wav_url
            file_size = os.path.getsize(file_path)

            with open(wav_url, "rb") as f:
                audio_bytes = f.read()

            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

            wav_url = f"file://{wav_url}"

            assistant_message = {
                "role": "assistant",
                "content": "",
                "tool_calls": []
            }

        # Submit the ASR task
        for _ in range(MAX_API_RETRY):
            try:
                stream = client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "input_audio",
                                    "input_audio": {
                                        "data": audio_base64,
                                        "format": "wav"
                                    }
                                }
                            ]
                        },
                        {
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "text",
                                    "text": combined_text
                                }
                            ]
                        }
                    ],
                    stream=True
                )

                for chunk in stream:
                    choice = chunk.choices[0]

                    # print streamed text
                    if choice.delta and choice.delta.content:
                        print(choice.delta.content, end="", flush=True)
                        assistant_message["content"] += choice.delta.content

                print()
                recog_text = assistant_message["content"]

                output = assistant_message["content"]

                recog_text = None
                if len(assistant_message["content"]):
                    recog_text = assistant_message["content"]
                if recog_text is None:
                    recog_text = ""

                lang_code = None
                language = language_code_mapping.get(lang_code, "Not Supported")

                return language, self.post_text_process(recog_text)
            except Exception as e:
                try:
                    print(f"Retry {_ + 1}...  {wav_url}\n{response}")
                    if response.code == "DataInspectionFailed":
                        print(f"DataInspectionFailed! Invalid input audio \"{wav_url}\"")
                        break
                except Exception as e:
                    print(f"Retry {_ + 1}...  {wav_url}\n{e}")
            time.sleep(random.uniform(*API_RETRY_SLEEP))
        raise Exception(f"{wav_url} task failed!\n{response}")


if __name__ == "__main__":
    qwen_asr = QwenASR(model="qwen3-asr")
    asr_text = qwen_asr.asr(wav_url="/path/to/your/wav_file.wav")
    print(asr_text)
