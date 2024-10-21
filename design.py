import streamlit as st
import pandas as pd
from db_utils import get_database_connection,  upload_file_to_ftp, download_file_from_ftp
from datetime import datetime
import streamlit as st
import random
import string
import os
from io import BytesIO
import ftplib





def create_evidence_form(id_detail_design, status_options):
    st.subheader('Create Evidence')
    tgl_waktu = datetime.now()
    st.write(f"Waktu saat ini: {tgl_waktu.strftime('%Y-%m-%d %H:%M:%S')}")

    status_id = st.selectbox("Status", list(status_options.keys()), format_func=lambda x: status_options[x])
    remarks = st.text_area("Remarks")
    uploaded_file = st.file_uploader("Upload File", type=["pdf"])

    if uploaded_file:
        file_path = os.path.join(uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        ftp = ftplib.FTP('ftp.devsecopsplatform.xyz')
        ftp.login(user='devsecops@devsecopsplatform.xyz', passwd='hamdanryuz123')
        with open(file_path, 'rb') as f:
            ftp.storbinary(f'STOR {uploaded_file.name}', f)
        ftp.quit()

        os.remove(file_path)

    if st.button("Create"):
        id_evidance_design = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        evidance = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        conn = get_database_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
            INSERT INTO evidance_design (id_evidance_design, id_detail_design, tgl, status_id, remarks, evidance)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (id_evidance_design, id_detail_design, tgl_waktu, status_id, remarks, uploaded_file.name))
            conn.commit()

            if uploaded_file:
                st.info(f"File '{uploaded_file.name}' telah diupload, tapi belum disimpan ke database.")

            st.success("Data berhasil disimpan.")
            del st.session_state.create_evidence
            st.rerun()
        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")
        finally:
            conn.close()
    if st.button("Close"):
        del st.session_state.create_evidence
        st.rerun()
        
def main_page():
    if st.button('Back'):
        st.session_state.page = 'stage'
        st.rerun()
        
    st.title("Design page")
    st.markdown('---')

    col1, col2 = st.columns(2)
    if col1.button('Secure SDLC', use_container_width=True):
        st.session_state.page = 'secure_sdlc_page'
    if col2.button('Threat Model', use_container_width=True):
        st.session_state.page = 'threat_model_page'

def secure_sdlc_page():
    if st.button('Back'):
        st.session_state.page = 'design_page'
        st.rerun()

    st.subheader('Secure SDLC')

    if 'user_role' not in st.session_state or 'user_id' not in st.session_state:
        st.error("User role atau ID tidak ditemukan. Silakan login kembali.")
        return

    user_role = st.session_state.user_role
    user_id = st.session_state.user_id

    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)

    base_query = """
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
        FROM evidance_design
        WHERE (id_detail_design, tgl) IN (
            SELECT id_detail_design, MAX(tgl)
            FROM evidance_design
            GROUP BY id_detail_design
        )
    ) ed ON dd.id_detail_design = ed.id_detail_design
    LEFT JOIN status_stage ss ON ed.status_id = ss.status_id
    WHERE dd.jenis_id = 'ds-1'
    """

    if user_role == 'admin':
        query = base_query + " ORDER BY ed.tgl DESC"
        cursor.execute(query)
    elif user_role == 'design':
        query = base_query + " AND d.pic = %s ORDER BY ed.tgl DESC"
        cursor.execute(query, (user_id,))

    results = cursor.fetchall()

    cursor.execute("SELECT status_id, deskripsi FROM status_stage")
    status_options = {row['status_id']: row['deskripsi'] for row in cursor.fetchall()}
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([4, 3, 3, 3, 3, 3, 2, 2])
    with col1:
        st.write('Nama Project')
    with col2:
        st.write('PIC Stage')
    with col3:
        st.write('PIC Project')
    with col4:
        st.write('Remarks')
    with col5:
        st.write('Evidance')
    with col6:
        st.write('Status')
    with col7:
        st.write('Action')
    with col8:
        st.write('History')
    st.write("---")
    if results:
        for idx, row in enumerate(results):
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([4, 3, 3, 3, 3, 3, 2, 2])
            with col1:
                st.write(row['nama_project'])
            with col2:
                st.write(row['pic_design'])
            with col3:
                st.write(row['pm'])
            with col4:
                st.write(row['remarks'])
            with col5:
                if row['evidance'] != '-':
                    file_name = row['evidance'].replace('\\', '/')
                    file_data = download_file_from_ftp(file_name)
                    new_file_name = f"secureSDLC_{row['tgl']}.pdf"
                    st.download_button(":material/picture_as_pdf:", data=file_data, file_name=new_file_name, mime="application/pdf", key=f"download_button_{idx}")

                else:
                    st.write('-')
            
            with col6:
                if row['status'] == 'Pending':
                    st.markdown(f"<p style='color: red;'>{row['status']}</p>", unsafe_allow_html=True)
                elif row['status'] == 'On Process' :
                    st.markdown(f"<p style='color: yellow;'>{row['status']}</p>", unsafe_allow_html=True)
                elif row['status'] == 'Complete' :
                    st.markdown(f"<p style='color: green;'>{row['status']}</p>", unsafe_allow_html=True)
            with col7:
                if st.button(':material/insert_drive_file:', key=f"create_{idx}"):
                    st.session_state.create_evidence = {
                        'id_detail_design': row['id_detail_design'],
                        'status_options': status_options
                    }
                    st.rerun()
            with col8:
                if st.button(":material/history:", key=f"history{idx}"):
                    st.session_state.page = 'history_secure_sdlc'
                    st.session_state.id_detail_design = row['id_detail_design']  # Store the id_detail_design
                    st.rerun()
            
    else:
        st.write("Tidak ada data yang ditemukan.")

    if 'create_evidence' in st.session_state:
        create_evidence_form(st.session_state.create_evidence ['id_detail_design'], 
                            st.session_state.create_evidence['status_options'])

    conn.close()
    

