import os
import re
import openai
import streamlit as st
from time import time
import textwrap

# File operations
def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()

# API functions
def chatbot(conversation, model="gpt-4-0613", temperature=0, max_tokens=2000):
    with st.spinner('Thinking...'):
        try:
            response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature, max_tokens=max_tokens)
            text = response['choices'][0]['message']['content']
            return text, response['usage']['total_tokens']
        except Exception as oops:
            st.error(f'Error communicating with OpenAI: "{oops}"')

def app():
    openai.api_key = open_file('key_openai.txt').strip()
    
    st.title("Medical Chatbot")
    
    # Initialize conversation
    conversation = [{'role': 'system', 'content': open_file('system_01_intake.md')}]
    
    user_input = st.text_area("Describe your symptoms to the intake bot. Type DONE when done.")
    
    if st.button("Submit Symptoms"):
        if user_input.strip() == 'DONE':
            st.warning("You have ended the conversation.")
        else:
            conversation.append({'role': 'user', 'content': user_input.strip()})
            response, _ = chatbot(conversation)
            if response:
                st.subheader("INTAKE:")
                st.write(response)
                
                # Save to log
                save_file(f'logs/log_{time()}_chat.txt', response)
                
                # CHARTING NOTES
                st.subheader("Generating Intake Notes")
                conversation = [{'role': 'system', 'content': open_file('system_02_prepare_notes.md')},
                               {'role': 'user', 'content': '<<BEGIN PATIENT INTAKE CHAT>>\n\n' + '\n\n'.join([msg['content'] for msg in conversation if msg['role'] == 'user']) + '\n\n<<END PATIENT INTAKE CHAT>>'}]
                notes, _ = chatbot(conversation)
                st.write("Notes version of conversation:")
                st.write(notes)
                
                # Save to log
                save_file(f'logs/log_{time()}_notes.txt', notes)
                
                # GENERATING REPORT
                st.subheader("Generating Hypothesis Report")
                conversation = [{'role': 'system', 'content': open_file('system_03_diagnosis.md')},
                               {'role': 'user', 'content': notes}]
                report, _ = chatbot(conversation)
                st.write("Hypothesis Report:")
                st.write(report)
                
                # Save to log
                save_file(f'logs/log_{time()}_diagnosis.txt', report)
                
                # CLINICAL EVALUATION
                st.subheader("Preparing for Clinical Evaluation")
                conversation = [{'role': 'system', 'content': open_file('system_04_clinical.md')},
                               {'role': 'user', 'content': notes}]
                clinical, _ = chatbot(conversation)
                st.write("Clinical Evaluation:")
                st.write(clinical)
                
                # Save to log
                save_file(f'logs/log_{time()}_clinical.txt', clinical)
                
                # REFERRALS & TESTS
                st.subheader("Generating Referrals and Tests")
                conversation = [{'role': 'system', 'content': open_file('system_05_referrals.md')},
                               {'role': 'user', 'content': notes}]
                referrals, _ = chatbot(conversation)
                st.write("Referrals and Tests:")
                st.write(referrals)
                
                # Save to log
                save_file(f'logs/log_{time()}_referrals.txt', referrals)

if __name__ == '__main__':
    if not os.path.exists('logs'):
        os.makedirs('logs')
    app()
