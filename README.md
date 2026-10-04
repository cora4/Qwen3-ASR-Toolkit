# Qwen3-ASR-Toolkit

[![PyPI version](https://badge.fury.io/py/qwen3-asr-toolkit.svg)](https://badge.fury.io/py/qwen3-asr-toolkit)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Also in](https://img.shields.io/badge/Also%20in-Java-orange.svg)](#-implementations-in-other-languages)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview 

An advanced, high-performance Python command-line toolkit for using the **Qwen-ASR API** (formerly Qwen3-ASR-Flash). This implementation overcomes the API's 3-minute audio length limitation by intelligently splitting long audio/video files and processing them in parallel, enabling rapid transcription of hours-long content.

## 🚀 Key Features

-   **Break the 3-Minute Limit**: Seamlessly transcribe audio and video files of any length by bypassing the official API's duration constraint.
-   **Smart Audio Splitting**: Utilizes **Voice Activity Detection (VAD)** to split audio into meaningful chunks at natural silent pauses. This ensures that words and sentences are not awkwardly cut off.
-   **Intelligent Post-Processing**: Automatically detects and removes common ASR **hallucinations and repetitive artifacts** for cleaner, more accurate transcripts.
-   **Automatic Audio Resampling**: Automatically converts audio from any sample rate and channel count to the 16kHz mono format required by the Qwen-ASR API. You can use any audio file without worrying about pre-processing.
-   **Universal Media Support**: Supports virtually any audio and video format (e.g., `.mp4`, `.mov`, `.mkv`, `.mp3`, `.wav`, `.m4a`) thanks to its reliance on FFmpeg.
-   **Simple & Easy to Use**: A straightforward command-line interface allows you to get started with just a single command.

## ⚙️ How It Works

This tool follows a robust pipeline to deliver fast and accurate transcriptions for long-form media:

1.  **Media Loading**: The script first loads your media file, whether it's a **local file or a remote URL**.
2.  **VAD-based Chunking**: It analyzes the audio stream using Voice Activity Detection (VAD) to identify silent segments.
3.  **Intelligent Splitting**: The audio is then split into smaller chunks based on the detected silences. Each chunk's duration is managed to stay under 1-minute, with a **user-configurable target length (defaulting to 45 seconds)**, preventing mid-sentence cuts.
4.  **API Calls**: A thread is initiated to upload and process these chunks using the Qwen-ASR API.
5.  **Result Aggregation & Cleaning**: The transcribed text segments from all chunks are collected, re-ordered, and then **post-processed to remove detected repetitions and hallucinations**.
6.  **Output Generation**: The final, cleaned transcription is printed to the console and saved to a `.txt` file.

## 🏁 Getting Started

Follow these steps to set up and run the project on your local machine.

### Prerequisites

-   Python 3.8 or higher.
-   **FFmpeg**: The script requires FFmpeg to be installed on your system to handle media files.
    -   **Ubuntu/Debian**: `sudo apt update && sudo apt install ffmpeg`
    -   **macOS**: `brew install ffmpeg`
    -   **Windows**: Download from the [official FFmpeg website](https://ffmpeg.org/download.html) and add it to your system's PATH.

### Installation

We recommend installing the tool directly from PyPI for the simplest setup.

#### Option 1: Install from PyPI (Recommended)

Simply run the following command in your terminal. This will install the package and make the `qwen3-asr` command available system-wide.

```bash
pip install qwen3-asr-toolkit
```

#### Option 2: Install from Source

If you want to install the latest development version or contribute to the project, you can install from the source code.

1.  Clone the repository:
    ```bash
    cd Qwen3-ASR-Toolkit
    ```

2.  Install the package:
    ```bash
    pip install .
    ```

## 📖 Usage

Once installed, you can use the `qwen3-asr` command directly from your terminal. By default, the tool will print progress information.

### Command

```bash
qwen3-asr -i <input_file_or_url> [-key <api_key>] [-j <num_threads>] [-c <context>] [-d <duration>] [-t <tmp_dir>] [--save-srt] [-s]
```

### Arguments

| Argument                  | Short  | Description                                                                          | Required/Optional                        |
| ------------------------- | ------ | ------------------------------------------------------------------------------------ | ---------------------------------------- |
| `--input-file`            | `-i`   | Path to the local media file or a remote URL (http/https) to transcribe.             | **Required**                             |
| `--context`               | `-c`   | Language context to guide the ASR model                                              | Optional, Default: `"None"`                  |
| `--num-threads`           | `-j`   | The number of concurrent threads to use for API calls.                               | Optional, **Default: 4**                 |
| `--vad-segment-threshold` | `-d`   | Target duration in seconds for each VAD-split audio chunk.                           | Optional, **Default: 45**               |
| `--tmp-dir`               | `-t`   | Path to a directory for storing temporary chunk files.                               | Optional, Default: `~/qwen3-asr-cache`   |
| `--silence`               | `-s`   | Silence mode. Suppresses detailed progress and chunking information on the terminal. | Optional                                 |

### Output

The full transcription result will be printed to the terminal (unless in `--silence` mode) and also saved in a `.txt` file in the same directory as the input file. For example, if you process `my_video.mp4`, the output will be saved to `my_video.txt`.

---

## ✨ Examples

Here are a few examples of how to use the tool.

#### 1. Basic Transcription of a Local File

Transcribe a video file using the default 4 threads.

```bash
qwen3-asr -i "/path/to/my/long_lecture.mp4"
```

#### 2. Transcribe a Remote Audio File

Directly process an audio file from a URL.

```bash
qwen3-asr -i "https://somewebsite.com/audios/podcast_episode.mp3"
```

#### 3. Provide Context and Customize Chunk Duration

If your audio contains specific language, use the `-c` flag. If you prefer shorter, more frequent subtitle segments, use `-d` to set a smaller chunk duration.

```bash
qwen3-asr -i "/path/to/my/tech_talk.mp4" -c "French" -d 60
```
*This command will try to split the audio into chunks around 60 seconds long, which can result in more granular subtitles.*

#### 6. Run in Silence Mode

Use the `-s` or `--silence` flag to prevent progress details from being printed to the terminal. The final transcript will still be saved to a file.

```bash
qwen3-asr -i "/path/to/my/meeting_recording.m4a" -s
```

## 🌍 Implementations in Other Languages

While this project provides a full-featured Python toolkit, we also host implementations in other programming languages to demonstrate how the same core logic can be applied across different technology stacks. We warmly welcome the community to contribute examples in more languages!

### ☕ Java Example

We have provided a Java version as a standalone example located in the `examples/java-example` directory of this repository. This example showcases how to implement the key features of the toolkit—including VAD-based audio chunking, parallel API requests, and result aggregation—using Java. It serves as a great starting point for Java developers looking to integrate Qwen-ASR into their applications.

### How to Contribute Your Version

If you have implemented a similar toolkit in another language (e.g., **Go**, **Rust**, **C#**, **JavaScript/Node.js**), we would love to feature it! Please open a pull request to add your implementation to the `examples` directory. For more details on contributing, see the [Contributing](#-contributing) section below.

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements, please feel free to fork the repo, create a feature branch, and open a pull request. You can also open an issue with the "enhancement" tag.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
