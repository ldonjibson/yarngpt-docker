yarngpt2-docker/
├─ app.py
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
├─ README.md
└─ models/
   ├─ wavtokenizer_mediumdata_frame75_3s_nq1_code4096_dim512_kmeans200_attn.yaml
   └─ wavtokenizer_large_speech_320_24k.ckpt


# YarnGPT2 Local Docker

## Put these files in `./models`
- wavtokenizer_mediumdata_frame75_3s_nq1_code4096_dim512_kmeans200_attn.yaml
- wavtokenizer_large_speech_320_24k.ckpt

## Run
```bash
docker compose up --build
```

## Test voices
```bash
curl http://localhost:8000/voices
```

## Generate audio
```bash
curl -X POST http://localhost:8000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello, this is a test.","lang":"english","speaker_name":"idera"}' \
  --output sample.wav
```


### Speaker selection
The model card lists these speakers, which I included in the API voice map: English idera, chinenye, jude, emma, umar, joke, zainab, osagie, remi, tayo; Yoruba yoruba_male2, yoruba_female2, yoruba_feamle1; Igbo igbo_female2, igbo_male2, igbo_female1; Hausa hausa_feamle1, hausa_female2, hausa_male2, hausa_male1.

### Setup notes
You must download the two WavTokenizer files into ./models before starting the container, because the model card’s sample code loads them locally rather than fetching them automatically.

You should also set HF_TOKEN in an .env file if your Hugging Face account needs authentication for model access. The container will then mount the HF cache so the model is not re-downloaded every time.

### Run commands
```bash
cp app.py Dockerfile docker-compose.yml requirements.txt README.md /path/to/yarngpt2-docker/
mkdir -p models output
docker compose up --build
```

### Test request
```bash
curl -X POST http://localhost:8000/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"This is a local YarnGPT2 test.","lang":"english","speaker_name":"zainab"}' \
  --output zainab.wav
```

One important caveat: the model card says YarnGPT2 is for experimental use and is not suitable for languages other than English or other accents, so Nigerian-language quality may vary by voice and text.

If you want, I can also give you a second version with a simple HTML frontend dropdown for all voices, so it behaves more like a real website.