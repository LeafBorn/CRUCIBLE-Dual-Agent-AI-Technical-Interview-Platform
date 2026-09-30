import os
import sys
import json
import time
import hmac
import hashlib
import base64
import shutil
import edge_tts
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Header, Request, status, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Ensure root directory is on Python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database import get_db, Base, engine
from data_space import User, UserProfile, UserHistory, init_db
from doc_loader import load_document, cleaning
from skill_matcher import extraction, extract_skills
from llm import genrate_ques, evaluate_ans, generate_cheatsheet, track_confidence, adaptive_interrogate, unified_turn_evaluation
from report import generate_summary, InterviewReport
from genrating_cheatsheet import build_cheatsheet_pdf

# Initialize SQLite database
init_db()

app = FastAPI(title="AI Interview Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DOCUMENTS_DIR = os.path.join(ROOT_DIR, "documents")
UPLOADS_DIR = os.path.join(ROOT_DIR, "uploads")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
TTS_CACHE_DIR = os.path.join(UPLOADS_DIR, "tts_cache")

os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(FRONTEND_DIR, exist_ok=True)
os.makedirs(TTS_CACHE_DIR, exist_ok=True)

# ----------------- Authentication Helpers -----------------
SECRET_KEY = "ai-interview-system-secure-key"

def hash_password(password: str) -> str:
    return hashlib.sha256(("salt_interview_" + password).encode()).hexdigest()

def create_token(username: str) -> str:
    payload = json.dumps({"u": username, "t": int(time.time())}).encode()
    b64_payload = base64.urlsafe_b64encode(payload).decode()
    sig = hmac.new(SECRET_KEY.encode(), b64_payload.encode(), hashlib.sha256).hexdigest()
    return f"{b64_payload}.{sig}"

def verify_token(token: str) -> Optional[str]:
    try:
        b64_payload, sig = token.split(".", 1)
        expected = hmac.new(SECRET_KEY.encode(), b64_payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(base64.urlsafe_b64decode(b64_payload.encode()).decode())
        return payload.get("u")
    except Exception:
        return None

def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing authorization header")
    
    parts = authorization.split()
    token = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else parts[0]
    username = verify_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session token")
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

# ----------------- Request / Response Models -----------------
class AuthRequest(BaseModel):
    username: str
    password: str

class MatchRequest(BaseModel):
    resume_text: str
    job_description: Optional[str] = ""
    target_role: Optional[str] = ""

class InterviewStartRequest(BaseModel):
    resume_text: str
    matching_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None

class EvaluateRequest(BaseModel):
    question: str
    answer: str

class TurnRequest(BaseModel):
    question: str
    answer: str
    latency_seconds: Optional[float] = 0.0
    current_difficulty: Optional[float] = 5.0
    target_role: Optional[str] = ""
    resume_text: Optional[str] = ""
    history: Optional[List[dict]] = []

class SummaryItem(BaseModel):
    q_no: int
    question: str
    answer: str

class FinishInterviewRequest(BaseModel):
    summary_data: List[SummaryItem]
    turns_data: Optional[List[dict]] = []
    breaking_points: Optional[List[str]] = []
    avg_confidence: Optional[float] = 0.0
    peak_difficulty: Optional[float] = 0.0

class CheatsheetRequest(BaseModel):
    resume_text: Optional[str] = None

class ProfileUpdateRequest(BaseModel):
    target_role: Optional[str] = None

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "en-US-AriaNeural"
    rate: Optional[str] = "+0%"
    pitch: Optional[str] = "+0Hz"

# ----------------- Auth Endpoints -----------------
@app.post("/api/auth/register")
def register(req: AuthRequest, db: Session = Depends(get_db)):
    username = req.username.strip()
    if not username or not req.password:
        raise HTTPException(status_code=400, detail="Username and password are required.")
    
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists. Please choose another or log in.")
    
    hashed = hash_password(req.password)
    new_user = User(username=username, password=hashed)
    db.add(new_user)
    
    profile = UserProfile(
        username=username,
        target_role="",
        resume_skill="[]",
        matching_skill="[]",
        missing_skill="[]",
        score=0
    )
    db.add(profile)
    db.commit()
    
    token = create_token(username)
    return {"message": "Account created successfully", "token": token, "username": username}

@app.post("/api/auth/login")
def login(req: AuthRequest, db: Session = Depends(get_db)):
    username = req.username.strip()
    hashed = hash_password(req.password)
    user = db.query(User).filter(User.username == username, User.password == hashed).first()
    
    if not user:
        u_check = db.query(User).filter(User.username == username).first()
        if not u_check:
            raise HTTPException(status_code=400, detail="Account does not exist. Please click 'Register' tab to create an account first.")
        raise HTTPException(status_code=401, detail="Incorrect password. Please verify your credentials.")
    
    token = create_token(username)
    return {"message": "Login successful", "token": token, "username": username}

@app.get("/api/auth/me")
def get_me(user: User = Depends(get_current_user)):
    return {"username": user.username}

# ----------------- Resume Upload & Skills -----------------
@app.post("/api/resume/upload")
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ext = Path(file.filename).suffix.lower()
    if ext not in [".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail="Only .pdf and .docx files are supported.")
    
    user_filename = f"{user.username}_resume{ext}"
    dest_path = os.path.join(UPLOADS_DIR, user_filename)
    
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    pages, raw_text = load_document(dest_path)
    clean_text = cleaning(raw_text)
    skills = sorted(list(extract_skills(clean_text)))
    
    # Update candidate profile resume skills in database
    profile = db.query(UserProfile).filter(UserProfile.username == user.username).first()
    if not profile:
        profile = UserProfile(username=user.username)
        db.add(profile)
    profile.resume_skill = json.dumps(skills)
    db.commit()
    
    return {
        "filename": file.filename,
        "pages": pages,
        "text": clean_text,
        "resume_skills": skills
    }

@app.post("/api/skills/match")
def match_skills(
    req: MatchRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume_text = req.resume_text.strip()
    if not resume_text:
        raise HTTPException(status_code=400, detail="Resume text is required for skill matching.")
    
    jd = (req.job_description or "").strip()
    profile = db.query(UserProfile).filter(UserProfile.username == user.username).first()
    if not profile:
        profile = UserProfile(username=user.username)
        db.add(profile)

    if req.target_role:
        profile.target_role = req.target_role.strip()

    if jd:
        matching, missing, score, res_skills = extraction(resume_text, jd)
        profile.resume_skill = json.dumps(res_skills)
        profile.matching_skill = json.dumps(matching)
        profile.missing_skill = json.dumps(missing)
        profile.score = int(score)
        db.commit()
        return {
            "has_jd": True,
            "matching_skills": matching,
            "missing_skills": missing,
            "score": score,
            "resume_skills": res_skills
        }
    else:
        res_skills = sorted(list(extract_skills(resume_text)))
        profile.resume_skill = json.dumps(res_skills)
        db.commit()
        return {
            "has_jd": False,
            "matching_skills": [],
            "missing_skills": [],
            "score": 0,
            "resume_skills": res_skills
        }

# ----------------- Interview Flow -----------------
@app.post("/api/interview/start")
def start_interview(
    req: InterviewStartRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user)
):
    resume_text = (req.resume_text or "").strip()
    if not resume_text:
        # Check if user has uploaded resume in uploads/
        for ext in [".pdf", ".docx"]:
            upath = os.path.join(UPLOADS_DIR, f"{user.username}_resume{ext}")
            if os.path.exists(upath):
                try:
                    _, raw = load_document(upath)
                    resume_text = cleaning(raw)
                    break
                except Exception:
                    pass
    if not resume_text:
        resume_text = "Candidate is a Software Engineer with skills in Python, Data Structures, Web Development, and Databases."

    try:
        if req.matching_skills and req.missing_skills:
            questions = genrate_ques(resume_text, req.matching_skills, req.missing_skills)
        else:
            questions = genrate_ques(resume_text)
        
        if not questions:
            questions = [
                "Could you please introduce yourself and summarize your core technical skills?",
                "Tell me about a challenging technical project you worked on recently.",
                "How do you approach debugging a complex issue in production?",
                "Where do you see your professional career in the next 2 to 3 years?"
            ]
        for q in questions[:4]:
            background_tasks.add_task(pregenerate_tts, q)
        return {"questions": questions}
    except Exception as e:
        print(f"Error generating questions: {e}")
        fb_questions = [
            "Please introduce yourself and highlight your primary technical expertise.",
            "Describe a project you built, the key architecture decisions, and obstacles you solved.",
            "Explain your approach to software testing and problem-solving.",
            "Why are you interested in this career path and what are your long-term goals?"
        ]
        for q in fb_questions:
            background_tasks.add_task(pregenerate_tts, q)
        return {
            "questions": fb_questions
        }

@app.post("/api/interview/evaluate")
def evaluate_interview_answer(
    req: EvaluateRequest,
    user: User = Depends(get_current_user)
):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question is required.")
    
    ans = (req.answer or "").strip()
    if not ans or ans.lower() == "no answer provided":
        raise HTTPException(status_code=400, detail="Please speak or type your answer into the box before submitting.")
    
    print(f"\n[Interview Evaluation - User: {user.username}]")
    print(f"Q: {req.question}")
    print(f"Candidate Answer: {ans}")
    
    try:
        feedback = evaluate_ans(req.question, ans)
        print(f"Evaluator Feedback: {feedback}\n")
        return {"feedback": feedback}
    except Exception as e:
        print(f"Error evaluating answer with LLM: {e}")
        raise HTTPException(status_code=500, detail=f"AI Evaluation error: {str(e)}")

# =========================================================================
# DUAL-AGENT INTERVIEW TURN: Confidence Tracker (Agent 2) + Adaptive Interrogator (Agent 1)
# =========================================================================
@app.post("/api/interview/turn")
def process_interview_turn(
    req: TurnRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    question = (req.question or "").strip()
    answer = (req.answer or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")
    if not answer or answer.lower() == "no answer provided":
        raise HTTPException(status_code=400, detail="Please speak or type your answer before submitting.")

    # 1. CONFIDENCE TRACKER (runs first on candidate answer)
    conf_res = track_confidence(
        question=question,
        answer=answer,
        latency_seconds=float(req.latency_seconds or 0.0),
        conversation_history=req.history or []
    )
    confidence_score = conf_res["confidence_score"]
    signals = conf_res["signals"]

    # Retrieve candidate resume context & skills
    profile = db.query(UserProfile).filter(UserProfile.username == user.username).first()
    resume_text = (req.resume_text or "").strip()
    matching_skills = []
    missing_skills = []
    target_role = (req.target_role or "").strip()

    if profile:
        target_role = target_role or profile.target_role or ""
        try:
            matching_skills = json.loads(profile.matching_skill) if profile.matching_skill else []
            missing_skills = json.loads(profile.missing_skill) if profile.missing_skill else []
        except Exception:
            pass

    if not resume_text:
        for ext in [".pdf", ".docx"]:
            upath = os.path.join(UPLOADS_DIR, f"{user.username}_resume{ext}")
            if os.path.exists(upath):
                try:
                    _, raw = load_document(upath)
                    resume_text = cleaning(raw)
                    break
                except Exception:
                    pass

    # Build updated history including this turn for the Interrogator
    current_diff = float(req.current_difficulty or 5.0)
    updated_history = list(req.history or [])
    updated_history.append({
        "turn": len(updated_history) + 1,
        "question": question,
        "answer": answer,
        "confidence": confidence_score,
        "difficulty": current_diff,
        "latency_seconds": float(req.latency_seconds or 0.0)
    })

    # 2. ADAPTIVE INTERROGATOR STRATEGY
    breaking_point = False
    weak_skill_identified = ""

    if len(updated_history) >= 3:
        last_3_conf = [float(t.get("confidence", 0.5)) for t in updated_history[-3:]]
        if all(c < 0.45 for c in last_3_conf):
            strategy = "Breaking point"
            breaking_point = True
            weak_skill_identified = target_role or "Core Technical Concept"
            next_difficulty = max(2.0, current_diff - 2.5)
            strategy_desc = f"Candidate reached breaking point on {weak_skill_identified} after 3 consecutive low-confidence responses. Marking weak area and shifting to a different foundational area."
        elif len(updated_history) >= 2 and (float(updated_history[-1].get("confidence", 0.5)) - float(updated_history[-2].get("confidence", 0.5)) <= -0.25):
            strategy = "Suddenly dropped"
            next_difficulty = current_diff
            strategy_desc = "Candidate confidence dropped sharply. Pivoting on the same weak area from an alternate angle to verify whether the gap is genuine."
        elif len(updated_history) >= 2 and float(updated_history[-1].get("confidence", 0.5)) >= 0.75 and (float(updated_history[-1].get("confidence", 0.5)) >= float(updated_history[-2].get("confidence", 0.5))):
            strategy = "High and rising"
            next_difficulty = min(10.0, current_diff + 2.0)
            strategy_desc = "Confidence is high and rising. Pushing harder with advanced edge cases, failure modes, and scale architecture (+2 difficulty)."
        elif float(updated_history[-1].get("confidence", 0.5)) < 0.55:
            strategy = "Slightly low"
            next_difficulty = max(1.0, current_diff - 1.5)
            strategy_desc = "Confidence is slightly low. Easing off to establish foundational baseline (-1.5 difficulty)."
        else:
            strategy = "Stable"
            next_difficulty = current_diff
            strategy_desc = "Confidence is steady. Maintaining natural conversational flow at current difficulty level."
    elif len(updated_history) == 1 or len(updated_history) == 2:
        latest_conf = float(updated_history[-1].get("confidence", 0.5))
        prev_conf = float(updated_history[-2].get("confidence", latest_conf)) if len(updated_history) >= 2 else latest_conf

        if latest_conf - prev_conf <= -0.25:
            strategy = "Suddenly dropped"
            next_difficulty = current_diff
            strategy_desc = "Candidate confidence dropped sharply. Pivoting on the same concept from an alternate angle."
        elif latest_conf >= 0.75:
            strategy = "High and rising"
            next_difficulty = min(10.0, current_diff + 2.0)
            strategy_desc = "Confidence is high. Pushing harder with edge cases (+2 difficulty)."
        elif latest_conf < 0.55:
            strategy = "Slightly low"
            next_difficulty = max(1.0, current_diff - 1.5)
            strategy_desc = "Slight hesitation. Easing off slightly to test core fundamentals."
        else:
            strategy = "Stable"
            next_difficulty = current_diff
            strategy_desc = "Confidence stable. Continuing at current difficulty level."
    else:
        strategy = "Stable"
        next_difficulty = 5.0
        strategy_desc = "Initial baseline question to commence the technical interview."

    next_difficulty = round(max(1.0, min(10.0, next_difficulty)), 1)

    # 3. UNIFIED FAST EVALUATION & NEXT QUESTION GENERATION (Single LLM Call)
    turn_eval = unified_turn_evaluation(
        question=question,
        answer=answer,
        strategy=strategy,
        strategy_desc=strategy_desc,
        difficulty=next_difficulty,
        target_role=target_role,
        resume_context=resume_text or "Software Engineer",
        history=updated_history
    )

    if turn_eval.get("contradiction_detected"):
        signals["contradiction_detected"] = True
        signals["contradiction_reason"] = turn_eval.get("contradiction_reason") or "Conflicted with prior statement."
        confidence_score = round(max(0.05, confidence_score - 0.25), 2)

    if turn_eval.get("next_question"):
        background_tasks.add_task(pregenerate_tts, turn_eval["next_question"])

    return {
        "confidence_score": confidence_score,
        "signals": signals,
        "feedback": turn_eval["feedback"],
        "next_question": turn_eval["next_question"],
        "difficulty": next_difficulty,
        "strategy": strategy,
        "strategy_description": strategy_desc,
        "breaking_point": breaking_point,
        "weak_skill_identified": weak_skill_identified
    }

@app.post("/api/interview/suggest_answer")
def suggest_interview_answer(
    req: EvaluateRequest,
    user: User = Depends(get_current_user)
):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")
    
    from llm import model
    from langchain_core.prompts import ChatPromptTemplate
    prompt = ChatPromptTemplate([
        ('system', '''You are a high-performing candidate answering an interview question.
Provide a clear, realistic, and structured answer in 3-4 sentences from first-person perspective.
Do not output greetings or prefixes, only the answer.'''),
        ('human', 'Question: {question}')
    ])
    try:
        chain = prompt | model
        res = chain.invoke({'question': question})
        return {"suggested_answer": res.content.strip()}
    except Exception as e:
        print(f"Error generating suggested answer: {e}")
        return {"suggested_answer": "In my development experience, I prioritize scalable design, clean data flow, and structured error handling to ensure production readiness."}

# ----------------- Edge TTS Endpoints -----------------
@app.post("/api/tts/generate")
async def generate_edge_tts(req: TTSRequest):
    text = (req.text or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required.")
    voice = (req.voice or "en-US-AriaNeural").strip()
    rate = (req.rate or "+0%").strip()
    pitch = (req.pitch or "+0Hz").strip()

    cache_key = hashlib.md5(f"{voice}_{rate}_{pitch}_{text}".encode("utf-8")).hexdigest()
    cache_file = os.path.join(TTS_CACHE_DIR, f"{cache_key}.mp3")

    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 0:
        return FileResponse(cache_file, media_type="audio/mpeg", headers={"Cache-Control": "public, max-age=86400"})

    try:
        communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, pitch=pitch)
        await communicate.save(cache_file)
        return FileResponse(cache_file, media_type="audio/mpeg", headers={"Cache-Control": "public, max-age=86400"})
    except Exception as e:
        print(f"Edge-TTS generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate speech: {str(e)}")

@app.get("/api/tts/stream")
async def stream_edge_tts(text: str, voice: str = "en-US-AriaNeural"):
    return await generate_edge_tts(TTSRequest(text=text, voice=voice))

async def pregenerate_tts(text: str, voice: str = "en-US-AriaNeural"):
    text = (text or "").strip()
    if not text:
        return
    cache_key = hashlib.md5(f"{voice}_+0%_+0Hz_{text}".encode("utf-8")).hexdigest()
    cache_file = os.path.join(TTS_CACHE_DIR, f"{cache_key}.mp3")
    if os.path.exists(cache_file) and os.path.getsize(cache_file) > 0:
        return
    try:
        communicate = edge_tts.Communicate(text=text, voice=voice, rate="+0%", pitch="+0Hz")
        await communicate.save(cache_file)
    except Exception as e:
        print(f"Edge-TTS pregeneration notice: {e}")

@app.on_event("startup")
async def startup_tts_warmup():
    default_questions = [
        "Could you please introduce yourself and summarize your core technical skills?",
        "Describe a challenging technical project you built, explaining the architecture and challenges solved.",
        "How do you approach debugging and optimizing performance in production?",
        "Where do you see your technical career progressing in the next few years?",
        "Please introduce yourself and highlight your primary technical expertise.",
        "Describe a project you built, the key architecture decisions, and obstacles you solved.",
        "Explain your approach to software testing and problem-solving.",
        "Why are you interested in this career path and what are your long-term goals?"
    ]
    for q in default_questions:
        try:
            await pregenerate_tts(q)
        except Exception:
            pass

@app.get("/api/resume/current")
def get_current_resume(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.username == user.username).first()
    resume_text = ""
    for ext in [".pdf", ".docx"]:
        upath = os.path.join(UPLOADS_DIR, f"{user.username}_resume{ext}")
        if os.path.exists(upath):
            try:
                _, raw = load_document(upath)
                resume_text = cleaning(raw)
                break
            except Exception:
                pass

    matching_skills = []
    missing_skills = []
    resume_skills = []
    target_role = ""
    score = 0
    if profile:
        target_role = profile.target_role or ""
        score = profile.score or 0
        try:
            matching_skills = json.loads(profile.matching_skill) if profile.matching_skill else []
        except Exception:
            pass
        try:
            missing_skills = json.loads(profile.missing_skill) if profile.missing_skill else []
        except Exception:
            pass
        try:
            resume_skills = json.loads(profile.resume_skill) if profile.resume_skill else []
        except Exception:
            pass

    return {
        "has_resume": bool(resume_text),
        "resume_text": resume_text,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "resume_skills": resume_skills,
        "target_role": target_role,
        "score": score
    }

@app.post("/api/interview/finish")
def finish_interview(
    req: FinishInterviewRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not req.summary_data:
        raise HTTPException(status_code=400, detail="No interview responses provided to summarize.")
    
    raw_data = [item.model_dump() for item in req.summary_data]
    report: InterviewReport = generate_summary(raw_data)
    
    # Store interview session in SQL user_history table
    new_history = UserHistory(
        username=user.username,
        score=int(report.Score),
        accuracy=float(report.Accuracy),
        blunder=int(report.Blunder),
        confidence=str(report.Confidence),
        streak=int(report.Streak),
        communication=str(report.Communication),
        created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        turns_data=json.dumps(req.turns_data or []),
        breaking_points=json.dumps(req.breaking_points or []),
        avg_confidence=float(req.avg_confidence or 0.0),
        peak_difficulty=float(req.peak_difficulty or 0.0)
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)
    print(f"✅ Successfully inserted interview history ID={new_history.id} for user={user.username}")
    
    return {
        "Score": int(report.Score),
        "Accuracy": float(report.Accuracy),
        "Blunder": int(report.Blunder),
        "Confidence": report.Confidence,
        "Streak": int(report.Streak),
        "Communication": report.Communication,
        "turns_data": req.turns_data or [],
        "breaking_points": req.breaking_points or [],
        "avg_confidence": float(req.avg_confidence or 0.0),
        "peak_difficulty": float(req.peak_difficulty or 0.0),
        "saved_to_db": True
    }

# ----------------- Preparation Hub & Documents -----------------
@app.get("/api/documents/list")
def list_documents(user: User = Depends(get_current_user)):
    docs = []
    if os.path.exists(DOCUMENTS_DIR):
        for fname in sorted(os.listdir(DOCUMENTS_DIR)):
            fpath = os.path.join(DOCUMENTS_DIR, fname)
            if os.path.isfile(fpath) and fname.lower().endswith((".pdf", ".docx", ".txt")):
                stat = os.stat(fpath)
                size_kb = round(stat.st_size / 1024, 1)
                docs.append({
                    "name": fname,
                    "size_bytes": stat.st_size,
                    "size_display": f"{size_kb} KB" if size_kb < 1024 else f"{round(size_kb/1024, 2)} MB",
                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "view_url": f"/api/documents/view/{fname}",
                    "download_url": f"/api/documents/download/{fname}"
                })
    return {"documents": docs}

@app.get("/api/documents/view/{filename}")
def view_document(filename: str):
    fpath = os.path.join(DOCUMENTS_DIR, filename)
    if not os.path.exists(fpath):
        raise HTTPException(status_code=404, detail="File not found")
    
    media_type = "application/pdf" if filename.lower().endswith(".pdf") else "application/octet-stream"
    return FileResponse(
        fpath,
        media_type=media_type,
        headers={"Content-Disposition": f'inline; filename="{filename}"'}
    )

@app.get("/api/documents/download/{filename}")
def download_document(filename: str):
    fpath = os.path.join(DOCUMENTS_DIR, filename)
    if not os.path.exists(fpath):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        fpath,
        media_type="application/octet-stream",
        filename=filename
    )

@app.post("/api/cheatsheet/generate")
def generate_user_cheatsheet(
    req: CheatsheetRequest,
    user: User = Depends(get_current_user)
):
    # Determine resume text
    resume_text = (req.resume_text or "").strip()
    
    if not resume_text:
        # Check if user has uploaded resume in uploads
        for ext in [".pdf", ".docx"]:
            upath = os.path.join(UPLOADS_DIR, f"{user.username}_resume{ext}")
            if os.path.exists(upath):
                _, raw = load_document(upath)
                resume_text = cleaning(raw)
                break
    
    if not resume_text:
        # Fallback default resume text if none uploaded yet
        resume_text = f"Candidate Username: {user.username}. Software Engineering skills: Python, Algorithms, Data Structures, Web Development, Databases."
    
    try:
        raw_cheatsheet = generate_cheatsheet(resume_text)
        out_filename = f"{user.username}_cheatsheet.pdf"
        out_path = os.path.join(DOCUMENTS_DIR, out_filename)
        
        build_cheatsheet_pdf(raw_cheatsheet, out_path)
        
        return {
            "success": True,
            "filename": out_filename,
            "raw_text": raw_cheatsheet,
            "view_url": f"/api/documents/view/{out_filename}",
            "download_url": f"/api/documents/download/{out_filename}"
        }
    except Exception as e:
        print(f"Error building cheatsheet: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate cheatsheet: {str(e)}")

# ----------------- Candidate Profile & SQL History -----------------
@app.get("/api/profile")
def get_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.username == user.username).first()
    if not profile:
        profile = UserProfile(username=user.username, target_role="", resume_skill="[]", matching_skill="[]", missing_skill="[]", score=0)
        db.add(profile)
        db.commit()
    
    def safe_json(val):
        if not val:
            return []
        try:
            return json.loads(val)
        except Exception:
            return [s.strip() for s in val.split(",") if s.strip()]

    return {
        "username": profile.username,
        "target_role": profile.target_role or "Not specified",
        "resume_skill": safe_json(profile.resume_skill),
        "matching_skill": safe_json(profile.matching_skill),
        "missing_skill": safe_json(profile.missing_skill),
        "score": profile.score or 0
    }

@app.put("/api/profile")
def update_profile(
    req: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.username == user.username).first()
    if not profile:
        profile = UserProfile(username=user.username)
        db.add(profile)
    if req.target_role is not None:
        profile.target_role = req.target_role.strip()
    db.commit()
    return {"message": "Profile updated successfully"}

@app.get("/api/profile/history")
def get_user_interview_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    history_records = (
        db.query(UserHistory)
        .filter(UserHistory.username == user.username)
        .order_by(UserHistory.id.desc())
        .all()
    )
    
    results = []
    for h in history_records:
        results.append({
            "id": h.id,
            "username": h.username,
            "score": h.score,
            "accuracy": h.accuracy,
            "blunder": h.blunder,
            "confidence": h.confidence,
            "streak": h.streak,
            "communication": h.communication,
            "created_at": h.created_at or "",
            "turns_data": json.loads(h.turns_data) if h.turns_data else [],
            "breaking_points": json.loads(h.breaking_points) if h.breaking_points else [],
            "avg_confidence": float(h.avg_confidence or 0.0),
            "peak_difficulty": float(h.peak_difficulty or 0.0)
        })
    return {"history": results}

# ----------------- Frontend Page Routes -----------------
@app.get("/", response_class=HTMLResponse)
def serve_home():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>AI Interview Platform</h1><p>Frontend loading...</p>")

@app.get("/login", response_class=HTMLResponse)
def serve_login():
    login_file = os.path.join(FRONTEND_DIR, "login.html")
    if os.path.exists(login_file):
        with open(login_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Login</h1>")

@app.get("/prep", response_class=HTMLResponse)
def serve_prep():
    prep_file = os.path.join(FRONTEND_DIR, "prep.html")
    if os.path.exists(prep_file):
        with open(prep_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Preparation Hub</h1>")

@app.get("/profile", response_class=HTMLResponse)
def serve_profile():
    profile_file = os.path.join(FRONTEND_DIR, "profile.html")
    if os.path.exists(profile_file):
        with open(profile_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Candidate Profile</h1>")

@app.get("/interview", response_class=HTMLResponse)
def serve_interview():
    interview_file = os.path.join(FRONTEND_DIR, "interview.html")
    if os.path.exists(interview_file):
        with open(interview_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Interview Room</h1>")

# Mount static files from frontend
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8000, reload=True)
