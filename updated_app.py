import streamlit as st
import pandas as pd
import os
import cv2
import json
import textwrap

def get_graph_knowledge(person):
    with open('celeb_graph_knowledge.json', 'r') as fp:
        data = json.load(fp)

    if person in data:
        return data[person]
    else:
        return None

def get_name(img_id):
    with open('celeb_boxes_10k.json', 'r') as fp:
        data = json.load(fp)

    celeb_names = []
    if img_id in data:
        for i in data[img_id]['names']:
            celeb_names.append(i)

    return celeb_names

def format_information(information):
    formatted_info = " ".join(information)
    formatted_info = formatted_info.capitalize() + "."
    formatted_info = textwrap.fill(formatted_info, width=60)
    return formatted_info



selected_option = 'Annotation'

img_folder = './img/'
results = [os.path.join(img_folder, img_name) for img_name in os.listdir(img_folder)]

if not results:
    st.markdown("<h3 style='text-align: center;'>Congratulations, you have nothing to label!​​​​​​​​​​​​​​​​​​​​​ &#x1F60a;</h3>", unsafe_allow_html=True)

annotations = pd.read_excel('annotations.xlsx', engine='openpyxl') if os.path.isfile('annotations.xlsx') else pd.DataFrame(columns=['ID', 'Image-text relation', 'Hate', 'Discard', 'Notes'])

col1, col2 = st.columns([2, 1])
st.title("Hate Speech Annotation")
st.markdown("<h2>What kind of hateful meme is this?</h2>", unsafe_allow_html=True)
st.markdown(
            "Please enter the necessary information and select the appropriate options to annotate the meme:"
        )
for result in results:
    img_id = result
    img_name = result
    img_score = result

    img = cv2.imread(img_name)
    if img is None:
        print("Failed to load image")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    height, width, channels = img.shape

    container = st.container()

    with container:
        col1 = container.columns([2])[0]
        col2 = container.columns([1])[0]

        col1.image(result, width=int(width*0.5))
        #col1.text("Image Path: " + img_id)
        celebs = get_name(img_id[6:])
        for i in celebs:
            col1.text("Celebrity name: {}".format(i))
            info = get_graph_knowledge(i)
            if info:
                col1.text("Information:")
                formatted_info = format_information(info)
                col1.text(formatted_info)

            else:
                col1.text("No information available for this celebrity.")


        st.markdown("<h2>What kind of hateful meme is this?</h2>", unsafe_allow_html=True)
        st.markdown(
            "Please enter the necessary information and select the appropriate options to annotate the meme:"
        )
        image_text_relation = col2.radio('Image-text relation', ['none', 'neutral', 'needs context', 'text supports hate', 'image supports hate'], key="{}.9".format(img_id))

        hate_levels = ['0 - Non hateful', '1', '2', '3', '4', '5', '6  - Hateful']
        selected_level = col2.radio('Hatefulness scale (from 0=Non hateful to 6=Hateful)', options=hate_levels, key="{}.11".format(img_id), index=0)

        col2.markdown('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        col2.markdown('<style>.row-widget.stRadio div div{padding:0px 8px;}</style>', unsafe_allow_html=True)

        discard = col2.checkbox('Press here if you want to discard this meme!', key="{}.12".format(img_id))
        notes = col2.text_area('Notes', key="{}.13".format(img_id))

        if col2.button('Submit', key="{}.14".format(img_id)):
            annotation_row = annotations.loc[annotations['ID'] == img_id[6:]]
            if annotation_row.empty:
                new_annotation = pd.DataFrame(
                    {'ID': [img_id[6:]], 'Image-text relation': [image_text_relation], 'Hatefulness scale': [selected_level],
                     'Discard': [discard], 'Notes': [notes]})
                annotations = pd.concat([annotations, new_annotation], ignore_index=True)

            else:
                annotation_row_index = annotation_row.index[0]
                annotations.loc[annotation_row_index, 'Image-text relation'] = image_text_relation
                annotations.loc[annotation_row_index, 'Hatefulness scale'] = selected_level
                annotations.loc[annotation_row_index, 'Discard'] = discard
                annotations.loc[annotation_row_index, 'Notes'] = notes

            annotations.to_excel('annotations.xlsx', index=False)
            col2.success('Annotation submitted successfully!'.format(image_text_relation, hate_levels))
# Display the annotations DataFrame
st.write('Annotations:', annotations)
