import streamlit as st
import mysql.connector
import project, user_management, stage
from db_utils import get_database_connection
import design
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
    else:
        st.warning("Anda tidak memiliki akses ke halaman ini.")

page_functions = {
    'main_page'     : main_page,
    'project'       : project.main_page,
    'create_project_page' : project.create_project_page,
    'user_management': user_management.main_page,
    'stage'         : stage.main_page,
    'design_page'   : design.main_page,
    'secure_sdlc_page' : design.secure_sdlc_page,
    'threat_model_page' : design.threat_model_page,
    'history_secure_sdlc' : lambda: design.history_secure_sdlc(st.session_state.id_detail_design),
    'history_threat_model' : lambda: design.history_threat_model(st.session_state.id_detail_design)
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