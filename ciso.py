import ftplib
import streamlit as st
import pandas as pd
from db_utils import get_database_connection, render_table_headers_ciso 
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

    # st.image("images/devsecops.png", width=500)
    col1, col2, col3 = st.columns([1, 1, 1])  # Kolom 1 dan 3 lebih kecil dari kolom 2

    # Tempatkan gambar di kolom kedua
    with col2:
        # st.image("images/devsecops.png", width=800)
        st.image("images/detail_devsecops.png", width=800)


    projects = get_all_projects()

    display_all_projects(projects)

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
            dv.develop_id,
            db.build_id,
            dt.test_id,
            dp.deploy_id,
            dm.monitor_id
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
        LEFT JOIN
            build db ON p.build_id = db.build_id
        LEFT JOIN
            test dt ON p.test_id = dt.test_id
        LEFT JOIN
            deploy dp ON p.deploy_id = dp.deploy_id
        LEFT JOIN
            monitor dm ON p.monitor_id = dm.monitor_id
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
                stages = ['design', 'develop', 'build', 'test', 'deploy', 'monitor']
                for stage in stages:
                    st.subheader(stage.title())
                    st.write('---')
                    results = get_data(stage, project)
                    render_table_headers_ciso()
                    st.write("---")
                    if results:
                        for idx, row in enumerate(results):
                            render_table_row_ciso(row, {1: 'Pending', 2: 'On Process', 3: 'Complete'}, idx, stage, stage)
                    else:
                        st.write("Tidak ada data yang ditemukan.")
                    st.write('---')

def get_data(stage, project):
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    query = f"""
        SELECT 
            p.nama_project, 
            ud.username AS pic_{stage}, 
            u.username AS pm, 
            dd.id_detail_{stage},
            COALESCE(ed.remarks, '-') AS remarks,
            COALESCE(ed.evidance, '-') AS evidance,
            COALESCE(ed.tgl, '-') AS tgl,
            COALESCE(ss.deskripsi, '-') AS status,
            dd.jenis_id as ddj,
            j.deskripsi_jenis as jd
        FROM detail_{stage} dd
        LEFT JOIN {stage} d ON dd.id_{stage} = d.{stage}_id
        LEFT JOIN project p ON d.{stage}_id = p.{stage}_id
        LEFT JOIN user ud ON d.pic = ud.id
        LEFT JOIN user u ON p.pic = u.id
        LEFT JOIN (
            SELECT id_detail_{stage}, remarks, evidance, tgl, status_id
            FROM evidance_{stage} ed1
            WHERE (id_detail_{stage}, tgl) IN (
                SELECT id_detail_{stage}, MAX(tgl)
                FROM evidance_{stage}
                GROUP BY id_detail_{stage}
            )
        ) ed ON dd.id_detail_{stage} = ed.id_detail_{stage}
        LEFT JOIN status_stage ss ON ed.status_id = ss.status_id
        LEFT JOIN jenis j ON dd.jenis_id = j.jenis_id
        WHERE dd.id_{stage} = %s AND p.project_id = %s
    """
    cursor.execute(query, (project[f'{stage}_id'], project['project_id']))
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

