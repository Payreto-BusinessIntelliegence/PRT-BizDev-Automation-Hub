import streamlit as st
import textract
import string
import pandas as pd
import nltk
import tempfile
import os
import re
import base64
from PIL import Image
from PyPDF2 import PdfReader
from docx import Document
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')

rpt_1 = Image.open('assets/resume_prioritization_tool/rpt_1.png')
rpt_2 = Image.open('assets/resume_prioritization_tool/rpt_2.png')
rpt_3 = Image.open('assets/resume_prioritization_tool/rpt_3.png')
rpt_4 = Image.open('assets/resume_prioritization_tool/rpt_4.png')
rpt_5 = Image.open('assets/resume_prioritization_tool/rpt_5.png')

def image_to_base64(image):
    import io
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

rpt_1_base64 = image_to_base64(rpt_1)
rpt_2_base64 = image_to_base64(rpt_2)
rpt_3_base64 = image_to_base64(rpt_3)
rpt_4_base64 = image_to_base64(rpt_4)
rpt_5_base64 = image_to_base64(rpt_5)

st.set_page_config(page_title="Resume Prioritization Tool", layout="wide")

st.title(':blue[Resume Prioritization Tool] 🖍')

with st.expander("**Expand to see how to use the tool**", expanded=False):
    st.write("**1. Keyword Preparation:**")
    st.write("a. Populate the 'must-have words' and 'good-to-have words' fields with comma-separated keywords.")
    st.write("NOTE: (1) Ensure that the 'must-have words' and 'good-to-have words' are in lowercase. (2) Ensure that the 'must-have words' are more specific and 'good-to-have words' are more general. (3) Ensure that keywords with two letters together are combined using a (-) sign, for example 'detail-oriented'.")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{rpt_1_base64}" alt="Instruction Image 1" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("**2. File Upload:**")
    st.write("a. Click on the 'Browse files' button to select one or multiple resumes / or drag and drop the files (PDF, DOCX, or DOC).")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{rpt_2_base64}" alt="Instruction Image 2" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("**3. Resume Analysis:**")
    st.write("a. The tool will automotically analyze each uploaded resume and calculate a score based on the presence of 'must-have words' and 'good-to-have words'.")
    st.write("NOTE: The formula for calculating the total score is: (must-have words score * 2) + (good-to-have words score * 1).")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{rpt_3_base64}" alt="Instruction Image 3" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("b. The results can be saved by clicking on the download button of the resulting DataFrame.")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{rpt_4_base64}" alt="Instruction Image 4" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{rpt_5_base64}" alt="Instruction Image 5" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )

must_have_words_input = st.text_input('Enter must-have words (comma-separated)',  'aml, compliance, transaction, monitoring, risk, investigation, pep, sanction')
good_to_have_words_input = st.text_input('Enter good-to-have words (comma-separated)', 'kyb, kyc, due, diligence, detail-oriented, analysis, review, payment, remittance, b2c, b2b')

must_have_words = set([word.strip() for word in must_have_words_input.split(',')])
good_to_have_words = set([word.strip() for word in good_to_have_words_input.split(',')])

uploaded_files = st.file_uploader("Upload resumes", type=["pdf", "docx", "doc"], accept_multiple_files=True)

def extract_text_from_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return str(e)

def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        text = ''
        for para in doc.paragraphs:
            text += para.text + '\n'
        return text
    except Exception as e:
        return str(e)

def extract_name_from_filename(file_name):
    name_without_extension = os.path.splitext(file_name)[0]
    name_pattern = re.compile(r'[a-zA-Z]+(?: [a-zA-Z]+)*')
    match = name_pattern.search(name_without_extension)
    if match:
        return match.group(0)
    else:
        return "Unknown"

if uploaded_files:
    fname = []
    applicant_names = []
    w1_score = []
    w2_score = []
    words = []
    alerts = []

    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        applicant_name = extract_name_from_filename(file_name)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        try:
            if file_name.endswith('.pdf'):
                text = extract_text_from_pdf(temp_file_path)
            elif file_name.endswith('.docx'):
                text = extract_text_from_docx(temp_file_path)
            else:
                text = textract.process(temp_file_path).decode()

            w1 = 0
            w2 = 0
            y = text.replace('\n', '')
            y = y.translate(str.maketrans('', '', string.punctuation))
            y = y.lower()
            y = y.split()
            y_set = set(y)
            tmpstr = ""
            for word in y_set:
                if word in must_have_words:
                    w1 += 1
                    tmpstr += f"{word}, "
                if word in good_to_have_words:
                    w2 += 1
                    tmpstr += f"{word}, "

            fname.append(file_name)
            applicant_names.append(applicant_name)
            w1_score.append(w1)
            w2_score.append(w2)
            words.append(tmpstr)
            alerts.append("successfully parsed")
        except Exception as e:
            fname.append(file_name)
            applicant_names.append(applicant_name)
            w1_score.append(0)
            w2_score.append(0)
            words.append('null')
            alerts.append(f"Cannot Scan CV: {e}")
        finally:
            os.remove(temp_file_path)

    result = pd.DataFrame({
        'file name': fname,
        'applicant name': applicant_names,
        'must-have words score': w1_score,
        'good-to-have words score': w2_score,
        'total score': [(w1 * 2) + w2 for w1, w2 in zip(w1_score, w2_score)],
        'words': words,
        'alerts': alerts
    })

    result = result[['file name', 'applicant name', 'must-have words score', 'good-to-have words score', 'total score', 'words', 'alerts']]
    result = result.sort_values(by=['total score'], ascending=False)

    st.dataframe(result, hide_index=True, use_container_width=True)