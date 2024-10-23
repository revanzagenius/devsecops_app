import streamlit as st
from develop import history_secure_coding, history_code_authentication, history_repository_access_control
from build import history_sast, history_secret_management, history_sca
import build
from deploy import history_hardening, history_config
from test import history_pentest, history_dast
import test
from design import history_secure_sdlc, history_threat_model
from monitor import history_monitor,history_rasp, history_audit, history_patch


def main_page():
    # Periksa apakah stage disimpan di session state
    if 'stage' in st.session_state:
        stage = st.session_state['stage']
        # Periksa apakah id_detail untuk stage tersebut ada di session state

        if f'id_detail_{stage}' in st.session_state:
            id_detail = st.session_state[f'id_detail_{stage}']
            id_jenis = st.session_state['jenis_id']
            if id_jenis == 'b-1':
                build.history_iast(id_detail)
            elif id_jenis == 'b-2':
                history_sast(id_detail)
            elif id_jenis == 'b-3':
                history_secret_management(id_detail)
            elif id_jenis == 'b-4':
                history_sca(id_detail)
            elif id_jenis == 'dep-1':
                history_hardening(id_detail)
            elif id_jenis == 'dep-2':
                history_config(id_detail)
            elif id_jenis == 'devs-1':
                history_secure_coding(id_detail)
            elif id_jenis == 'devs-2':
                history_code_authentication(id_detail)
            elif id_jenis == 'devs-3':
                history_repository_access_control(id_detail)
            elif id_jenis == 'ds-1':
                history_secure_sdlc(id_detail)
            elif id_jenis == 'ds-2':
                history_threat_model(id_detail)
            elif id_jenis == 'om-1':
                history_rasp(id_detail)
            elif id_jenis == 'om-2':
                history_audit(id_detail)
            elif id_jenis == 'om-3':
                history_monitor(id_detail)
            elif id_jenis == 'om-4':
                history_patch(id_detail)
            elif id_jenis == 't-1':
                test.history_iast(id_detail)
            elif id_jenis == 't-2':
                history_pentest(id_detail)
            elif id_jenis == 't-3':
                history_dast(id_detail)
            else:
                st.write("ID Jenis tidak dikenal.")
        else:
            st.write("ID Detail tidak ditemukan.")
    else:
        st.write("Stage tidak ditemukan.")
