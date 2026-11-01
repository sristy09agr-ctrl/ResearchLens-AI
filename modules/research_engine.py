
import json
import re


def _extract_json(text):
    """Extract a JSON object or array from an AI response."""
    text = (text or "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}|\[.*\]", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def plan_research_questions(client, query):
    """
    Break a complex research question into smaller questions.

    Returns a list of sub-questions.
    """

    prompt = f"""
You are the research planning component of ResearchLens AI.

Break the following research question into 2 to 4 smaller,
independent questions that can be answered using research papers.

Rules:
- Preserve the original intent.
- Focus on relevant scientific evidence.
- Avoid unnecessary questions.
- If the original question is simple, return it as one question.
- Return ONLY valid JSON in this format:

{{
    "questions": [
        "Question 1",
        "Question 2"
    ]
}}

Research question:
{query}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    result = _extract_json(response.text)

    if not isinstance(result, dict):
        return [query]

    questions = result.get("questions", [])

    if not isinstance(questions, list):
        return [query]

    questions = [
        str(question).strip()
        for question in questions
        if isinstance(question, str) and question.strip()
    ]

    # Avoid empty or excessive plans.
    return questions[:4] if questions else [query]


def generate_research_report(client, query, evidence):
    """
    Generate a structured research report from retrieved evidence.
    """

    prompt = f"""
You are ResearchLens AI, a scientific research report generator.

Create a structured report answering the research question.

Use ONLY the evidence supplied below.

Research question:
{query}

Evidence:
{evidence}

Use the following structure:

# Research Report

## 1. Research Overview
Explain the topic and objective.

## 2. Key Findings
Summarize the important findings with citations.

## 3. Methodologies
Explain the methods used in the supplied papers.

## 4. Comparison and Discussion
Compare the findings and methodologies.

## 5. Agreements and Contradictions
Identify agreements and disagreements only when supported by evidence.

## 6. Research Gaps
Identify possible gaps suggested by the supplied evidence.
Do not invent gaps.

## 7. Limitations
Mention limitations explicitly supported by the evidence.

## 8. Conclusion
Provide an evidence-based conclusion.

IMPORTANT:
- Cite claims using the supplied passage numbers, such as [1].
- Never invent citations.
- Clearly state when evidence is insufficient.
- Distinguish established findings from possible interpretations.
- Do not use outside knowledge.

Return the report in Markdown.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text or "Unable to generate the research report."
