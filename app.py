'''
In this annotation tool, the annotator is given the image WITH celebrity information (name, graph_knowledge)
'''


import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import json
import cv2
import PIL as pil
import io
import os
import random
import sqlite3
import emoji
import xlsxwriter
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import seaborn as sns
import socket
import ssl
import requests
import ast

def get_graph_knowledge(person):
    
    with open('celeb_graph_knowledge.json', 'r') as fp:
        data = json.load(fp)
    return data[person]


def get_name(img_id):

    with open('celeb_boxes_10k.json', 'r') as fp:
        data = json.load(fp)

    celeb_names = []
    for i in data[img_id]['names']:
        celeb_names.append(i)#data[img_id]['names'][0]

    return celeb_names



sns.set_style('darkgrid')

option1 = ' '
option2 = 'Annotation'
selected_option = st.sidebar.selectbox(
    'Choose a view',
    (option1, option2)
)

img_path = './img/'


# ----- Annotation -----
if selected_option == option2: 
    st.markdown("<h1 style='text-align: center;'>Hello! Please label some of the memes below.</h1>", unsafe_allow_html=True)

    results = []

    check = False
    for result in os.listdir(img_path):
        img_name = result
        results.append(os.path.join(img_path, img_name))
    
    if(len(results) == 0):
        st.markdown("<h3 style='text-align: center;'>Congratulations, you have nothing to label!​​​​​​​​​​​​​​​​​​​​​ &#x1F60a;</h3>", unsafe_allow_html=True)


    for result in results:

        img_id = result
        img_name = result
        img_score = result
        img = cv2.imread(img_name)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        height, width, channels = img.shape
        
        col1, col2 = st.beta_columns(2)
        with col1:
            st.image(img, width=int(width*0.5))
            #st.text(img_id)
            celebs = get_name(img_id[6:])
            for i in celebs:
                st.text("Celebrity name : {}".format(i))#get_name(img_id[6:])
                info = get_graph_knowledge(i)#get_name(img_id[6:])
                new_title = '<p style="font-family:sans-serif; color: #2e4053   ; font-size: 15px;"> ' + info + '</p>'
                st.markdown(new_title, unsafe_allow_html=True)
            #st.markdown("Information : {}".format(get_graph_knowledge(get_name(img_id[6:]))))

        with col2:
            st.markdown("<h2>What kind of hateful meme is this?</h2>", unsafe_allow_html=True)

            # Difficulties with translation and processing of the meme
            # difficulties_checkbox = st.checkbox('Difficulties with translation and processing of the meme', key="{}.1".format(img_id))
            # if(difficulties_checkbox == True):
            #     ambiguity = st.checkbox('Ambiguity in the original meme (phonetic ambiguities included) could not be translated', key="{}.2".format(img_id))
            #     if(ambiguity == True):
            #         ambiguity_could = st.checkbox('Could be translated', key="{}.3".format(img_id))
            #         ambiguity_couldnot = st.checkbox('Could not be translated', key="{}.4".format(img_id))

            #     not_understood = st.checkbox('I am not sure I understood the original meme', key="{}.5".format(img_id))
            #     historical_knowledge = st.checkbox('Historical and cultural knowledge needed to understand', key="{}.6".format(img_id))
            #     cofounder = st.checkbox('I guess this is a confounder', key="{}.7".format(img_id))
            #     other_reason = st.checkbox('Other reason', key="{}.8".format(img_id))
            
            # else :
            # Image-text relation
            image_text_relation = st.radio('Image-text relation', ['None', 'Supporing', 'Need'], key="{}.9".format(img_id))

            # Translation
            #translation = st.text_area('Translation', key="{}.10".format(img_id))

            # Hate
            hate = st.selectbox('Hateful', ['Hateful', 'Not hateful'], key="{}.11".format(img_id))
            
            # Discard
            discard = st.checkbox('Press here if you want to discard this meme!', key="{}.12".format(img_id))

            # Notes
            notes = st.text_area('Notes', key="{}.13".format(img_id))
        
            if(st.button('Submit', key="{}.14".format(img_id))):

                if(os.path.isfile('annotations.xlsx')):
                    annotations = pd.read_excel('annotations.xlsx')

                else:
                    annotations = pd.DataFrame(columns = ['ID', 'Image-text relation', 'Hate', 'Discard', 'Notes'])
                    
                if(img_id[6:] not in annotations['ID'].unique()):
                    annotations.loc[len(annotations), 'ID'] = img_id[6:]

                # difficulties_hanlder = ''
                # if(difficulties_checkbox == True):
                #     if(ambiguity == True):
                #         difficulties_hanlder += 'Ambiguity,'
                #         if(ambiguity_could == True):
                #             difficulties_hanlder += 'Ambiguity and could be translated,'
                #         if(ambiguity_couldnot == True):
                #             difficulties_hanlder += 'Ambiguity and could not be translated,'
                #     if(not_understood == True):
                #         difficulties_hanlder += 'Not understood,'
                #     if(historical_knowledge == True):
                #         difficulties_hanlder += 'Historical and cultural knowledge needed,'
                #     if(cofounder == True):
                #         difficulties_hanlder += 'Cofounder,'
                #     if(other_reason == True):
                #         difficulties_hanlder += 'Other reason,'
                #     annotations.loc[annotations.ID == img_id[6:], "Difficulties"] = difficulties_hanlder

                #else:

                image_text_relation_handler = ''
                #translation_handler = ''
                hate_handler = ''
                discared_handler = ''
                notes_handler = ''

                image_text_relation_handler = str(image_text_relation)
                
                #translation_handler = translation
                
                hate_handler = hate
                
                if(discard == True):
                    discared_handler = 'The annotator decided to discard this meme'
                
                notes_handler = notes

                annotations.loc[annotations.ID == img_id[6:], "Image-text relation"] = image_text_relation_handler
                #annotations.loc[annotations.ID == img_id[6:], "Translation"] = translation_handler
                annotations.loc[annotations.ID == img_id[6:], "Hate"] = hate_handler
                annotations.loc[annotations.ID == img_id[6:], "Discard"] = discared_handler
                annotations.loc[annotations.ID == img_id[6:], "Notes"] = notes_handler

                writer = pd.ExcelWriter('annotations.xlsx',engine = 'xlsxwriter')
                annotations.to_excel(writer,sheet_name = 'Sheet1')
                writer.save()




