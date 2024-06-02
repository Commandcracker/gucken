import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='transformers.utils.generic')

from transformers import pipeline

pipe = pipeline(
  "automatic-speech-recognition",
  model="openai/whisper-tiny.en"
)

url = "audio [audio].mp3"
prediction: str = pipe(url)["text"]

print(prediction.strip())
