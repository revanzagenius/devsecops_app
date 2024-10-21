from io import BytesIO
import mysql.connector
import ftplib
import streamlit as st
import random
import string
from datetime import datetime
import os

def get_database_connection():
    return mysql.connector.connect(
        host="103.185.53.105",
        user="devsecop_user",  
        # password="Sthr33.c0.1d!", 
        password="C?%A{^2A~bBi", 
        database="devsecop_database"
    )

def upload_file_to_ftp(file_path, file_name):
    ftp = ftplib.FTP('ftp.devsecopplatform.xyz')
    ftp.login(user="devsecops@devsecopsplatform.xyz",passwd="hamdanryuz123")
    with open(file_path, 'rb') as f:
        ftp.storbinary(f'STOR {file_name}', f)
    ftp.quit()

def download_file_from_ftp(file_name):
    ftp = ftplib.FTP('ftp.devsecopsplatform.xyz')
    ftp.login(user='devsecops@devsecopsplatform.xyz', passwd='hamdanryuz123')
    buffer = BytesIO()
    def callback(data):
        buffer.write(data)
    ftp.retrbinary(f'RETR {file_name}', callback)
    ftp.quit()
    return buffer.getvalue()

def render_page(jenis_id, page_name, pdf_prefix, stage):
    if st.button('Back'):
        st.session_state.page = f'{stage}_page'
        st.rerun()
    
    st.subheader(page_name)

    # Check for user authentication
    if 'user_role' not in st.session_state or 'user_id' not in st.session_state:
        st.error("User role atau ID tidak ditemukan. Silakan login kembali.")
        return

    user_role = st.session_state.user_role
    user_id = st.session_state.user_id

    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)

    # Construct the SQL query using placeholders and f-strings properly
    base_query = f"""
    SELECT 
        p.nama_project, 
        ud.username AS pic_{stage}, 
        u.username AS pm, 
        dd.id_detail_{stage},
        COALESCE(ed.remarks, '-') AS remarks,
        COALESCE(ed.evidance, '-') AS evidance,
        COALESCE(ed.tgl, '-') AS tgl,
        COALESCE(ss.deskripsi, '-') AS status
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
    WHERE dd.jenis_id = %s
    """

    if user_role == 'admin':
        query = base_query + " ORDER BY ed.tgl DESC"
        cursor.execute(query, (jenis_id,))
    elif user_role in ('develop', 'design', 'build','test','deploy','monitor'):
        query = base_query + " AND d.pic = %s ORDER BY ed.tgl DESC"
        cursor.execute(query, (jenis_id, user_id))
    elif user_role =='pm':
        query = base_query + " AND p.pic = %s ORDER BY ed.tgl DESC"
        cursor.execute(query, (jenis_id, user_id,))

    results = cursor.fetchall()

    # Fetch status options for the dropdown
    cursor.execute("SELECT status_id, deskripsi FROM status_stage")
    status_options = {row['status_id']: row['deskripsi'] for row in cursor.fetchall()}


    render_table_headers()


    st.write("---")
    if results:
        for idx, row in enumerate(results):
            render_table_row(row, status_options, idx, pdf_prefix, stage)
    else:
        st.write("Tidak ada data yang ditemukan.")

    # Check if the evidence form needs to be displayed
    if 'create_evidence' in st.session_state:
        create_evidence_form(
            st.session_state.create_evidence[f'id_detail_{stage}'], 
            st.session_state.create_evidence['status_options'],
            stage
        )

    conn.close()

def render_table_headers():
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

def render_table_row(row, status_options, idx, pdf_prefix, stage):
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([4, 3, 3, 3, 3, 3, 2, 2])
    
    with col1:
        st.write(row['nama_project'])
    with col2:
        st.write(row[f'pic_{stage}'])
    with col3:
        st.write(row['pm'])
    with col4:
        st.write(row['remarks'])
    with col5:
        if row['evidance'] != '-':
            file_name = row['evidance'].replace('\\', '/')
            file_data = download_file_from_ftp(file_name)
            new_file_name = f"{pdf_prefix}_{row['tgl']}.pdf"
            st.download_button(":material/picture_as_pdf:", data=file_data, file_name=new_file_name, mime="application/pdf", key=f"download_button_{idx}")
        else:
            st.write('-')
    with col6:
        color = {'Pending': 'red', 'On Process': 'yellow', 'Complete': 'green'}.get(row['status'], 'black')
        st.markdown(f"<p style='color: {color};'>{row['status']}</p>", unsafe_allow_html=True)
    with col7:
        if st.button(':material/insert_drive_file:', key=f"create_{idx}"):
            st.session_state.create_evidence = {
                f'id_detail_{stage}': row[f'id_detail_{stage}'],
                'status_options': status_options
            }
            st.rerun()
    with col8:
        if st.button(":material/history:", key=f"history{idx}"):
            st.session_state.page = f"history_{pdf_prefix.lower()}"
            st.session_state[f'id_detail_{stage}'] = row[f'id_detail_{stage}']
            st.rerun()

