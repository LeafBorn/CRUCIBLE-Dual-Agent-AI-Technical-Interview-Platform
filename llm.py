from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
import re
from dotenv import load_dotenv
import random

num = random.randint(15,20)

load_dotenv()

model = init_chat_model(model='groq:openai/gpt-oss-20b', temperature=0.7)

def genrate_ques(resume_context:str, matching_skill:list = None, missing_skill: list = None):

    if matching_skill and missing_skill:
        skill_context = f'''
Candidate has these skills (ask deep): {', '.join(matching_skill)}
Candidate lacks these skills (ask basic awareness): {', '.join(missing_skill)}
Matching Skills: ask deep questions that test real understanding and practical knowledge;
Missing Skills: ask basic awareness questions to assess fundamental knowledge.
'''
    else:
        skill_context = f'''
"Ask questions based on the skills mentioned in the candidate's resume,
focusing on their actual understanding, practical knowledge, and experience with those skills."
'''

    prompt = ChatPromptTemplate([
    ('system', '''
You are an expert technical interviewer conducting a real job interview.
Based on the candidate resume, generate exactly {num_questions} interview questions.

Follow this order like a real interview:
- Ask the candidate to introduce themselves.
- Ask simple background questions about their education and current interests
- Then skils and their fundamentals  
- {skill_context}
- Then deep dive into projects and technologies
- Ask about their work experience, internship experience, or previous professional experience if mentioned in the resume
- Then DSA and problem solving
- End with HR and motivation

Rules:
- Questions must be specific to THIS candidate resume
- Reference actual project names, skills, technologies
- Return ONLY a numbered list, nothing else like Here are the interview questions 

1. question
2. question
...
'''),
    ('human', 'Here is the candidate resume:\n{resume_context}')
])

    chain = prompt | model

    raw = chain.invoke({'resume_context': resume_context,
                        'skill_context': skill_context,
                        'num_questions': num}).content

    questions = []
    for line in raw.split('\n'):
        line = line.strip()
        if not line:
            continue
        cleaned = re.sub(r'^\d+[\.\)]\s*', '', line)
        if cleaned:
            questions.append(cleaned)

    return questions



def evaluate_ans(question, answer):
    prompt =  ChatPromptTemplate([
        ('system', '''
You are a friendly interview coach.

If the answer is correct:
- Appreciate briefly

If the answer is wrong or incomplete:
- Tell me what is wrong 
- Correct the mistake clearly
- Explain the right concept in simple words

Keep it short and clear. Max 5-6 lines.
'''),
        ('human', '''
Question: {question}
Candidate Answer: {answer}
''')
    ])


    chain = prompt | model
    response = chain.invoke({
        'question' : question,
        'answer' : answer
    })

    return response.content.strip()


#------------ Feature ---------------------------
def generate_cheatsheet(resume_context: str) -> str:
    prompt = ChatPromptTemplate([
        ('system', '''
Generate a quick interview cheat sheet from the resume.
You are an expert interview coach. Analyze the resume and return ONLY this exact format (no extra text):

SELF INTRODUCTION:
- <proper introduction including nam, education, skill, goal>

PROJECT PITCHES:
- <project name>: < how to build, what difficulty face and how to overcome>
 
KEY TECHNOLOGIES:
- <tech>: <1 line definition>
 
DSA TOPICS TO REVISE:
- <topic> : <1 line definition>
HR ANSWERS:
- Why this role: <answer>
- Strength: <answer>
- Weakness: <answer>
- Long term goal: <answer>
- Why you hired in this compancy: <answer>
- What is your salary expectation: <answer>
 
WEAK AREAS TO COVER:
- <area>
 
Rules:
- Each section MUST start with the exact heading shown above (all caps, colon)
- Each item MUST start with '- '
- No markdown, no bold, no extra formatting
- Be concise and interview-ready"""
 
'''),
        ('human', 'Resume:\n{resume_context}')
    ])

    chain = prompt | model
    response = chain.invoke({"resume_context": resume_context})
    return response.content.strip()


# =========================================================================
# AGENT 2 — CONFIDENCE TRACKER (runs first on candidate answer)
# Scores how confident the candidate sounded using 4 signals:
# 1. Answer length (short = dodging, detailed = knowing)
# 2. Hedging words ("maybe", "I think", "shayad", "not sure", etc.)
# 3. Response latency (fast = knew it, long pause = struggling/searching)
# 4. Contradiction (conflicts with earlier session statements)
# =========================================================================
HEDGING_PATTERN = re.compile(
    r'\b(maybe|i think|shayad|not sure|not really sure|probably|might be|i guess|not certain|'
    r'kinda|sort of|perhaps|possibly|i believe|could be|i assume|not fully sure|honestly not sure|'
    r'dont know much|doubtful|may be|lagta hai|pata nahi)\b',
    re.IGNORECASE
)

