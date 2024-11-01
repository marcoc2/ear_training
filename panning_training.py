import sys
import numpy as np
import soundfile as sf
import sounddevice as sd
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
                             QFileDialog, QSlider, QMessageBox, QHBoxLayout, QSpinBox)
from PyQt5.QtCore import Qt

class PanningTrainingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.audio_data = None
        self.sample_rate = None
        self.panned_audio = None
        self.original_clip = None
        self.panning_position = None
        self.clip_start = 0
        self.error_margin = 10  # Margem de erro inicial padrão

    def initUI(self):
        self.setWindowTitle('Treinamento Auditivo - Detecção de Panning')
        
        self.error_margin = 10      

        # Botão para selecionar arquivo de áudio
        self.open_button = QPushButton('Selecionar Arquivo de Áudio', self)
        self.open_button.clicked.connect(self.open_file)

        # Botão para reproduzir áudio original
        self.play_original_button = QPushButton('Reproduzir Áudio Original', self)
        self.play_original_button.clicked.connect(self.play_original)
        self.play_original_button.setEnabled(False)

        # Botão para reproduzir áudio com panning
        self.play_panned_button = QPushButton('Reproduzir Áudio com Panning', self)
        self.play_panned_button.clicked.connect(self.play_panned)
        self.play_panned_button.setEnabled(False)

        # Botão para selecionar uma nova porção de áudio
        self.new_clip_button = QPushButton('Nova Porção de Áudio', self)
        self.new_clip_button.clicked.connect(self.new_clip)
        self.new_clip_button.setEnabled(False)

        # Slider para que o usuário selecione o panning estimado
        self.panning_slider = QSlider(Qt.Horizontal)
        self.panning_slider.setMinimum(-100)
        self.panning_slider.setMaximum(100)
        self.panning_slider.setValue(0)  # Valor inicial no centro
        self.panning_slider.setTickPosition(QSlider.TicksBelow)
        self.panning_slider.setTickInterval(10)

        # Label para exibir a posição do slider
        self.slider_label = QLabel('Panning Estimado: Centro (0%)')

        # Atualizar o label conforme o slider se move
        self.panning_slider.valueChanged.connect(self.update_slider_label)

        # SpinBox para definir a margem de erro
        self.error_margin_box = QSpinBox()
        self.error_margin_box.setRange(1, 50)  # Margem de erro entre 1% e 50%
        self.error_margin_box.setValue(self.error_margin)  # Valor padrão de 10%
        self.error_margin_box.valueChanged.connect(self.update_error_margin)

        # Label para o SpinBox
        self.error_label = QLabel('Margem de Erro (%):')

        # Botão para verificar a resposta
        self.check_button = QPushButton('Verificar')
        self.check_button.clicked.connect(self.check_answer)
        self.check_button.setEnabled(False)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.open_button)

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.play_original_button)
        h_layout.addWidget(self.play_panned_button)
        layout.addLayout(h_layout)

        layout.addWidget(self.new_clip_button)
        layout.addWidget(self.slider_label)
        layout.addWidget(self.panning_slider)

        # Layout para a margem de erro
        error_layout = QHBoxLayout()
        error_layout.addWidget(self.error_label)
        error_layout.addWidget(self.error_margin_box)
        layout.addLayout(error_layout)

        layout.addWidget(self.check_button)

        self.setLayout(layout)
        self.show()

    def open_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Selecionar Arquivo de Áudio", "",
                                                  "Arquivos de Áudio (*.wav *.flac *.ogg)", options=options)
        if fileName:
            self.full_audio_data, self.sample_rate = sf.read(fileName)
            if len(self.full_audio_data.shape) > 1:
                self.full_audio_data = np.mean(self.full_audio_data, axis=1)
            
            self.new_clip()
            self.play_original_button.setEnabled(True)
            self.play_panned_button.setEnabled(True)
            self.new_clip_button.setEnabled(True)
            self.check_button.setEnabled(True)
            QMessageBox.information(self, 'Arquivo Carregado', 'O arquivo de áudio foi carregado e modificado.')

    def new_clip(self):
        max_start = max(0, len(self.full_audio_data) - 5 * self.sample_rate)
        if max_start <= 0:
            self.clip_start = 0
        else:
            self.clip_start = np.random.randint(0, max_start)
        clip_end = self.clip_start + 5 * self.sample_rate
        self.audio_data = self.full_audio_data[int(self.clip_start):int(clip_end)]
        if len(self.audio_data) < 5 * self.sample_rate:
            self.audio_data = np.pad(self.audio_data, (0, int(5 * self.sample_rate - len(self.audio_data))), 'constant')
        self.original_clip = self.audio_data.copy()
        self.apply_random_panning()

    def apply_random_panning(self):
        # Gera uma posição de panning aleatória entre -100 e 100
        self.panning_position = np.random.randint(-100, 101)
        
        # Calcula os níveis de volume para cada canal
        left_gain = max(0, (100 - self.panning_position) / 100)
        right_gain = max(0, (100 + self.panning_position) / 100)

        # Aplica o panning ao áudio
        self.panned_audio = np.stack((self.audio_data * left_gain, self.audio_data * right_gain), axis=-1)

        # Normalização para evitar saturação
        max_val = np.max(np.abs(self.panned_audio))
        if max_val > 1.0:
            self.panned_audio /= max_val

    def play_original(self):
        sd.stop()
        sd.play(self.original_clip, self.sample_rate)

    def play_panned(self):
        if self.panned_audio is not None:
            sd.stop()
            sd.play(self.panned_audio, self.sample_rate)

    def update_slider_label(self):
        value = self.panning_slider.value()
        position_text = 'Centro (0%)' if value == 0 else f'Dir. {value}%' if value > 0 else f'Esq. {abs(value)}%'
        self.slider_label.setText(f'Panning Estimado: {position_text}')

    def update_error_margin(self):
        self.error_margin = self.error_margin_box.value()

    def check_answer(self):
        user_choice = self.panning_slider.value()
        correct_panning = self.panning_position
        # Verifica se o usuário está dentro da margem de erro configurada
        if abs(user_choice - correct_panning) <= self.error_margin:
            QMessageBox.information(self, 'Resultado',
                                    f'Parabéns! Você acertou a posição do panning.\nPanning correto: {correct_panning}%')
        else:
            QMessageBox.information(self, 'Resultado',
                                    f'Você errou. A posição do panning era {correct_panning}%.')

        # Seleciona uma nova porção de áudio e aplica um novo panning aleatório
        self.new_clip()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PanningTrainingApp()
    sys.exit(app.exec_())

