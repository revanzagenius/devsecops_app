import streamlit as st
from db_utils import get_database_connection
import uuid
import random
import string
import pandas as pd

def generate_random_id():
    return str(uuid.uuid4())[:8]
    
def get_users_by_role(role):
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id, username FROM user WHERE role = %s"
    cursor.execute(query, (role,))
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users

def user_dropdown(role, label):
    users = get_users_by_role(role)
    user_options = [user['username'] for user in users]
    pic_username = st.selectbox(label, user_options)
    pic_id = next((user['id'] for user in users if user['username'] == pic_username), None)
    return pic_id

def get_jenis_by_stage(stage):
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT jenis_id, deskripsi_jenis FROM jenis WHERE stage = %s"
    cursor.execute(query, (stage,))
    jenis = cursor.fetchall()
    cursor.close()
    conn.close()
    return jenis

def get_status_step():
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id_status_detail, deskripsi FROM status_step"
    cursor.execute(query)
    steps = cursor.fetchall()
    cursor.close()
    conn.close()
    return steps

def get_status_step_detail():
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT id_status_detail, deskripsi FROM status_step_detail"
    cursor.execute(query)
    steps = cursor.fetchall()
    cursor.close()
    conn.close()
    return steps


def main_page():
    if st.button('Back'):
        st.session_state['page'] = 'main_page'
    
    st.subheader('Project Page')
    
    if st.button("Create New Project"):
        st.session_state['page'] = 'create_project_page'

    # Mendapatkan koneksi database
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)

    # Base query
    base_query = """
        SELECT 
            p.project_id,
            p.nama_project,
            ud.username as design_pic,
            udv.username as develop_pic,
            ub.username as build_pic,
            ut.username as test_pic,
            udp.username as deploy_pic,
            um.username as monitor_pic,
            u.username as pm,
            stat_sp.deskripsi as stat_sp,
            stat_sc.deskripsi as stat_sc,
            stat_sn.deskripsi as stat_sn
        FROM 
            project p
        LEFT JOIN 
            design d ON p.design_id = d.design_id
        LEFT JOIN 
            user ud ON d.pic = ud.id
        LEFT JOIN 
            develop dv ON p.develop_id = dv.develop_id
        LEFT JOIN 
            user udv ON dv.pic = udv.id
        LEFT JOIN 
            build b ON p.build_id = b.build_id
        LEFT JOIN 
            user ub ON b.pic = ub.id
        LEFT JOIN 
            test t ON p.test_id = t.test_id
        LEFT JOIN 
            user ut ON t.pic = ut.id
        LEFT JOIN 
            deploy dp ON p.deploy_id = dp.deploy_id
        LEFT JOIN 
            user udp ON dp.pic = udp.id
        LEFT JOIN 
            monitor m ON p.monitor_id = m.monitor_id
        LEFT JOIN 
            user um ON m.pic = um.id
        LEFT JOIN 
            user u ON p.pic = u.id
        LEFT JOIN 
            status_step stat_sp ON p.previous = stat_sp.id_status_detail
        LEFT JOIN 
            status_step_detail stat_sc ON p.current = stat_sc.id_status_detail
        LEFT JOIN 
            status_step stat_sn ON p.next = stat_sn.id_status_detail
    """
    
    user_role = st.session_state.get('user_role', '')
    
    if user_role == 'pm':
        pm_id = st.session_state.get('user_id', None)  # Mengambil ID PM dari session
        query = base_query + " WHERE p.pic = %s ORDER BY p.nama_project ASC"
        cursor.execute(query, (pm_id,))
    else:
        query = base_query + " ORDER BY p.nama_project ASC"
        cursor.execute(query)
    
    projects = cursor.fetchall()

    cursor.close()
    conn.close()

    st.write('---')
    col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13 = st.columns([1, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2])
    
    with col1:
        st.write('No')
    with col2:
        st.write('Nama Project')
    with col3:
        st.write('PIC Project')
    with col4:
        st.write('PIC Design')
    with col5:
        st.write('PIC Develop')
    with col6:
        st.write('PIC Build')
    with col7:
        st.write('PIC Test')
    with col8:
        st.write('PIC Deploy')
    with col9:
        st.write('PIC Monitor')
    with col13:
        st.write('Action')
    with col10:
        st.write('Previous')
    with col11:
        st.write('Current')
    with col12:
        st.write('Next')
    
    st.write('---')

    if projects:
        for idx, project in enumerate(projects, start=1):
            col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13 = st.columns([1, 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2])
            
            with col1:
                st.write(idx)  # Nomor urut
            with col2:
                st.write(project['nama_project'])  # Nama Project
            with col3:
                st.write(project['pm'])  # PIC Project (PM)
            with col4:
                st.write(project['design_pic'])  # PIC Design
            with col5:
                st.write(project['develop_pic'])  # PIC Develop
            with col6:
                st.write(project['build_pic'])  # PIC Build
            with col7:
                st.write(project['test_pic'])  # PIC Test
            with col8:
                st.write(project['deploy_pic'])  # PIC Deploy
            with col9:
                st.write(project['monitor_pic'])  # PIC Monitor
            # Di dalam loop projects di main_page()
            with col13:
                col13_1, col13_2 = st.columns(2)
                with col13_1:
                    if st.button(':material/edit:', key=f'editProj_{idx}'):
                        st.session_state['page'] = 'edit_project_page'
                        st.session_state['project_id'] = project['project_id']
                with col13_2:
                    if st.button(':material/edit_note:', key=f'editStatus_{idx}'):
                        st.session_state['page'] = 'edit_project_status'
                        st.session_state['project_id'] = project['project_id']
            with col10:
                st.write(project['stat_sp'])  # Previous Stage
            with col11:
                st.write(project['stat_sc'])  # Current Stage
            with col12:
                st.write(project['stat_sn'])  # Next Stage
            
            st.write('---')

