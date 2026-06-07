import os
import random
from pathlib import Path

import torch
import torchaudio
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from transformers import AutoModelForCausalLM

from yarngpt.audiotokenizer import AudioTokenizerV2

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

MODEL_ID = os.getenv("MODEL_ID", "saheedniyi/YarnGPT2")
HF_TOKEN = os.getenv("HF_TOKEN")
WAV_CONFIG = os.getenv(
    "WAV_CONFIG",
    "/app/models/wavtokenizer_mediumdata_frame75_3s_nq1_code4096_dim512_kmeans200_attn.yaml",
)
WAV_CKPT = os.getenv("WAV_CKPT", "/app/models/wavtokenizer_large_speech_320_24k.ckpt")
OUT_DIR = Path(os.getenv("OUT_DIR", "/app/output"))
OUT_DIR.mkdir(parents=True, exist_ok=True)

VOICE_MAP = {
    "english": ["idera", "chinenye", "jude", "emma", "umar", "joke", "zainab", "osagie", "remi", "tayo"],
    "yoruba": ["yoruba_male2", "yoruba_female2", "yoruba_feamle1"],
    "igbo": ["igbo_female2", "igbo_male2", "igbo_female1"],
    "hausa": ["hausa_feamle1", "hausa_female2", "hausa_male2", "hausa_male1"],
}

app = FastAPI(title="YarnGPT2 Local API")
model = None
audio_tokenizer = None
templates = Jinja2Templates(directory="templates")


class TTSRequest(BaseModel):
    text: str
    lang: str = "english"
    speaker_name: str | None = None
    temperature: float = 0.1
    repetition_penalty: float = 1.1
    max_length: int = 4000

@app.on_event("startup")
def load_models():
    global model, audio_tokenizer
    if not Path(WAV_CONFIG).exists() or not Path(WAV_CKPT).exists():
        raise RuntimeError("Missing WavTokenizer files in /app/models.")

    audio_tokenizer = AudioTokenizerV2(MODEL_ID, WAV_CKPT, WAV_CONFIG)

    kwargs = {"torch_dtype": "auto"}
    if HF_TOKEN:
        kwargs["token"] = HF_TOKEN

    model = AutoModelForCausalLM.from_pretrained(MODEL_ID, **kwargs).to(audio_tokenizer.device)
    model.eval()

@app.get("/")
def root():
    return {"status": "ok", "model": MODEL_ID, "voices": VOICE_MAP}

@app.get("/voices")
def voices():
    return VOICE_MAP

@app.post("/synthesize")
def synthesize(req: TTSRequest):
    lang = req.lang.lower().strip()
    if lang not in VOICE_MAP:
        raise HTTPException(400, f"Unsupported lang: {lang}")

    speaker = req.speaker_name or random.choice(VOICE_MAP[lang])
    if speaker not in VOICE_MAP[lang]:
        raise HTTPException(400, f"Unsupported speaker for {lang}: {speaker}")

    prompt = audio_tokenizer.create_prompt(req.text, lang=lang, speaker_name=speaker)
    input_ids = audio_tokenizer.tokenize_prompt(prompt)

    with torch.no_grad():
        output = model.generate(
            input_ids=input_ids,
            temperature=req.temperature,
            repetition_penalty=req.repetition_penalty,
            max_length=req.max_length,
        )

    codes = audio_tokenizer.get_codes(output)
    audio = audio_tokenizer.get_audio(codes)
    out_file = OUT_DIR / f"yarngpt2_{lang}_{speaker}.wav"
    torchaudio.save(str(out_file), audio, 24000)

    return FileResponse(str(out_file), media_type="audio/wav", filename=out_file.name)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})