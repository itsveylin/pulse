
from groq import Groq
import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

SYSTEM_PROMPT = """
You are Pulse, a cozy study companion.

PERSONALITY:
- Warm, calm, and conversational.
- Explain concepts clearly.
- Keep normal responses under 300 words.
- Remember previous conversation context.
- Encourage learning without excessive praise.

GOAL DETECTION:

Identify personal goals expressed by the current user.

INTENT VALUES:

1. explicit:
The user clearly commits to an action.

Examples:
- I want to learn Python.
- My goal is to complete DSA.
- I plan to build a project.
- I have decided to study SQL daily.

2. ambiguous:
The user considers taking an action but has not committed.

Examples:
- I should probably learn Python.
- Maybe I should study SQL.
- I am thinking about learning Java.
- I might start a project.

3. none:
The user is discussing something without expressing an
actual personal intention.

Examples:
- Explain Python loops.
- I studied Python yesterday.
- I haven't decided what to learn next.
- I don't know which subject to choose.
- I'm unsure about my next step.

IMPORTANT RULES:
- Past activities are not future goals.
- Being undecided is not a goal.
- Do not invent a goal just to fill the goal field.
- Do not turn suggestions you give the user into their goals.
- Do not interpret a question as a goal.
- Only identify goals belonging to the current user.
- Never invent a deadline.
- Missing deadlines must be null.

GOAL TYPES:
- study
- skill
- project
- career
- personal
- general

Return ONLY valid JSON:

{
    "response": "Your conversational response.",
    "goal_detection": {
        "intent": "explicit",
        "goal": "Learn Python",
        "deadline": null,
        "goal_type": "skill"
    }
}

When there is no goal, return intent "none" and goal null.

For uncertain intentions, return intent "ambiguous".

Do not use Markdown code fences.
"""


AMBIGUOUS_PATTERNS = [
    r"\bshould probably\b",
    r"\bmaybe i should\b",
    r"\bperhaps i should\b",
    r"\bi might\b",
    r"\bi could\b",
    r"\bi may\b",
    r"\bi am thinking about\b",
    r"\bi'm thinking about\b",
    r"\bi have been thinking about\b",
    r"\bi've been thinking about\b",
    r"\bi am considering\b",
    r"\bi'm considering\b",
    r"\bconsidering\b",
    r"\bthinking of\b",
    r"\bmaybe i can\b",
]


NO_GOAL_PATTERNS = [
    r"\bi haven't decided\b",
    r"\bi have not decided\b",
    r"\bi'm undecided\b",
    r"\bi am undecided\b",
    r"\bi'm not sure\b",
    r"\bi am not sure\b",
    r"\bi don't know what to\b",
    r"\bi do not know what to\b",
    r"\bi haven't chosen\b",
    r"\bi have not chosen\b",
    r"\bi haven't figured out\b",
    r"\bi have not figured out\b",
    r"\bi'm unsure\b",
    r"\bi am unsure\b",
]


EXPLICIT_PATTERNS = [
    r"\bi want to\b",
    r"\bi plan to\b",
    r"\bi have decided to\b",
    r"\bi've decided to\b",
    r"\bi am going to\b",
    r"\bi'm going to\b",
    r"\bmy goal is to\b",
    r"\bi intend to\b",
    r"\bi need to\b",
]


def analyze_message(question, history):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    messages.extend(history)

    messages.append({
        "role": "user",
        "content": question
    })

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        max_tokens=1200,
        response_format={
            "type": "json_object"
        }
    )

    raw_response = response.choices[0].message.content

    try:
        result = json.loads(raw_response)

        if not isinstance(result, dict):
            raise ValueError("Invalid JSON response")

        goal_data = result.get("goal_detection", {})

        if not isinstance(goal_data, dict):
            goal_data = {}

        intent = goal_data.get("intent", "none")

        if intent not in ["explicit", "ambiguous", "none"]:
            intent = "none"

        goal = goal_data.get("goal")

        if not isinstance(goal, str) or not goal.strip():
            goal = None
            intent = "none"

        normalized_question = question.lower()

        has_explicit_intent = any(
            re.search(pattern, normalized_question)
            for pattern in EXPLICIT_PATTERNS
        )

        has_no_goal_signal = any(
            re.search(pattern, normalized_question)
            for pattern in NO_GOAL_PATTERNS
        )

        has_ambiguous_intent = any(
            re.search(pattern, normalized_question)
            for pattern in AMBIGUOUS_PATTERNS
        )

        # Explicit commitments take precedence.
        if has_explicit_intent:
            intent = "explicit"

        # Undecided statements are not goals.
        elif has_no_goal_signal:
            intent = "none"
            goal = None

        # Uncertain intentions require confirmation.
        elif has_ambiguous_intent and goal:
            intent = "ambiguous"

        deadline = goal_data.get("deadline")

        if deadline is not None:
            deadline = str(deadline).strip() or None

        goal_type = goal_data.get("goal_type", "general")

        allowed_types = [
            "study",
            "skill",
            "project",
            "career",
            "personal",
            "general"
        ]

        if goal_type not in allowed_types:
            goal_type = "general"

        answer = result.get("response", "")

        if not isinstance(answer, str) or not answer.strip():
            answer = "☕ I couldn't formulate a response. Could you try again?"

        return {
            "response": answer,
            "goal_detection": {
                "intent": intent,
                "goal": goal,
                "deadline": deadline,
                "goal_type": goal_type
            }
        }

    except (json.JSONDecodeError, ValueError, TypeError):

        return {
            "response": raw_response or "☕ I couldn't process that message.",
            "goal_detection": {
                "intent": "none",
                "goal": None,
                "deadline": None,
                "goal_type": "general"
            }
        }


def ask_ai(question, history):

    result = analyze_message(question, history)

    return result["response"]
