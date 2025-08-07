import streamlit as st
from transformers import pipeline

sentiment_classifier = pipeline("text-classification", model="deepseek-ai/DeepSeek-V3")
print(sentiment_classifier("i am very excited"))