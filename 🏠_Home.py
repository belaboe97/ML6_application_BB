import streamlit as st
from dotenv import dotenv_values
from openai import AzureOpenAI
import pymongo

with st.sidebar:
    st.image("ML6_logo.png", use_column_width=True)  # Display the image
    st.write("")  # Add some space between the image and navigation items
    #st.header("Navigation")  # Optional header
    #page = st.selectbox("Select a page", ["Page 1", "Page 2", "Page 3"])
    # Add more navigation items as needed
    st.sidebar.text("Copyright 2024 @ Bela Bönte")


st.write("Welcome to my small ML6 Application 🚀 \n Please start with uploading the data under Data Managment and create a video under Creative Center")