def history_secure_sdlc(id_detail_design):
    if st.button('Back'):
        st.session_state.page = 'secure_sdlc_page'
        st.rerun()
    st.subheader('History Secure SDLC')

    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)

    # Query to fetch the relevant data based on id_detail_design
    query = """
        SELECT 
        p.nama_project, 
        ud.username AS pic_design, 
        u.username AS pm, 
        ed.tgl, 
        ed.remarks, 
        ss.deskripsi as status, 
        ed.evidance
        FROM evidance_design ed
        JOIN detail_design dd ON ed.id_detail_design = dd.id_detail_design
        JOIN design d ON dd.id_design = d.design_id
        JOIN project p ON d.design_id = p.design_id
        LEFT JOIN user ud ON d.pic = ud.id
        LEFT JOIN user u ON p.pic = u.id
        LEFT JOIN status_stage ss ON ed.status_id = ss.status_id
        WHERE dd.id_detail_design = %s
        ORDER BY ed.tgl DESC;
    """
    cursor.execute(query, (id_detail_design,))
    results = cursor.fetchall()

    col1, col2, col3, col4, col5, col6, col7 = st.columns([4,4,4,4,4,4,4])
    with col1:
        st.write('Nama Project')
    with col2:
        st.write('PIC Project')
    with col3:
        st.write('PIC Stage')
    with col4:
        st.write('Waktu')
    with col5:
        st.write('Remarks')
    with col6:
        st.write('Status')
    with col7:
        st.write('Evidance')
    st.write('---')
    if results:
        for idx, result in enumerate(results):
            col1, col2, col3, col4, col5,col6,col7 = st.columns([4,4,4,4,4,4,4])
            with col1:
                st.write(result['nama_project'])
            with col2:
                st.write(result['pm'])
            with col3:
                st.write(result['pic_design'])
            with col4:
                st.write(result['tgl'])
            with col5:
                st.write(result['remarks'])
            with col6:
                if result['status'] == 'Pending':
                    st.markdown(f"<p style='color: red;'>{result['status']}</p>", unsafe_allow_html=True)
                elif result['status'] == 'On Process' :
                    st.markdown(f"<p style='color: yellow;'>{result['status']}</p>", unsafe_allow_html=True)
                elif result['status'] == 'Complete' :
                    st.markdown(f"<p style='color: green;'>{result['status']}</p>", unsafe_allow_html=True)
            with col7:
                if result['evidance'] != '-':
                    file_name = result['evidance'].replace('\\', '/')
                    file_data = download_file_from_ftp(file_name)
                    new_file_name = f"secureSDLC_{result['tgl']}.pdf"
                    st.download_button(":material/picture_as_pdf:", data=file_data, file_name=new_file_name, mime="application/pdf", key=f"download_button_{idx}")
                else:
                    st.write('-')
    else:
        st.write("Tidak ada data yang ditemukan.")

    conn.close()

