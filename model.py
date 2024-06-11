import PyPDF2
from transformers import pipeline
from nltk.tokenize import word_tokenize
import re

def extract_text_from_pdf(pdf_path):
    text = ''
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    # Additional cleaning steps for scientific text (if needed)
    return text


model_name = "distilbert-base-cased-distilled-squad"  # Specify the model name
qa_pipeline = pipeline("question-answering", model=model_name)

# Now you can use qa_pipeline for question-answering with the specified model.

def answer_question(context, question):
    reformulated_question = question

    qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")
    result = qa_pipeline(question=reformulated_question, context=context)
    answer_start = result['start']
    answer_end = result['end']
    answer = context[answer_start:answer_end]

    # Include surrounding context (optional)
    surrounding_text = "..." + context[max(0, answer_start-20):answer_end+120] + "..."

    return f"Answer: {answer} (Context: {surrounding_text})"




