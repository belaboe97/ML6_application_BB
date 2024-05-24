import streamlit as st
from moviepy.editor import *
import urllib.request
import json
import os
import ssl
from dotenv import dotenv_values
from openai import AzureOpenAI
import requests
import azure.cognitiveservices.speech as speechsdk
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from moviepy.editor import *

import librosa

with st.sidebar:
    st.image("ML6_logo.png", use_column_width=True)  # Display the image
    st.write("")  # Add some space between the image and navigation items
    #st.header("Navigation")  # Optional header
    #page = st.selectbox("Select a page", ["Page 1", "Page 2", "Page 3"])
    # Add more navigation items as needed
    st.sidebar.text("Copyright 2024 @ Bela Bönte")

# https://docs.streamlit.io/develop/tutorials/llms/llm-quickstart
# Get and init services

env_name = "config.env" # following example.env template change to your own .env file name
config = dotenv_values(env_name)

search_endpoint = "https://ai4searchnew.search.windows.net"
azure_search_key = config["azure_search_key"]

index_name = config["azure_index_name"]
client = AzureOpenAI(api_key=config['openai_api_key'], azure_endpoint=config['openai_api_endpoint'], api_version=config['openai_api_version'],)


def get_embeddings(text: str):
    # There are a few ways to get embeddings. This is just one example.
    embedding = client.embeddings.create(input=[text], model="text-embedding-ada-002")
    return embedding.data[0].embedding