def edit_status_page():
    if st.button('Back'):
        st.session_state['page'] = 'project'
        st.rerun()
    
    project_id = st.session_state['project_id']
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch existing project status
    query = """
        SELECT
            p.project_id,
            p.nama_project,
            p.previous,
            p.current,
            p.next
        FROM project p
        WHERE p.project_id = %s
    """
    cursor.execute(query, (project_id,))
    project_data = cursor.fetchone()
    cursor.close()

    st.subheader(f"Edit Status - {project_data['nama_project']}")

    # Get the available status options
    status_steps = get_status_step()
    status_options = {'-': '-', **{step['deskripsi']: step['id_status_detail'] for step in status_steps}}

    status_steps2 = get_status_step_detail()
    status_options2 = {'-': '-', **{step['deskripsi']: step['id_status_detail'] for step in status_steps2}}

    with st.form("edit_status"):
        previous = st.selectbox(
            "Previous Stage",
            options=list(status_options.keys()),
            index=list(status_options.values()).index(project_data['previous'])
        )
        current = st.selectbox(
            "Current Stage",
            options=list(status_options2.keys()),
            index=list(status_options2.values()).index(project_data['current'])
        )
        next_stage = st.selectbox(
            "Next Stage",
            options=list(status_options.keys()),
            index=list(status_options.values()).index(project_data['next'])
        )

        if st.form_submit_button("Update Status"):
            conn = get_database_connection()
            cursor = conn.cursor()

            previous_id = status_options[previous]
            current_id = status_options2[current]
            next_id = status_options[next_stage]

            query = "UPDATE project SET previous = %s, current = %s, next = %s WHERE project_id = %s"
            cursor.execute(query, (previous_id, current_id, next_id, project_id))
            conn.commit()

            cursor.close()
            conn.close()

            st.success("Status updated successfully!")
            st.session_state['page'] = 'project'
            st.rerun()

