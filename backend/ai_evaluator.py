import os
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def evaluate_code_with_ai(
    code: str,
    language: str,
    problem_description: str,
    sample_input: str,
    sample_output: str,
    constraints: str = None
) -> dict:
    """
    Evaluate code using GPT-4o without execution.
    Returns score (0-10), status, and feedback.
    """
    
    prompt = f"""You are an expert code evaluator for a hackathon. Analyze the following code submission.

**Problem Description:**
{problem_description}

**Sample Input:**
{sample_input}

**Expected Output:**
{sample_output}

{f"**Constraints:**\n{constraints}" if constraints else ""}

**Submitted Code ({language}):**
```{language}
{code}
```

**Evaluation Criteria:**
1. **Correctness (40%)**: Does the logic correctly solve the problem for the given sample?
2. **Code Quality (30%)**: Is the code clean, readable, and well-structured?
3. **Efficiency (20%)**: Is the algorithm efficient? Any obvious optimizations?
4. **Edge Cases (10%)**: Does it handle edge cases mentioned in constraints?

**Important:** 
- Do NOT execute the code
- Analyze the logic and algorithm
- Check if it would produce the expected output for the sample input
- Consider time/space complexity

**Response Format (JSON only):**
{{
    "score": <0-10>,
    "status": "<passed/failed/partial>",
    "correctness": <0-4>,
    "code_quality": <0-3>,
    "efficiency": <0-2>,
    "edge_cases": <0-1>,
    "feedback": "<detailed feedback in 2-3 sentences>",
    "suggestions": "<improvement suggestions if any>"
}}

Provide only valid JSON, no additional text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert programming judge. Analyze code submissions and provide scores in JSON format only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Try to parse JSON
        try:
            result = json.loads(result_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(result_text)
        
        # Ensure all required fields exist
        score = float(result.get('score', 0))
        status = result.get('status', 'failed')
        feedback = result.get('feedback', 'Code evaluated.')
        
        return {
            "score": min(max(score, 0), 10),  # Clamp between 0-10
            "status": status,
            "feedback": feedback,
            "details": {
                "correctness": result.get('correctness', 0),
                "code_quality": result.get('code_quality', 0),
                "efficiency": result.get('efficiency', 0),
                "edge_cases": result.get('edge_cases', 0)
            },
            "suggestions": result.get('suggestions', '')
        }
        
    except Exception as e:
        print(f"AI Evaluation Error: {e}")
        # Return a default score if AI fails
        return {
            "score": 5.0,
            "status": "partial",
            "feedback": "Code received but could not be fully evaluated. Manual review may be required.",
            "details": {
                "correctness": 2,
                "code_quality": 2,
                "efficiency": 1,
                "edge_cases": 0
            },
            "suggestions": "Error in automatic evaluation."
        }


async def batch_evaluate_codes(submissions: list) -> list:
    """
    Evaluate multiple code submissions in batch
    """
    results = []
    for submission in submissions:
        result = await evaluate_code_with_ai(
            code=submission['code'],
            language=submission['language'],
            problem_description=submission['problem_description'],
            sample_input=submission['sample_input'],
            sample_output=submission['sample_output'],
            constraints=submission.get('constraints')
        )
        results.append(result)
    
    return results