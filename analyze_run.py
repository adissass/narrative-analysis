from mlx_lm import load, generate
import json


model, tokenizer = load('mlx-community/Hermes-2-Theta-Llama-3-8B-4bit')

def parse_agenda(text, subject, bio):
    prompt = f"""
You are analyzing an event of the character {subject} from the One Piece manga series.
Each entry describes something that happens to or is done by {subject}.
Use the character background below to judge whether the event reflects positively or negatively.

Character Profile:
{bio}

Extract structured information from this entry.
Return strict JSON with fields:
- event: full description of the action (subject + summarized text of entry)
- subject: '{subject}'
- sentiment: overall polarity (great, good, neutral, bad, horrible)

Entry: '{text}'
"""

    messages = [{"role": "user", "content": prompt}]
    formatted_prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True)
    res = generate(model, tokenizer, prompt=formatted_prompt, verbose=False)

    # Extract JSON from response
    start, end = res.find("{"), res.rfind("}") + 1
    if start != -1 and end > start:
        json_str = res[start:end]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
