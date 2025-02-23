import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QFileDialog,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QSplitter,
    QListWidget,
    QMessageBox,
    QProgressBar,
    QComboBox,
    QLabel,
    QHBoxLayout,
    QFrame,
    QGraphicsOpacityEffect,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QLinearGradient
from openai import OpenAI
import os
import tempfile
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from pydub import AudioSegment
import math
import moviepy.editor as mp
import logging
from tqdm import tqdm
import time

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class TranscriptionWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, file_path, chunk_duration_ms=25000):
        super().__init__()
        logger.debug(f"Initializing TranscriptionWorker with file: {file_path}")
        self.file_path = file_path
        self.chunk_duration_ms = chunk_duration_ms
        self.is_cancelled = False

    def run(self):
        try:
            logger.info("Starting transcription process")

            # Chunk creation phase (30% of total progress)
            chunks = self.chunk_audio(self.file_path)
            logger.debug(f"Created {len(chunks)} chunks")

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            full_transcription = []

            # Transcription phase (70% of total progress)
            for i, chunk_path in tqdm(
                enumerate(chunks, 1),
                desc="Transcribing chunks",
                total=len(chunks),
                unit="chunk",
            ):
                if self.is_cancelled:
                    logger.info("Transcription cancelled")
                    break

                # Calculate combined progress (30% from chunking + 70% from transcription)
                chunk_progress = (i / len(chunks)) * 70  # 70% for transcription phase
                total_progress = 30 + chunk_progress  # Add 30% from chunking phase

                self.progress.emit(
                    int(total_progress),
                    f"Transcribing: {total_progress:.1f}% (chunk {i}/{len(chunks)})",
                )

                logger.debug(
                    f"Processing chunk {i}/{len(chunks)} ({(i/len(chunks)*100):.1f}%)"
                )

                with open(chunk_path, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1", file=audio_file, response_format="text"
                    )
                    full_transcription.append(transcription)

                os.unlink(chunk_path)

            if not self.is_cancelled:
                logger.info("Transcription completed successfully (100%)")
                self.progress.emit(100, "Transcription complete (100%)")
                self.finished.emit(" ".join(full_transcription))

        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            self.error.emit(str(e))

    def chunk_audio(self, audio_path):
        logger.debug(f"Loading audio file: {audio_path}")
        self.progress.emit(0, "Loading audio file (0%)")

        # Load audio with progress tracking
        file_size = os.path.getsize(audio_path)
        progress_chunks = []

        def progress_callback(data, _):
            progress_chunks.append(data)
            progress = (len(b"".join(progress_chunks)) / file_size) * 100
            self.progress.emit(int(progress), f"Loading audio file ({progress:.1f}%)")

        audio = AudioSegment.from_file(audio_path, progress_callback=progress_callback)
        chunks = []

        total_duration_ms = len(audio)
        num_chunks = math.ceil(total_duration_ms / self.chunk_duration_ms)

        logger.debug(f"Splitting {total_duration_ms}ms audio into {num_chunks} chunks")
        self.progress.emit(0, f"Preparing to split audio into {num_chunks} chunks")

        for i in tqdm(range(num_chunks), desc="Creating chunks", unit="chunk"):
            start_ms = i * self.chunk_duration_ms
            end_ms = min((i + 1) * self.chunk_duration_ms, total_duration_ms)
            chunk = audio[start_ms:end_ms]

            split_progress = ((i + 1) / num_chunks) * 100
            self.progress.emit(
                int(split_progress),
                f"Splitting audio: {split_progress:.1f}% ({i+1}/{num_chunks} chunks)",
            )

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_chunk:
                chunk.export(temp_chunk.name, format="mp3")
                chunks.append(temp_chunk.name)

        return chunks


