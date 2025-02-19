import sys
import pyaudio
import wave
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QComboBox
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class AudioRecorder(QThread):
    update_status = pyqtSignal(str)
    update_plot = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.frames = []
        self.stream = None
        self.p = pyaudio.PyAudio()

        self.device_input = None
        self.device_output = None

    def set_device_input(self, device_index):
        self.device_input = device_index

    def set_device_output(self, device_index):
        self.device_output = device_index

    def start_recording(self):
        self.is_recording = True
        self.frames = []
        self.update_status.emit("Nagrywanie...")
        self.start()

    def stop_recording(self):
        self.is_recording = False
        self.update_status.emit("Zatrzymano nagrywanie.")
        self.wait()

    def run(self):
        # Parametry nagrywania
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        RECORD_SECONDS = 5  # czas nagrywania w sekundach
        OUTPUT_FILENAME = "output.wav"

        # Otwarcie strumienia
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  output=False,
                                  input_device_index=self.device_input,
                                  frames_per_buffer=CHUNK)

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            if not self.is_recording:
                break
            data = self.stream.read(CHUNK)
            self.frames.append(data)

            # Przesyłanie danych do wizualizacji
            audio_data = np.frombuffer(data, dtype=np.int16)
            self.update_plot.emit(audio_data)

        self.stream.stop_stream()
        self.stream.close()

        # Zapisz dane do pliku
        wf = wave.open(OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        self.p.terminate()

class RecorderApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Nagrywarka Audio")

        # Utworzenie GUI
        self.status_label = QLabel("Status: Oczekiwanie", self)
        self.start_button = QPushButton("Rozpocznij nagrywanie", self)
        self.stop_button = QPushButton("Zatrzymaj nagrywanie", self)

        self.stop_button.setEnabled(False)

        # Dodanie ComboBox do wyboru urządzenia wejściowego i wyjściowego
        self.input_device_box = QComboBox(self)
        self.output_device_box = QComboBox(self)

        # Załaduj dostępne urządzenia
        self.load_devices()

        # Ustawienie layoutu
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(QLabel("Wybierz urządzenie wejściowe:"))
        layout.addWidget(self.input_device_box)
        layout.addWidget(QLabel("Wybierz urządzenie wyjściowe:"))
        layout.addWidget(self.output_device_box)

        # Dodanie wizualizacji wykresu audio
        self.canvas = FigureCanvas(plt.figure())
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        # Inicjalizacja obiektu AudioRecorder
        self.recorder = AudioRecorder()
        self.recorder.update_status.connect(self.update_status)
        self.recorder.update_plot.connect(self.update_plot)

        # Podłączenie przycisków do funkcji
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)

        self.show()

    def load_devices(self):
        """Załadowanie dostępnych urządzeń audio"""
        input_devices = []
        output_devices = []

        # Wyszukiwanie urządzeń wejściowych
        for i in range(self.recorder.p.get_device_count()):
            info = self.recorder.p.get_device_info_by_index(i)
            if info['maxInputChannels'] > 0:
                input_devices.append((i, info['name']))

            if info['maxOutputChannels'] > 0:
                output_devices.append((i, info['name']))

        # Uzupełnienie ComboBox
        self.input_device_box.addItems([d[1] for d in input_devices])
        self.output_device_box.addItems([d[1] for d in output_devices])

        # Ustawienie urządzeń jako pierwsze dostępne
        if input_devices:
            self.recorder.set_device_input(input_devices[0][0])

        if output_devices:
            self.recorder.set_device_output(output_devices[0][0])

        # Dodanie funkcji zmiany urządzenia
        self.input_device_box.currentIndexChanged.connect(self.change_input_device)
        self.output_device_box.currentIndexChanged.connect(self.change_output_device)

    def change_input_device(self):
        """Zmiana urządzenia wejściowego"""
        device_index = self.input_device_box.currentIndex()
        self.recorder.set_device_input(device_index)

    def change_output_device(self):
        """Zmiana urządzenia wyjściowego"""
        device_index = self.output_device_box.currentIndex()
        self.recorder.set_device_output(device_index)

    def update_status(self, status):
        self.status_label.setText(f"Status: {status}")

    def update_plot(self, audio_data):
        """Aktualizowanie wykresu poziomu dźwięku"""
        plt.clf()  # Czyść poprzedni wykres
        plt.plot(audio_data)
        self.canvas.draw()

    def start_recording(self):
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.recorder.start_recording()

    def stop_recording(self):
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)
        self.recorder.stop_recording()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = RecorderApp()
    sys.exit(app.exec_())
