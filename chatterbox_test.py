import torchaudio as ta
from chatterbox.tts import ChatterboxTTS

model = ChatterboxTTS.from_pretrained(device="cuda")  # Use "cuda" if you have a compatible GPU
text = "Hello, this is Chatterbox TTS by Resemble AI."
wav = model.generate(text)
ta.save("output.wav", wav, model.sr)
print("Done! Check output.wav")
