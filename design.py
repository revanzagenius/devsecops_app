
import ftplib
import streamlit as st
import pandas as pd
from db_utils import get_database_connection 
from datetime import datetime
import streamlit as st
from datetime import datetime
from db_utils import get_database_connection,  upload_file_to_ftp, download_file_from_ftp, render_page, render_table_headers, render_table_row, display_history

def main_page():
    if st.button('Back'):
        st.session_state.page = 'stage'
        st.rerun()
        
    st.title("Design page")
    st.markdown('---')

    col1, col2 = st.columns(2)
    if col1.button('Secure SDLC', use_container_width=True):
        st.session_state.page = 'secure_sdlc_page'
    if col2.button('Threat Model', use_container_width=True):
        st.session_state.page = 'threat_model_page'


def history_secure_sdlc(id_detail_design):
    display_history(id_detail_design, 'Secure SDLC', 'secure_sdlc_page', 'secure_sdlc', 'design')

def history_threat_model(id_detail_design):
    display_history(id_detail_design, 'Threat Model', 'threat_model_page', 'threat_model', 'design')


def secure_sdlc_page():
    render_page('ds-1', 'Secure SDLC', 'secure_sdlc', 'design')

def threat_model_page():
    render_page('ds-2', 'Threat Model', 'threat_model', 'design')

