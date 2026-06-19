import streamlit as st
import pandas as pd
import re
import arrow
import html
import base64
from PIL import Image
from ics import Calendar

gc_1 = Image.open('assets/google_calendar/gc_1.png')
gc_2 = Image.open('assets/google_calendar/gc_2.png')
gc_3 = Image.open('assets/google_calendar/gc_3.png')
gc_4 = Image.open('assets/google_calendar/gc_4.png')
gc_5 = Image.open('assets/google_calendar/gc_5.png')
gc_6 = Image.open('assets/google_calendar/gc_6.png')
gc_7 = Image.open('assets/google_calendar/gc_7.png')
gc_8 = Image.open('assets/google_calendar/gc_8.png')
gc_9 = Image.open('assets/google_calendar/gc_9.png')
gc_10 = Image.open('assets/google_calendar/gc_10.png')
gc_11 = Image.open('assets/google_calendar/gc_11.png')

def image_to_base64(image):
    import io
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

gc_1_base64 = image_to_base64(gc_1)
gc_2_base64 = image_to_base64(gc_2)
gc_3_base64 = image_to_base64(gc_3)
gc_4_base64 = image_to_base64(gc_4)
gc_5_base64 = image_to_base64(gc_5)
gc_6_base64 = image_to_base64(gc_6)
gc_7_base64 = image_to_base64(gc_7)
gc_8_base64 = image_to_base64(gc_8)
gc_9_base64 = image_to_base64(gc_9)
gc_10_base64 = image_to_base64(gc_10)
gc_11_base64 = image_to_base64(gc_11)

st.set_page_config(page_title="Google Calendar Event Extraction", layout="wide")

