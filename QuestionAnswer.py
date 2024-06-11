import json
import re
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM, set_seed
from sklearn.feature_extraction.text import TfidfVectorizer

def load_chunks_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def preprocess_chunks(chunks):
    return [re.sub(r'\s+', ' ', chunk) for chunk in chunks]

def find_relevant_chunks(chunks, question, tokenizer, max_length=1024, top_n=3):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(chunks + [question])
    cosine_similarities = (vectors[-1] * vectors[:-1].T).toarray()
    most_relevant_indices = np.argsort(cosine_similarities, axis=1)[0, -top_n:][::-1]
    relevant_chunks = [chunks[i] for i in most_relevant_indices]
    
    combined_context = ""
    for chunk in relevant_chunks:
        tokenized_chunk = tokenizer.encode(chunk, add_special_tokens=False, truncation=True)  # Ensure truncation to avoid exceeding max length
        if len(tokenizer.encode(combined_context, add_special_tokens=False)) + len(tokenized_chunk) < max_length - 100:
            combined_context += " " + chunk
        else:
            break
    
    return combined_context.strip()

def load_model(output_dir):
    tokenizer = AutoTokenizer.from_pretrained(output_dir)
    model = AutoModelForCausalLM.from_pretrained(output_dir)
    return pipeline('text-generation', model=model, tokenizer=tokenizer), tokenizer

def clean_repeated_phrases(text):
    sentences = text.split('. ')
    seen = set()
    result = []
    for sentence in sentences:
        if sentence not in seen:
            result.append(sentence)
            seen.add(sentence)
    return '. '.join(result).strip()

def iterative_ask_question(pipeline, tokenizer, question, context, max_iterations=3, max_new_tokens=200, temperature=0.7, top_p=0.9, seed=42):
    set_seed(seed)
    prompt = f"Context: {context}\n\nQuestion: {question}\n\nAnswer:"
    response = pipeline(prompt, max_new_tokens=max_new_tokens, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id, temperature=temperature, top_p=top_p)
    generated_text = response[0]['generated_text']
    
    for _ in range(max_iterations):
        if "Answer:" in generated_text:
            answer = generated_text.split("Answer:")[1].strip()
        else:
            answer = generated_text
        answer = clean_repeated_phrases(answer)
        
        # If answer seems repetitive or irrelevant, refine the context and prompt again
        if len(answer.split()) < 10 or "not available" in answer.lower() or "chief secretary" in answer.lower():
            prompt = f"Refine context: {context}\n\nQuestion: {question}\n\nAnswer:"
            response = pipeline(prompt, max_new_tokens=max_new_tokens, num_return_sequences=1, pad_token_id=tokenizer.eos_token_id, temperature=temperature, top_p=top_p)
            generated_text = response[0]['generated_text']
        else:
            break
    
    return answer