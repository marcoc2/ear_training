import sys
import numpy as np
import soundfile as sf
from scipy.signal import butter, lfilter
import sounddevice as sd
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
                             QFileDialog, QComboBox, QMessageBox, QHBoxLayout)
from PyQt5.QtCore import Qt

class EarTrainingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.audio_data = None
        self.sample_rate = None
        self.modified_audio = None
        self.original_clip = None
        self.altered_band = None
        self.bands = None
        self.clip_start = 0

    def initUI(self):
        self.setWindowTitle('Treinamento Auditivo - Detecção de Faixa de Frequência')

        self.open_button = QPushButton('Selecionar Arquivo de Áudio', self)
        self.open_button.clicked.connect(self.open_file)

        self.play_original_button = QPushButton('Reproduzir Áudio Original', self)
        self.play_original_button.clicked.connect(self.play_original)
        self.play_original_button.setEnabled(False)

        self.play_modified_button = QPushButton('Reproduzir Áudio Modificado', self)
        self.play_modified_button.clicked.connect(self.play_modified)
        self.play_modified_button.setEnabled(False)

        self.new_clip_button = QPushButton('Nova Porção de Áudio', self)
        self.new_clip_button.clicked.connect(self.new_clip)
        self.new_clip_button.setEnabled(False)

        self.label = QLabel('Selecione a faixa de frequência alterada:', self)

        self.combo_box = QComboBox(self)
        self.combo_box.setEnabled(False)

        self.check_button = QPushButton('Verificar', self)
        self.check_button.clicked.connect(self.check_answer)
        self.check_button.setEnabled(False)

        # Layouts
        layout = QVBoxLayout()
        layout.addWidget(self.open_button)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.play_original_button)
        h_layout.addWidget(self.play_modified_button)
        layout.addLayout(h_layout)

        layout.addWidget(self.new_clip_button)
        layout.addWidget(self.label)
        layout.addWidget(self.combo_box)
        layout.addWidget(self.check_button)

        self.setLayout(layout)
        self.show()

    def open_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo de Áudio", "",
                                                  "Arquivos de Áudio (*.wav *.flac *.ogg)", options=options)
        if fileName:
            self.full_audio_data, self.sample_rate = sf.read(fileName)
            # Se o áudio tiver mais de um canal, converte para mono
            if len(self.full_audio_data.shape) > 1:
                self.full_audio_data = np.mean(self.full_audio_data, axis=1)
            # Prepara as faixas de frequência e inicializa a primeira porção
            self.prepare_bands()
            self.new_clip()
            self.play_original_button.setEnabled(True)
            self.play_modified_button.setEnabled(True)
            self.combo_box.setEnabled(True)
            self.check_button.setEnabled(True)
            self.new_clip_button.setEnabled(True)
            QMessageBox.information(self, 'Arquivo Carregado', 'O arquivo de áudio foi carregado e modificado.')

    def prepare_bands(self):
        nyquist = self.sample_rate / 2
        # Definir faixas de frequência dentro dos limites
        self.bands = [
            (20, 60),
            (60, 250),
            (250, 500),
            (500, 1000),
            (1000, 2000),
            (2000, 4000),
            (4000, 6000),
            (6000, 10000),
            (10000, 15000),
            (15000, min(20000, nyquist - 1))
        ]
        # Atualizar a combo box com as faixas de frequência
        self.combo_box.clear()
        for low, high in self.bands:
            self.combo_box.addItem(f"{int(low)} - {int(high)} Hz")

    def new_clip(self):
        # Selecionar uma porção aleatória de 5 segundos
        max_start = max(0, len(self.full_audio_data) - 5 * self.sample_rate)
        if max_start <= 0:
            self.clip_start = 0
        else:
            self.clip_start = np.random.randint(0, max_start)
        clip_end = self.clip_start + 5 * self.sample_rate
        self.audio_data = self.full_audio_data[int(self.clip_start):int(clip_end)]
        # Garantir que a porção tenha o tamanho correto
        if len(self.audio_data) < 5 * self.sample_rate:
            self.audio_data = np.pad(self.audio_data, (0, int(5 * self.sample_rate - len(self.audio_data))), 'constant')
        self.original_clip = self.audio_data.copy()
        self.apply_random_gain()

    def apply_random_gain(self):
        # Selecionar uma faixa aleatória
        self.altered_band = np.random.randint(0, len(self.bands))
        low, high = self.bands[self.altered_band]
        nyquist = self.sample_rate / 2
        # Normalizar as frequências
        low_norm = low / nyquist
        high_norm = high / nyquist
        # Evitar valores fora do intervalo (0, 1)
        low_norm = max(low_norm, 1e-5)
        high_norm = min(high_norm, 0.99999)
        # Criar filtro
        b, a = butter(4, [low_norm, high_norm], btype='band')
        # Filtrar áudio
        filtered_audio = lfilter(b, a, self.audio_data)
        # Aplicar ganho
        gain = 12  # ganho de 12 dB
        filtered_audio *= 10**(gain / 20)
        # Evitar clipping
        self.modified_audio = self.audio_data + filtered_audio
        max_val = np.max(np.abs(self.modified_audio))
        if max_val > 1.0:
            self.modified_audio /= max_val

    def play_original(self):
        sd.play(self.original_clip, self.sample_rate)

    def play_modified(self):
        sd.play(self.modified_audio, self.sample_rate)

    def check_answer(self):
        user_choice = self.combo_box.currentIndex()
        if user_choice == self.altered_band:
            QMessageBox.information(self, 'Resultado', 'Parabéns! Você acertou a faixa de frequência alterada.')
        else:
            correct_band = f"{int(self.bands[self.altered_band][0])} - {int(self.bands[self.altered_band][1])} Hz"
            QMessageBox.information(self, 'Resultado',
                                    f'Você errou. A faixa alterada foi {correct_band}.')
        # Preparar nova tentativa
        self.new_clip()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EarTrainingApp()
    sys.exit(app.exec_())

