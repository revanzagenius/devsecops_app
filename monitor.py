import streamlit as st
import pandas as pd
from db_utils import get_database_connection 
from db_utils import get_database_connection,  upload_file_to_ftp, download_file_from_ftp, render_page, render_table_headers, render_table_row, display_history

def main_page():
    if st.button('Back'):
        st.session_state.page = 'stage'
        st.rerun()
        
    st.title("Monitor / Operate page")
    st.markdown('---')

    col1, col2, col3, col4 = st.columns(4)
    if col1.button('RASP', use_container_width=True):
        st.session_state.page = 'rasp_page'
    if col2.button('Audit', use_container_width=True):
        st.session_state.page = 'audit_page'
    if col3.button('Monitor', use_container_width=True):
        # st.session_state.page = 'monitor_page'
        st.write('button_name')
    if col4.button('Patch', use_container_width=True):
        st.session_state.page = 'patch_page'

def rasp_page():
    render_page('om-1', 'RASP', 'rasp', 'monitor')

def audit_page():
    render_page('om-2', 'Audit', 'audit', 'monitor')

def monitor_page():
    render_page('om-3', 'Monitor', 'monitor', 'monitor')

def patch_page():
    render_page('om-4', 'Patch', 'patch', 'monitor')

def history_rasp(id_detail_monitor):
    display_history(id_detail_monitor, 'RASP', 'rasp_page', 'rasp', 'monitor')

def history_audit(id_detail_monitor):
    display_history(id_detail_monitor, 'Audit', 'audit_page', 'audit', 'monitor')

def history_monitor(id_detail_monitor):
    display_history(id_detail_monitor, 'Monitor', 'monitor_page', 'monitor', 'monitor')

def history_patch(id_detail_monitor):
    display_history(id_detail_monitor, 'Patch', 'patch_page', 'patch', 'monitor')
