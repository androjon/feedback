import streamlit as st
import json
import datetime
from google.cloud import storage
import os

# Sätt miljövariabel för Google Cloud-autentisering
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "din-nyckel-fil.json"

# Konfiguration för GCS
BUCKET_NAME = "din-bucket-namn"
BLOB_NAME = "feedback.json"

def load_feedback():
    """Ladda befintlig feedback från GCS."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(BLOB_NAME)

    if blob.exists():
        data = blob.download_as_text()
        return json.loads(data)
    else:
        return []

def save_feedback(feedback_data):
    """Spara feedback till GCS."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(BLOB_NAME)
    blob.upload_from_string(json.dumps(feedback_data, indent=2), content_type='application/json')

# Streamlit UI
st.title("Välkommen till återkopplingsappen!")

if 'form_visible' not in st.session_state:
    st.session_state.form_visible = False

if st.button("Ge återkoppling"):
    st.session_state.form_visible = True

# Visa formuläret i sidebar om knappen tryckts
if st.session_state.form_visible:
    with st.sidebar:
        st.header("Återkoppling")
        question_1 = st.text_input("Hur upplevde du appen?")
        question_2 = st.selectbox("Skulle du rekommendera den?", ["Ja", "Nej", "Kanske"])

        if st.button("Spara"):
            # Ladda gammal feedback, lägg till ny
            feedback = load_feedback()
            new_entry = {
                "tid": datetime.datetime.now().isoformat(),
                "upplevelse": question_1,
                "rekommendation": question_2
            }
            feedback.append(new_entry)
            save_feedback(feedback)
            st.success("Tack för din återkoppling!")

            # Dölj formuläret
            st.session_state.form_visible = False
