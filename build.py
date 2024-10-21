import streamlit as st
import pandas as pd
from db_utils import get_database_connection 
from db_utils import get_database_connection,  upload_file_to_ftp, download_file_from_ftp, render_page, render_table_headers, render_table_row, display_history

def main_page():
    if st.button('Back'):
        st.session_state.page = 'stage'
        st.rerun()
        
    st.title("Build page")
    st.markdown('---')

    col1, col2, col3, col4 = st.columns(4)
    if col1.button('IAST', use_container_width=True):
        st.session_state.page = 'iast_page'
    if col2.button('SAST', use_container_width=True):
        st.session_state.page = 'sast_page'
    if col3.button('Secret Management', use_container_width=True):
        st.session_state.page = 'secret_management_page'
    if col4.button('SCA', use_container_width=True):
        st.session_state.page = 'sca_page'

def iast_page():
    render_page('b-1', 'IAST', 'iast', 'build')

def sast_page():
    render_page('b-2', 'SAST', 'sast', 'build')

def secret_management_page():
    render_page('b-3', 'Secret Management', 'secret_management', 'build')

def sca_page():
    render_page('b-4', 'SCA', 'sca', 'build')

def history_iast(id_detail_build):
    display_history(id_detail_build, 'IAST', 'iast_page', 'iast', 'build')

def history_sast(id_detail_build):
    display_history(id_detail_build, 'SAST', 'sast_page', 'sast', 'build')

def history_secret_management(id_detail_build):
    display_history(id_detail_build, 'Secret Management', 'secret_management_page', 'secret_management', 'build')

def history_sca(id_detail_build):
    display_history(id_detail_build, 'SCA', 'sca_page', 'sca', 'build')