def get_images_for_video(image1, image2, image3): 

    img_array = [image1, image2, image3]

    st.write("We are generating your images. Please stay tuned for a short moment")
    for idx, image_idea in enumerate(img_array):

        url = "https://ai4d.openai.azure.com/openai/deployments/Dalle3/images/generations?api-version=2024-02-01"

        payload = json.dumps({
            "prompt": f"{image_idea}",
            "size": "1024x1792",
            "n": 1,
            "quality": "standard",
            "style": "vivid",
            })
        headers = {
        'api-key': config["openai_api_key"],
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        json_obj = json.loads(response.text)
        image_url = json_obj["data"][0]["url"] #the image on the web
        save_name = f'scene{idx}_.jpg' #local name to be saved
        urllib.request.urlretrieve(image_url, save_name)

    return json.dumps({"satus" : "Created three images"})

    

def get_sounds_for_video(sound1, sound2, sound3):

    soundArray = [ sound1, sound2, sound3] 
    
    st.write("We are generating your sounds. Please wait a second")
    for idx, sound_idea in enumerate(soundArray):

        text = sound_idea
        # Creates an instance of a speech config with specified subscription key and service region.
        speech_config = speechsdk.SpeechConfig(subscription="24b413f992dd44d3b43683733b7c5cb4", region="westeurope")
        # Sets the synthesis voice name.
        # e.g. "en-US-AndrewMultilingualNeural".
        # The full list of supported voices can be found here:
        # https://aka.ms/csspeech/voicenames
        # And, you can try get_voices_async method to get all available voices.
        # See speech_synthesis_get_available_voices() sample below.
        voice = "en-US-AndrewMultilingualNeural"
        #de-DE-FlorianMultilingualNeural"
        speech_config.speech_synthesis_voice_name = voice
        # Creates a speech synthesizer for the specified voice,
        # using the default speaker as audio output.
        speech_config.set_speech_synthesis_output_format(speechsdk.SpeechSynthesisOutputFormat.Riff24Khz16BitMonoPcm)
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

        # Receives a text from console input and synthesizes it to speaker.
        result = speech_synthesizer.speak_text_async(text).get()

        stream = speechsdk.AudioDataStream(result)
        stream.save_to_wav_file(f"scene1_{idx}.wav")

    return json.dumps({"status": "Created voicelines sucessfully"})


def get_documents(query): 

    st.write("Searching the Database")
    embedding = get_embeddings(query)
    search_client = SearchClient(search_endpoint, index_name, AzureKeyCredential(azure_search_key))
    vector_query = VectorizedQuery(vector=embedding, k_nearest_neighbors=3, fields="text_vector")
    results = search_client.search(
        vector_queries=[vector_query],
        select = ["title", "chunk"]
    )
    myres = []
    for res in results: 
        print(res)
        myres.append({
            "title": res["title"],
            "content": res["chunk"]
        })
    return json.dumps(myres)

def edit_video(): 
    st.write("Your video is edited and rendered. Please wait a short moment.")
    audio1 = AudioFileClip("scene1_0.wav")
    duration1 =librosa.get_duration(filename='scene1_0.wav')
    clip = ImageClip("scene0_.jpg").set_duration(duration1)

    audio2 = AudioFileClip("scene1_1.wav")
    duration2 = librosa.get_duration(filename='scene1_1.wav')
    clip1 = ImageClip("scene1_.jpg").set_start(duration1).set_duration(duration2)

    audio3 = AudioFileClip("scene1_2.wav")
    duration3 = librosa.get_duration(filename='scene1_2.wav')
    clip2 = ImageClip("scene2_.jpg").set_start(duration1+duration2).set_duration(duration3)

    #title_clip = TextClip("TestTitle", color='green', kerning=5, fontsize=140).set_duration(8).set_start(0.5).crossfadein(2).set_position(('center',400))


    theme_sound = AudioFileClip("01 Dr. No_ The James Bond Theme - Symphonic Version.mp3").set_end(duration1+duration2+duration3)

    mixed = CompositeAudioClip([audio1, audio2.set_start(duration1), audio3.set_start(duration1+duration2), theme_sound.fx(afx.volumex, 0.2)])

    video = CompositeVideoClip([clip,clip1,clip2])

    video.audio = mixed


    # Write the result to a file (many options available !)
    video.write_videofile("currentVideo.mp4", threads = 8, fps=24)

    return json.dumps({"status" : "video created"})


#st.link_button("Search Pexels on Local Docker", f"http://www.localhost:3000/getVideoInformations?query={text_input}&amount={number_input}")
tools = [    
       
        {"type": "function",
            "function": {
                "name": "get_documents",
                "description": "Ask for informations support the video idea. Always cite the docuemnt",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query to find relevant documents",
                        },
                    },
                    "required": ["query"],
                },
            },
        },
        {
        "type": "function",
            "function": {
                "name": "get_images_for_video",
                "description": "Create images for the video. Create the exact images described in the previous chat.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image1": {
                                "type": "string", 
                                "description" : "Take the previously defined idea for image 1"
                                },
                        "image2": {"type": "string", 
                                   "description" : "Take the previously defined idea for image 2"},
                                   
                        "image3": {"type": "string", 
                                   "description" : "Take the previously defined idea for image 3"},
                                   },
                    },
                    "required": ["images"],
                },
            },
            {
            "type": "function",
                "function": {
                    "name": "get_sounds_for_video",
                    "description": "Create Voicelines for a video. Create the exact voicelines given in the previous chat.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sound1": {
                                    "type": "string", 
                                    "description" : "Take the previously defined idea for sound 1"
                                    },
                            "sound2": {"type": "string", 
                                    "description" : "Take the previously defined idea for sound 2"},
                            "sound3": {"type": "string", 
                                    "description" : "Take the previously defined idea for sound 3"},
                                    },
                        },
                        "required": ["sounds"],
                },
            },
            {
            "type": "function",
                "function": {
                    "name": "edit_video",
                    "description": "Edit the final video by editing all video parts together.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": ["edit"],
                    },
                }
            }
    ]




# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for interaction in st.session_state.chat_history:
    if interaction["inputs"]["question"]:
        with st.chat_message("user"):
            st.write(interaction["inputs"]["question"])
    if interaction["outputs"]["answer"]:
        with st.chat_message("assistant"):
            st.write(interaction["outputs"]["answer"])

