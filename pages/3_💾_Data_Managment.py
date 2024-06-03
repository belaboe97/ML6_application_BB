import streamlit as st
import requests 
import xml.etree.ElementTree as ET

with st.sidebar:
    st.image("ML6_logo.png", use_column_width=True)  # Display the image
    st.write("")  # Add some space between the image and navigation items
    #st.header("Navigation")  # Optional header
    #page = st.selectbox("Select a page", ["Page 1", "Page 2", "Page 3"])
    # Add more navigation items as needed
    st.sidebar.text("Copyright 2024 @ Bela Bönte")


uploaded_files = st.file_uploader("Choose a file")
if uploaded_files is not None:
    # To read file as bytes:
    bytes_data = uploaded_files.getvalue()

    url = f"https://stazureaiai4222842333297.blob.core.windows.net/ai4data/{uploaded_files.name}?sp=racwdli&st=2024-05-02T14:48:58Z&se=2024-05-29T22:48:58Z&spr=https&sv=2022-11-02&sr=c&sig=pVrxZ8hYhMnDTYHe13KwG4ppuqWwuCuiXRIx2NgK9bg%3D"

    payload = bytes_data
    headers = {
    'x-ms-date': 'Thursday, May 2, 2024 5:13:22 PM',
    'x-ms-blob-type': 'BlockBlob',
    'Content-Type': 'application/pdf'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

file_list = ["Wahlprogramm"]



st.write("Uploaded Files:")

url = "https://stazureaiai4222842333297.blob.core.windows.net/ai4data?restype=container&comp=list&sp=racwdli&st=2024-05-02T14:48:58Z&se=2024-05-29T22:48:58Z&spr=https&sv=2022-11-02&sr=c&sig=pVrxZ8hYhMnDTYHe13KwG4ppuqWwuCuiXRIx2NgK9bg%3D"

payload = "<file contents here>"
headers = {
  'x-ms-date': 'Thursday, May 2, 2024 5:13:22 PM',
  'x-ms-blob-type': 'BlockBlob',
  'Content-Type': 'application/pdf'
}

response = requests.request("GET", url, headers=headers, data=payload)

root = ET.fromstring(response.text)

# Extract blob names
blob_names = [blob.find('Name').text for blob in root.findall('.//Blob')]


for file_name in blob_names:
    # Provide a checkbox for each file name to allow users to remove files
    remove_file = st.checkbox(file_name)
    #if remove_file:
        # Remove the file name from the file_list if the checkbox is selected
    #    file_list.remove(file_name)