def history_threat_model(id_detail_design):
    if st.button('Back'):
        st.session_state.page = 'threat_model_page'
        st.rerun()
    st.subheader('History Threat Model')

    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)

    # Query to fetch the relevant data based on id_detail_design
    query = """
        SELECT 
        p.nama_project, 
        ud.username AS pic_design, 
        u.username AS pm, 
        ed.tgl, 
        ed.remarks, 
        ss.deskripsi as status, 
        ed.evidance
        FROM evidance_design ed
        JOIN detail_design dd ON ed.id_detail_design = dd.id_detail_design
        JOIN design d ON dd.id_design = d.design_id
        JOIN project p ON d.design_id = p.design_id
        LEFT JOIN user ud ON d.pic = ud.id
        LEFT JOIN user u ON p.pic = u.id
        LEFT JOIN status_stage ss ON ed.status_id = ss.status_id
        WHERE dd.id_detail_design = %s
        ORDER BY ed.tgl DESC;
    """
    cursor.execute(query, (id_detail_design,))
    results = cursor.fetchall()

    col1, col2, col3, col4, col5, col6, col7 = st.columns([4,4,4,4,4,4,4])
    with col1:
        st.write('Nama Project')
    with col2:
        st.write('PIC Project')
    with col3:
        st.write('PIC Stage')
    with col4:
        st.write('Waktu')
    with col5:
        st.write('Remarks')
    with col6:
        st.write('Status')
    with col7:
        st.write('Evidance')
    st.write('---')
    if results:
        for idx, result in enumerate(results):
            col1, col2, col3, col4, col5,col6,col7 = st.columns([4,4,4,4,4,4,4])
            with col1:
                st.write(result['nama_project'])
            with col2:
                st.write(result['pm'])
            with col3:
                st.write(result['pic_design'])
            with col4:
                st.write(result['tgl'])
            with col5:
                st.write(result['remarks'])
            with col6:
                if result['status'] == 'Pending':
                    st.markdown(f"<p style='color: red;'>{result['status']}</p>", unsafe_allow_html=True)
                elif result['status'] == 'On Process' :
                    st.markdown(f"<p style='color: yellow;'>{result['status']}</p>", unsafe_allow_html=True)
                elif result['status'] == 'Complete' :
                    st.markdown(f"<p style='color: green;'>{result['status']}</p>", unsafe_allow_html=True)
            with col7:
                if result['evidance'] != '-':
                    file_name = result['evidance'].replace('\\', '/')
                    file_data = download_file_from_ftp(file_name)
                    new_file_name = f"ThreatModel_{result['tgl']}.pdf"
                    st.download_button(":material/picture_as_pdf:", data=file_data, file_name=new_file_name, mime="application/pdf", key=f"download_button_{idx}")
                else:
                    st.write('-')
    else:
        st.write("Tidak ada data yang ditemukan.")

    conn.close()
            
def threat_model_page():
    if st.button('Back'):
        st.session_state.page = 'design_page'
        st.rerun()

    st.subheader('Threat Model')

    if 'user_role' not in st.session_state or 'user_id' not in st.session_state:
        st.error("User role atau ID tidak ditemukan. Silakan login kembali.")
        return

    user_role = st.session_state.user_role
    user_id = st.session_state.user_id

    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)

    base_query = """
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
        FROM evidance_design
        WHERE (id_detail_design, tgl) IN (
            SELECT id_detail_design, MAX(tgl)
            FROM evidance_design
            GROUP BY id_detail_design
        )
    ) ed ON dd.id_detail_design = ed.id_detail_design
    LEFT JOIN status_stage ss ON ed.status_id = ss.status_id
    WHERE dd.jenis_id = 'ds-2'
    """

    if user_role == 'admin':
        query = base_query + " ORDER BY ed.tgl DESC"
        cursor.execute(query)
    elif user_role == 'design':
        query = base_query + " AND d.pic = %s ORDER BY ed.tgl DESC"
        cursor.execute(query, (user_id,))

    results = cursor.fetchall()

    cursor.execute("SELECT status_id, deskripsi FROM status_stage")
    status_options = {row['status_id']: row['deskripsi'] for row in cursor.fetchall()}
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([4, 3, 3, 3, 3, 3, 2, 2])
    with col1:
        st.write('Nama Project')
    with col2:
        st.write('PIC Stage')
    with col3:
        st.write('PIC Project')
    with col4:
        st.write('Remarks')
    with col5:
        st.write('Evidance')
    with col6:
        st.write('Status')
    with col7:
        st.write('Action')
    with col8:
        st.write('History')
    st.write("---")
    if results:
        for idx, row in enumerate(results):
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([4, 3, 3, 3, 3, 3, 2, 2])
            with col1:
                st.write(row['nama_project'])
            with col2:
                st.write(row['pic_design'])
            with col3:
                st.write(row['pm'])
            with col4:
                st.write(row['remarks'])
            with col5:
                if row['evidance'] != '-':
                    file_name = row['evidance'].replace('\\', '/')
                    file_data = download_file_from_ftp(file_name)
                    new_file_name = f"ThreatModel_{row['tgl']}.pdf"
                    st.download_button(":material/picture_as_pdf:", data=file_data, file_name=new_file_name, mime="application/pdf", key=f"download_button_{idx}")
                else:
                    st.write('-')
            with col6:
                if row['status'] == 'Pending':
                    st.markdown(f"<p style='color: red;'>{row['status']}</p>", unsafe_allow_html=True)
                elif row['status'] == 'On Process' :
                    st.markdown(f"<p style='color: yellow;'>{row['status']}</p>", unsafe_allow_html=True)
                elif row['status'] == 'Complete' :
                    st.markdown(f"<p style='color: green;'>{row['status']}</p>", unsafe_allow_html=True)
            with col7:
                if st.button(':material/insert_drive_file:', key=f"create_{idx}"):
                    st.session_state.create_evidence = {
                        'id_detail_design': row['id_detail_design'],
                        'status_options': status_options
                    }
                    st.rerun()
            with col8:
                if st.button(":material/history:", key=f"history{idx}"):
                    st.session_state.page = 'history_threat_model'
                    st.session_state.id_detail_design = row['id_detail_design']  # Store the id_detail_design
                    st.rerun()
            
    else:
        st.write("Tidak ada data yang ditemukan.")

    if 'create_evidence' in st.session_state:
        create_evidence_form(st.session_state.create_evidence ['id_detail_design'], 
                            st.session_state.create_evidence['status_options'])

    conn.close()


