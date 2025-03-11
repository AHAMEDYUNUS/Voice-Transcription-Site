from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import assemblyai as aai
import os

app = Flask(__name__)
CORS(app)

# Set your AssemblyAI API key here
aai.settings.api_key = "49f7ae167f0549e5b4c963a258af842e"


@app.route('/')
def home():
   return "Hello, Flask is working!"

#def home():
#   return app.send_static_file('C:/Simple transcription/frontend/index.html')

@app.route('/process', methods=['POST'])
def process_audio():
    audio_file = request.files['audio']
    temp_path = "temp_audio.wav"
    audio_file.save(temp_path)
    
    # Configure AssemblyAI with speaker diarization
    config = aai.TranscriptionConfig(
        #speech_model=aai.SpeechModel.nano,
        speaker_labels=True,
        language_code="en",  # Auto-detect language
    )

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(temp_path, config=config)
    
    if transcript.error:
        return jsonify({'error': transcript.error}), 500

    # Process utterances and translate to English
    result = []
    for utterance in transcript.utterances:
        result.append({
            'speaker': utterance.speaker,
            'text': utterance.text
        })
    
    os.remove(temp_path)
    return jsonify({'transcript': result})

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    data = request.json['transcript']
    pdf_buffer = BytesIO()
    
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    for entry in data:
        text = f"<b>Speaker {entry['speaker']}:</b> {entry['text']}"
        p = Paragraph(text, styles["Normal"])
        story.append(p)
    
    doc.build(story)
    pdf_buffer.seek(0)
    
    return send_file(pdf_buffer, mimetype='application/pdf', 
                    as_attachment=True, download_name='transcript.pdf')

if __name__ == '__main__':
    app.run(debug=True)