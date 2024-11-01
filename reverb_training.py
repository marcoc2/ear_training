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

        # Inicializa a biblioteca de IRs (impulsos) de reverb antes da interface
        self.ir_library = {
            "Sala Pequena": "small_room_ir.wav",
            "Sala Grande": "large_hall_ir.wav",
            "Igreja": "church_ir.wav"
        }
        self.loaded_irs = {}  # Armazenará os IRs carregados

        # Configura a interface do usuário
        self.initUI()

        # Carrega os IRs após a interface ser configurada
        for name, path in self.ir_library.items():
            try:
                ir_data, ir_sample_rate = sf.read(path)
                self.loaded_irs[name] = ir_data
            except FileNotFoundError:
                QMessageBox.warning(self, "Erro", f"Arquivo IR '{path}' não encontrado.")


    def initUI(self):
        self.setWindowTitle('Treinamento Auditivo - Detecção de Reverb')

        # Botão para selecionar arquivo de áudio
        self.open_button = QPushButton('Selecionar Arquivo de Áudio', self)
        self.open_button.clicked.connect(self.open_file)

        # Botão para reproduzir áudio original
        self.play_original_button = QPushButton('Reproduzir Áudio Original', self)
        self.play_original_button.clicked.connect(self.play_original)
        self.play_original_button.setEnabled(False)

        # Botão para reproduzir áudio com reverb
        self.play_reverbed_button = QPushButton('Reproduzir Áudio com Reverb', self)
        self.play_reverbed_button.clicked.connect(self.play_reverbed)
        self.play_reverbed_button.setEnabled(False)

        # ComboBox para escolher o tipo de reverb
        self.reverb_selector = QComboBox(self)
        self.reverb_selector.addItems(list(self.ir_library.keys()))
        self.reverb_selector.currentTextChanged.connect(self.apply_reverb)
        self.reverb_selector.setEnabled(False)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.open_button)
        layout.addWidget(self.play_original_button)
        layout.addWidget(self.play_reverbed_button)
        layout.addWidget(QLabel("Selecione o Tipo de Reverb:"))
        layout.addWidget(self.reverb_selector)

        self.setLayout(layout)
        self.show()

    def open_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo de Áudio", "",
                                                  "Arquivos de Áudio (*.wav *.flac *.ogg)", options=options)
        if fileName:
            self.audio_data, self.sample_rate = sf.read(fileName)
            if len(self.audio_data.shape) > 1:
                self.audio_data = np.mean(self.audio_data, axis=1)  # Converte para mono
            self.play_original_button.setEnabled(True)
            self.play_reverbed_button.setEnabled(True)
            self.reverb_selector.setEnabled(True)
            QMessageBox.information(self, 'Arquivo Carregado', 'O arquivo de áudio foi carregado com sucesso.')

    def apply_reverb(self):
        # Aplica a convolução com o IR selecionado
        reverb_type = self.reverb_selector.currentText()
        ir_data = self.loaded_irs.get(reverb_type)
        if ir_data is not None:
            self.reverbed_audio = convolve(self.audio_data, ir_data, mode='full')
            # Normalização para evitar saturação
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ReverbTrainingApp()
    sys.exit(app.exec_())

