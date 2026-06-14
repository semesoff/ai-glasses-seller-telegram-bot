import json
import logging
import re
import shutil
import subprocess
import wave
from html import unescape
from pathlib import Path

from app.config import get_settings

logger = logging.getLogger(__name__)

try:
    from vosk import KaldiRecognizer, Model
except ImportError:  # pragma: no cover
    KaldiRecognizer = None
    Model = None


class VoiceService:
    def __init__(self, model_path: Path | None = None) -> None:
        self.model_path = model_path or get_settings().vosk_model_path
        self._model = None

    def available(self) -> bool:
        return Model is not None and self.model_path.exists()

    def _load_model(self):
        if not self.available():
            raise RuntimeError(
                f"Vosk model is not available at {self.model_path}. "
                "Download a Russian Vosk model and set VOSK_MODEL_PATH."
            )
        if self._model is None:
            self._model = Model(str(self.model_path))
        return self._model

    def _convert_ogg_to_wav(self, input_ogg: Path, output_wav: Path) -> None:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(input_ogg),
                "-ar",
                "16000",
                "-ac",
                "1",
                str(output_wav),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def transcribe(self, input_ogg: Path) -> str:
        wav_path = input_ogg.with_suffix(".wav")
        self._convert_ogg_to_wav(input_ogg, wav_path)
        model = self._load_model()
        with wave.open(str(wav_path), "rb") as wav_file:
            recognizer = KaldiRecognizer(model, wav_file.getframerate())
            chunks: list[str] = []
            while True:
                data = wav_file.readframes(4000)
                if not data:
                    break
                if recognizer.AcceptWaveform(data):
                    chunks.append(json.loads(recognizer.Result()).get("text", ""))
            chunks.append(json.loads(recognizer.FinalResult()).get("text", ""))
        return " ".join(part for part in chunks if part).strip()

    def prepare_spoken_reply(self, text: str) -> str:
        cleaned = unescape(text)
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        cleaned = re.sub(r"[*_`>#\[\]()]", " ", cleaned)
        cleaned = re.sub(r"https?://\S+", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if not cleaned:
            return "Ответ готов."

        sentences = re.split(r"(?<=[.!?])\s+", cleaned)
        short = " ".join(sentence for sentence in sentences[:2] if sentence).strip()
        if len(short) < 40 and len(sentences) > 2:
            short = " ".join(sentences[:3]).strip()
        if len(short) > 250:
            short = short[:247].rsplit(" ", 1)[0].rstrip(".,;:") + "..."
        return short or cleaned[:250]

    def _synthesize_with_rhvoice(self, text: str, wav_path: Path) -> bool:
        executable = shutil.which("RHVoice-client")
        if not executable:
            return False
        try:
            subprocess.run(
                [executable, "-o", str(wav_path)],
                input=text,
                text=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
        return wav_path.exists()

    def _synthesize_with_piper(self, text: str, wav_path: Path) -> bool:
        executable = shutil.which("piper")
        model_path = get_settings().piper_model_path
        if not executable or not model_path or not model_path.exists():
            return False
        try:
            subprocess.run(
                [executable, "--model", str(model_path), "--output_file", str(wav_path)],
                input=text,
                text=True,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
        return wav_path.exists()

    def _synthesize_with_espeak(self, text: str, wav_path: Path) -> bool:
        try:
            subprocess.run(
                [
                    "espeak-ng",
                    "-v",
                    "ru",
                    "-s",
                    "145",
                    "-p",
                    "45",
                    "-a",
                    "160",
                    "-w",
                    str(wav_path),
                    text,
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False
        return wav_path.exists()

    def synthesize(self, text: str, output_dir: Path) -> Path | None:
        output_dir.mkdir(parents=True, exist_ok=True)
        wav_path = output_dir / "reply.wav"
        ogg_path = output_dir / "reply.ogg"
        spoken_text = self.prepare_spoken_reply(text)
        backend = None
        if self._synthesize_with_rhvoice(spoken_text, wav_path):
            backend = "rhvoice"
        elif self._synthesize_with_piper(spoken_text, wav_path):
            backend = "piper"
        elif self._synthesize_with_espeak(spoken_text, wav_path):
            backend = "espeak-ng"
        else:
            return None
        logger.info("tts_backend=%s text_len=%s", backend, len(spoken_text))
        try:
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(wav_path), "-c:a", "libopus", str(ogg_path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            return None
        return ogg_path if ogg_path.exists() else None