def create_project_page():
    if st.button('Back'):
        st.session_state['page'] = 'project'
        st.rerun()

    st.subheader("Create New Project")
    with st.form("create_project"):
        nama_project = st.text_input("Nama Project")
        project_id = generate_random_id()
        design_id = generate_random_id()
        develop_id = generate_random_id()
        build_id = generate_random_id()
        test_id = generate_random_id()
        deploy_id = generate_random_id()
        monitor_id = generate_random_id()
        pic_id = user_dropdown('pm', "PIC PM")
        pic_design = user_dropdown('design', "PIC Design")
        pic_develop = user_dropdown('develop', "PIC Develop")
        pic_build = user_dropdown('build', "PIC Build")
        pic_test = user_dropdown('test', "PIC Test")
        pic_deploy = user_dropdown('deploy', "PIC Deploy")
        pic_monitor = user_dropdown('monitor', "PIC Monitor")
        status_steps = get_status_step()
        status_options = {'-': '-', **{step['deskripsi']: step['id_status_detail'] for step in status_steps}}

        status_steps2 = get_status_step_detail()
        status_options2 = {'-': '-', **{step['deskripsi']: step['id_status_detail'] for step in status_steps2}}

        previous = st.selectbox("Previous", options=list(status_options.keys()), format_func=lambda x: x)
        current = st.selectbox("Current", options=list(status_options2.keys()), format_func=lambda x: x)
        next = st.selectbox("Next", options=list(status_options.keys()), format_func=lambda x: x)

        if st.form_submit_button("Create Project"):
            conn = get_database_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM design WHERE design_id = %s"
            cursor.execute(query, (design_id,))
            if not cursor.fetchone():
                query = "INSERT INTO design (design_id, pic) VALUES (%s, %s)"
                cursor.execute(query, (design_id,pic_design))
                conn.commit()

                design_jenis = get_jenis_by_stage('design')
                for jenis in design_jenis:
                    
                    query = "INSERT INTO detail_design (id_detail_design, id_design, jenis_id, information) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (generate_random_id(), design_id, jenis['jenis_id'], ''))
                    conn.commit()
            

            query = "SELECT * FROM develop WHERE develop_id = %s"
            cursor.execute(query, (develop_id,))
            if not cursor.fetchone():
                query = "INSERT INTO develop (develop_id, pic) VALUES (%s, %s)"
                cursor.execute(query, (develop_id,pic_develop))
                conn.commit()

                develop_jenis = get_jenis_by_stage('develop')
                for jenis in develop_jenis:
                    
                    query = "INSERT INTO detail_develop (id_detail_develop, id_develop, jenis_id, information) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (generate_random_id(), develop_id, jenis['jenis_id'], ''))
                    conn.commit()

            query = "SELECT * FROM build WHERE build_id = %s"
            cursor.execute(query, (build_id,))
            if not cursor.fetchone():
                query = "INSERT INTO build (build_id, pic) VALUES (%s, %s)"
                cursor.execute(query, (build_id,pic_build))
                conn.commit()

                build_jenis = get_jenis_by_stage('build')
                for jenis in build_jenis:
                    
                    query = "INSERT INTO detail_build (id_detail_build, id_build, jenis_id, information) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (generate_random_id(), build_id, jenis['jenis_id'], ''))
                    conn.commit()

            query = "SELECT * FROM test WHERE test_id = %s"
            cursor.execute(query, (test_id,))
            if not cursor.fetchone():
                query = "INSERT INTO test (test_id, pic) VALUES (%s, %s)"
                cursor.execute(query, (test_id,pic_test))
                conn.commit()

                test_jenis = get_jenis_by_stage('test')
                for jenis in test_jenis:
                    
                    query = "INSERT INTO detail_test (id_detail_test, id_test, jenis_id, information) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (generate_random_id(), test_id, jenis['jenis_id'], ''))
                    conn.commit()

            query = "SELECT * FROM deploy WHERE deploy_id = %s"
            cursor.execute(query, (deploy_id,))
            if not cursor.fetchone():
                query = "INSERT INTO deploy (deploy_id, pic) VALUES (%s, %s)"
                cursor.execute(query, (deploy_id,pic_deploy))
                conn.commit()

                deploy_jenis = get_jenis_by_stage('deploy')
                for jenis in deploy_jenis:
                    
                    query = "INSERT INTO detail_deploy (id_detail_deploy, id_deploy, jenis_id, information) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (generate_random_id(), deploy_id, jenis['jenis_id'], ''))
                    conn.commit()

            query = "SELECT * FROM monitor WHERE monitor_id = %s"
            cursor.execute(query, (monitor_id,))
            if not cursor.fetchone():
                query = "INSERT INTO monitor (monitor_id, pic) VALUES (%s, %s)"
                cursor.execute(query, (monitor_id,pic_monitor))
                conn.commit()

                monitor_jenis = get_jenis_by_stage('monitor')
                for jenis in monitor_jenis:
                    
                    query = "INSERT INTO detail_monitor (id_detail_monitor, id_monitor, jenis_id, information) VALUES (%s, %s, %s, %s)"
                    cursor.execute(query, (generate_random_id(), monitor_id, jenis['jenis_id'], ''))
                    conn.commit()

            previous_id = status_options[previous]
            current_id = status_options2[current]
            next_id = status_options[next]

            query = "INSERT INTO project (project_id, design_id, develop_id, build_id, test_id, deploy_id, monitor_id, pic, nama_project, previous, current, next) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (project_id, design_id, develop_id, build_id, test_id, deploy_id, monitor_id, pic_id, nama_project, previous_id, current_id, next_id))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("Project created successfully!")
            st.rerun()

