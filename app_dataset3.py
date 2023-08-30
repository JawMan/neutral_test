import base64

import numpy as np
import streamlit as st
import pandas as pd
import os
import cv2
import json
import textwrap
import matplotlib.pyplot as plt
from matplotlib import patches
from datetime import datetime, timedelta
import time
import datetime
import dropbox
from dropbox.exceptions import AuthError, ApiError
import streamlit.components.v1 as components
from pdf2image import convert_from_bytes
import base64
import fitz
from PIL import Image
from io import BytesIO
import subprocess

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

def format_duration(duration):
    seconds = int(duration)
    formatted_time = str(timedelta(seconds=seconds))
    return formatted_time

def on_number_click(number, decision_parts):
    if number not in decision_parts:
        decision_parts.append(number)
        st.text_input('What exactly makes this meme hateful or non hateful from your perspective? (prominent tokens or elements of image)', value=', '.join(decision_parts))

def on_zero_click(decision_parts):
    if '0' not in decision_parts:
        decision_parts.append('0')
        st.text_input('What exactly makes this meme hateful or non-hateful from your perspective? (prominent tokens or elements of image)', value=', '.join(decision_parts))

def generate_dropbox_token():
    curl_command = "curl https://api.dropbox.com/oauth2/token -d grant_type=refresh_token -d refresh_token=5vBQfudJIkkAAAAAAAAAAbfsc6GTrQMg8nQCVG51gvDS35iFWzwQhMcz--C_0ynU -u xnq24rlmf2m8epf:jvnxwa6p07i7ldu"

    try:
        # execute curl command and capture its output
        output = subprocess.check_output(curl_command.split(), text=True)
        # extract token from the output
        token = output.split('"')[3]

        return token
    except subprocess.CalledProcessError as e:
        st.error("An error occurred while generating the Dropbox token.")
        st.error(e)
        return None

def upload_to_dropbox(annotations, access_token):
    try:
        # create Dropbox client
        dbx = dropbox.Dropbox(access_token)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        annotations_file = f"annotations_{timestamp}.xlsx"

        # save annotation table in Dropbox
        dropbox_path = f"/{annotations_file}"
        # save annotation table as local file
        annotations.to_excel(annotations_file, index=False)
        # upload annotation table to Dropbox
        with open(annotations_file, "rb") as file:
            dbx.files_upload(file.read(), dropbox_path)

        # delete local file after successful uploading
        os.remove(annotations_file)

        return True
    except (dropbox.exceptions.AuthError, dropbox.exceptions.ApiError) as e:
        st.error("An error occurred while uploading the annotation table to Dropbox.")
        st.error(str(e))
        return False

def initialize_session_state():
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0

def initialize_session_state_intro():
    if 'pdf_downloaded' not in st.session_state:
        st.session_state.pdf_downloaded = False

    if 'go_to_annotation' not in st.session_state:
        st.session_state.go_to_annotation = False

def show_image_fin(img_id, col):
    img = cv2.imread(img_id)
    if img is None:
        print("Failed to load image")
        return

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    col.image(img, use_column_width=True)

def show_image(image_path):
    st.image(image_path, width=500)

def convert_pdf_to_image(pdf_content):
    # convert PDF to image using PyMuPDF
    pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
    page = pdf_document.load_page(0)  # Load the first page
    image = page.get_pixmap(alpha=False)

    # convert Pixmap to bytes using PIL library
    image_bytes = image.tobytes()

    return image_bytes

def show_introduction():
    st.title("Welcome to the Annotation Tool!")
    st.write("This is the introduction section.")

    with open("annotation_tool_instructions.pdf", "rb") as file:
        file_content = file.read()
        if st.download_button(
            label="**Download Instructions (PDF)**",
            data=file_content,
            file_name="annotation_tool_instructions.pdf",
            mime="application/pdf"
        ):
            st.session_state.pdf_downloaded = True

            #st.cache_resource.pdf_downloaded = True

    # display preview of PDF file
    st.markdown("**Please download and read the guidelines carefully before starting the annotation process!**\n\n")
    st.markdown("### Example of meme annotation")
    container = st.container()
    with container:
        col1, col2 = st.columns([1, 2])
        image = Image.open('examples/KaceyMusgraves1_FB.png')


        col1.image(image, caption='Example meme #1')

        video_file = open('annotation_submit_next.mp4', 'rb')
        video_bytes = video_file.read()

        col2.video(video_bytes)
        st.markdown("### Have you downloaded the above PDF and read the instructions carefully?\n")
        if st.session_state.pdf_downloaded:
            if st.button("Alright, you've just downloaded the PDF!\n"
                         "Please move on to the 'Annotation' section.\n"
                         "You can either click here or select 'Annotation' on the left side!"):
                # set 'go_to_annotation' flag to indicate that user should move to the annotation section
                st.session_state.go_to_annotation = True
                st.experimental_set_query_params(section="Annotation")


    # image_content = convert_pdf_to_image(file_content)
    # if image_content:
    #     image = Image.open(BytesIO(image_content))
    #     st.image(image, width=700)
    # else:
    #     st.write("Unable to preview the PDF.")


