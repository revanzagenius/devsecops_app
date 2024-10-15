import streamlit as st
import pandas as pd
from db_utils import get_database_connection

def main_page():
    if st.button('Back'):
        st.session_state['page'] = 'main_page'
    st.subheader('User Management Page')

    # Tambahkan tombol untuk menambah user baru
    if st.button('Add New User'):
        st.session_state['add_user'] = True

    if 'add_user' in st.session_state and st.session_state['add_user']:
        add_new_user()
    else:
        display_users()

def display_users():
    # Ambil data dari database
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, username, email, role FROM user"  # Tidak menampilkan password untuk keamanan
    cursor.execute(query)
    users = cursor.fetchall()
    cursor.close()
    conn.close()

    # Buat DataFrame
    df = pd.DataFrame(users)

    # Tampilkan tabel
    st.dataframe(df, use_container_width=True, hide_index=True)

def add_new_user():
    st.subheader("Add New User")
    with st.form("add_user_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["admin", "design", "develop", "build", "test", "deploy", "monitor", "pm", "ciso"])
        
        if st.form_submit_button("Add User"):
            conn = get_database_connection()
            cursor = conn.cursor()
            query = "INSERT INTO user (username, email, password, role) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (username, email, password, role))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("User added successfully!")
            st.session_state['add_user'] = False
            st.rerun()

if __name__ == "__main__":
    if 'add_user' not in st.session_state:
        st.session_state['add_user'] = False
    main_page()