def track_confidence(
    question: str,
    answer: str,
    latency_seconds: float = 0.0,
    conversation_history: list = None
) -> dict:
    ans_clean = (answer or "").strip()
    words = ans_clean.split()
    word_count = len(words)

    # 1. Answer Length & Detail Signal (0.0 to 1.0)
    if word_count == 0:
        length_score = 0.0
    elif word_count < 8:
        length_score = 0.25
    elif word_count < 20:
        length_score = 0.55
    elif word_count < 45:
        length_score = 0.85
    elif word_count <= 160:
        length_score = 1.0
    else:
        length_score = 0.85

    # 2. Hedging Words Signal (each occurrence lowers score)
    hedging_matches = HEDGING_PATTERN.findall(ans_clean)
    hedging_count = len(hedging_matches)
    if hedging_count == 0:
        hedging_score = 1.0
    elif hedging_count == 1:
        hedging_score = 0.75
    elif hedging_count == 2:
        hedging_score = 0.50
    elif hedging_count == 3:
        hedging_score = 0.30
    else:
        hedging_score = 0.15

    # 3. Response Latency Signal (latency in seconds before answering)
    if latency_seconds <= 4.0:
        latency_score = 1.0
    elif latency_seconds <= 10.0:
        latency_score = 0.90
    elif latency_seconds <= 18.0:
        latency_score = 0.70
    elif latency_seconds <= 30.0:
        latency_score = 0.45
    else:
        latency_score = 0.25

    # 4. Instant Signals Weighted Score:
    # 35% Answer Length + 35% Hedging Words + 30% Response Latency
    combined_score = (
        0.35 * length_score +
        0.35 * hedging_score +
        0.30 * latency_score
    )

    # Check for fast heuristic contradiction if history exists
    contradiction_detected = False
    contradiction_reason = ""
    if conversation_history and len(conversation_history) > 0:
        ans_lower = ans_clean.lower()
        for prev in conversation_history[-3:]:
            prev_ans = (prev.get("answer") or "").lower()
            # Flag obvious self-contradictions (e.g. saying 'never used' after saying 'used', or 'don't know' after claiming expertise)
            if ("never used" in ans_lower or "no experience" in ans_lower) and ("i built" in prev_ans or "production" in prev_ans):
                contradiction_detected = True
                contradiction_reason = "Claimed production experience earlier but now states never used."
                combined_score -= 0.30
                break

    # Clamp between 0.05 and 1.0
    final_confidence = round(max(0.05, min(1.0, combined_score)), 2)

    return {
        "confidence_score": final_confidence,
        "signals": {
            "answer_length_words": word_count,
            "length_score": round(length_score, 2),
            "hedging_count": hedging_count,
            "hedging_words": hedging_matches,
            "hedging_score": round(hedging_score, 2),
            "latency_seconds": round(latency_seconds, 1),
            "latency_score": round(latency_score, 2),
            "contradiction_detected": contradiction_detected,
            "contradiction_reason": contradiction_reason,
            "llm_confidence": final_confidence
        }
    }


