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
        
    st.title("Test page")
    st.markdown('---')

    col1, col2, col3 = st.columns(3)
    if col1.button('IAST', use_container_width=True):
        st.session_state.page = 'iast_page'
    if col2.button('Pentest', use_container_width=True):
        st.session_state.page = 'pentest_page'
    if col3.button('DAST', use_container_width=True):
        st.session_state.page = 'dast_page'

def history_iast(id_detail_test):
    display_history(id_detail_test, 'IAST', 'iast_page', 'iast', 'test')

def history_pentest(id_detail_test):
    display_history(id_detail_test, 'Pentest', 'pentest_page', 'pentest', 'test')

def history_dast(id_detail_test):
    display_history(id_detail_test, 'DAST', 'dast_page', 'dast', 'test')

def iast_page():
    render_page('t-1', 'IAST', 'iast', 'test')

def pentest_page():
    render_page('t-2', 'Pentest', 'pentest', 'test')

def dast_page():
    render_page('t-3', 'DAST', 'dast', 'test')

  
