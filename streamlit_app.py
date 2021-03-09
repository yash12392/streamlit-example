import streamlit as st 
from contract_note import angel_pdf_to_csv
import tempfile
from download import download_button

st.set_page_config(page_title='Contract Note Convertor')

st.title('Contract Note Convertor')

uploaded_file = st.file_uploader(label = 'Please upload Angel Broking Contract Note in PDF', type = ['pdf'])

if uploaded_file is not None:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix = ".pdf")
    tfile.write(uploaded_file.read())
    
    df = angel_pdf_to_csv(tfile.name)

    st.write(df)

    download_button_str = download_button(df, 'test.csv', 'Click to Download!')

    st.markdown(download_button_str, unsafe_allow_html=True)