def create_evidence_form(id_detail_stage, status_options, stage):
    st.subheader(f'Create Evidence for {stage.capitalize()}')
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
        id_evidance_stage = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        evidance = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        conn = get_database_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            query = f"""
            INSERT INTO evidance_{stage} (id_evidance_{stage}, id_detail_{stage}, tgl, status_id, remarks, evidance)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (id_evidance_stage, id_detail_stage, tgl_waktu, status_id, remarks, uploaded_file.name))
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

def display_history(id_detail_stage, page_name, back_page_name, file_prefix, stage):
    user_role = st.session_state.user_role
    user_id = st.session_state.user_id
    if user_role == 'ciso':
        if st.button('Back'):
            st.session_state.page = 'ciso'
            st.rerun()
    else:
        if st.button('Back'):
            st.session_state.page = back_page_name
            st.rerun()

    st.subheader(f'History {page_name}')

    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)

    query = f"""
        SELECT 
        p.nama_project, 
        ud.username AS pic_{stage}, 
        u.username AS pm, 
        ed.tgl, 
        ed.remarks, 
        ss.deskripsi as status, 
        ed.evidance
        FROM evidance_{stage} ed
        JOIN detail_{stage} dd ON ed.id_detail_{stage} = dd.id_detail_{stage}
        JOIN {stage} d ON dd.id_{stage} = d.{stage}_id
        JOIN project p ON d.{stage}_id = p.{stage}_id
        LEFT JOIN user ud ON d.pic = ud.id
        LEFT JOIN user u ON p.pic = u.id
        LEFT JOIN status_stage ss ON ed.status_id = ss.status_id
        WHERE dd.id_detail_{stage} = %s
        ORDER BY ed.tgl DESC;
    """
    cursor.execute(query, (id_detail_stage,))
    results = cursor.fetchall()

    # Display table headers
    col1, col2, col3, col4, col5, col6, col7 = st.columns([4, 4, 4, 4, 4, 4, 4])
    with col1:
        st.write('Nama Project')
    with col2:
        st.write('PIC Project')
    with col3:
        st.write(f'PIC {stage.capitalize()}')
    with col4:
        st.write('Waktu')
    with col5:
        st.write('Remarks')
    with col6:
        st.write('Status')
    with col7:
        st.write('Evidence')
    st.write('---')

    if results:
        for idx, result in enumerate(results):
            col1, col2, col3, col4, col5, col6, col7 = st.columns([4, 4, 4, 4, 4, 4, 4])
            with col1:
                st.write(result['nama_project'])
            with col2:
                st.write(result['pm'])
            with col3:
                st.write(result[f'pic_{stage}'])
            with col4:
                st.write(result['tgl'])
            with col5:
                st.write(result['remarks'])
            with col6:
                status_color = {
                    'Pending': 'red',
                    'On Process': 'yellow',
                    'Complete': 'green'
                }
                status = result['status']
                st.markdown(f"<p style='color: {status_color.get(status, 'black')};'>{status}</p>", unsafe_allow_html=True)
            with col7:
                if result['evidance'] != '-':
                    file_name = result['evidance'].replace('\\', '/')
                    file_data = download_file_from_ftp(file_name)
                    new_file_name = f"{file_prefix}_{result['tgl']}.pdf"
                    st.download_button(":material/picture_as_pdf:", data=file_data, file_name=new_file_name, mime="application/pdf", key=f"download_button_{idx}")
                else:
                    st.write('-')
    else:
        st.write("Tidak ada data yang ditemukan.")

    conn.close()

def generate_random_string(length=4):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def render_table_headers_ciso():
    col1, col2, col3, col4, col5, col6, col7 = st.columns([4, 3, 3, 3, 3, 3, 2])
    with col1:
        st.write('Jenis Stage')
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
        st.write('History')

def render_table_row_ciso(row, status_options, idx, pdf_prefix, stage):
    col1, col2, col3, col4, col5, col6, col7 = st.columns([4, 3, 3, 3, 3, 3, 2])
    
    with col1:
        st.write(row['jd'])
    with col2:
        st.write(row[f'pic_{stage}'])
    with col3:
        st.write(row['pm'])
    with col4:
        st.write(row['remarks'])
    with col5:
        if row['evidance'] != '-':
            file_name = row['evidance'].replace('\\', '/')
            file_data = download_file_from_ftp(file_name)
            new_file_name = f"{pdf_prefix}_{row['tgl']}.pdf"
            st.download_button(":material/picture_as_pdf:", data=file_data, file_name=new_file_name, mime="application/pdf", key=f"download_button_{generate_random_string()}")
        else:
            st.write('-')
    with col6:
        status = row['status'] if row['status'] else '-'
        color = {'Pending': 'red', 'On Process': 'yellow', 'Complete': 'green', '-':'white'}.get(status, 'black')
        st.markdown(f"<p style='color: {color};'>{status}</p>", unsafe_allow_html=True)
    with col7:
        if st.button(":material/history:", key=f"history_button_{idx}_{row['nama_project']}_{row[f'id_detail_{stage}']}"):
            st.session_state[f'id_detail_{stage}'] = row[f'id_detail_{stage}']
            st.session_state['jenis_id'] = row['ddj']  # Simpan jenis_id (ddj)
            st.session_state['stage'] = stage  # Simpan stage
            st.session_state['page'] = 'history_ciso'  # Redirect ke halaman history_ciso
            st.rerun()
