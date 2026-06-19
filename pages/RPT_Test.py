## This is still a work in progress and is still subject to changes/improvements ###
import streamlit as st
#import textract
import string
import pandas as pd
import nltk
import tempfile
import os
import re
import spacy
from PyPDF2 import PdfReader
from docx import Document
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

st.set_page_config(page_title="Payreto RPT", layout="wide")
st.title(':blue[Resume Prioritization Tool] 📝')

# Load spaCy model
@st.cache_resource
def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except IOError:
        st.error("spaCy English model not found. Please install it with: python -m spacy download en_core_web_sm")
        st.stop()

nlp = load_spacy_model()
nltk.download('stopwords')

must_have_words_input = st.text_input('Enter must-have words (comma-separated)')
good_to_have_words_input = st.text_input('Enter good-to-have words (comma-separated)')

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

def calculate_tenure(text):
    """
    Calculate total working years from resume text using spaCy NLP
    """
    try:
        current_year = datetime.now().year
        doc = nlp(text)
        
        date_ranges = []
        
        # Common date range patterns in resumes
        date_patterns = [
            # 2020-2023, 2020 - 2023, 2020 to 2023
            r'(\d{4})\s*(?:[-–—]|to)\s*(\d{4})',
            # 2020-Present, 2020 - Current
            r'(\d{4})\s*(?:[-–—]|to)\s*(?:present|current|now)',
            # Jan 2020 - Dec 2023
            r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+(\d{4})\s*[-–—]\s*(?:(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+)?(\d{4})',
            # Jan 2020 - Present
            r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+(\d{4})\s*[-–—]\s*(?:present|current|now)',
        ]
        
        text_lower = text.lower()
        
        # Split text into sentences to check context around dates
        sentences = [sent.text.lower() for sent in doc.sents]
        
        for sentence in sentences:
            # Skip sentences that contain education-related terms
            education_indicators = [
                'education', 'school', 'university', 'college', 'degree', 'bachelor', 
                'master', 'phd', 'doctorate', 'graduation', 'graduated', 'studied', 
                'course', 'certification', 'academic', 'gpa', 'transcript', 'semester'
            ]
            
            if any(edu_term in sentence for edu_term in education_indicators):
                continue
            
            # Look for date patterns in work-related sentences
            work_indicators = [
                'experience', 'work', 'career', 'professional', 'employed', 'position',
                'job', 'role', 'company', 'organization', 'employer', 'manager', 'analyst',
                'developer', 'engineer', 'consultant', 'specialist', 'coordinator'
            ]
            
            has_work_context = any(indicator in sentence for indicator in work_indicators)
            
            # Also check surrounding sentences for work context
            if not has_work_context:
                sentence_idx = sentences.index(sentence)
                prev_sentence = sentences[sentence_idx - 1] if sentence_idx > 0 else ""
                next_sentence = sentences[sentence_idx + 1] if sentence_idx < len(sentences) - 1 else ""
                
                combined_context = prev_sentence + " " + sentence + " " + next_sentence
                has_work_context = any(indicator in combined_context for indicator in work_indicators)
            
            if has_work_context:
                for pattern in date_patterns:
                    matches = re.finditer(pattern, sentence)
                    for match in matches:
                        groups = match.groups()
                        start_year = int(groups[0])
                        
                        if len(groups) == 1 or groups[1] is None:
                            # Pattern with "present/current"
                            end_year = current_year
                        else:
                            try:
                                end_year = int(groups[1])
                            except:
                                end_year = current_year
                        
                        # Validate years are reasonable
                        if (1980 <= start_year <= current_year and 
                            start_year <= end_year <= current_year and
                            (end_year - start_year) <= 50):  # Max 50 years experience
                            date_ranges.append((start_year, end_year))
        
        explicit_experience = 0
        

        experience_patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|work|professional)',
            r'(?:over|more than|approximately)\s*(\d+)\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*(?:in|of|working|professional)',
        ]
        
        for sentence in sentences:
            # Skip sentences that contain education-related terms
            education_indicators = [
                'education', 'school', 'university', 'college', 'degree', 'bachelor', 
                'master', 'phd', 'doctorate', 'graduation', 'graduated', 'studied', 
                'course', 'certification', 'academic', 'gpa', 'transcript'
            ]
            
            if any(edu_term in sentence for edu_term in education_indicators):
                continue
                
            # Only look in sentences that seem work-related
            work_indicators = ['experience', 'work', 'career', 'professional', 'employed', 'position']
            if any(indicator in sentence for indicator in work_indicators):
                for pattern in experience_patterns:
                    matches = re.findall(pattern, sentence)
                    if matches:
                        for match in matches:
                            try:
                                years = int(match) if isinstance(match, str) else int(match[0])
                                if 0 < years <= 50:
                                    explicit_experience = max(explicit_experience, years)
                            except:
                                continue
        
        total_from_ranges = 0
        if date_ranges:
            # Sort and merge overlapping ranges
            date_ranges.sort()
            merged_ranges = []
            
            for start, end in date_ranges:
                if merged_ranges and start <= merged_ranges[-1][1] + 1:
                    # Merge overlapping or adjacent ranges (allow 1 year gap)
                    merged_ranges[-1] = (merged_ranges[-1][0], max(merged_ranges[-1][1], end))
                else:
                    merged_ranges.append((start, end))
            
            # Calculate total years from merged ranges
            total_from_ranges = sum(end - start + 1 for start, end in merged_ranges)
        
        years_in_work_context = []
        work_section_found = False
        
        # Check if we're in a work experience section
        work_section_indicators = [
            'work experience', 'professional experience', 'employment history',
            'career summary', 'professional background', 'work history'
        ]
        
        for indicator in work_section_indicators:
            if indicator in text_lower:
                work_section_found = True
                break
        
        if work_section_found:
            # Extract years mentioned in DATE entities within work context
            for ent in doc.ents:
                if ent.label_ == "DATE":
                    year_matches = re.findall(r'\b(\d{4})\b', ent.text)
                    for year_str in year_matches:
                        year = int(year_str)
                        if 1980 <= year <= current_year:
                            years_in_work_context.append(year)
            
            # If we have years but no clear ranges, estimate from span
            if years_in_work_context and not date_ranges:
                years_in_work_context = sorted(set(years_in_work_context))
                if len(years_in_work_context) >= 2:
                    span = years_in_work_context[-1] - years_in_work_context[0] + 1
                    if span <= 50:
                        total_from_ranges = span
        

        if explicit_experience > 0:
            return explicit_experience
        elif total_from_ranges > 0:
            return total_from_ranges
        else:
            return 0
            
    except Exception as e:
        print(f"Error in tenure calculation: {e}")
        return 0

