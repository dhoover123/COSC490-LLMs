import language_tool_python
import textstat
import torch
from transformers import pipeline
import re

# Initialize tools
grammar_tool = language_tool_python.LanguageTool('en-US')
creativity_model = pipeline('text-generation', model='gpt2')

# Load your game transcript
def load_text(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# Grammar Check
def grammar_score(text):
    matches = grammar_tool.check(text)
    num_errors = len(matches)
    words = len(text.split())
    error_rate = num_errors / words if words else 1
    score = max(0, 100 - (error_rate * 1000))
    return round(score, 2)

# Timing Check (based on pacing: looking for huge paragraphs or abrupt ends)
def timing_score(text):
    sentences = re.split(r'[.!?]', text)
    average_length = sum(len(s.split()) for s in sentences if s) / len(sentences)
    if 10 <= average_length <= 25:
        return 90 + (5 * (25 - average_length) / 15)  # High score if in ideal pacing range
    else:
        return max(40, 70 - abs(average_length - 17) * 2)

# Creativity Check (very basic: surprise GPT2 with your text and see how "hard" it is for GPT2 to continue logically)
def creativity_score(text):
    prompt = text[:300]  # First 300 characters
    outputs = creativity_model(prompt, max_length=350, num_return_sequences=1)
    continuation = outputs[0]['generated_text'][len(prompt):]
    surprise_factor = 1 - (len(continuation.strip()) / 50)  # Short continuation means model was "surprised"
    score = 70 + (surprise_factor * 30)
    return round(min(score, 100), 2)

# Consistency Check (measure repeated characters, names, place names)
def consistency_score(text):
    names = re.findall(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)?\b', text)
    name_freq = {}
    for name in names:
        name_freq[name] = name_freq.get(name, 0) + 1

    frequent_names = [n for n, freq in name_freq.items() if freq >= 3]
    if not frequent_names:
        return 50
    variation = len(set(frequent_names)) / len(frequent_names)
    score = 80 + (1 - variation) * 20
    return round(min(score, 100), 2)

# Final evaluator
def evaluate(file_path):
    text = load_text(file_path)
    return {
        "Grammar": grammar_score(text),
        "Timing": timing_score(text),
        "Creativity": creativity_score(text),
        "Consistency": consistency_score(text)
    }

# Example usage
if __name__ == "__main__":
    results = evaluate('your_game_transcript.txt')
    for category, score in results.items():
        print(f"{category}: {score}/100")