with st.sidebar:
    st.markdown("<h1 class='centered' style='color: #fee6aa;'>Google Calendar Event Extraction Tool</h1>", unsafe_allow_html=True)
    st.write("")
    st.markdown(
    """
        <div style="display: flex; justify-content: center;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Google_Calendar_icon_%282020%29.svg/768px-Google_Calendar_icon_%282020%29.svg.png" 
            alt="test" style="width:150px; height:auto;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")
    st.write("")
    st.write("""
             
    This Streamlit application allows users to upload .ics files from their Google Calendar to extract and analyze specific events. Initially developed to streamline event tracking, this tool is especially valuable for Business Development Associates who need to monitor their KPI-related activities.
    
    Key features:
    - Seamless Upload: Simply input your .ics file to begin processing.
    - Event Filtering: Extract and filter events based on predefined criteria, such as date range, attendees, and invitations status.
    - KPI Reporting: Gain insights into the meetings you've attended, enabling better performance tracking and improved accountability.
    """)
st.markdown(
    """
    <div style="display: flex; align-items: center; justify-content: center;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Google_Calendar_icon_%282020%29.svg/768px-Google_Calendar_icon_%282020%29.svg.png" alt="Calendar Icon" style="width: 40px; margin-right: 10px;">
        <h1 style='color: #fee6aa; margin: 0; display: inline;'>Google Calendar Event Extraction</h1>
    </div>
    """,
    unsafe_allow_html=True
)

st.write("")
st.write("")
st.write("")
st.write("")
st.write("")

with st.expander("**Expand to see how to use the tool**", expanded=False):
    st.write("**1. Data Preparation:**")
    st.write("How to Export Data Straight from Google Calendar:")
    st.write("a. Open your Google Calendar")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{gc_1_base64}" alt="Instruction Image 1" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("b. Click the settings icon")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{gc_2_base64}" alt="Instruction Image 2" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("c. After clicking the settings after the find the “Import & export” in the left hand tab and click it.")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{gc_3_base64}" alt="Instruction Image 3" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("d. Once in the “Import & export” click the export button to export the Google Calendar data.")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{gc_4_base64}" alt="Instruction Image 4" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("e. You first need to unzip the file because the exported data is in zipped format.")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{gc_5_base64}" alt="Instruction Image 5" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{gc_6_base64}" alt="Instruction Image 6" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    st.write("**2. Tool Usage:**")
    st.write("Once the file is unzipped, you are now ready to input the extracted file.")
    st.write("a. Go the BizDev Automation Hub Streamlit App and select the *Google Calendar Event Extraction tool*.")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{gc_7_base64}" alt="Instruction Image 7" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("b. Upload the extracted file from Google Calendar into the file uploader or alternatively you can click the *Browse files* button to select the file.")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{gc_8_base64}" alt="Instruction Image 8" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("c. Once the file is uploaded, the extracted data will be displayed in the table below.")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{gc_9_base64}" alt="Instruction Image 9" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("d. You can also filter events in the *Filter Events* section.")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{gc_10_base64}" alt="Instruction Image 10" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("e. After filtering, you can export the filtered data to a CSV file by clicking the *Export Filtered Data* button.")
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{gc_11_base64}" alt="Instruction Image 11" style="width: 100%; max-width: 900px; margin-top: 5px; margin-bottom: 20px;">
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")
st.write("")

uploaded_file = st.file_uploader("Upload Extracted File from Google Calendar", type=["ics"])

# Helper Functions (previously defined functions remain the same)
def clean_ics_description(description):
    """Clean and format event descriptions from ICS file."""
    description = str(description)
    description = html.unescape(description)
    description = re.sub(r'<a [^>]*href="([^"]+)".*?>', r'"\1" ', description)
    description = re.sub(r'<[^>]+>', '', description)
    description = re.sub(r'(?<!\n)\n+', '\n', description)
    description = re.sub(r'-::~:~:.*?::-', '', description, flags=re.DOTALL)
    description = re.sub(r'\n+', '\n', description)
    description = re.sub(r'\s+\n', '\n', description)
    return description.strip()

def clean_organizer_name(organizer_string):
    """Extract organizer name from the ICS organizer field."""
    if pd.isna(organizer_string):
        return organizer_string

    try:
        organizer_string = str(organizer_string)
        start_marker = 'CN='
        end_marker = ':mailto:'

        if start_marker in organizer_string and end_marker in organizer_string:
            start_pos = organizer_string.index(start_marker) + len(start_marker)
            end_pos = organizer_string.index(end_marker)
            return organizer_string[start_pos:end_pos]

        return organizer_string
    except Exception as e:
        print(f"Error processing organizer: {organizer_string}")
        return organizer_string

def clean_attendee_with_status(attendee):
    """Extract attendee name and status from the ICS attendee field."""
    try:
        attendee_string = str(attendee)
        start_name_idx = attendee_string.find('CN=') + 3
        end_name_idx = (
            attendee_string.find('@', start_name_idx)
            if '@' in attendee_string[start_name_idx:start_name_idx + 50]
            else min(
                idx
                for idx in [
                    attendee_string.find(';CUTYPE', start_name_idx),
                    attendee_string.find(':mailto:', start_name_idx)
                ] if idx > -1
            )
        )
        name = attendee_string[start_name_idx:end_name_idx].replace('.', ' ').title()

        status_start = attendee_string.find('PARTSTAT=') + 9
        status_end = (
            attendee_string.find(';', status_start)
            if attendee_string.find(';', status_start) > -1
            else attendee_string.find(':', status_start)
        )
        status = attendee_string[status_start:status_end] if status_start > 8 else "UNKNOWN"

        return f"{name}: {status}"
    except:
        return str(attendee)

def clean_attendees_list_with_status(attendees):
    """Clean and format the attendees list."""
    if isinstance(attendees, (list, tuple)):
        cleaned_entries = [clean_attendee_with_status(attendee) for attendee in attendees]
        return ', '.join(cleaned_entries)
    return str(attendees)

def process_large_ics_file(file_path, chunk_size=1000):
    """
    Process large ICS files in chunks to manage memory usage.
    
    :param file_path: Path to the ICS file
    :param chunk_size: Number of events to process in each chunk
    :return: List of dictionaries containing event data
    """
    data = []
    
    # Use progress bar for user feedback
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            calendar_data = f.read()
        
        # Parse the entire calendar to get total events
        total_calendar = Calendar(calendar_data)
        total_events = len(list(total_calendar.events))
        status_text.text(f"Total events found: {total_events}")
        
        # Create a new calendar parser for chunked processing
        calendar = Calendar(calendar_data)
        events_iterator = iter(calendar.events)
        
        processed_events = 0
        while True:
            # Collect a chunk of events
            chunk_events = []
            for _ in range(chunk_size):
                try:
                    event = next(events_iterator)
                    chunk_events.append(event)
                except StopIteration:
                    break
            
            # If no more events, break the loop
            if not chunk_events:
                break
            
            # Process this chunk of events
            for event in chunk_events:
                attendees = [str(attendee) for attendee in event.attendees] if event.attendees else []
                data.append({
                    "Event Name": event.name,
                    "Start": event.begin,
                    "End": event.end,
                    "Description": event.description,
                    "Location": event.location,
                    "Organizer": str(event.organizer) if event.organizer else None,
                    "Attendees": attendees,
                })
            
            # Update progress
            processed_events += len(chunk_events)
            progress = min(processed_events / total_events, 1.0)
            progress_bar.progress(progress)
            status_text.text(f"Processed {processed_events}/{total_events} events")
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        return data
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return []

# Main Logic
if uploaded_file is not None:
    # Save uploaded file temporarily
    with open("temp_calendar.ics", "wb") as f:
        f.write(uploaded_file.getvalue())
    
    # Process file in chunks
    data = process_large_ics_file("temp_calendar.ics")
    
    if data:
        df = pd.DataFrame(data)
        pd.set_option('display.max_colwidth', None)

        # Convert datetime objects
        df['Start'] = df['Start'].apply(lambda x: x.datetime if isinstance(x, arrow.Arrow) else x)
        df['End'] = df['End'].apply(lambda x: x.datetime if isinstance(x, arrow.Arrow) else x)

        # Display extracted data
        st.write("Extracted Google Calendar Data")
        st.dataframe(data=df, use_container_width=True, hide_index=True)

        # Clean data
        df['Description'] = df['Description'].apply(clean_ics_description)
        df['Organizer'] = df['Organizer'].apply(clean_organizer_name)
        df['Attendees'] = df['Attendees'].apply(clean_attendees_list_with_status)

        # Display cleaned data
        st.write("Cleaned Google Calendar Data")
        st.dataframe(data=df, use_container_width=True, hide_index=True)

        # Filter Events Interactive Section (same as before)
        def filter_events_interactive(df):
            st.subheader("Filter Events")
            start_date = st.text_input("Start date (YYYY-MM-DD):", "")
            end_date = st.text_input("End date (YYYY-MM-DD):", "")
            attendee_name = st.text_input("Enter attendee name (or leave blank to skip):", "").strip()
            status = st.text_input("Enter status (e.g., ACCEPTED, DECLINED, NEEDS-ACTION, or leave blank to include all):", "").strip().upper()

            if start_date and end_date:
                try:
                    start_date = pd.to_datetime(start_date).tz_localize('UTC')
                    end_date = pd.to_datetime(end_date).tz_localize('UTC')
                    filtered_df = df[(df['Start'] >= start_date) & (df['End'] <= end_date)]

                    if attendee_name:
                        attendee_name = attendee_name.title()
                        if status:
                            filtered_df = filtered_df[filtered_df['Attendees'].str.contains(
                                f"{attendee_name}: {status}", case=False, na=False)]
                        else:
                            filtered_df = filtered_df[filtered_df['Attendees'].str.contains(
                                attendee_name, case=False, na=False)]

                    st.write("Filtered Events")
                    st.dataframe(filtered_df.sort_values(by=['Start', 'End'], ascending=[True, True]))
                except ValueError:
                    st.error("Invalid date format! Please use YYYY-MM-DD.")
            else:
                st.warning("Please enter both start and end dates.")

        filter_events_interactive(df)
    else:
        st.error("Failed to process the file. Please check the file format and try again.")
else:
    st.warning("Please upload a file to proceed.")