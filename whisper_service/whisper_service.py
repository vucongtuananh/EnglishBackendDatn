from flask import Flask, request, jsonify
import whisper
from pydub import AudioSegment
import os
import re
import difflib

app = Flask(__name__)

# Load Whisper model
print("Loading Whisper model...")
model = whisper.load_model("small.en")

def convert_m4a_to_wav(m4a_path):
    """
    Chuyển đổi file .m4a thành .wav
    """
    wav_path = m4a_path.replace(".m4a", ".wav")
    audio = AudioSegment.from_file(m4a_path, format="m4a")
    audio.export(wav_path, format="wav")
    return wav_path

def normalize_text(text):
    """
    Chuẩn hóa văn bản: viết thường, loại bỏ dấu câu
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", "", text)  # Loại bỏ dấu câu
    return text

def find_mistakes(reference_text, transcribed_text):
    reference_text = normalize_text(reference_text)
    transcribed_text = normalize_text(transcribed_text)

    ref_words = reference_text.split()
    trans_words = transcribed_text.split()

    matcher = SequenceMatcher(None, ref_words, trans_words)
    mistakes = []

    for opcode, i1, i2, j1, j2 in matcher.get_opcodes():
        if opcode == 'equal':
            continue
        elif opcode == 'replace':
            for r, t, pos in zip(ref_words[i1:i2], trans_words[j1:j2], range(i1 + 1, i2 + 1)):
                mistakes.append({"position": pos, "expected": r, "transcribed": t})
        elif opcode == 'delete':
            for r, pos in zip(ref_words[i1:i2], range(i1 + 1, i2 + 1)):
                mistakes.append({"position": pos, "expected": r, "transcribed": "(missing)"})
        elif opcode == 'insert':
            for t in trans_words[j1:j2]:
                mistakes.append({"position": i1 + 1, "expected": "(extra)", "transcribed": t})

    mistake_percentage = (len(mistakes) / len(ref_words)) * 100 if ref_words else 0
    return mistakes, round(mistake_percentage, 2)

@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    audio_path = "temp_audio.m4a"
    audio_file.save(audio_path)

    # Chuyển file .m4a thành .wav
    wav_path = convert_m4a_to_wav(audio_path)

    print("Transcribing audio...")
    result = model.transcribe(wav_path, language="en")  
    print("Transcribing audio...,", result)
    transcribed_text = result["text"]

    # Lấy reference text từ request
    reference_text = request.form.get("reference", "")

    # Nếu có reference, tìm lỗi sai
    mistakes, mistake_percentage = (find_mistakes(reference_text, transcribed_text)
                                    if reference_text else (None, None))

    response = {"text": transcribed_text}
    if mistakes is not None:
        response["mistakes"] = mistakes
        response["mistake_percentage"] = mistake_percentage

    # Xóa file tạm
    os.remove(audio_path)
    os.remove(wav_path)

    return jsonify(response)

if __name__ == "__main__":
    print("Starting Whisper API on port 8080...")
    app.run(host="0.0.0.0", port=8080, debug=True)