class PreprocessWorker(QThread):
    progress = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            logger.debug(f"Starting preprocessing for file: {self.file_path}")
            if self.file_path.lower().endswith(".mp4"):
                self.progress.emit("Converting video to audio (0%)")
                temp_dir = Path("temp")
                temp_dir.mkdir(exist_ok=True)

                output_path = temp_dir / f"{Path(self.file_path).stem}.mp3"

                # Get video duration for progress calculation
                video = mp.VideoFileClip(self.file_path)
                duration = video.duration

                def progress_callback(t):
                    progress = (t / duration) * 100
                    self.progress.emit(f"Converting video: {progress:.1f}%")

                # Convert with progress tracking
                video.audio.write_audiofile(
                    str(output_path),
                    verbose=False,
                    logger=None,
                    progress_callback=progress_callback,
                )
                video.close()

                logger.debug(f"Video converted to audio: {output_path} (100%)")
                self.progress.emit("Conversion complete (100%)")
                self.finished.emit(str(output_path))
            else:
                logger.debug("File is already in audio format")
                self.finished.emit(self.file_path)
        except Exception as e:
            logger.error(f"Preprocessing error: {str(e)}")
            self.error.emit(str(e))


class LoadingWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(20)
        self.setStyleSheet(
            """
            LoadingWidget {
                background-color: #f0f0f0;
                border-radius: 5px;
            }
        """
        )

        # Create opacity effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # Create animation
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(1500)
        self.animation.setLoopCount(-1)
        self.animation.setStartValue(0.3)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Create gradient
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor("#f0f0f0"))
        gradient.setColorAt(1, QColor("#e0e0e0"))

        # Draw rounded rectangle
        painter.setBrush(gradient)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 5, 5)


class TranscriberWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        logger.info("Initializing Transcriber Window")
        self.setWindowTitle("Video Transcriber")
        self.setGeometry(100, 100, 1000, 600)

        # Create main splitter
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(self.splitter)

        # Create sidebar
        self.sidebar = QWidget()
        sidebar_layout = QVBoxLayout(self.sidebar)

        # Create history list
        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self.load_transcription)
        sidebar_layout.addWidget(self.history_list)

        # Create main content area
        self.main_content = QWidget()
        layout = QVBoxLayout(self.main_content)

        # Add widgets to splitter
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.main_content)

        # Set splitter proportions
        self.splitter.setSizes([200, 800])

        # Create buttons
        self.select_file_btn = QPushButton("Select Audio File")
        self.select_file_btn.clicked.connect(self.select_file)

        self.transcribe_btn = QPushButton("Transcribe")
        self.transcribe_btn.clicked.connect(self.transcribe_audio)
        self.transcribe_btn.setEnabled(False)

        self.save_btn = QPushButton("Save Transcription")
        self.save_btn.clicked.connect(self.save_transcription)
        self.save_btn.setEnabled(False)

        # Add model selector
        model_layout = QHBoxLayout()
        model_label = QLabel("Model Size:")
        self.model_selector = QComboBox()
        self.model_selector.addItems(["tiny", "base", "small", "medium", "large"])
        self.model_selector.setCurrentText("base")
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_selector)

        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        # Create text display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)

        # Add status label
        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        # Create skeleton widgets
        self.skeleton_container = QWidget()
        skeleton_layout = QVBoxLayout(self.skeleton_container)
        for _ in range(3):
            loading_widget = LoadingWidget()
            skeleton_layout.addWidget(loading_widget)
        self.skeleton_container.hide()
        layout.addWidget(self.skeleton_container)

        # Add widgets to layout
        layout.addWidget(self.select_file_btn)
        layout.addWidget(self.transcribe_btn)
        layout.addLayout(model_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.text_display)
        layout.addWidget(self.save_btn)

        self.selected_file = None
        self.transcription_text = None

        # Create transcriptions directory
        self.transcriptions_dir = Path("transcriptions")
        self.transcriptions_dir.mkdir(exist_ok=True)

        # Load existing transcriptions
        self.load_transcription_history()

        self.worker = None
        self.preprocess_worker = None

    def load_transcription_history(self):
        """Load existing transcription files into the sidebar."""
        self.history_list.clear()
        for file in self.transcriptions_dir.glob("*.txt"):
            self.history_list.addItem(file.name)

    def load_transcription(self, item):
        """Load a selected transcription from history."""
        file_path = self.transcriptions_dir / item.text()
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.text_display.setText(content)
        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Could not load transcription: {str(e)}"
            )

    def select_file(self):
        logger.debug("Opening file selector")
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio/Video File",
            "",
            "Media Files (*.mp3 *.mp4 *.mpeg *.mpga *.m4a *.wav *.webm)",
        )
        if file_name:
            logger.info(f"Selected file: {file_name}")
            self.status_label.setText("Processing file...")
            self.select_file_btn.setEnabled(False)

            # Start preprocessing
            self.preprocess_worker = PreprocessWorker(file_name)
            self.preprocess_worker.progress.connect(self.status_label.setText)
            self.preprocess_worker.finished.connect(self.handle_preprocessing_complete)
            self.preprocess_worker.error.connect(self.handle_preprocessing_error)
            self.preprocess_worker.start()

    def handle_preprocessing_complete(self, file_path):
        logger.debug(f"Preprocessing completed: {file_path}")
        self.selected_file = file_path
        self.transcribe_btn.setEnabled(True)
        self.select_file_btn.setEnabled(True)
        self.status_label.setText(f"Ready to transcribe: {Path(file_path).name}")

    def handle_preprocessing_error(self, error_message):
        logger.error(f"Preprocessing error: {error_message}")
        self.select_file_btn.setEnabled(True)
        self.status_label.clear()
        QMessageBox.critical(self, "Error", f"Error processing file: {error_message}")

    def transcribe_audio(self):
        if not self.selected_file:
            logger.warning("No file selected for transcription")
            return

        logger.info(f"Starting transcription for: {self.selected_file}")
        # Disable UI elements
        self.select_file_btn.setEnabled(False)
        self.transcribe_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.text_display.hide()

        # Show loading UI
        self.skeleton_container.show()
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Preparing transcription...")

        # Create and start worker thread
        self.worker = TranscriptionWorker(self.selected_file)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.handle_transcription_complete)
        self.worker.error.connect(self.handle_transcription_error)
        self.worker.start()

    def update_progress(self, value, status):
        self.progress_bar.setValue(value)
        self.status_label.setText(status)

    def handle_transcription_complete(self, text):
        logger.info("Transcription completed successfully")
        # Reset UI
        self.select_file_btn.setEnabled(True)
        self.transcribe_btn.setEnabled(True)
        self.skeleton_container.hide()
        self.text_display.show()
        self.progress_bar.setVisible(False)
        self.status_label.clear()

        # Update text and save
        self.transcription_text = text
        self.text_display.setText(text)
        self.save_btn.setEnabled(True)

        # Auto-save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcription_{timestamp}.txt"
        file_path = self.transcriptions_dir / filename

        logger.debug(f"Saving transcription to: {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.transcription_text)

        self.load_transcription_history()

    def handle_transcription_error(self, error_message):
        logger.error(f"Transcription error: {error_message}")
        self.select_file_btn.setEnabled(True)
        self.transcribe_btn.setEnabled(True)
        self.skeleton_container.hide()
        self.text_display.show()
        self.progress_bar.setVisible(False)
        self.status_label.clear()

        QMessageBox.critical(
            self, "Error", f"Error during transcription: {error_message}"
        )

    def closeEvent(self, event):
        logger.info("Closing application")
        # Clean up temp directory
        temp_dir = Path("temp")
        if temp_dir.exists():
            for file in temp_dir.glob("*"):
                file.unlink()
            temp_dir.rmdir()

        if self.worker and self.worker.isRunning():
            self.worker.is_cancelled = True
            self.worker.wait()
        if self.preprocess_worker and self.preprocess_worker.isRunning():
            self.preprocess_worker.wait()
        logger.debug("Cleanup completed")
        event.accept()

    def save_transcription(self):
        if not self.transcription_text:
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Transcription", "", "Text Files (*.txt)"
        )

        if file_name:
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(self.transcription_text)


def main():
    logger.info("Starting Video Transcriber Application")
    app = QApplication(sys.argv)
    window = TranscriberWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
