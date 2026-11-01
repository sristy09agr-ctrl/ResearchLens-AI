
import json
import re


def _extract_json(text):
    """Extract JSON from the model response."""

    text = (text or "").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return None


def verify_answer(client, question, answer, evidence):
    """
    Verify an AI-generated answer against retrieved evidence.

    Returns:
        A dictionary containing:
        - overall_status
        - supported_claims
        - unsupported_claims
        - warnings
    """

    prompt = f"""
You are the evidence verification component of ResearchLens AI.

Your task is to verify an AI-generated answer using ONLY
the supplied research evidence.

Original question:
{question}

Generated answer:
{answer}

Available evidence:
{evidence}

Instructions:

1. Identify the important factual claims in the answer.
2. Check whether each claim is supported by the evidence.
3. Identify claims that are unsupported or contradicted.
4. Check whether the citations refer to relevant evidence passages.
5. Do not assume a claim is correct merely because it sounds scientific.
6. If evidence is insufficient, classify the claim as unsupported.

Return ONLY valid JSON in this format:

{{
    "overall_status": "verified",
    "supported_claims": [
        {{
            "claim": "Example claim",
            "reason": "Supported by evidence passage [1]"
        }}
    ],
    "unsupported_claims": [
        {{
            "claim": "Example unsupported claim",
            "reason": "No supplied passage supports this claim"
        }}
    ],
    "warnings": [
        "Any important verification warnings"
    ]
}}

The overall_status must be one of:
- verified
- partially_verified
- unsupported

Return empty arrays when there are no items.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        result = _extract_json(response.text)

        if not isinstance(result, dict):
            raise ValueError("Invalid verification response.")

        supported = result.get("supported_claims", [])
        unsupported = result.get("unsupported_claims", [])
        warnings = result.get("warnings", [])

        if not isinstance(supported, list):
            supported = []

        if not isinstance(unsupported, list):
            unsupported = []

        if not isinstance(warnings, list):
            warnings = []

        status = result.get("overall_status", "unsupported")

        if status not in (
            "verified",
            "partially_verified",
            "unsupported"
        ):
            status = "unsupported"

        # Do not label an answer verified if unsupported claims remain.
        if unsupported and status == "verified":
            status = "partially_verified"

        return {
            "overall_status": status,
            "supported_claims": supported,
            "unsupported_claims": unsupported,
            "warnings": warnings
        }

    except Exception as error:
        return {
            "overall_status": "verification_failed",
            "supported_claims": [],
            "unsupported_claims": [],
            "warnings": [
                f"Verification could not be completed: {str(error)}"
            ]
        }