def update_pic_if_changed(new_pic_id, old_pic_id, table, id_column, id_value):
    if new_pic_id != old_pic_id:
        conn = get_database_connection()
        cursor = conn.cursor()
        query = f"UPDATE {table} SET pic = %s WHERE {id_column} = %s"
        cursor.execute(query, (new_pic_id, id_value))
        conn.commit()
        cursor.close()
        conn.close()

def user_dropdown(role, label, default=None):
    users = get_users_by_role(role)
    user_options = [user['username'] for user in users]
    if default:
        index_default = user_options.index(default) if default in user_options else 0
    else:
        index_default = 0
    pic_username = st.selectbox(label, user_options, index=index_default)
    pic_id = next((user['id'] for user in users if user['username'] == pic_username), None)
    return pic_id

# def edit_project_page():
#     if st.button('Back'):
#         st.session_state['page'] = 'project'
#         st.rerun()
#     project_id = st.session_state['project_id']
#     conn = get_database_connection()
#     cursor = conn.cursor(dictionary=True)

#     # Fetch existing project data including statuses and PICs
#     # Fetch existing project data including statuses and PICs
#     query = """
#         SELECT
#             p.project_id,
#             p.nama_project,
#             p.previous,
#             p.current,
#             p.next,
#             d.pic as old_design_pic,
#             dv.pic as old_develop_pic,
#             b.pic as old_build_pic,
#             t.pic as old_test_pic,
#             dp.pic as old_deploy_pic,
#             m.pic as old_monitor_pic,
#             p.pic as old_pm_pic,
#             ud.username as design_pic_username,
#             udv.username as develop_pic_username,
#             ub.username as build_pic_username,
#             ut.username as test_pic_username,
#             udp.username as deploy_pic_username,
#             um.username as monitor_pic_username,
#             u.username as pm_username,
#             p.design_id, p.develop_id, p.build_id, p.test_id, p.deploy_id, p.monitor_id
#         FROM project p
#         LEFT JOIN design d ON p.design_id = d.design_id
#         LEFT JOIN user ud ON d.pic = ud.id
#         LEFT JOIN develop dv ON p.develop_id = dv.develop_id
#         LEFT JOIN user udv ON dv.pic = udv.id
#         LEFT JOIN build b ON p.build_id = b.build_id
#         LEFT JOIN user ub ON b.pic = ub.id
#         LEFT JOIN test t ON p.test_id = t.test_id
#         LEFT JOIN user ut ON t.pic = ut.id
#         LEFT JOIN deploy dp ON p.deploy_id = dp.deploy_id
#         LEFT JOIN user udp ON dp.pic = udp.id
#         LEFT JOIN monitor m ON p.monitor_id = m.monitor_id
#         LEFT JOIN user um ON m.pic = um.id
#         LEFT JOIN user u ON p.pic = u.id
#         WHERE p.project_id = %s
#     """
#     cursor.execute(query, (project_id,))
#     project_data = cursor.fetchone()
#     cursor.close()

