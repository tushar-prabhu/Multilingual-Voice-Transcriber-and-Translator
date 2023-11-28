import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import QThread, pyqtSignal, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
import speech_recognition as sr
from translate import Translator
from gtts import gTTS,lang

class SpeechRecognitionThread(QThread):
    recognition_result = pyqtSignal(str)

    def __init__(self, recognizer):
        super().__init__()
        self.recognizer = recognizer

    def run(self):
        try:
            with sr.Microphone() as source:
                print("Debug: Microphone accessed")
                audio = self.recognizer.listen(source)
                print("Debug: Audio recorded")

            try:
                print("Recognizing...")
                text = self.recognizer.recognize_google(audio)
                print("Debug: Audio recognized")
                self.recognition_result.emit(text)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio.")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))
        except Exception as e:
            print("An error occurred: ", str(e))

class VoiceConverterApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.start_button = QPushButton('Start Recording', self)
        self.spoken_label = QLabel('Spoken Text:', self)
        self.translated_label = QLabel('Translated Text:', self)

        vbox = QVBoxLayout()
        vbox.addWidget(self.start_button)
        vbox.addWidget(self.spoken_label)
        vbox.addWidget(self.translated_label)

        self.setLayout(vbox)

        self.start_button.clicked.connect(self.start_recording)

        self.recording = False
        self.translator = Translator(to_lang="ja")

        # Create a separate thread for speech recognition
        self.recognition_thread = SpeechRecognitionThread(sr.Recognizer())
        self.recognition_thread.recognition_result.connect(self.translate_and_play)
        self.recognition_thread.finished.connect(self.on_recognition_finished)

        # Create a QMediaPlayer object for audio playback
        self.player = QMediaPlayer()

    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.start_button.setEnabled(False)
            self.spoken_label.clear()
            self.translated_label.clear()
            self.recognition_thread.start()

    def translate_and_play(self, text):
        print("Debug: Translating text")
        # Display spoken text
        self.spoken_label.setText('Spoken Text: ' + text)

        # Translate the text to Japanese
        translated_text = self.translator.translate(text)

        print("Debug: Text translated")

        # Display translated text
        self.translated_label.setText('Translated Text: ' + translated_text)

        # Stop QMediaPlayer and clear its media
        self.player.stop()
        self.player.setMedia(QMediaContent())

        # Save the translated text as an audio file
        print("Debug: Saving audio file")
        tts = gTTS(translated_text, lang='ja')
        tts.save("translated_audio.mp3")
        print("Debug: Audio file saved")
        print(lang.tts_langs())
        # Play the audio using QMediaPlayer
        print("Debug: Playing audio")
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile("translated_audio.mp3")))
        self.player.play()
        print("Debug: Audio played")

    def on_recognition_finished(self):
        # Delete the finished QThread
        self.recognition_thread.deleteLater()

        # Create a new QThread for speech recognition
        self.recognition_thread = SpeechRecognitionThread(sr.Recognizer())
        self.recognition_thread.recognition_result.connect(self.translate_and_play)
        self.recognition_thread.finished.connect(self.on_recognition_finished)

        # Reset the recording flag and enable the start button
        self.recording = False
        self.start_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    converter_app = VoiceConverterApp()
    converter_app.setWindowTitle('Voice Converter App')
    converter_app.resize(400, 200)
    converter_app.show()
    app.exec_()
