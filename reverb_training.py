import sys
import numpy as np
import soundfile as sf
import sounddevice as sd
from scipy.signal import convolve
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
                             QFileDialog, QComboBox, QMessageBox)

class ReverbTrainingApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # Inicializa as variáveis e a biblioteca de IRs antes de configurar a interface
        self.ir_library = {
            "Small Room": "IRs/small_room_ir.wav",
            "Large Hall": "IRs/large_hall_ir.wav",
            "Church": "IRs/church_ir.wav"
        }
        self.loaded_irs = {}
        self.audio_data = None
        self.sample_rate = None
        self.reverbed_audio = None  # Inicializa reverbed_audio como None
        self.correct_reverb = None  # Tipo de reverb correto
        self.clip_start = 0  # Inicializa o ponto inicial do clipe

        # Carregar IRs
        for name, path in self.ir_library.items():
            try:
                ir_data, ir_sample_rate = sf.read(path)
                # Converter IR para mono se estiver em estéreo
                if ir_data.ndim > 1:
                    ir_data = np.mean(ir_data, axis=1)
                self.loaded_irs[name] = ir_data
            except FileNotFoundError:
                QMessageBox.warning(self, "Error", f"IR file '{path}' not found.")
        
        # Configura a interface
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Reverb Training - Identify the Reverb Type')

        # Button to load an audio file
        self.open_button = QPushButton('Select Audio File', self)
        self.open_button.clicked.connect(self.open_file)

        # Button to play original audio
        self.play_original_button = QPushButton('Play Original Audio', self)
        self.play_original_button.clicked.connect(self.play_original)
        self.play_original_button.setEnabled(False)

        # Button to play audio with reverb
        self.play_reverbed_button = QPushButton('Play Audio with Reverb', self)
        self.play_reverbed_button.clicked.connect(self.play_reverbed)
        self.play_reverbed_button.setEnabled(False)

        # ComboBox to let the user guess the reverb type
        self.guess_selector = QComboBox(self)
        self.guess_selector.addItems(list(self.ir_library.keys()))
        self.guess_selector.setEnabled(False)

        # Button to submit the guess
        self.check_button = QPushButton('Check Guess', self)
        self.check_button.clicked.connect(self.check_guess)
        self.check_button.setEnabled(False)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.open_button)
        layout.addWidget(self.play_original_button)
        layout.addWidget(self.play_reverbed_button)
        layout.addWidget(QLabel("Guess the Reverb Type:"))
        layout.addWidget(self.guess_selector)
        layout.addWidget(self.check_button)

        self.setLayout(layout)
        self.show()

    def open_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "",
                                                  "Audio Files (*.wav *.flac *.ogg)", options=options)
        if fileName:
            self.full_audio_data, self.sample_rate = sf.read(fileName)
            if len(self.full_audio_data.shape) > 1:
                self.full_audio_data = np.mean(self.full_audio_data, axis=1)  # Convert to mono

            # Select a random 5-second clip
            self.select_random_clip()

            # Apply a random reverb effect
            self.apply_random_reverb()

            self.play_original_button.setEnabled(True)
            self.play_reverbed_button.setEnabled(True)
            self.guess_selector.setEnabled(True)
            self.check_button.setEnabled(True)
            QMessageBox.information(self, 'File Loaded', 'Audio file loaded successfully. Try to guess the reverb type!')

    def select_random_clip(self):
        # Select a random 5-second clip from the full audio
        max_start = max(0, len(self.full_audio_data) - 5 * self.sample_rate)
        if max_start <= 0:
            self.clip_start = 0
        else:
            self.clip_start = np.random.randint(0, max_start)
        clip_end = self.clip_start + 5 * self.sample_rate
        self.audio_data = self.full_audio_data[int(self.clip_start):int(clip_end)]
        if len(self.audio_data) < 5 * self.sample_rate:
            self.audio_data = np.pad(self.audio_data, (0, int(5 * self.sample_rate - len(self.audio_data))), 'constant')

    def apply_random_reverb(self):
        # Select a random reverb type
        self.correct_reverb = np.random.choice(list(self.ir_library.keys()))
        ir_data = self.loaded_irs.get(self.correct_reverb)
        
        if ir_data is not None:
            # Apply the selected IR to the audio clip
            self.reverbed_audio = convolve(self.audio_data, ir_data, mode='full')
            # Normalize to avoid saturation
            max_val = np.max(np.abs(self.reverbed_audio))
            if max_val > 1.0:
                self.reverbed_audio /= max_val

    def play_original(self):
        sd.stop()
        sd.play(self.audio_data, self.sample_rate)

    def play_reverbed(self):
        if self.reverbed_audio is not None:
            sd.stop()
            sd.play(self.reverbed_audio[:len(self.audio_data)], self.sample_rate)
        else:
            QMessageBox.warning(self, "Error", "Reverb has not been applied. Please load an audio file first.")

    def check_guess(self):
        # Get the user's guess and compare it to the correct reverb
        user_guess = self.guess_selector.currentText()
        if user_guess == self.correct_reverb:
            QMessageBox.information(self, "Result", "Correct! You guessed the reverb type.")
        else:
            QMessageBox.information(self, "Result", f"Incorrect. The correct reverb was: {self.correct_reverb}.")
        
        # Apply a new random reverb for the next round
        self.select_random_clip()
        self.apply_random_reverb()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ReverbTrainingApp()
    sys.exit(app.exec_())

