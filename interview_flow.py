import numpy as np
import sounddevice as sd
import threading
import warnings
warnings.filterwarnings("ignore")


from kokoro import KPipeline
from doc_loader import load_document, cleaning
from llm import genrate_ques, evaluate_ans
from report import generate_summary
from skill_matcher import extraction 
from transcription import get_transcriber



pipeline = KPipeline(lang_code="a", repo_id='hexgrad/Kokoro-82M')
transcriber = get_transcriber(model_size="base")

def generate_audio(text: str):
    
    all_audio = []
    for _, _, audio in pipeline(text, voice="af_heart"): 
        all_audio.append(audio)
    return np.concatenate(all_audio)

def play_audio(audio):
    
    sd.play(audio, 24000)
    sd.wait()

# --- Load & Setup ---
p, t = load_document(r"C:\Users\hp\Downloads\Resume_in_pdf.pdf")
print(f'Total pages: {p}')
text = cleaning(t)

job_description = input('Paste Job Description or Press Enter to skip : ').strip()
if job_description:
    matching, missing, score, res_skill = extraction(text, job_description)

    print(f"\n✅ Matching Skills : {', '.join(matching)}")
    print(f"❌ Missing Skills  : {', '.join(missing)}")
    print(f"📊 Match Score     : {score}%")
    print(f"\n😁 Your Skills : {', '.join(res_skill)}")

    questions = genrate_ques(text, matching, missing)
else:
    questions = genrate_ques(text)

print('\n Question are Generated Succussfully!.  Ready for Interview')
summary_data = []


next_audio_store = [generate_audio(questions[0])]

for i, question in enumerate(questions):
    print(f"\nQ{i+1}: {question}")

    # Current question play karo
    play_audio(next_audio_store[0])

    # User answer de raha hai — iss time mein parallel:
    # 1. Next question ka audio generate karo (background)
    # 2. Feedback bhi baad mein parallel milega
    
    next_audio_store[0] = None
    next_thread = None

    if i + 1 < len(questions):
        def preload_next(q):
            next_audio_store[0] = generate_audio(q)
        next_thread = threading.Thread(target=preload_next, args=(questions[i+1],))
        next_thread.start()

    # Answer lo with real-time transcription
    answer = transcriber.record_answer(
        prompt=f"\n🎙️  Listening for your answer to Q{i+1}... (Speak now, Press ENTER when done):"
    )
    if not answer:
        answer = "No answer provided"

    # Feedback aur next audio parallel
    feedback_store = [None]
    def run_feedback():
        feedback_store[0] = evaluate_ans(question, answer)
    
    feedback_thread = threading.Thread(target=run_feedback)
    feedback_thread.start()

    # Dono threads finish hone do
    feedback_thread.join()
    if next_thread:
        next_thread.join()

    print(f"\nFeedback: {feedback_store[0]}")
    print("-" * 60)

    summary_data.append({
        "q_no": i + 1,
        "question": question,
        "answer": answer
        
    })

# Final Report

print("\nGenerating Final Report...")
report = generate_summary(summary_data)
print(report)


