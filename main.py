import sys
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, \
    QGraphicsOpacityEffect, QScrollArea
from PyQt5.QtCore import QThread, pyqtSignal, QUrl, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont
import speech_recognition as sr
from translate import Translator
from gtts import gTTS

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
        self.setGeometry(100, 100, 600, 300)
        self.setWindowTitle('Voice Converter App')

        self.start_button = QPushButton('Start Recording', self)
        self.start_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; border: none; color: white; padding: 10px; font-size: 16px; border-radius: 6px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )

        self.spoken_scroll_area = QScrollArea(self)
        self.spoken_label = QLabel('Spoken Text:', self.spoken_scroll_area)
        self.spoken_label.setFont(QFont('Arial', 12))
        self.spoken_scroll_area.setWidgetResizable(True)
        self.spoken_scroll_area.setWidget(self.spoken_label)

        self.translated_scroll_area = QScrollArea(self)
        self.translated_label = QLabel('Translated Text:', self.translated_scroll_area)
        self.translated_label.setFont(QFont('Arial', 12))
        self.translated_scroll_area.setWidgetResizable(True)
        self.translated_scroll_area.setWidget(self.translated_label)

        self.language_dropdown = QComboBox(self)
        self.language_dropdown.setFont(QFont('Arial', 12))
        self.language_dict = {
            # ... (unchanged)
            "Select Language": "",
            "Afrikaans": "af",
            "Arabic": "ar",
            "Bulgarian": "bg",
            "Bengali": "bn",
            "Bosnian": "bs",
            "Catalan": "ca",
            "Czech": "cs",
            "Danish": "da",
            "German": "de",
            "Greek": "el",
            "English": "en",
            "Spanish": "es",
            "Estonian": "et",
            "Finnish": "fi",
            "French": "fr",
            "Gujarati": "gu",
            "Hindi": "hi",
            "Croatian": "hr",
            "Hungarian": "hu",
            "Indonesian": "id",
            "Icelandic": "is",
            "Italian": "it",
            "Hebrew": "iw",
            "Japanese": "ja",
            "Javanese": "jw",
            "Khmer": "km",
            "Kannada": "kn",
            "Korean": "ko",
            "Latin": "la",
            "Latvian": "lv",
            "Malayalam": "ml",
            "Marathi": "mr",
            "Malay": "ms",
            "Myanmar (Burmese)": "my",
            "Nepali": "ne",
            "Dutch": "nl",
            "Norwegian": "no",
            "Polish": "pl",
            "Portuguese": "pt",
            "Romanian": "ro",
            "Russian": "ru",
            "Sinhala": "si",
            "Slovak": "sk",
            "Albanian": "sq",
            "Serbian": "sr",
            "Sundanese": "su",
            "Swedish": "sv",
            "Swahili": "sw",
            "Tamil": "ta",
            "Telugu": "te",
            "Thai": "th",
            "Filipino": "tl",
            "Turkish": "tr",
            "Ukrainian": "uk",
            "Urdu": "ur",
            "Vietnamese": "vi",
            "Chinese (Simplified)": "zh-CN",
            "Chinese (Mandarin/Taiwan)": "zh-TW",
            "Chinese (Mandarin)": "zh"
        }
        self.language_dropdown.addItems(list(self.language_dict.keys()))

        vbox = QVBoxLayout()
        vbox.addWidget(self.start_button)
        vbox.addWidget(self.language_dropdown)
        vbox.addWidget(self.spoken_scroll_area)
        vbox.addWidget(self.translated_scroll_area)

        self.setLayout(vbox)

        self.start_button.clicked.connect(self.start_recording)

        self.recording = False
        self.selected_language = ""
        self.translator = Translator(to_lang="")  # Set a default value for to_lang

        self.recognition_thread = SpeechRecognitionThread(sr.Recognizer())
        self.recognition_thread.recognition_result.connect(self.translate_and_play)
        self.recognition_thread.finished.connect(self.on_recognition_finished)

        self.player = QMediaPlayer()

        self.fade_in_animation()

    def fade_in_animation(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.start_button.setEnabled(False)
            self.spoken_label.clear()
            self.translated_label.clear()
            self.selected_language = self.language_dict.get(self.language_dropdown.currentText(), "")
            if self.selected_language:
                self.translator.to_lang = self.selected_language  # Set the target language
                self.recognition_thread.start()

    def translate_and_play(self, text):
        print("Debug: Translating text")
        self.spoken_label.setText('Spoken Text: ' + text)

        translator = Translator(to_lang=self.selected_language)
        translated_text = translator.translate(text)

        print("Debug: Text translated")

        self.translated_label.setText('Translated Text: ' + translated_text)

        self.player.stop()
        self.player.setMedia(QMediaContent())

        print("Debug: Saving audio file")
        tts = gTTS(translated_text, lang=self.selected_language)
        tts.save("translated_audio.mp3")
        print("Debug: Audio file saved")

        print("Debug: Playing audio")
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile("translated_audio.mp3")))
        self.player.play()
        print("Debug: Audio played")

    def on_recognition_finished(self):
        self.recognition_thread.deleteLater()

        self.recognition_thread = SpeechRecognitionThread(sr.Recognizer())
        self.recognition_thread.recognition_result.connect(self.translate_and_play)
        self.recognition_thread.finished.connect(self.on_recognition_finished)

        self.recording = False
        self.start_button.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    converter_app = VoiceConverterApp()
    converter_app.show()
    sys.exit(app.exec_())
