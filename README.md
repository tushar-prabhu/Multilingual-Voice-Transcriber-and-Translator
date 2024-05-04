# Multilingual Voice Transcriber and Translator

This application is a multilingual voice transcriber and translator built with PyQt5, Google Text-to-Speech (gTTS), and the `translate` and `speech_recognition` libraries.

## Table of Contents

- [Problem Statement](#problem-statement)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Note](#note)

## Problem Statement

In our increasingly globalized world, language barriers can pose significant challenges. This project aims to address this need by developing a multilingual voice transcriber and translator. The application listens to spoken language, transcribes it into text, translates the text into a selected language, and then converts the translated text back into speech, thereby facilitating communication across different languages.

## Features

- **Voice Transcription**: The application can transcribe spoken language into text using Google's Speech Recognition service.
- **Translation**: The transcribed text can be translated into various languages using the `translate` library.
- **Text-to-Speech**: The translated text can be converted back into speech using Google's Text-to-Speech service (gTTS).
- **Download Audio**: The audio of the translated text can be downloaded as an MP3 file.
- **Copy Text**: Both the transcribed and translated texts can be copied to the clipboard.

## Installation

_**Note**: Currently, Python 3.12.2 is being used as the interpreter for this project._

1. Clone this repository.
2. Install the dependencies:

```bash
pip install -r requirements.txt
```

## Usage

- Run the application:

```bash
python main.py
```

- Select the target language for translation from the dropdown menu.

- Click the 'Start Recording' button to start the voice transcription. Speak clearly into the microphone.

- The application will transcribe the spoken language into text, translate the text into the selected language, and then convert the translated text back into speech.

- The 'Download Audio' button allows you to download the audio of the translated text as an MP3 file.

- The 'Copy Spoken Text' and 'Copy Translated Text' buttons allow you to copy the transcribed and translated texts to the clipboard, respectively.

## License

This project is licensed under the terms of the [MIT license](LICENSE)

## Note

This project is a personal endeavor and updates or improvements are made based on my interest and availability. While I strive to ensure its functionality, the application may contain bugs and does not cover all edge cases. Your patience and understanding are appreciated.
