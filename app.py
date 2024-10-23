import streamlit as st
import mysql.connector
import project, user_management, stage, ciso
from db_utils import get_database_connection
import design, develop, build, test, deploy, monitor, history_ciso
st.set_page_config(layout='wide')

def logout():
    st.session_state.clear()  

# Fungsi untuk koneksi ke database


# Fungsi untuk verifikasi login
def verify_login(username, password):
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM user WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))
    user = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return user

def navigate_to(page):
    st.session_state['page'] = page

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = verify_login(username, password)
        if user:
            st.session_state['user'] = user
            st.session_state['logged_in'] = True
            st.success("Login berhasil!")
            st.session_state['user_role'] = user.get('role', '')
            st.session_state['user_id'] = user.get('id', '')
            st.session_state['page'] = 'main_page'  # Set page to main_page after successful login
        else:
            st.error("Username atau password salah!")

def main_page():
    user = st.session_state.get('user', {})
    role = user.get('role', '')

    

    if role == 'admin':
        if st.button("Logout"):
            logout()
        col1, col2, col3 = st.columns(3)
        if col1.button('Project', use_container_width=True):
            navigate_to("project")
        if col2.button('User Management', use_container_width=True):
            navigate_to("user_management")
        if col3.button('Devsecops Stage', use_container_width=True):
            navigate_to("stage")
    elif role == 'pm':
        if st.button("Logout"):
            logout()
        col1, col2 = st.columns(2)
        if col1.button('Project', use_container_width=True):
            navigate_to("project")
        if col2.button('Devsecops Stage', use_container_width=True):
            navigate_to("stage")
    elif role in ['design', 'develop', 'build', 'test', 'deploy', 'monitor']:
        if st.button("Logout"):
            logout()
        col1, = st.columns(1)
        if col1.button('Devsecops Stage', use_container_width=True):
            navigate_to("stage")
    elif role == 'ciso':
        col1, = st.columns(1)
        if col1.button('CISO', use_container_width=True):
            navigate_to("ciso")
    else:
        st.warning("Anda tidak memiliki akses ke halaman ini.")

page_functions = {
    'main_page'     : main_page,
    'ciso'       : ciso.main_page,
    'project'       : project.main_page,
    'create_project_page' : project.create_project_page,
    'edit_project_page' : project.edit_project_page,
    'edit_project_status' : project.edit_status_page,
    'user_management': user_management.main_page,
    'stage'         : stage.main_page,
    'design_page'   : design.main_page,
    'secure_sdlc_page' : design.secure_sdlc_page,
    'threat_model_page' : design.threat_model_page,
    'history_secure_sdlc' : lambda: design.history_secure_sdlc(st.session_state.id_detail_design),
    'history_threat_model' : lambda: design.history_threat_model(st.session_state.id_detail_design),
    'develop_page'   : develop.main_page,
    'secure_coding_page'   : develop.secure_coding_page,
    'code_authentication_page'   : develop.code_authentication_page,
    'repository_access_control_page'   : develop.repository_access_control_page,
    'history_secure_coding' : lambda: develop.history_secure_coding(st.session_state.id_detail_develop),
    'history_code_authentication' : lambda: develop.history_code_authentication(st.session_state.id_detail_develop),
    'history_repository_access_control' : lambda: develop.history_repository_access_control(st.session_state.id_detail_develop),
    'build_page'   : build.main_page,
    'iast_page'   : build.iast_page,
    'sast_page'   : build.sast_page,
    'secret_management_page'   : build.secret_management_page,
    'sca_page'   : build.sca_page,
    'history_iast' : lambda: build.history_iast(st.session_state.id_detail_build),
    'history_sast' : lambda: build.history_sast(st.session_state.id_detail_build),
    'history_secret_management' : lambda: build.history_secret_management(st.session_state.id_detail_build),
    'history_sca' : lambda: build.history_sca(st.session_state.id_detail_build),
    'test_page'   : test.main_page,
    'iast_page'   : test.iast_page,
    'pentest_page'   : test.pentest_page,
    'dast_page'   : test.dast_page,
    'history_iast' : lambda: test.history_iast(st.session_state.id_detail_test),
    'history_pentest' : lambda: test.history_pentest(st.session_state.id_detail_test),
    'history_dast' : lambda: test.history_dast(st.session_state.id_detail_test),
    'deploy_page'   : deploy.main_page,
    'hardening_page'   : deploy.hardening_page,
    'config_page'   : deploy.config_page,
    'history_hardening' : lambda: deploy.history_hardening(st.session_state.id_detail_deploy),
    'history_config' : lambda: deploy.history_config(st.session_state.id_detail_deploy),
    'monitor_page'   : monitor.main_page,
    'rasp_page'   : monitor.rasp_page,
    'audit_page'   : monitor.audit_page,
    'monitor2_page'   : monitor.monitor2_page,
    'patch_page'   : monitor.patch_page,
    'history_rasp' : lambda: monitor.history_rasp(st.session_state.id_detail_monitor),
    'history_audit' : lambda: monitor.history_audit(st.session_state.id_detail_monitor),
    'history_monitor2' : lambda: monitor.history_monitor(st.session_state.id_detail_monitor),
    'history_patch' : lambda: monitor.history_patch(st.session_state.id_detail_monitor),
    'history_ciso' : history_ciso.main_page

}


def router():
    if not st.session_state.get('logged_in', False):
        login_page()
    else:
        page_function = page_functions.get(st.session_state.get("page", "main_page"), main_page)
        page_function()

if __name__ == "__main__":
    if 'page' not in st.session_state:
        st.session_state['page'] = 'main_page'
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    router()