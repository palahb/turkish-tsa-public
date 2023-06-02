import re
import torch
import numpy as np
from transformers import BertTokenizerFast, BertForSequenceClassification

from flask import Flask, json, g, request, jsonify, json

t_bert_model = BertForSequenceClassification.from_pretrained("./turkish-tsa-public/model")
t_bert_tokenizer = BertTokenizerFast.from_pretrained("./turkish-tsa-public/tokenizer")

sentiment_label_map = {0: "negative", 1: "neutral", 2: "positive"}

def predict_sentiment(text, model, tokenizer):
    model.eval()
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        preds = torch.argmax(outputs.logits, dim=1)

    return preds.item()

def process_sentence(sentence, target_word):
    target_word = target_word.replace('I', 'ı').replace('İ', 'i').lower()
    sentence = sentence.replace('I', 'ı').replace('İ', 'i').lower()
    sentence = re.sub(r'\s+', ' ', sentence)
    sentence = re.sub(r'#(\w+)', r'\1', sentence)
    sentence = re.sub(r'@\w+', '', sentence)
    sentence = re.sub(r'http\S+|www\S+', '', sentence)
    sentence = re.sub(r'\b({0})\b'.format(re.escape(target_word)), r'[TAR] \1 [TAR]', sentence)
    sentence = '[CLS] ' + sentence

    return sentence.strip()

def evaluater(sentence, target_word):
    processed_sentence = process_sentence(sentence, target_word)
    pred = predict_sentiment(processed_sentence, t_bert_model, t_bert_tokenizer)
    sentiment_label = sentiment_label_map[pred]
    return sentiment_label

app = Flask(__name__)

@app.route("/evaluate", methods=["POST"])
def evaluate():
    json_data = json.loads(request.data)

    result = {"targeted_sentiment": evaluater(json_data['sentence'],json_data['target'])}
    response = app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )
    return response


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)