import streamlit as st
import pandas as pd
from db_utils import get_database_connection
import design


def show_button(button_name, user_role):
    if user_role == 'admin' or user_role == button_name.lower():
        if st.button(button_name, use_container_width=True):
            if button_name.lower() == 'design':
                st.session_state.page = 'design_page'
            else:
                st.write(button_name)


def get_all_projects():
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT 
            p.project_id,
            p.nama_project,
            u.username as PIC,
            ss_prev.deskripsi as previous,
            ssd.deskripsi as current,
            ss_next.deskripsi as next,
            ed.evidance as evidence,
            ed.tgl as remarks
        FROM 
            project p
        LEFT JOIN 
            user u ON p.pic = u.id
        LEFT JOIN 
            evidance_design ed ON p.project_id = ed.id_detail_design
        LEFT JOIN
            status_step ss_prev ON p.previous = ss_prev.id_status_detail
        LEFT JOIN
            status_step_detail ssd ON p.current = ssd.id_status_detail
        LEFT JOIN
            status_step ss_next ON p.next = ss_next.id_status_detail
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def display_all_projects(projects):
    if projects:
        df = pd.DataFrame(projects)
        columns_order = ['nama_project', 'PIC', 'previous', 'current', 'next', 'remarks', 'evidence']
        df = df[columns_order]
        st.write("All Projects:")
        st.dataframe(df, hide_index=True)
    else:
        st.write("No projects found.")

def main_page():
    if st.button('Back'):
        st.session_state['page'] = 'main_page'
    st.subheader('Stage DevSecOps Page')

    user_role = st.session_state.get('user', {}).get('role', '')

    stages = ["Design", "Develop", "Build", "Test", "Deploy", "Monitor"]

    for stage in stages:
        show_button(stage, user_role)
    if user_role == 'admin':
        projects = get_all_projects()
        display_all_projects(projects)


    