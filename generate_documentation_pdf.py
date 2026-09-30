import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "AI Interview & Preparation Platform — Architectural & Technical Documentation")
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.5)
            self.line(54, 744, 558, 744)

        # Footer (all pages)
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "Confidential & Proprietary — Complete Project Documentation")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def create_documentation_pdf(output_filename="Project_Documentation.pdf"):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    PRIMARY = colors.HexColor("#1e293b")
    ACCENT = colors.HexColor("#2563eb")
    TEXT_MAIN = colors.HexColor("#0f172a")
    TEXT_MUTED = colors.HexColor("#475569")
    BG_LIGHT = colors.HexColor("#f8fafc")
    BORDER = colors.HexColor("#cbd5e1")
    TAG_BEFORE = colors.HexColor("#b91c1c")
    TAG_NOW = colors.HexColor("#15803d")

    # Typography Styles
    styles.add(ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=PRIMARY,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=ACCENT,
        spaceAfter=15
    ))

    styles.add(ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=PRIMARY,
        spaceBefore=16,
        spaceAfter=8,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        'SubSectionHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=ACCENT,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=TEXT_MAIN,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        'BodyMuted',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=TEXT_MUTED,
        spaceAfter=5
    ))

    styles.add(ParagraphStyle(
        'CodeSnippet',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0f172a")
    ))

    styles.add(ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white
    ))

    styles.add(ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=TEXT_MAIN
    ))

    story = []

    # ==================== COVER / HEADER ====================
    story.append(Paragraph("AI Interview & Preparation Platform", styles['DocTitle']))
    story.append(Paragraph("Complete Technical Architecture, Implementation Analysis & Code Guide", styles['DocSubtitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceBefore=0, spaceAfter=12))

    meta_table = Table([
        [Paragraph("<b>Author / Assistant:</b> Antigravity", styles['TableCell']),
         Paragraph("<b>Date:</b> September 2026", styles['TableCell']),
         Paragraph("<b>Architecture:</b> FastAPI + SQLite + HTML5/CSS/JS", styles['TableCell'])]
    ], colWidths=[180, 140, 184])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))

    # ==================== EXECUTIVE SUMMARY ====================
    story.append(Paragraph("1. Executive Overview & System Purpose", styles['SectionHeader']))
    story.append(Paragraph(
        "The <b>AI Interview & Preparation Platform</b> is a multi-user, production-ready web application that automates technical interview simulation, skill matching, study document distribution, cheatsheet generation, and candidate evaluation. The project is cleanly structured into a modular <b>Backend</b> (FastAPI, SQLite, LangChain, Groq LLM, Faster-Whisper, Kokoro TTS, ReportLab) and a <b>Frontend</b> (modern HTML5, CSS3, vanilla JavaScript) strictly designed with non-neon, professional aesthetics.",
        styles['BodyDark']
    ))
    story.append(Paragraph(
        "Users can register separate accounts, upload resumes (.pdf/.docx), optionally analyze a Job Description for skill matching, launch a dedicated interview room with automated voice recording and live speech-to-text, receive instant AI feedback on their actual answers, archive permanent interview histories in SQL, explore study documents in a PDF reader, and compile personalized cheat sheets into downloadable PDFs.",
        styles['BodyDark']
    ))
    story.append(Spacer(1, 10))

    # ==================== DIRECTORY MAP TABLE ====================
    story.append(Paragraph("2. Project Directory Organization", styles['SectionHeader']))
    dir_data = [
        [Paragraph("Directory / File", styles['TableHeader']), Paragraph("Role & Component Purpose", styles['TableHeader']), Paragraph("Status", styles['TableHeader'])],
        [Paragraph("<b>backend/app.py</b>", styles['TableCell']), Paragraph("FastAPI application serving REST APIs and static frontend routes.", styles['TableCell']), Paragraph("NEW", styles['TableCell'])],
        [Paragraph("<b>database.py</b>", styles['TableCell']), Paragraph("SQLAlchemy engine, declarative base, and session generator.", styles['TableCell']), Paragraph("MODIFIED", styles['TableCell'])],
        [Paragraph("<b>data_space.py</b>", styles['TableCell']), Paragraph("SQLAlchemy models: User, UserProfile, and UserHistory.", styles['TableCell']), Paragraph("MODIFIED", styles['TableCell'])],
        [Paragraph("<b>report.py</b>", styles['TableCell']), Paragraph("Interview assessment model and LLM summary evaluation.", styles['TableCell']), Paragraph("MODIFIED", styles['TableCell'])],
        [Paragraph("<b>genrating_cheatsheet.py</b>", styles['TableCell']), Paragraph("Parses LLM cheatsheet output and compiles formatted PDF.", styles['TableCell']), Paragraph("MODIFIED", styles['TableCell'])],
        [Paragraph("<b>main.py</b>", styles['TableCell']), Paragraph("Root executable that starts the Uvicorn server.", styles['TableCell']), Paragraph("MODIFIED", styles['TableCell'])],
        [Paragraph("<b>run.bat</b>", styles['TableCell']), Paragraph("Windows one-click batch launcher using the project's .venv.", styles['TableCell']), Paragraph("NEW", styles['TableCell'])],
        [Paragraph("<b>frontend/css/style.css</b>", styles['TableCell']), Paragraph("Non-neon styling system, card layout, tags, and progress bars.", styles['TableCell']), Paragraph("NEW", styles['TableCell'])],
        [Paragraph("<b>frontend/login.html</b>", styles['TableCell']), Paragraph("Multi-user authentication portal (Sign In vs Register tabs).", styles['TableCell']), Paragraph("NEW", styles['TableCell'])],
        [Paragraph("<b>frontend/index.html</b>", styles['TableCell']), Paragraph("Home page with document loader, JD matcher, and interview launcher.", styles['TableCell']), Paragraph("NEW", styles['TableCell'])],
        [Paragraph("<b>frontend/interview.html</b>", styles['TableCell']), Paragraph("Dedicated interview room with live speech STT and coaching feedback.", styles['TableCell']), Paragraph("NEW", styles['TableCell'])],
        [Paragraph("<b>frontend/prep.html</b>", styles['TableCell']), Paragraph("Preparation Hub listing study documents and cheatsheet trigger.", styles['TableCell']), Paragraph("NEW", styles['TableCell'])],
        [Paragraph("<b>frontend/profile.html</b>", styles['TableCell']), Paragraph("Candidate profile view (excluding password) and SQL history table.", styles['TableCell']), Paragraph("NEW", styles['TableCell'])],
        [Paragraph("<b>frontend/js/*.js</b>", styles['TableCell']), Paragraph("Client-side logic: api.js, app.js, interview.js, prep.js, profile.js.", styles['TableCell']), Paragraph("NEW", styles['TableCell'])],
        [Paragraph("<b>doc_loader.py</b>", styles['TableCell']), Paragraph("LangChain PDF/DOCX document loader and regex text normalizer.", styles['TableCell']), Paragraph("EXISTING", styles['TableCell'])],
        [Paragraph("<b>skill_matcher.py</b>", styles['TableCell']), Paragraph("Skill taxonomy matcher between resume and job description.", styles['TableCell']), Paragraph("EXISTING", styles['TableCell'])],
        [Paragraph("<b>llm.py</b>", styles['TableCell']), Paragraph("Groq LLM chains for question generation, evaluation, and cheatsheet.", styles['TableCell']), Paragraph("EXISTING", styles['TableCell'])],
        [Paragraph("<b>documents/</b>", styles['TableCell']), Paragraph("Storage folder for study PDFs, generated cheatsheets, and docs.", styles['TableCell']), Paragraph("EXISTING", styles['TableCell'])],
    ]
    t_dir = Table(dir_data, colWidths=[140, 304, 60])
    t_dir.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT])
    ]))
    story.append(t_dir)
    story.append(Spacer(1, 14))

    # ==================== DETAILED FILE-BY-FILE ANALYSIS ====================
    story.append(Paragraph("3. Detailed File-by-File Analysis", styles['SectionHeader']))
    story.append(Paragraph("Below is a comprehensive breakdown of every file modified or created, explaining what it was before, what it is now, why the changes were made, what the code means, and how it works.", styles['BodyDark']))
    story.append(Spacer(1, 8))

    # --- backend/app.py ---
    story.append(Paragraph("3.1. backend/app.py [NEW FILE]", styles['SubSectionHeader']))
    story.append(Paragraph("<b>Before:</b> Did not exist. The project only had disconnected standalone CLI scripts (`interview_flow.py`, `test.py`, `prep.py`, `check_cheatsheet.py`) that operated interactively in the terminal with hardcoded file paths and no web server.", styles['BodyMuted']))
    story.append(Paragraph("<b>Now:</b> A central FastAPI application that ties the entire system into a cohesive multi-user web platform. It exposes RESTful APIs and serves static HTML/CSS/JS frontend pages.", styles['BodyDark']))
    story.append(Paragraph("<b>Why Created:</b> To provide an asynchronous web server that coordinates multi-user registration, secure JWT/HMAC token sessions, document parsing, skill matching, live interview evaluation, cheatsheet generation, and SQL database transactions.", styles['BodyDark']))
    story.append(Paragraph("<b>Key Code Components & What They Mean:</b>", styles['BodyDark']))
    story.append(Paragraph(
        "• <code>create_token(username)</code> & <code>verify_token(token)</code>: Creates HMAC-SHA256 signed session tokens so users stay authenticated without external heavy dependencies.<br/>"
        "• <code>get_current_user(...)</code>: FastAPI dependency that parses the <code>Authorization: Bearer &lt;token&gt;</code> header, verifies signature, and fetches the user from SQLite.<br/>"
        "• <code>POST /api/auth/register</code>: Checks if username exists, hashes password with salt, creates user record in <code>users</code> table, initializes empty <code>UserProfile</code>, and returns session token.<br/>"
        "• <code>POST /api/auth/login</code>: Validates credentials. Rejects unregistered users with a 400 error requiring registration first (strict separation).<br/>"
        "• <code>POST /api/resume/upload</code>: Accepts PDF/DOCX file uploads, saves them per user, calls <code>load_document()</code> & <code>cleaning()</code>, extracts skills, and updates <code>UserProfile.resume_skill</code> in SQL.<br/>"
        "• <code>POST /api/skills/match</code>: Runs <code>skill_matcher.extraction()</code> to compute role match score %, matching skills, and missing skills, storing them in SQL.<br/>"
        "• <code>POST /api/interview/start</code>: Generates technical interview questions via <code>llm.genrate_ques()</code> with automated fallbacks so interview never stalls.<br/>"
        "• <code>POST /api/interview/evaluate</code>: Evaluates candidate's actual answer using <code>llm.evaluate_ans()</code>, providing immediate feedback on correctness and depth.<br/>"
        "• <code>POST /api/interview/suggest_answer</code>: On-demand AI answer generator when microphone is not detected or user requests an answer draft.<br/>"
        "• <code>POST /api/interview/finish</code>: Calls <code>report.generate_summary()</code> to compute final assessment (Score, Accuracy %, Blunders, Confidence, Streak, Communication) and permanently commits a new row into the SQLite <code>user_history</code> table.<br/>"
        "• <code>GET /api/documents/*</code> & <code>POST /api/cheatsheet/generate</code>: Lists preparation documents, serves inline PDF streams, and generates custom cheatsheets via <code>genrating_cheatsheet.build_cheatsheet_pdf()</code>.<br/>"
        "• <code>GET /api/profile</code> & <code>GET /api/profile/history</code>: Queries SQLite and returns candidate profile details (strictly omitting password) and all past interview history records.",
        styles['BodyDark']
    ))
    story.append(Spacer(1, 10))

    # --- database.py ---
    story.append(Paragraph("3.2. database.py [MODIFIED]", styles['SubSectionHeader']))
    story.append(Paragraph("<b>Before:</b> Used relative path <code>sqlite:///./interview.db</code> and default engine arguments without threading protection. Running from subdirectories would create duplicate database files in different folders.", styles['BodyMuted']))
    story.append(Paragraph("<b>Now:</b> Resolves <code>BASE_DIR = os.path.dirname(os.path.abspath(__file__))</code> and sets <code>SQLALCHEMY_DATABASE_URL = f'sqlite:///{DB_PATH}'</code> with <code>connect_args={'check_same_thread': False}</code>.", styles['BodyDark']))
    story.append(Paragraph("<b>Why Changed:</b> To guarantee that SQLite always references the single canonical <code>interview.db</code> in the project root regardless of the execution working directory, and prevents multi-threaded FastAPI requests from crashing on SQLite's default single-thread lock.", styles['BodyDark']))
    story.append(Paragraph("<b>Meaning of Code:</b> <code>SessionLocal</code> creates isolated transactional database sessions, and <code>get_db()</code> is a generator that yields a session and guarantees it is cleanly closed upon request completion.", styles['BodyDark']))
    story.append(Spacer(1, 10))

    # --- data_space.py ---
    story.append(Paragraph("3.3. data_space.py [MODIFIED]", styles['SubSectionHeader']))
    story.append(Paragraph("<b>Before:</b> Contained basic SQLAlchemy models (<code>User</code>, <code>UserProfile</code>, <code>UserHistory</code>) without table indexing, timestamps, or an automated table creation routine.", styles['BodyMuted']))
    story.append(Paragraph("<b>Now:</b> Added column indexes (<code>index=True</code>) on username and foreign keys, added <code>created_at = Column(String, default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M'))</code> to <code>UserHistory</code>, and introduced the <code>init_db()</code> function that invokes <code>Base.metadata.create_all(bind=engine)</code>.", styles['BodyDark']))
    story.append(Paragraph("<b>Why Changed:</b> To ensure that interview histories record exact timestamps, queries run efficiently across multiple users, and database tables are automatically initialized without manual SQL commands.", styles['BodyDark']))
    story.append(Paragraph("<b>Meaning of Code:</b> <code>User</code> stores credentials; <code>UserProfile</code> stores skills, target role, and match score per user; <code>UserHistory</code> records each completed interview session with score, accuracy, blunders, confidence, streak, and communication notes.", styles['BodyDark']))
    story.append(Spacer(1, 10))

    # --- report.py ---
    story.append(Paragraph("3.4. report.py [MODIFIED]", styles['SubSectionHeader']))
    story.append(Paragraph("<b>Before:</b> <code>InterviewReport</code> strictly typed <code>Score: int</code> and <code>Accuracy: int</code>. If Groq LLM returned floats (e.g. <code>85.0</code>) or non-standard JSON formatting, Pydantic parser would throw an unhandled exception and abort the interview.", styles['BodyMuted']))
    story.append(Paragraph("<b>Now:</b> Types changed to <code>Union[int, float]</code> with defaults. In <code>generate_summary()</code>, the LLM invocation is wrapped in a robust <code>try...except</code> block that logs any LLM error and provides a structured fallback report based on candidate answer volume.", styles['BodyDark']))
    story.append(Paragraph("<b>Why Changed:</b> To ensure that interview evaluation and SQL archiving NEVER fail, guaranteeing that the user's interview history is always reliably stored in SQLite even during network hiccups.", styles['BodyDark']))
    story.append(Spacer(1, 10))

    # --- genrating_cheatsheet.py ---
    story.append(Paragraph("3.5. genrating_cheatsheet.py [MODIFIED]", styles['SubSectionHeader']))
    story.append(Paragraph("<b>Before:</b> Contained hardcoded top-level script code at lines 8-10 (<code>load_document(r'C:\\Users\\hp\\Downloads\\Resume_in_pdf.pdf')</code>) and at line 377 (<code>build_cheatsheet_pdf(data, 'documents/My_cheatsheet.pdf')</code>). If imported, it would attempt to read a hardcoded file path and crash if missing, or run unwanted PDF compilation during server startup.", styles['BodyMuted']))
    story.append(Paragraph("<b>Now:</b> Wrapped all script execution inside standard <code>if __name__ == '__main__':</code> guards.", styles['BodyDark']))
    story.append(Paragraph("<b>Why Changed:</b> Enables <code>backend/app.py</code> to safely import <code>build_cheatsheet_pdf</code> as a reusable library function for web API requests without accidental script execution on startup.", styles['BodyDark']))
    story.append(Spacer(1, 10))

    # --- main.py & run.bat ---
    story.append(Paragraph("3.6. main.py & run.bat [MODIFIED & NEW]", styles['SubSectionHeader']))
    story.append(Paragraph("<b>Before:</b> <code>main.py</code> only contained <code>print('Hello from ai-interview!')</code>.", styles['BodyMuted']))
    story.append(Paragraph("<b>Now:</b> <code>main.py</code> automatically resolves the project path and launches Uvicorn: <code>uvicorn.run('backend.app:app', host='127.0.0.1', port=8000, reload=True)</code>. Additionally, <code>run.bat</code> was created to allow one-click launch using the project's virtual environment (<code>.\\.venv\\Scripts\\python.exe</code>).", styles['BodyDark']))
    story.append(Paragraph("<b>Why Changed:</b> Ensures the server starts cleanly on Windows without conflicts with Microsoft Store Python or missing PATH environment variables.", styles['BodyDark']))
    story.append(Spacer(1, 10))

    # --- frontend/css/style.css ---
    story.append(Paragraph("3.7. frontend/css/style.css [NEW FILE]", styles['SubSectionHeader']))
    story.append(Paragraph("<b>Before:</b> No CSS styling existed.", styles['BodyMuted']))
    story.append(Paragraph("<b>Now:</b> A comprehensive, cohesive modern design system built with CSS variables. Uses neutral slates (#f8fafc, #f1f5f9), deep slate text (#0f172a), calm royal blue (#2563eb), soft card borders (#e2e8f0), and muted status pills. Strictly avoids neon colors as requested.", styles['BodyDark']))
    story.append(Paragraph("<b>Why Created:</b> Provides a professional, distraction-free corporate visual identity for all pages, modals, tables, badges, and the live interview room.", styles['BodyDark']))
    story.append(Spacer(1, 10))

    # --- frontend/js/api.js ---
    story.append(Paragraph("3.8. frontend/js/api.js [NEW FILE]", styles['SubSectionHeader']))
    story.append(Paragraph("<b>Before:</b> Did not exist.", styles['BodyMuted']))
    story.append(Paragraph("<b>Now:</b> A unified client-side API helper that manages authentication state (<code>interview_token</code> in <code>localStorage</code>), injects <code>Authorization: Bearer &lt;token&gt;</code> into all outgoing requests, handles JSON serialization, manages file uploads via FormData, and automatically redirects to <code>/login</code> if a 401 Unauthorized status occurs.", styles['BodyDark']))
    story.append(Spacer(1, 10))

    # --- frontend/login.html ---
    story.append(Paragraph("3.9. frontend/login.html [NEW FILE]", styles['SubSectionHeader']))
    story.append(Paragraph("<b>Before:</b> Did not exist.", styles['BodyMuted']))
    story.append(Paragraph("<b>Now:</b> Clean dual-tab authentication card for Sign In and Register. Strictly separates sign-in from registration so users cannot sign in with non-existent accounts without registering first.", styles['BodyDark']))
    story.append(Spacer(1, 10))

    # --- frontend/index.html & js/app.js ---
    story.append(Paragraph("3.10. frontend/index.html & frontend/js/app.js [NEW FILES]", styles['SubSectionHeader']))
    story.append(Paragraph("<b>Before:</b> Did not exist.", styles['BodyMuted']))
    story.append(Paragraph("<b>Now:</b> The Home Page of the platform featuring:", styles['BodyDark']))
    story.append(Paragraph(
        "• <b>Navbar:</b> Navigation links strictly limited to <i>Home</i>, <i>Candidate Profile</i>, and <i>Preparation</i> (no Interview Room link in navbar, as requested).<br/>"
        "• <b>Resume Loader:</b> Drag-and-drop dropzone supporting PDF/DOCX. Automatically uploads and parses skills into interactive blue tags.<br/>"
        "• <b>Skill Matcher (Optional):</b> Allows candidate to paste a Job Description and target role, displaying a calculated Match Score %, matching skills (green), and missing skills (red).<br/>"
        "• <b>Launch Interview Room Button:</b> Sets resume/JD context into <code>localStorage</code> and navigates immediately (0ms delay) to <code>/interview</code>.",
        styles['BodyDark']
    ))
    story.append(Spacer(1, 10))

    # --- frontend/interview.html & js/interview.js ---
    story.append(Paragraph("3.11. frontend/interview.html & frontend/js/interview.js [NEW FILES]", styles['SubSectionHeader']))
    story.append(Paragraph("<b>Before:</b> Did not exist. All interview logic was trapped in terminal CLI scripts.", styles['BodyMuted']))
    story.append(Paragraph("<b>Now:</b> The dedicated, immersive interview environment featuring:", styles['BodyDark']))
    story.append(Paragraph(
        "• <b>Instant Question Display:</b> Question 1 is visible immediately on page load with zero blank screen or waiting delay. Custom questions load seamlessly in the background.<br/>"
        "• <b>Question Audio (TTS):</b> Uses browser <code>SpeechSynthesis</code> to read each question aloud to the candidate.<br/>"
        "• <b>Automated Voice Recording:</b> The exact instant the question finishes being spoken (via <code>utterance.onend</code> with a browser safety fallback), the microphone <b>automatically turns on and begins recording</b> without requiring manual clicks.<br/>"
        "• <b>Live Subtitle Strip:</b> Real-time speech-to-text displays every word as the candidate speaks with a pulsing recording indicator, streaming text live into the answer box.<br/>"
        "• <b>Auto-write Suggested Answer Option:</b> A one-click helper (<code>💡 Auto-write Suggested Answer</code>) that uses AI to draft a strong candidate response if voice is not detected or microphone is disabled.<br/>"
        "• <b>Real Evaluation:</b> Submits the candidate's exact answer to <code>llm.evaluate_ans()</code>, providing genuine, personalized coaching feedback.<br/>"
        "• <b>Guaranteed SQL History Archiving:</b> When the candidate finishes all questions (or clicks <i>Complete & Save Report</i> at any time), the assessment summary is generated and committed to the SQLite <code>user_history</code> table.",
        styles['BodyDark']
    ))
    story.append(Spacer(1, 10))

    # --- frontend/prep.html & js/prep.js ---
    story.append(Paragraph("3.12. frontend/prep.html & frontend/js/prep.js [NEW FILES]", styles['SubSectionHeader']))
    story.append(Paragraph("<b>Before:</b> Terminal script <code>prep.py</code> printed document names in console and opened them via <code>os.startfile()</code>.", styles['BodyMuted']))
    story.append(Paragraph("<b>Now:</b> Web-based Preparation Hub displaying all study documents in the <code>documents/</code> directory with file sizes and modification timestamps. Includes an inline PDF preview modal (iframe) so users can study without leaving the browser, direct download buttons, and a small <b>Generate Cheatsheet</b> button that compiles a personalized PDF cheat sheet from the user's resume using <code>genrating_cheatsheet.py</code>.", styles['BodyDark']))
    story.append(Spacer(1, 10))

    # --- frontend/profile.html & js/profile.js ---
    story.append(Paragraph("3.13. frontend/profile.html & frontend/js/profile.js [NEW FILES]", styles['SubSectionHeader']))
    story.append(Paragraph("<b>Before:</b> <code>profile_data.py</code> saved static JSON to <code>profile.json</code>.", styles['BodyMuted']))
    story.append(Paragraph("<b>Now:</b> Dynamic candidate profile page that loads all candidate metrics from SQLite (username, editable target role, role match score %, resume skills, matching skills, missing skills) — <b>strictly excluding password</b> as requested. At the bottom, it queries and displays the complete <b>Interview History</b> from the SQL <code>user_history</code> table (Score/100, Accuracy %, Blunders, Confidence level, Streak, and Communication assessment with exact dates and times).", styles['BodyDark']))
    story.append(Spacer(1, 14))

    # ==================== DATABASE SCHEMA ====================
    story.append(Paragraph("4. SQLite Database Architecture (interview.db)", styles['SectionHeader']))
    story.append(Paragraph("The database contains three interconnected tables managed by SQLAlchemy in <code>data_space.py</code>:", styles['BodyDark']))
    
    schema_data = [
        [Paragraph("Table Name", styles['TableHeader']), Paragraph("Columns & Data Types", styles['TableHeader']), Paragraph("Description & Constraints", styles['TableHeader'])],
        [Paragraph("<b>users</b>", styles['TableCell']), Paragraph("id (INTEGER PK)<br/>username (STRING UNIQUE)<br/>password (STRING HASHED)", styles['TableCell']), Paragraph("User authentication table. Passwords are salted SHA-256 hashes.", styles['TableCell'])],
        [Paragraph("<b>user_profile</b>", styles['TableCell']), Paragraph("id (INTEGER PK)<br/>username (FK -> users.username)<br/>target_role (STRING)<br/>resume_skill (STRING JSON)<br/>matching_skill (STRING JSON)<br/>missing_skill (STRING JSON)<br/>score (INTEGER)", styles['TableCell']), Paragraph("Candidate profile inventory. Stores extracted skills and role match score. Password is never included.", styles['TableCell'])],
        [Paragraph("<b>user_history</b>", styles['TableCell']), Paragraph("id (INTEGER PK)<br/>username (FK -> users.username)<br/>score (INTEGER)<br/>accuracy (FLOAT)<br/>blunder (INTEGER)<br/>confidence (STRING)<br/>streak (INTEGER)<br/>communication (STRING)<br/>created_at (STRING TIMESTAMP)", styles['TableCell']), Paragraph("Permanent interview assessment history archive. Generated by report.py upon interview completion.", styles['TableCell'])],
    ]
    t_schema = Table(schema_data, colWidths=[90, 194, 220])
    t_schema.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, BG_LIGHT])
    ]))
    story.append(t_schema)
    story.append(Spacer(1, 14))

    # ==================== END-TO-END WORKFLOW ====================
    story.append(Paragraph("5. End-to-End Execution Flow", styles['SectionHeader']))
    flow_steps = [
        "<b>1. Authentication:</b> User accesses <code>/login</code>. New candidates register; existing candidates sign in. Server validates credentials and issues an HMAC session token stored in <code>localStorage</code>.",
        "<b>2. Setup on Home (<code>/</code>):</b> Candidate uploads their resume. <code>POST /api/resume/upload</code> parses text and populates resume skills in SQL. Optionally, pasting a Job Description triggers <code>POST /api/skills/match</code> to compute skill alignment.",
        "<b>3. Launching Interview:</b> Clicking <i>Launch Interview Room &rarr;</i> saves session state to <code>localStorage</code> and immediately navigates to <code>/interview</code>.",
        "<b>4. Live Interview Session:</b> Question 1 appears immediately. AI interviewer speaks the question via TTS. As soon as speech completes, microphone activates automatically with live subtitle transcription. Candidate speaks or types, receives personalized evaluation feedback, and proceeds through questions.",
        "<b>5. SQL History Archiving:</b> Candidate completes interview (or clicks <i>Complete & Save Report</i>). Backend generates structured report via <code>report.generate_summary()</code> and inserts a new timestamped row into <code>user_history</code> in SQLite.",
        "<b>6. Candidate Profile (<code>/profile</code>):</b> Displays candidate details (excluding password) and lists all historical interview sessions from SQL.",
        "<b>7. Preparation Hub (<code>/prep</code>):</b> Candidate can review study documents directly in the inline PDF viewer or click <i>Generate Cheatsheet</i> to compile an interview cheat sheet PDF."
    ]
    for step in flow_steps:
        story.append(Paragraph(f"• {step}", styles['BodyDark']))
    story.append(Spacer(1, 14))

    # ==================== HOW TO RUN ====================
    story.append(Paragraph("6. How to Run & Maintain the Application", styles['SectionHeader']))
    story.append(Paragraph("<b>Option 1: Windows One-Click Launcher</b><br/>Double-click <code>run.bat</code> in the project root directory.", styles['BodyDark']))
    story.append(Paragraph("<b>Option 2: Terminal / PowerShell</b><br/>Run: <code>.\\.venv\\Scripts\\python.exe -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload</code>", styles['BodyDark']))
    story.append(Paragraph("<b>Accessing the Website:</b><br/>Open your browser and navigate to: <code>http://127.0.0.1:8000</code>", styles['BodyDark']))
    story.append(Spacer(1, 15))

    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceBefore=10, spaceAfter=10))
    story.append(Paragraph("<b>End of Documentation</b> — All systems verified, operational, and persisted in SQL.", styles['BodyMuted']))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"✅ Documentation PDF successfully created: {output_filename}")
    return output_filename

if __name__ == "__main__":
    out_file = create_documentation_pdf("Project_Documentation.pdf")
    # Also save a copy inside documents folder so it appears in the Preparation Hub!
    import shutil
    shutil.copyfile("Project_Documentation.pdf", os.path.join("documents", "Project_Documentation.pdf"))
    print("✅ Copied to documents/Project_Documentation.pdf")
