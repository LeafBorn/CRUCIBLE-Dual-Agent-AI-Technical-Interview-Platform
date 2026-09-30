
import re
SKILLS = [
    # ── Programming Languages ──────────────────────────────────────────────
    "python", "java", "javascript", "typescript", "c", "c++", "c#", "r",
    "scala", "go", "rust", "kotlin", "swift", "php", "ruby", "matlab",
    "julia", "dart", "perl", "haskell", "lua", "bash", "shell scripting",
    "assembly", "vba", "groovy", "elixir", "clojure",

    # ── Web & Mobile Development ───────────────────────────────────────────
    "html", "css", "sass", "tailwind css", "bootstrap",
    "react", "nextjs", "vuejs", "angular", "svelte", "redux",
    "nodejs", "expressjs", "nestjs", "graphql", "rest api", "websocket",
    "flutter", "react native", "android development", "ios development",
    "webpack", "vite", "babel",

    # ── Backend & Databases ────────────────────────────────────────────────
    "fastapi", "flask", "django", "spring boot", "rails", "laravel",
    "microservices", "grpc", "rabbitmq", "kafka", "celery",
    "mysql", "postgresql", "sqlite", "oracle", "sql server",
    "mongodb", "redis", "cassandra", "dynamodb", "firebase",
    "elasticsearch", "neo4j", "influxdb",

    # ── Machine Learning & AI ──────────────────────────────────────────────
    "machine learning", "deep learning", "nlp", "computer vision",
    "reinforcement learning", "federated learning", "graph neural networks",
    "time series forecasting", "anomaly detection", "recommendation systems",
    "feature engineering", "model optimization", "transfer learning",
    "object detection", "image segmentation", "speech recognition",
    "text classification", "sentiment analysis", "named entity recognition",

    # ── ML Frameworks & Libraries ──────────────────────────────────────────
    "tensorflow", "pytorch", "keras", "scikit-learn", "xgboost",
    "lightgbm", "catboost", "statsmodels", "prophet",
    "huggingface", "transformers", "bert", "gpt", "llama", "mistral",
    "langchain", "langgraph", "llamaindex", "openai api", "anthropic api",
    "diffusers", "stable diffusion", "whisper",
    "pandas", "numpy", "matplotlib", "seaborn", "plotly", "scipy",
    "opencv", "mediapipe", "pillow", "albumentations",
    "spacy", "nltk", "gensim", "sentence-transformers",
    "faiss", "chromadb", "pinecone", "weaviate",

    # ── MLOps & Data Engineering ───────────────────────────────────────────
    "mlops", "airflow", "prefect", "dagster", "mlflow", "dvc",
    "wandb", "optuna", "ray", "triton", "bentoml", "seldon",
    "spark", "hadoop", "hive", "flink", "dbt", "great expectations",
    "data pipeline", "etl", "feature store", "model registry",

    # ── DevOps & Cloud ─────────────────────────────────────────────────────
    "docker", "kubernetes", "helm", "terraform", "ansible", "jenkins",
    "github actions", "gitlab ci", "circleci", "ci/cd",
    "aws", "azure", "gcp", "heroku", "vercel", "netlify",
    "linux", "nginx", "apache", "serverless", "lambda",
    "monitoring", "prometheus", "grafana", "datadog", "elk stack",

    # ── Data Science & Analytics ───────────────────────────────────────────
    "sql", "data analysis", "data visualization", "statistical analysis",
    "hypothesis testing", "a/b testing", "regression analysis",
    "clustering", "dimensionality reduction", "pca",
    "tableau", "power bi", "looker", "metabase", "excel",
    "google analytics", "mixpanel", "amplitude",

    # ── Security & Networking ──────────────────────────────────────────────
    "cybersecurity", "penetration testing", "ethical hacking",
    "network security", "cryptography", "oauth", "jwt",
    "ssl/tls", "firewall", "ids/ips", "siem", "soc",
    "vulnerability assessment", "owasp", "devsecops",
    "networking", "tcp/ip", "dns", "http/https", "vpn", "load balancing",

    # ── Blockchain & Web3 ──────────────────────────────────────────────────
    "blockchain", "solidity", "ethereum", "smart contracts",
    "web3", "nft", "defi", "ipfs", "hardhat", "truffle",

    # ── Embedded & Hardware ────────────────────────────────────────────────
    "embedded systems", "arduino", "raspberry pi", "fpga",
    "iot", "mqtt", "rtos", "arm", "pcb design", "verilog", "vhdl",

    # ── Version Control & Collaboration ───────────────────────────────────
    "git", "github", "gitlab", "bitbucket", "jira", "confluence",
    "notion", "trello", "linear", "agile", "scrum", "kanban",

    # ── Design & UX ───────────────────────────────────────────────────────
    "ui design", "ux design", "figma", "adobe xd", "sketch",
    "wireframing", "prototyping", "user research", "usability testing",
    "information architecture", "design systems", "responsive design",
    "adobe photoshop", "adobe illustrator", "canva", "blender",
    "motion design", "3d modeling", "typography", "color theory",
    "accessibility", "wcag",

    # ── Business & Management ──────────────────────────────────────────────
    "project management", "product management", "program management",
    "strategic planning", "business analysis", "requirements gathering",
    "stakeholder management", "risk management", "change management",
    "operations management", "supply chain management", "crm",
    "erp", "six sigma", "lean", "pmp", "okr", "kpi",
    "business development", "vendor management", "procurement",

    # ── Finance & Accounting ───────────────────────────────────────────────
    "financial analysis", "financial modeling", "valuation",
    "accounting", "budgeting", "forecasting", "cash flow analysis",
    "investment analysis", "portfolio management", "risk analysis",
    "taxation", "auditing", "ifrs", "gaap", "quickbooks", "sap",
    "excel financial modeling", "equity research", "derivatives",
    "quantitative finance", "algorithmic trading",

    # ── Marketing & Sales ──────────────────────────────────────────────────
    "digital marketing", "seo", "sem", "content marketing",
    "social media marketing", "email marketing", "growth hacking",
    "brand management", "market research", "competitive analysis",
    "sales strategy", "crm tools", "salesforce", "hubspot",
    "copywriting", "ad campaigns", "google ads", "meta ads",
    "affiliate marketing", "influencer marketing", "conversion optimization",

    # ── Soft Skills ───────────────────────────────────────────────────────
    "communication", "leadership", "teamwork", "problem solving",
    "critical thinking", "time management", "adaptability",
    "conflict resolution", "negotiation", "decision making",
    "emotional intelligence", "creativity", "attention to detail",
    "public speaking", "presentation skills", "mentoring", "coaching",
    "active listening", "collaboration", "analytical thinking",
    "self motivation", "work ethic", "accountability",

    # ── Research & Writing ────────────────────────────────────────────────
    "research", "technical writing", "documentation", "report writing",
    "academic writing", "grant writing", "data journalism",
    "latex", "scientific writing", "literature review",
]

def extract_skills(text):
    text = text.lower()
    found = []
    for skill in SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text):
            found.append(skill)
    return set(found)

def match_score(matching, jd_skills):
    if not jd_skills:
        return 0.0
    skill_score = len(matching) / len(jd_skills)
    return round(skill_score * 100, 1)

def extraction(Resume, Job_des):
    resume_skills = extract_skills(Resume)
    jd_skills = extract_skills(Job_des)

    matching = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)
    score = match_score(matching, jd_skills)

    return matching, missing, score, list(resume_skills)