#     # Get the available status options
#     status_steps = get_status_step()
#     status_options = {'-': '-', **{step['deskripsi']: step['id_status_detail'] for step in status_steps}}

#     status_steps2 = get_status_step_detail()
#     status_options2 = {'-': '-', **{step['deskripsi']: step['id_status_detail'] for step in status_steps2}}

#     with st.form("edit_project"):
#         new_nama_project = st.text_input("Nama Project", project_data['nama_project'])

#         pic_pm = user_dropdown('pm', "PIC PM", default=project_data['pm_username'])
#         pic_design = user_dropdown('design', "PIC Design", default=project_data['design_pic_username'])
#         pic_develop = user_dropdown('develop', "PIC Develop", default=project_data['develop_pic_username'])
#         pic_build = user_dropdown('build', "PIC Build", default=project_data['build_pic_username'])
#         pic_test = user_dropdown('test', "PIC Test", default=project_data['test_pic_username'])
#         pic_deploy = user_dropdown('deploy', "PIC Deploy", default=project_data['deploy_pic_username'])
#         pic_monitor = user_dropdown('monitor', "PIC Monitor", default=project_data['monitor_pic_username'])

#         # Current and new status selections (Previous, Current, Next)
#         previous = st.selectbox(
#             "Previous Stage",
#             options=list(status_options.keys()),
#             index=list(status_options.values()).index(project_data['previous'])
#         )
#         current = st.selectbox(
#             "Current Stage",
#             options=list(status_options2.keys()),
#             index=list(status_options2.values()).index(project_data['current'])
#         )
#         next_stage = st.selectbox(
#             "Next Stage",
#             options=list(status_options.keys()),
#             index=list(status_options.values()).index(project_data['next'])
#         )

#         if st.form_submit_button("Update Project"):
#             conn = get_database_connection()
#             cursor = conn.cursor()

#             # Update nama_project if it has changed
#             if new_nama_project != project_data['nama_project']:
#                 query = "UPDATE project SET nama_project = %s WHERE project_id = %s"
#                 cursor.execute(query, (new_nama_project, project_id))
#                 conn.commit()

#             update_pic_if_changed(pic_design, project_data['old_design_pic'], 'design', 'design_id', project_data['design_id'])
#             update_pic_if_changed(pic_develop, project_data['old_develop_pic'], 'develop', 'develop_id', project_data['develop_id'])
#             update_pic_if_changed(pic_build, project_data['old_build_pic'], 'build', 'build_id', project_data['build_id'])
#             update_pic_if_changed(pic_test, project_data['old_test_pic'], 'test', 'test_id', project_data['test_id'])
#             update_pic_if_changed(pic_deploy, project_data['old_deploy_pic'], 'deploy', 'deploy_id', project_data['deploy_id'])
#             update_pic_if_changed(pic_monitor, project_data['old_monitor_pic'], 'monitor', 'monitor_id', project_data['monitor_id'])
#             update_pic_if_changed(pic_pm, project_data['old_pm_pic'], 'project', 'project_id', project_id)

#             previous_id = status_options[previous]
#             current_id = status_options2[current]
#             next_id = status_options[next_stage]

#             if previous_id != project_data['previous'] or current_id != project_data['current'] or next_id != project_data['next']:
#                 query = "UPDATE project SET previous = %s, current = %s, next = %s WHERE project_id = %s"
#                 cursor.execute(query, (previous_id, current_id, next_id, project_id))
#                 conn.commit()

#             cursor.close()
#             conn.close()