# =========================================================================
# UNIFIED TURN EVALUATION: Evaluates Answer & Crafts Next Question in 1 LLM Call
# Eliminates multi-turn network latency (drops delay from ~10s to ~1.5s)
# =========================================================================
def unified_turn_evaluation(
    question: str,
    answer: str,
    strategy: str,
    strategy_desc: str,
    difficulty: float,
    target_role: str,
    resume_context: str,
    history: list = None
) -> dict:
    recent_turns_text = "\n".join([
        f"Turn {i+1} (Diff: {t.get('difficulty', 5.0)}, Conf: {t.get('confidence', 0.5)}):\nQ: {t.get('question','')}\nA: {t.get('answer','')}"
        for i, t in enumerate(history[-4:])
    ]) if history else "No previous turns in this session."

    prompt = ChatPromptTemplate([
        ('system', '''You are an expert technical interviewer and interview coach.
The candidate has answered an interview question. Perform two tasks in strict format:

1. Provide short, constructive coaching feedback (3-4 bullet points):
   - What was accurate and good in their answer.
   - What was missing or could be improved technically.
   - The correct concept in clear, simple terms.
2. Check if the candidate's latest answer contradicts any statement they made in earlier turns.
3. Formulate the EXACT next technical interview question strictly following this strategy:
   Strategy: "{strategy}" (Difficulty: {difficulty}/10.0)
   Directive: {strategy_desc}
   Target Role: {target_role}

Return ONLY this exact format:
FEEDBACK:
- <feedback point 1>
- <feedback point 2>
- <feedback point 3>

CONTRADICTION: NO (or YES: <reason>)

NEXT_QUESTION:
<exact next interview question without prefix>'''),
        ('human', f'''Current Question: {question}
Candidate Answer: {answer}

Target Role: {target_role or "Software Engineer"}
Candidate Background / Skills:
{(resume_context or "Software Engineer")[:800]}

Session History:
{recent_turns_text}''')
    ])

    try:
        chain = prompt | model
        raw_output = chain.invoke({
            "strategy": strategy,
            "strategy_desc": strategy_desc,
            "difficulty": difficulty,
            "target_role": target_role or "Software Engineer"
        }).content.strip()

        feedback_part = ""
        contradiction_part = "NO"
        next_q_part = ""

        # Parse sections
        parts = re.split(r'\n(?=FEEDBACK:|CONTRADICTION:|NEXT_QUESTION:)', raw_output, flags=re.IGNORECASE)
        for part in parts:
            part = part.strip()
            if part.upper().startswith("FEEDBACK:"):
                feedback_part = part.split(":", 1)[-1].strip()
            elif part.upper().startswith("CONTRADICTION:"):
                contradiction_part = part.split(":", 1)[-1].strip()
            elif part.upper().startswith("NEXT_QUESTION:"):
                next_q_part = part.split(":", 1)[-1].strip()

        if not feedback_part:
            feedback_part = raw_output
        if not next_q_part:
            next_q_part = f"Can you elaborate on how you apply this in a production environment?"

        next_q_part = re.sub(r'^(Q\d+[:.]?|\d+[\.\)]|Next Question:)\s*', '', next_q_part).strip(' "')

        is_contradiction = contradiction_part.upper().startswith("YES")
        contra_reason = contradiction_part.split(":", 1)[-1].strip() if is_contradiction else ""

        return {
            "feedback": feedback_part,
            "contradiction_detected": is_contradiction,
            "contradiction_reason": contra_reason,
            "next_question": next_q_part
        }
    except Exception as e:
        print(f"[unified_turn_evaluation] Error: {e}")
        return {
            "feedback": "Answer noted. Let's move on to the next technical topic.",
            "contradiction_detected": False,
            "contradiction_reason": "",
            "next_question": f"Could you walk me through a technical architecture you built and how you handled edge cases?"
        }


