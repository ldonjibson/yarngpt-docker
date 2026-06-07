import sys
from pathlib import Path

from huggingface_hub import hf_hub_download

MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "wavtokenizer_large_speech_320_24k.ckpt": {
        "repo_id": "novateur/WavTokenizer-large-speech-75token",
        "filename": "wavtokenizer_large_speech_320_v2.ckpt",
    },
}


def main() -> None:
    for out_name, info in FILES.items():
        dest = MODELS_DIR / out_name
        if dest.exists():
            print(f"[SKIP] {out_name} already exists")
            continue
        print(f"[DL] {info['repo_id']}/{info['filename']} -> {out_name}")
        try:
            downloaded = hf_hub_download(
                repo_id=info["repo_id"],
                filename=info["filename"],
                local_dir=MODELS_DIR,
                local_dir_use_symlinks=False,
            )
            Path(downloaded).rename(dest)
            print(f"[OK] {out_name}")
        except Exception as e:
            print(f"[FAIL] {out_name}: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
