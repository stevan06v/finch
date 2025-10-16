import whisper

if __name__ == "__main__":
    model = whisper.load_model("medium")

    audio = whisper.load_audio("./media/audio.mp3")
    audio = whisper.pad_or_trim(audio)

    mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)

    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")

    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)

    print(result.text)