# =========================================================================
# AGENT 1 — ADAPTIVE INTERROGATOR (Decides what question to ask next)
# Reads the confidence score and decides the strategy:
# 1. High and rising        -> Push harder (jump +2 difficulty, edge cases, failure modes)
# 2. Suddenly dropped       -> Pivot (probe same weak area from a different angle)
# 3. Low for 3 turns        -> Breaking point (mark confirmed weak skill, stop pushing)
# 4. Slightly low           -> Ease off (ask something a bit easier to find true level)
# 5. Stable                 -> Maintain (natural follow-up, same difficulty)
# =========================================================================
def adaptive_interrogate(
    resume_context: str,
    target_role: str = "",
    matching_skills: list = None,
    missing_skills: list = None,
    history: list = None,
    current_difficulty: float = 5.0
) -> dict:
    history = history or []
    current_difficulty = float(current_difficulty or 5.0)

    # Identify strategy based on confidence history
    breaking_point = False
    weak_skill_identified = ""

    if len(history) >= 3:
        # Check if last 3 turns were low confidence (< 0.45)
        last_3_conf = [float(t.get("confidence", 0.5)) for t in history[-3:]]
        if all(c < 0.45 for c in last_3_conf):
            strategy = "Breaking point"
            breaking_point = True
            weak_skill_identified = history[-1].get("topic") or target_role or "Core Technical Concept"
            next_difficulty = max(2.0, current_difficulty - 2.5)
            strategy_desc = f"Candidate reached breaking point on {weak_skill_identified} after 3 consecutive low-confidence responses. Marking weak area and shifting to a different foundational area."
        elif len(history) >= 2 and (float(history[-1].get("confidence", 0.5)) - float(history[-2].get("confidence", 0.5)) <= -0.25):
            strategy = "Suddenly dropped"
            next_difficulty = current_difficulty
            strategy_desc = "Candidate confidence dropped sharply. Pivoting on the same weak area from an alternate angle to verify whether the gap is genuine."
        elif len(history) >= 2 and float(history[-1].get("confidence", 0.5)) >= 0.75 and (float(history[-1].get("confidence", 0.5)) >= float(history[-2].get("confidence", 0.5))):
            strategy = "High and rising"
            next_difficulty = min(10.0, current_difficulty + 2.0)
            strategy_desc = "Confidence is high and rising. Pushing harder with advanced edge cases, failure modes, and scale architecture (+2 difficulty)."
        elif float(history[-1].get("confidence", 0.5)) < 0.55:
            strategy = "Slightly low"
            next_difficulty = max(1.0, current_difficulty - 1.5)
            strategy_desc = "Confidence is slightly low. Easing off to establish foundational baseline (-1.5 difficulty)."
        else:
            strategy = "Stable"
            next_difficulty = current_difficulty
            strategy_desc = "Confidence is steady. Maintaining natural conversational flow at current difficulty level."
    elif len(history) == 1 or len(history) == 2:
        latest_conf = float(history[-1].get("confidence", 0.5))
        prev_conf = float(history[-2].get("confidence", latest_conf)) if len(history) >= 2 else latest_conf

        if latest_conf - prev_conf <= -0.25:
            strategy = "Suddenly dropped"
            next_difficulty = current_difficulty
            strategy_desc = "Candidate confidence dropped sharply. Pivoting on the same concept from an alternate angle."
        elif latest_conf >= 0.75:
            strategy = "High and rising"
            next_difficulty = min(10.0, current_difficulty + 2.0)
            strategy_desc = "Confidence is high. Pushing harder with edge cases (+2 difficulty)."
        elif latest_conf < 0.55:
            strategy = "Slightly low"
            next_difficulty = max(1.0, current_difficulty - 1.5)
            strategy_desc = "Slight hesitation. Easing off slightly to test core fundamentals."
        else:
            strategy = "Stable"
            next_difficulty = current_difficulty
            strategy_desc = "Confidence stable. Continuing at current difficulty level."
    else:
        # First turn
        strategy = "Stable"
        next_difficulty = 5.0
        strategy_desc = "Initial baseline question to commence the technical interview."

    # Clamp next difficulty between 1.0 and 10.0
    next_difficulty = round(max(1.0, min(10.0, next_difficulty)), 1)

    # Build prompt for LLM to craft the specific next question
    recent_turns_text = "\n".join([
        f"Turn {i+1} [Diff: {t.get('difficulty', 5.0)}, Conf: {t.get('confidence', 0.5)}]:\n"
        f"Interviewer: {t.get('question','')}\nCandidate: {t.get('answer','')}"
        for i, t in enumerate(history[-4:])
    ]) if history else "No previous turns yet."

    skills_text = f"Matching skills: {', '.join(matching_skills or [])}\nMissing skills: {', '.join(missing_skills or [])}"

    prompt = ChatPromptTemplate([
        ('system', '''You are Agent 1 — The Adaptive Technical Interrogator.
You conduct realistic technical interviews by adapting to the candidate's confidence level.

STRATEGY DIRECTIVE:
Your current strategy is: "{strategy}"
Directive Details: {strategy_desc}
Assigned Question Difficulty Level: {difficulty} / 10.0

STRATEGY GUIDELINES:
- "High and rising": Jump difficulty. Ask about race conditions, edge cases, failure recovery, caching stampedes, distributed scale, or internal compiler/engine mechanics.
- "Suddenly dropped": PIVOT. Do NOT repeat the previous question. Target the same underlying skill or concept, but reframe the question from a practical, day-to-day scenario to check if they genuinely lack the concept.
- "Breaking point": The candidate has failed 3 questions in a row on this topic. STOP grilling them on this skill. Acknowledge and transition smoothly to a completely different topic from their resume at a foundational level.
- "Slightly low": Ask a slightly simpler question on the fundamental mechanics or basics of the topic.
- "Stable": Ask a natural follow-up question digging deeper into their response.

Output ONLY the exact next interview question. Do not include prefixes like "Question:" or conversational preamble. Ask the question directly.'''),
        ('human', f'''Candidate Resume / Profile Context:
{resume_context[:1800]}

Target Role: {target_role or "Software Engineer"}
{skills_text}

Interview Conversation So Far:
{recent_turns_text}

Now generate the NEXT interview question for this candidate according to strategy "{strategy}":''')
    ])

    try:
        chain = prompt | model
        next_q = chain.invoke({
            "strategy": strategy,
            "strategy_desc": strategy_desc,
            "difficulty": next_difficulty
        }).content.strip()

        # Clean any leading quotes or numbering
        next_q = re.sub(r'^(Q\d+[:.]?|\d+[\.\)]|Next Question:)\s*', '', next_q).strip(' "')
        if not next_q:
            next_q = f"How would you approach designing a resilient backend architecture for {target_role or 'this role'}?"
    except Exception as e:
        print(f"[Agent 1 Interrogator] Error: {e}")
        next_q = f"Could you walk me through an end-to-end technical project from your resume and how you handled unexpected edge cases?"

    return {
        "next_question": next_q,
        "difficulty": next_difficulty,
        "strategy": strategy,
        "strategy_description": strategy_desc,
        "breaking_point": breaking_point,
        "weak_skill_identified": weak_skill_identified
    }