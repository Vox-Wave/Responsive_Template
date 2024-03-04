from django.apps import AppConfig
import whisper,os
from pathlib import Path
from keras.models import load_model
import pickle, joblib

whisper_model = None
speech_emotion_model = None
label_encoder = None
text_emotion_model = None
cv = None

class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

    def ready(self):
        global whisper_model
        global speech_emotion_model
        global encoded_emotion
        global label_encoder
        global text_emotion_model
        global cv
        # Load the model when the app is ready
        whisper_model = whisper.load_model("base")
        BASE_DIR = Path(__file__).resolve().parent.parent
        # Load the saved model
        saved_model_path = os.path.join(BASE_DIR, "saved_models", "speech_emotion_model.h5")
        speech_emotion_model = load_model(saved_model_path)
        # Load the encoder
        encoder_path = os.path.join(BASE_DIR, "saved_models", "speech_label_encoder.pkl")
        with open(encoder_path, 'rb') as f:
            label_encoder = pickle.load(f)

        # Load the saved model
        pipeline_file = os.path.join(BASE_DIR, "saved_models", "text_emotion_model.pkl")
        text_emotion_model = joblib.load(pipeline_file)

        cv_path = os.path.join(BASE_DIR, "saved_models", "count_vectorizer.pkl")
        cv = joblib.load(cv_path)