if uploaded_files:
    fname = []
    applicant_names = []
    w1_score = []
    w2_score = []
    words = []
    alerts = []
    tenure_years = []

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
            #else:
            #    text = textract.process(temp_file_path).decode()

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
            
            # Calculate tenure from the original text using spaCy
            tenure = calculate_tenure(text)

            fname.append(file_name)
            applicant_names.append(applicant_name)
            w1_score.append(w1)
            w2_score.append(w2)
            words.append(tmpstr)
            tenure_years.append(tenure)
            alerts.append("successfully parsed")
        except Exception as e:
            fname.append(file_name)
            applicant_names.append(applicant_name)
            w1_score.append(0)
            w2_score.append(0)
            words.append('null')
            tenure_years.append(0)
            alerts.append(f"Cannot Scan CV: {e}")
        finally:
            os.remove(temp_file_path)

    result = pd.DataFrame({
        'file name': fname,
        'applicant name': applicant_names,
        'must-have words score': w1_score,
        'good-to-have words score': w2_score,
        'tenure (years)': tenure_years,
        'total score': [(w1 * 2) + w2 for w1, w2 in zip(w1_score, w2_score)],
        'words': words,
        'alerts': alerts
    })

    result = result[['file name', 'applicant name', 'must-have words score', 'good-to-have words score', 'tenure (years)', 'total score', 'words', 'alerts']]
    result = result.sort_values(by=['total score', 'tenure (years)'], ascending=[False, False])

    st.dataframe(result, hide_index=True, use_container_width=True)

    conn = st.connection("gsheets", type=GSheetsConnection)

    worksheet_name = st.text_input('Enter Google Sheets worksheet name')
    if st.button('Save Results to Google Sheets'):
        try:
            conn.create(worksheet=worksheet_name, data=result)
            st.success('Results successfully written to Google Sheets!')
        except Exception as e:
            st.error(f"Could not write to Google Sheets: {e}")