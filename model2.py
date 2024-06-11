import fitz  # PyMuPDF
import re
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, TextDataset, DataCollatorForLanguageModeling
import json

def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

def preprocess_text(text):
    # Remove multiple newlines and unnecessary whitespace
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, chunk_size=2000):
    # Split text into chunks of specified size
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def save_chunks_to_file(chunks, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False)

def train_language_model(text, model_name="gpt2", output_dir="./Science_model2"):
    # Save text to a temporary file for creating a dataset
    with open("temp_text.txt", "w", encoding='utf-8') as f:
        f.write(text)

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    # Create a dataset
    dataset = TextDataset(
        tokenizer=tokenizer,
        file_path="temp_text.txt",
        block_size=128
    )

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )

    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=True,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        save_steps=10_000,
        save_total_limit=2,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=dataset,
    )

    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)


# pdf_path = "Science.pdf"
# text = extract_text_from_pdf(pdf_path)
# cleaned_text = preprocess_text(text)
# chunks_file_path = "Science_preprocessed_chunks.json"
# chunks = chunk_text(cleaned_text)
# save_chunks_to_file(chunks, chunks_file_path)
# train_language_model(cleaned_text)
