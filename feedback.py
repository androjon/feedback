import streamlit as st
import json
import datetime
from google.cloud import storage
from google.oauth2 import service_account  # ✅ Lägg till denna

@st.cache_data
def import_data(filename):
    with open(filename) as file:
        content = file.read()
    output = json.loads(content)
    return output

def fetch_data():
    st.session_state.occupationdata = import_data("all_valid_occupations_with_info_v25.json")
    for key, value in st.session_state.occupationdata.items():
        st.session_state.valid_occupations[value["preferred_label"]] = key
    st.session_state.valid_occupation_names = sorted(list(st.session_state.valid_occupations.keys()))

def show_initial_information():
    st.logo("af-logotyp-rgb-540px.jpg")
    st.title(":primary[Yrkesinfo]")
    initial_text = "Ett försöka att erbjuda information/stöd för arbetsförmedlare när det kommer till att välja <em>rätt</em> yrke och underlätta relaterade informerade bedömningar och beslut när det kommer till GYR-Y (Geografisk och yrkesmässig rörlighet - Yrke). Informationen är taxonomi-, statistik- och annonsdriven. 1180 yrkesbenämningar bedöms ha tillräckligt annonsunderlag för pålitliga beräkningar. Resterande yrkesbenämningar kompletteras med beräkningar på yrkesgruppsnivå."
    st.markdown(f"<p style='font-size:12px;'>{initial_text}</p>", unsafe_allow_html=True)

def initiate_session_state():
    if "valid_occupations" not in st.session_state:
        st.session_state.valid_occupations = {}
        st.session_state.form_visible = False

    credentials_dict = st.secrets["gcp_service_account"]
    st.session_state.credentials = service_account.Credentials.from_service_account_info(credentials_dict)

def load_feedback():
    """Ladda befintlig feedback från GCS."""
    storage_client = storage.Client(credentials = st.session_state.credentials, project = st.session_state.credentials.project_id)  # ✅ Använd credentials
    bucket = storage_client.bucket("androjons_bucket")
    blob = bucket.blob("feedback.json")

    if blob.exists():
        data = blob.download_as_text()
        return json.loads(data)
    else:
        return []

def save_feedback(feedback_data):
    """Spara feedback till GCS."""
    storage_client = storage.Client(credentials = st.session_state.credentials, project = st.session_state.credentials.project_id)  # ✅ Använd credentials
    bucket = storage_client.bucket("androjons_bucket")
    blob = bucket.blob("feedback.json")
    json_string = json.dumps(feedback_data, indent = 2, ensure_ascii = False)
    json_bytes = json_string.encode('utf-8')  # ✅ Konvertera till bytes
    blob.upload_from_string(json_bytes, content_type='application/json; charset=utf-8') 

def create_feedback(selected_occupation):
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
                "rekommendation": question_2,
                "selected_occupation": selected_occupation
            }
            feedback.append(new_entry)
            save_feedback(feedback)
            #st.success("Tack för din återkoppling!")

            # Dölj formuläret
            st.session_state.form_visible = False
            st.rerun()

def choose_occupation_name():
    show_initial_information()
    #yrkesval = .empty()
    selected_occupation_name = st.selectbox(
        "Välj en yrkesbenämning",
        (st.session_state.valid_occupation_names), placeholder = "", index = None)
    if selected_occupation_name:
        id_selected_occupation = st.session_state.valid_occupations.get(selected_occupation_name)
        st.write(f"{selected_occupation_name} - id: {id_selected_occupation}")

    if st.button("Ge återkoppling"):
        st.session_state.form_visible = True

    if st.session_state.form_visible == True:
        create_feedback(selected_occupation_name)

def main ():
    initiate_session_state()
    fetch_data()
    choose_occupation_name()
    
if __name__ == '__main__':
    main ()
