from flask import Flask, render_template, request
import os
import subprocess
import webbrowser
from threading import Timer
from speech_recognition import Recognizer, AudioFile
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"mp3", "m4a"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_mp3_to_wav(mp3_path):
    wav_path = mp3_path.rsplit('.', 1)[0] + '.wav'
    subprocess.run(['ffmpeg', '-i', mp3_path, wav_path, '-y'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return wav_path

def transcribe_audio(wav_path):
    recognizer = Recognizer()
    with AudioFile(wav_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio, language="tr-TR")
        return text
    except Exception as e:
        return f"Ses tanıma hatası: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return "Dosya bulunamadı."
        file = request.files["file"]
        if file.filename == "":
            return "Dosya seçilmedi."
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            wav_path = convert_mp3_to_wav(file_path)
            metin = transcribe_audio(wav_path)

            return render_template("index.html", metin=metin)
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  
    app.run(host="0.0.0.0", port=port)