messages = [{
    "role": "system", 
    "content" : f"""
    You are a chatbot to help create a video for the job applicant Bela Bonte as an ML Engineer. Bela is a blonde male person from europe. Your name is ML6Helper. Your language is english. 
    Your starting context is a summary of the job description given by: {"ML6 is looking for exceptional Machine Learning Engineers to join their fast-growing team, focusing on creating intelligent technology that accelerates business performance. The role has expanded beyond model development to include consulting, data engineering, software engineering, and building production-ready applications using Python and frameworks like TensorFlow, PyTorch, and HuggingFace. Engineers will deploy solutions on cloud platforms such as GCP, AWS, and Azure. Responsibilities include translating customer needs into technical solutions, deploying ML models and pipelines, staying current with ML research, and collaborating with Data Engineers, Software Engineers, Project Managers, and clients. Candidates should have a degree in computer science or a related field, experience in software development and ML/AI, proficiency in Python, and strong communication skills. Preferred qualifications include experience with version control, cloud platforms, data engineering, and open-source contributions.ML6 offers a dynamic and innovative work environment, focusing on rapid growth, fairness, and transparency in rewards. The company fosters continuous learning and collaboration through events like chapter conferences and meetups. Employees can expect to work on cutting-edge projects for top-tier international companies and experience significant career growth. ML6 values mutual trust, open feedback, and interpersonal connections, creating a workplace where employees thrive and contribute to impactful AI solutions."}. 

    You are guiding the applicant from brainstorming an idea, to researching to content creation. 
    - You propose topics for the application video. 
    - You first create an video idea. 
    - You than search for documents supporting the match between candidate and ML6 
    - Each Video has three images and three voicelines. 
    - The video images support the video idea.
    - The voicelines support the video idea.
    - Create Images only if asked.
    - Create Voicelines only if asked. 
    - Create Video only if asked. 
    """
    }]


search_endpoint = "https://ai4searchnew.search.windows.net"
search_index = "azureblob-index"
completed = True
if completed: 
    if user_input := st.chat_input("Ask me anything..."):

        # Display user message in chat message container
        st.chat_message("user").markdown(user_input)

        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            tool_choice="auto",  # auto is default, but we'll be explicit
        )
        response_message =response.choices[0].message

        #st.write_stream(response)
        


        tool_calls = response_message.tool_calls
        if tool_calls:
            # Step 3: call the function
            # Note: the JSON response may not always be valid; be sure to handle errrs
            available_functions = {
                "get_images_for_video" : get_images_for_video, 
                "get_sounds_for_video" : get_sounds_for_video,
                "get_documents" : get_documents, 
                "edit_video": edit_video
            }  # only one function in this example, but you can have multiple
            messages.append(response_message)  # extend conversation with assistant's reply
            # Step 4: send the info for each function call and function response to the model
            for idx, tool_call in enumerate(tool_calls):

                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)

                function_args = json.loads(response_message.tool_calls[idx].function.arguments)
                function_response = function_to_call(**function_args)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )  # extend conversation with function response

            second_response = client.chat.completions.create(
                model="gpt-4",
                messages=messages
            ) 

            if response_message.tool_calls[0].function.name == "get_images_for_video":
                with st.chat_message("assistant"):
                    col1, col2, col3 = st.columns([1,1,1]) 
                    with col1:
                        st.image('./scene0_.jpg', caption=function_args.get("image1"))
                    with col2:
                        st.image('./scene1_.jpg', caption=function_args.get("image2"))
                    with col3:
                        st.image('./scene2_.jpg', caption=function_args.get("image3"))
                
            
            if response_message.tool_calls[0].function.name == "get_sounds_for_video":
                with st.chat_message("assistant"): 
                    st.audio('./scene1_0.wav', format="audio/wav", start_time=0)
                    st.audio('./scene1_1.wav', format="audio/wav", start_time=0)
                    st.audio('./scene1_2.wav', format="audio/wav", start_time=0)

#                    st.session_state.chat_history.append(
#                    {"outputs": {"answer": st.audio('./scene1_0.wav', format="audio/wav", start_time=0)}, 
#                     "outputs": {"answer": st.audio('./scene1_1.wav', format="audio/wav", start_time=0)}, 
#                     "outputs": {"answer": st.audio('./scene1_2.wav', format="audio/wav", start_time=0)}}
#            )

            if response_message.tool_calls[0].function.name == "edit_video": 
                col1, col2, col3 = st.columns([2,1,1]) 
                with col1: 
                    with st.chat_message("assistant"): 
                        st.video("currentVideo.mp4", format="video/mp4") 


            st.write(second_response.choices[0].message.content)

            st.session_state.chat_history.append(
                {"inputs": {"question": user_input},
                "outputs": {"answer": second_response.choices[0].message.content}}
            )
        else: 
            messages.append(response_message)
            st.chat_message("assistant").markdown(response.choices[0].message.content)
            st.session_state.chat_history.append(
                {"inputs": {"question": user_input},
                "outputs": {"answer": response.choices[0].message.content}}
            )

