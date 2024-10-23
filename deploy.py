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
        
    st.title("Deploy page")
    st.markdown('---')

    col1, col2 = st.columns(2)
    if col1.button('Hardening', use_container_width=True):
        st.session_state.page = 'hardening_page'
    if col2.button('Config', use_container_width=True):
        st.session_state.page = 'config_page'


def history_hardening(id_detail_deploy):
    display_history(id_detail_deploy, 'Hardening', 'hardening_page', 'hardening', 'deploy')

def history_config(id_detail_deploy):
    display_history(id_detail_deploy, 'Config', 'config_page', 'config', 'deploy')


def hardening_page():
    render_page('dep-1', 'Hardening', 'hardening', 'deploy')

def config_page():
    render_page('dep-2', 'Config', 'config', 'deploy')
