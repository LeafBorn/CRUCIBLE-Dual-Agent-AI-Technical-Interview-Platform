from typing import Union
from pydantic import BaseModel, field_validator
from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

model = init_chat_model(model='groq:openai/gpt-oss-20b', temperature=0.7)


class InterviewReport(BaseModel):
    Score : Union[int, float] = 70
    Accuracy : Union[int, float] = 70
    Blunder : int = 0
    Confidence : str = "moderate"
    Streak : int = 1
    Communication : str = "Good communication and clear explanation."

    def __str__(self):
        return f"""

    Score : {self.Score}/100
    Accuracy : {self.Accuracy}%
    Blunder : {self.Blunder}
    Confidence : {self.Confidence}
    Streak : {self.Streak}
    Communication : {self.Communication}
"""

parser = PydanticOutputParser(pydantic_object=InterviewReport)

def generate_summary(summary_data : list) -> InterviewReport:
    transcript = ''
    for r in summary_data:
        transcript += f"Q{r.get('q_no', 1)}: {r.get('question', '')}\n"
        transcript += f"Answer: {r.get('answer', '')}\n"

    summary_prompt = ChatPromptTemplate([
        ('system', '''
You are a senior interviewer giving final structured assessment.

Analyze the full interview and return structured output.

{format_instructions}

Rules:
- Score: overall score out of 100 (integer)
- Accuracy: percentage of correct/relevant answers out of total (0 to 100)
- Blunder: Count total blunder in all answer (integer)
- Streak: how many correct answers in a row at best (integer)
- Confidence : Give the one word about how much answer close to question (e.g. high, moderate, low)
- Communication: one clear sentence on how well they explained
'''),
        ('human', '''
Full Interview:
{transcript}
''')
    ])

    try:
        chain = summary_prompt | model | parser
        report = chain.invoke({
            'transcript' : transcript,
            'format_instructions' : parser.get_format_instructions()
        })
        return report
    except Exception as e:
        print(f"Warning in generate_summary: {e}. Generating fallback report.")
        # Calculate rough fallback based on answers length
        total_answers = len([s for s in summary_data if s.get('answer') and s.get('answer') != 'No answer provided'])
        score = min(90, max(20, total_answers * 20))
        return InterviewReport(
            Score=score,
            Accuracy=score,
            Blunder=max(0, len(summary_data) - total_answers),
            Confidence="moderate",
            Streak=max(1, total_answers),
            Communication="Answers provided were evaluated based on the interview transcript."
        )