import ftplib
import streamlit as st
import pandas as pd
from db_utils import get_database_connection 
from datetime import datetime
import streamlit as st
import random
import string
from datetime import datetime
import os
from db_utils import get_database_connection,  upload_file_to_ftp, download_file_from_ftp, render_page, render_table_headers, render_table_row, display_history

def main_page():
    if st.button('Back'):
        st.session_state.page = 'stage'
        st.rerun()
        
    st.title("Develop page")
    st.markdown('---')

    col1, col2, col3 = st.columns(3)
    if col1.button('Secure Coding', use_container_width=True):
        st.session_state.page = 'secure_coding_page'
    if col2.button('Code Authentication', use_container_width=True):
        st.session_state.page = 'code_authentication_page'
    if col3.button('Repository Access Control', use_container_width=True):
        st.session_state.page = 'repository_access_control_page'

def history_secure_coding(id_detail_develop):
    display_history(id_detail_develop, 'Secure SDLC', 'secure_coding_page', 'secure_coding', 'develop')

def history_code_authentication(id_detail_develop):
    display_history(id_detail_develop, 'Code Authentication', 'code_authentication_page', 'code_authentication', 'develop')

def history_repository_access_control(id_detail_develop):
    display_history(id_detail_develop, 'Repository Access Control', 'repository_access_control_page', 'repository_access_control', 'develop')

def secure_coding_page():
    render_page('devs-1', 'Secure Coding', 'secure_coding', 'develop')

def code_authentication_page():
    render_page('devs-2', 'Code Authentication', 'code_authentication', 'develop')

def repository_access_control_page():
    render_page('devs-3', 'Repository Access Control', 'repository_access_control', 'develop')

  
