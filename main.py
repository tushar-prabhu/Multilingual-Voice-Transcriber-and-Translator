import sys
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, \
    QGraphicsOpacityEffect, QScrollArea, QStatusBar, QFileDialog, QPlainTextEdit
from PyQt5.QtCore import QThread, pyqtSignal, QUrl, QPropertyAnimation, QEasingCurve, Qt
from PyQt5.QtGui import QFont, QClipboard, QTextCursor
import speech_recognition as sr
from translate import Translator
from gtts import gTTS


class SpeechRecognitionThread(QThread):
    recognition_result = pyqtSignal(str)
    status_signal = pyqtSignal(str)

    def __init__(self, recognizer):
        super().__init__()
        self.recognizer = recognizer

    def run(self):
        try:
            with sr.Microphone() as source:
                self.status_signal.emit("Microphone accessed")
                audio = self.recognizer.listen(source)
                self.status_signal.emit("Audio recorded")

            try:
                self.status_signal.emit("Recognizing...")
                text = self.recognizer.recognize_google(audio)
                self.status_signal.emit("Audio recognized")
                self.recognition_result.emit(text)
            except sr.UnknownValueError:
                self.status_signal.emit("Google Speech Recognition could not understand audio.")
            except sr.RequestError as e:
                self.status_signal.emit(f"Could not request results from Google Speech Recognition service; {str(e)}")
        except Exception as e:
            self.status_signal.emit(f"An error occurred: {str(e)}")


class VoiceConverterApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 800, 600)  # Increased window size
        self.setWindowTitle('Multilingual Voice Transcriber and Translator')

        self.start_button = QPushButton('Start Recording', self)
        self.start_button.setStyleSheet(
            "QPushButton { background-color: #4CAF50; border: none; color: white; padding: 10px; font-size: 16px; border-radius: 6px; }"
            "QPushButton:hover { background-color: #45a049; }"
        )

        self.spoken_scroll_area = QScrollArea(self)
        self.spoken_label = QPlainTextEdit(self.spoken_scroll_area)
        self.spoken_label.setFont(QFont('Arial', 14))  # Increased font size
        self.spoken_label.setReadOnly(True)
        self.spoken_scroll_area.setWidgetResizable(True)
        self.spoken_scroll_area.setWidget(self.spoken_label)

        self.translated_scroll_area = QScrollArea(self)
        self.translated_label = QPlainTextEdit(self.translated_scroll_area)
        self.translated_label.setFont(QFont('Arial', 14))  # Increased font size
        self.translated_label.setReadOnly(True)
        self.translated_scroll_area.setWidgetResizable(True)
        self.translated_scroll_area.setWidget(self.translated_label)

        self.language_dropdown = QComboBox(self)
        self.language_dropdown.setFont(QFont('Arial', 14))  # Increased font size
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

        self.status_bar = QStatusBar(self)

        self.download_button = QPushButton('Download Audio', self)
        self.download_button.setStyleSheet(
            "QPushButton { background-color: #008CBA; border: none; color: white; padding: 10px; font-size: 16px; border-radius: 6px; }"
            "QPushButton:hover { background-color: #00688B; }"
        )
        self.download_button.setEnabled(False)  # Disable initially
        self.download_button.clicked.connect(self.download_audio)

        self.copy_spoken_button = QPushButton('Copy Spoken Text', self)
        self.copy_spoken_button.clicked.connect(self.copy_spoken_text)

        self.copy_translated_button = QPushButton('Copy Translated Text', self)
        self.copy_translated_button.clicked.connect(self.copy_translated_text)

        vbox = QVBoxLayout()
        vbox.addWidget(self.start_button)
        vbox.addWidget(self.language_dropdown)
        vbox.addWidget(self.spoken_scroll_area)
        vbox.addWidget(self.copy_spoken_button)
        vbox.addWidget(self.translated_scroll_area)
        vbox.addWidget(self.copy_translated_button)
        vbox.addWidget(self.status_bar)
        vbox.addWidget(self.download_button)

        # Add some spacing between widgets
        vbox.setSpacing(15)

        self.setLayout(vbox)

        self.start_button.clicked.connect(self.start_recording)

        self.recording = False
        self.selected_language = ""
        self.translator = Translator(to_lang="")  # Set a default value for to_lang

        self.recognition_thread = SpeechRecognitionThread(sr.Recognizer())
        self.recognition_thread.recognition_result.connect(self.translate_and_play)
        self.recognition_thread.status_signal.connect(self.update_status)
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
        self.update_status("Translating text")
        self.spoken_label.setPlainText('Spoken Text: ' + text)

        translator = Translator(to_lang=self.selected_language)
        translated_text = translator.translate(text)

        self.update_status("Text translated")

        self.translated_label.setPlainText('Translated Text: ' + translated_text)

        self.player.stop()
        self.player.setMedia(QMediaContent())

        self.update_status("Saving audio file")
        tts = gTTS(translated_text, lang=self.selected_language)
        tts.save("translated_audio.mp3")
        self.update_status("Audio file saved")

        # Enable the download button
        self.download_button.setEnabled(True)

        self.update_status("Playing audio")
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile("translated_audio.mp3")))
        self.player.play()
        self.update_status("Audio played")

    def on_recognition_finished(self):
        self.recognition_thread.deleteLater()

        self.recognition_thread = SpeechRecognitionThread(sr.Recognizer())
        self.recognition_thread.recognition_result.connect(self.translate_and_play)
        self.recognition_thread.status_signal.connect(self.update_status)
        self.recognition_thread.finished.connect(self.on_recognition_finished)

        self.recording = False
        self.start_button.setEnabled(True)

    def update_status(self, status):
        self.status_bar.showMessage(status)

    def download_audio(self):
        translated_text = self.translated_label.toPlainText().replace('Translated Text: ', '')
        tts = gTTS(translated_text, lang=self.selected_language)
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Audio File", "translated_audio.mp3", "Audio Files (*.mp3)")
        if file_path:
            tts.save(file_path)
            self.update_status("Audio file saved")

    def copy_spoken_text(self):
        spoken_text = self.spoken_label.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(spoken_text)
        self.update_status("Spoken text copied to clipboard")

    def copy_translated_text(self):
        translated_text = self.translated_label.toPlainText()
        clipboard = QApplication.clipboard()
        clipboard.setText(translated_text)
        self.update_status("Translated text copied to clipboard")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    converter_app = VoiceConverterApp()
    converter_app.show()
    sys.exit(app.exec_())