def scroll_to_top():
    # scroll to top using custom HTML
    js = '''
    <script>
        var body = window.parent.document.querySelector(".main");
        console.log(body);
        body.scrollTop = 0;
    </script>
    '''
    st.components.v1.html(js)

def show_annotation():
    st.title("Meme Annotation")


    #selected_option = 'Annotation'
    #img_folder = './jm_memes/Dataset1'
    #img_folder = './jm_memes/Dataset2'
    img_folder = './jm_memes/Dataset3'
    #img_folder = './jm_memes/Dataset4'

    results = [os.path.join(img_folder, img_name) for img_name in os.listdir(img_folder) if img_name.endswith((".jpeg", ".jpg", ".png"))]
    if not results:
        st.markdown("<h3 style='text-align: center;'>Congratulations, you have nothing to label!​​​​​​​​​​​​​​​​​​​​​ &#x1F60a;</h3>", unsafe_allow_html=True)

    annotations = pd.read_excel('annotations.xlsx', engine='openpyxl') if os.path.isfile('annotations.xlsx') else pd.DataFrame(columns=['ID', 'Image-text relation','Modality towards hate', 'Decision part','Hatefulness scale', 'Confidence score', 'Discard'])

    initialize_session_state()

    current_index = st.session_state.current_index

    if current_index >= len(results):
        current_index = 0

    img_id = results[current_index]
    img_index = current_index + 1

    with open('assets/style.css', 'r') as css_file:
        st.markdown(f'<style>{css_file.read()}</style>', unsafe_allow_html=True)

    container = st.container()
    container.column_width = 'auto'


    with container:
        #col1, col2 = st.columns([100, 1])
        col1 = container.columns([2])[0]
        col2 = container.columns([1])[0]
        # col3 = container.columns([2])[0]
        col1.markdown("<h2>What kind of hateful meme is this?</h2>", unsafe_allow_html=True)
        col1.markdown(
            "Please enter the necessary information and select the appropriate options to annotate the meme:"
        )

        # anchor tag to create a hyperlink to displayed image
        col1.markdown(f'<a id="image_{img_index}" class="scroll-to-top"></a>', unsafe_allow_html=True)

        show_image_fin(img_id, col1)

        with open('assets/style.css') as f:
            col2.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        next_button = col2.button("**Next**", key='next_button', help="Next Button", use_container_width=True, on_click=scroll_to_top)
        #next_button = st.markdown("<button class='custom-next-button'>Next</button>", unsafe_allow_html=True)

        # update current index if the 'Next' button is clicked

        if next_button:
            st.session_state.current_index += 1
            if st.session_state.current_index >= len(results):
                st.session_state.current_index = 0

            col2.empty()  # empty element as anchor
            col2.markdown("<h2 style='visibility:hidden;'>Top of Page</h2>", unsafe_allow_html=True)  # Hide the anchor
            st.experimental_rerun()
        # col2.button("Next", key=f'next_button_{img_id}', help="Next Button")

        # add number input textbox for jumping to specific meme
        jump_to_meme = col2.number_input("Jump to meme (Please enter a number)", value=1, min_value=1,
                                         max_value=len(results))

        if col2.button("Go to meme", key='go_to_meme_button', on_click=scroll_to_top):
            # update current index to jump to the selected meme
            st.session_state.current_index = jump_to_meme - 1
            # rerun the app to display the selected meme
            st.experimental_rerun()
        # display information about the current meme index and number of memes in total
        st.info(f"Current meme: {st.session_state.current_index + 1} of {len(results)}")
        missing_memes = len(results) - st.session_state.current_index - 1
        st.info(f"Missing memes: {missing_memes}")

        col1.write("**Image-text relation**\n\n"
                  "The definition of 'image-text relation' describes the connection\n"
                  "between the accompanying text and the image in a meme or other visual communication.\n"
                  "It investigates how the language and image interact to convey a specific\n"
                  "meaning or message. Understanding the image-text relationship in the context\n"
                  "of offensive memes is crucial for assessing the purpose and effects of such content.\n\n"
                  "**Please select one or more of the following options:**")
        image_text_relation_options = ['neutral', 'needs context', 'text supports image', 'image supports text']
        with col1:
            cols = st.columns(5)
            selected_options = []
            for i, option in enumerate(image_text_relation_options):
                key = f"image_text_relation_{img_id}_{i}_{option}"  # generate unique key
                selected = cols[i % 4].checkbox(option, key=key)
                if selected:
                    selected_options.append(option)
            image_text_relation = ', '.join(selected_options)

        modality_towards_hate = col1.radio('**Modality contributes towards hate**',
                                           ['none', 'text supports hate', 'image supports hate',
                                            'text&image supports hate'], key="{}.9".format(img_id))

        decision_parts = col1.text_area(
            '**What exactly makes this meme hateful or non hateful from your perspective? (prominent tokens or elements of meme)**',
            key="{}.14".format(img_id))

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

        # st.markdown("<h2>What kind of hateful meme is this?</h2>", unsafe_allow_html=True)
        # st.markdown(
        #     "Please enter the necessary information and select the appropriate options to annotate the meme:"
        # )

        hate_levels = ['0 - Non hateful', '1', '2', '3', '4', '5 - Hateful']
        selected_level = col1.radio('**Hatefulness scale (Choose from 0=Non hateful to 5=Hateful)**', options=hate_levels,
                                    key="{}.11".format(img_id), index=0)

        col1.markdown('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        col1.markdown('<style>.row-widget.stRadio div div{padding:0px 8px;}</style>', unsafe_allow_html=True)

        confidence_levels = ['0 - Not confident ', '1', '2', '3', '4', '5 - Confident']
        selected_confidence = col1.radio(
            '**Confidence score - How much confident are you by giving that score?\n'
            '(Choose from 0=Not confident to 5=Confident)**',
            options=confidence_levels,
            key="{}.12".format(img_id), index=0)

        col1.markdown('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)
        col1.markdown('<style>.row-widget.stRadio div div{padding:0px 6px;}</style>', unsafe_allow_html=True)
        discard = col1.checkbox('*Press here if you want to discard this meme!*', key="{}.13".format(img_id))

        # timer-related variables
        session_state = st.session_state
        if 'start_time' not in session_state:
            session_state.start_time = None

        if img_index == 1:
            if col1.button('**Submit t1**', key="{}.15".format(img_id)):
                if session_state.start_time is None:
                    session_state.start_time = time.time()
                    # st.write('Timer started.')
                else:
                    st.warning(' ')
                    # annotate and save the existing data
                annotation_row = annotations.loc[annotations['ID'] == img_id[6:]]
                # checkbox with selected checkboxes
                #checkbox = [str(i) for i, value in enumerate(image_text_relation_options) if value]
                if annotation_row.empty:
                    new_annotation = pd.DataFrame({
                        'ID': [img_id[6:]],
                        'Image-text relation': [image_text_relation],
                        'Modality towards hate': [modality_towards_hate],
                        'Decision part': [decision_parts],
                        'Hatefulness scale': [selected_level],
                        'Confidence score': [selected_confidence],
                        'Discard': [discard]
                    })
                    annotations = pd.concat([annotations, new_annotation], ignore_index=True)
                else:
                    annotation_row_index = annotation_row.index[0]
                    annotations.loc[annotation_row_index, 'Image-text relation'] = image_text_relation
                    annotations.loc[annotation_row_index, 'Modality towards hate'] = modality_towards_hate
                    annotations.loc[annotation_row_index, 'Decision part'] = decision_parts
                    annotations.loc[annotation_row_index, 'Hatefulness scale'] = selected_level
                    annotations.loc[annotation_row_index, 'Confidence score'] = selected_confidence
                    annotations.loc[annotation_row_index, 'Discard'] = discard
                annotations.to_excel('annotations.xlsx', index=False)
                col1.success('Annotation submitted successfully!')
        elif img_index == 2:
            if col1.button('Submit t2', key="{}.16".format(img_id)):
                if session_state.start_time is not None:
                    end_time = time.time()
                    duration = round(end_time - session_state.start_time, 2)
                    formatted_duration = format_duration(duration)
                    # st.write(f'Timer stopped. Duration: {formatted_duration}')

                    # annotate and save formatted elapsed time
                    annotation_row = annotations.loc[annotations['ID'] == img_id[6:]]
                    # update checkbox with selected checkboxes
                    #checkbox = [str(i) for i, value in enumerate(image_text_relation_options) if value]
                    if annotation_row.empty:
                        new_annotation = pd.DataFrame({
                            'ID': [img_id[6:]],
                            'Image-text relation': [image_text_relation],
                            'Modality towards hate': [modality_towards_hate],
                            'Decision part': [decision_parts],
                            'Hatefulness scale': [selected_level],
                            'Confidence score': [selected_confidence],
                            'Discard': [discard],
                            'Elapsed Time (s)': [formatted_duration]
                        })
                        annotations = pd.concat([annotations, new_annotation], ignore_index=True)
                    else:
                        annotation_row_index = annotation_row.index[0]
                        annotations.loc[annotation_row_index, 'Image-text relation'] = image_text_relation
                        annotations.loc[annotation_row_index, 'Modality towards hate'] = modality_towards_hate
                        annotations.loc[annotation_row_index, 'Decision part'] = decision_parts
                        annotations.loc[annotation_row_index, 'Hatefulness scale'] = selected_level
                        annotations.loc[annotation_row_index, 'Confidence score'] = selected_confidence
                        annotations.loc[annotation_row_index, 'Discard'] = discard
                        annotations.loc[
                            annotation_row_index, 'Elapsed Time (s)'] = formatted_duration

                    annotations.to_excel('annotations.xlsx', index=False)
                    col1.success('Annotation submitted successfully!')

        else:
            if col1.button('Submit', key="{}.17".format(img_id)):
                annotation_row = annotations.loc[annotations['ID'] == img_id[6:]]
                # update checkbox with selected checkboxes
                #checkbox = [str(i) for i, value in enumerate(image_text_relation_options) if value]
                if annotation_row.empty:
                    new_annotation = pd.DataFrame({
                        'ID': [img_id[6:]],
                        'Image-text relation': [image_text_relation],
                        'Modality towards hate': [modality_towards_hate],
                        'Decision part': [decision_parts],
                        'Hatefulness scale': [selected_level],
                        'Confidence score': [selected_confidence],
                        'Discard': [discard]
                    })
                    annotations = pd.concat([annotations, new_annotation], ignore_index=True)
                else:
                    annotation_row_index = annotation_row.index[0]
                    annotations.loc[annotation_row_index, 'Image-text relation'] = image_text_relation
                    annotations.loc[annotation_row_index, 'Modality towards hate'] = modality_towards_hate
                    annotations.loc[annotation_row_index, 'Decision part'] = decision_parts
                    annotations.loc[annotation_row_index, 'Hatefulness scale'] = selected_level
                    annotations.loc[annotation_row_index, 'Confidence score'] = selected_confidence
                    annotations.loc[annotation_row_index, 'Discard'] = discard

                annotations.to_excel('annotations.xlsx', index=False)
                col1.success('Annotation submitted successfully!')


    # load annotation table from the file (if exists)
    annotations_file = "annotations.xlsx"
    annotations = pd.read_excel(annotations_file) if os.path.isfile(annotations_file) else pd.DataFrame()

    # st.markdown("<h3>Annotation Results</h3>", unsafe_allow_html=True)
    # st.write('Annotations:', annotations)
    st.subheader('Annotations')
    st.dataframe(annotations)
    # st.write(annotations)
    if st.button("Generate Dropbox Token"):
        # generate the Dropbox token
        token = generate_dropbox_token()
        if token:
            st.success("Dropbox token generated successfully!")
            st.write("**Please copy following token to upload your results:**", token)
    # prompt user: 'enter the Dropbox access token'
    dropbox_access_token = st.text_input("Enter your Dropbox access token")

    if st.button("Upload Results"):
        if dropbox_access_token:
            success = upload_to_dropbox(annotations, dropbox_access_token)
            if success:
                st.success("Annotation table uploaded successfully! Thanks for your patience :)")
        else:
            st.warning("Please enter your Dropbox access token.")


def main():
    # apply custom CSS styles
    st.markdown('<link href="style.css" rel="stylesheet">', unsafe_allow_html=True)

    current_section = st.experimental_get_query_params().get("section", ["Introduction"])[0]

    option = st.sidebar.radio("Select an option", ("Introduction", "Annotation"), index=0 if current_section == "Introduction" else 1)
    initialize_session_state_intro()

    # display selected section 'Introduction'
    if option == "Introduction":
        show_introduction()
        if st.session_state.go_to_annotation:
            # switch the sidebar option to "Annotation"
            st.experimental_set_query_params(section="Annotation")
            show_annotation()
            # reset the 'go_to_annotation' flag to avoid automatically going to the annotation section on subsequent visits
            st.session_state.go_to_annotation = False

    elif option == "Annotation":
        show_annotation()

if __name__ == "__main__":
    main()