#             st.success("Project updated successfully!")
#             st.session_state['page'] = 'project'
#             st.rerun()
def edit_project_page():
    if st.button('Back'):
        st.session_state['page'] = 'project'
        st.rerun()

    project_id = st.session_state['project_id']
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch existing project data including PICs (without statuses)
    query = """
        SELECT
            p.project_id,
            p.nama_project,
            d.pic as old_design_pic,
            dv.pic as old_develop_pic,
            b.pic as old_build_pic,
            t.pic as old_test_pic,
            dp.pic as old_deploy_pic,
            m.pic as old_monitor_pic,
            p.pic as old_pm_pic,
            ud.username as design_pic_username,
            udv.username as develop_pic_username,
            ub.username as build_pic_username,
            ut.username as test_pic_username,
            udp.username as deploy_pic_username,
            um.username as monitor_pic_username,
            u.username as pm_username,
            p.design_id, p.develop_id, p.build_id, p.test_id, p.deploy_id, p.monitor_id
        FROM project p
        LEFT JOIN design d ON p.design_id = d.design_id
        LEFT JOIN user ud ON d.pic = ud.id
        LEFT JOIN develop dv ON p.develop_id = dv.develop_id
        LEFT JOIN user udv ON dv.pic = udv.id
        LEFT JOIN build b ON p.build_id = b.build_id
        LEFT JOIN user ub ON b.pic = ub.id
        LEFT JOIN test t ON p.test_id = t.test_id
        LEFT JOIN user ut ON t.pic = ut.id
        LEFT JOIN deploy dp ON p.deploy_id = dp.deploy_id
        LEFT JOIN user udp ON dp.pic = udp.id
        LEFT JOIN monitor m ON p.monitor_id = m.monitor_id
        LEFT JOIN user um ON m.pic = um.id
        LEFT JOIN user u ON p.pic = u.id
        WHERE p.project_id = %s
    """
    cursor.execute(query, (project_id,))
    project_data = cursor.fetchone()
    cursor.close()

    with st.form("edit_project"):
        new_nama_project = st.text_input("Nama Project", project_data['nama_project'])

        # PIC dropdowns (remove status section)
        pic_pm = user_dropdown('pm', "PIC PM", default=project_data['pm_username'])
        pic_design = user_dropdown('design', "PIC Design", default=project_data['design_pic_username'])
        pic_develop = user_dropdown('develop', "PIC Develop", default=project_data['develop_pic_username'])
        pic_build = user_dropdown('build', "PIC Build", default=project_data['build_pic_username'])
        pic_test = user_dropdown('test', "PIC Test", default=project_data['test_pic_username'])
        pic_deploy = user_dropdown('deploy', "PIC Deploy", default=project_data['deploy_pic_username'])
        pic_monitor = user_dropdown('monitor', "PIC Monitor", default=project_data['monitor_pic_username'])

        if st.form_submit_button("Update Project"):
            conn = get_database_connection()
            cursor = conn.cursor()

            # Update nama_project if it has changed
            if new_nama_project != project_data['nama_project']:
                query = "UPDATE project SET nama_project = %s WHERE project_id = %s"
                cursor.execute(query, (new_nama_project, project_id))
                conn.commit()

            # Update PICs if changed
            update_pic_if_changed(pic_design, project_data['old_design_pic'], 'design', 'design_id', project_data['design_id'])
            update_pic_if_changed(pic_develop, project_data['old_develop_pic'], 'develop', 'develop_id', project_data['develop_id'])
            update_pic_if_changed(pic_build, project_data['old_build_pic'], 'build', 'build_id', project_data['build_id'])
            update_pic_if_changed(pic_test, project_data['old_test_pic'], 'test', 'test_id', project_data['test_id'])
            update_pic_if_changed(pic_deploy, project_data['old_deploy_pic'], 'deploy', 'deploy_id', project_data['deploy_id'])
            update_pic_if_changed(pic_monitor, project_data['old_monitor_pic'], 'monitor', 'monitor_id', project_data['monitor_id'])
            update_pic_if_changed(pic_pm, project_data['old_pm_pic'], 'project', 'project_id', project_id)

            cursor.close()
            conn.close()

            st.success("Project updated successfully!")
            st.session_state['page'] = 'project'
            st.rerun()

