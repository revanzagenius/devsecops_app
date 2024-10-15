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
from db_utils import get_database_connection,  upload_file_to_ftp, download_file_from_ftp, render_page, render_table_headers, render_table_row, display_history, render_table_row_ciso

def main_page():
    if st.button("Logout"):
        st.session_state.clear()  
    st.subheader('CISO Page')

    projects = get_all_projects()
    display_all_projects(projects)

# def get_all_projects():
#     conn = get_database_connection()
#     cursor = conn.cursor(dictionary=True)
#     try:
#         query = """
#         SELECT 
#             p.project_id,
#             p.nama_project as nama_project, 
#             u.username as PIC,
#             ss_prev.deskripsi as previous,
#             ssd.deskripsi as current,
#             ss_next.deskripsi as next,
#             ed.evidance as evidence,
#             ed.tgl as remarks
#         FROM 
#             project p
#         LEFT JOIN 
#             user u ON p.pic = u.id
#         LEFT JOIN 
#             evidance_design ed ON p.project_id = ed.id_detail_design
#         LEFT JOIN
#             status_step ss_prev ON p.previous = ss_prev.id_status_detail
#         LEFT JOIN
#             status_step_detail ssd ON p.current = ssd.id_status_detail
#         LEFT JOIN
#             status_step ss_next ON p.next = ss_next.id_status_detail
#         """
#         cursor.execute(query)
#         return cursor.fetchall()
#     except Exception as e:
#         st.error(f"An error occurred: {e}")
#         return []
#     finally:
#         cursor.close()
#         conn.close()

# def display_all_projects(projects):
#     st.write("All Projects:")
#     st.write('---')
#     col1, col2, col3, col4, col5, col6 = st.columns([1,3,3,3,3,3])
#     with col1:
#         st.write('No')
#     with col2:
#         st.write('Nama Project')
#     with col3:
#         st.write('PIC Project')
#     with col4:
#         st.write('Previous Stage')
#     with col5:
#         st.write('Current Stage')
#     with col6:
#         st.write('Next Stage')
#     st.write('---')
#     if projects:
#         for idx, project in enumerate(projects, start=1):
#             col1, col2, col3, col4, col5, col6 = st.columns([1,3,3,3,3,3])
#             with col1:
#                 st.write(idx)
#             with col2:
#                 st.write(project['nama_project'])
#             with col3:
#                 st.write(project['PIC'])
#             with col4:
#                 st.write(project['previous'])
#             with col5:
#                 st.write(project['current'])
#             with col6:
#                 st.write(project['next'])

def get_all_projects():
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT 
            p.project_id,
            p.nama_project as nama_project, 
            u.username as PIC,
            ss_prev.deskripsi as previous,
            ssd.deskripsi as current,
            ss_next.deskripsi as next,
            ed.evidance as evidence,
            ed.tgl as remarks,
            d.design_id,
            dv.develop_id
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
        LEFT JOIN
            design d ON p.design_id = d.design_id
        LEFT JOIN
            develop dv ON p.develop_id = dv.develop_id
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
    st.write("All Projects:")
    st.write('---')
    col1, col2, col3, col4, col5, col6 = st.columns([1,3,3,3,3,3])
    with col1:
        st.write('No')
    with col2:
        st.write('Nama Project')
    with col3:
        st.write('PIC Project')
    with col4:
        st.write('Previous Stage')
    with col5:
        st.write('Current Stage')
    with col6:
        st.write('Next Stage')
    st.write('---')
    if projects:
        for idx, project in enumerate(projects, start=1):
            col1, col2, col3, col4, col5, col6 = st.columns([1,3,3,3,3,3])
            with col1:
                st.write(idx)
            with col2:
                st.write(project['nama_project'])
            with col3:
                st.write(project['PIC'])
            with col4:
                st.write(project['previous'])
            with col5:
                st.write(project['current'])
            with col6:
                st.write(project['next'])
            with st.expander(f"Detail {project['nama_project']}"):
                st.write('Design')
                conn = get_database_connection()
                cursor = conn.cursor(dictionary=True)
                query = """
                SELECT 
                    p.nama_project, 
                    ud.username AS pic_design, 
                    u.username AS pm, 
                    dd.id_detail_design,
                    COALESCE(ed.remarks, '-') AS remarks,
                    COALESCE(ed.evidance, '-') AS evidance,
                    COALESCE(ed.tgl, '-') AS tgl,
                    COALESCE(ss.deskripsi, '-') AS status
                FROM detail_design dd
                LEFT JOIN design d ON dd.id_design = d.design_id
                LEFT JOIN project p ON d.design_id = p.design_id
                LEFT JOIN user ud ON d.pic = ud.id
                LEFT JOIN user u ON p.pic = u.id
                LEFT JOIN (
                    SELECT id_detail_design, remarks, evidance, tgl, status_id
                    FROM evidance_design ed1
                    WHERE (id_detail_design, tgl) IN (
                        SELECT id_detail_design, MAX(tgl)
                        FROM evidance_design
                        GROUP BY id_detail_design
                    )
                ) ed ON dd.id_detail_design = ed.id_detail_design
                LEFT JOIN status_stage ss ON ed.status_id = ss.status_id
                WHERE dd.id_design = %s AND p.project_id = %s
                """
                cursor.execute(query, (project['design_id'], project['project_id']))
                results_design = cursor.fetchall()
                render_table_headers()
                st.write("---")
                if results_design:
                    for idx, row in enumerate(results_design):
                        render_table_row_ciso(row, {1: 'Pending', 2: 'On Process', 3: 'Complete'}, idx, 'design', 'design')
                else:
                    st.write("Tidak ada data yang ditemukan.")
                st.write('---')
                cursor.close()
                conn.close()
                
                st.write('Develop')
                conn = get_database_connection()
                cursor = conn.cursor(dictionary=True)
                query = """
                SELECT 
                    p.nama_project, 
                    ud.username AS pic_develop, 
                    u.username AS pm, 
                    dd.id_detail_develop,
                    COALESCE(ed.remarks, '-') AS remarks,
                    COALESCE(ed.evidance, '-') AS evidance,
                    COALESCE(ed.tgl, '-') AS tgl,
                    COALESCE(ss.deskripsi, '-') AS status
                FROM detail_develop dd
                LEFT JOIN develop d ON dd.id_develop = d.develop_id
                LEFT JOIN project p ON d.develop_id = p.develop_id
                LEFT JOIN user ud ON d.pic = ud.id
                LEFT JOIN user u ON p.pic = u.id
                LEFT JOIN (
                    SELECT id_detail_develop, remarks, evidance, tgl, status_id
                    FROM evidance_develop ed1
                    WHERE (id_detail_develop, tgl) IN (
                        SELECT id_detail_develop, MAX(tgl)
                        FROM evidance_develop
                        GROUP BY id_detail_develop
                    )
                ) ed ON dd.id_detail_develop = ed.id_detail_develop
                LEFT JOIN status_stage ss ON ed.status_id = ss.status_id
                WHERE dd.id_develop = %s AND p.project_id = %s
                """
                cursor.execute(query, (project['develop_id'], project['project_id']))
                results_develop = cursor.fetchall()
                render_table_headers()
                st.write("---")
                if results_develop:
                    for idx, row in enumerate(results_develop):
                        render_table_row_ciso(row, {1: 'Pending', 2: 'On Process', 3: 'Complete'}, idx, 'develop', 'develop')
                else:
                    st.write("Tidak ada data yang ditemukan.")
                cursor.close()
                conn.close()
