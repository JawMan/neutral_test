import streamlit as st
import os

# Define the content for the Introduction section
def show_introduction():
    st.title("Welcome to the Annotation Tool!")
    st.write("This is the introduction section.")

# Define the path to the dataset folder
dataset_folder = "jm_memes/dataset1"

# Get the list of image file paths in the dataset folder
image_files = sorted([os.path.join(dataset_folder, file) for file in os.listdir(dataset_folder) if file.endswith((".jpg", ".png"))])

# Track the current index of the displayed image
current_index = 0

# Function to display the image
def show_image(image_path):
    st.image(image_path, width=500)

# Define the content for the Annotation section
def show_annotation():
    st.title("Meme Annotation")
    st.markdown("<h2>What kind of hateful meme is this?</h2>", unsafe_allow_html=True)

    # Initialize session state for the image index
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0

    # Display the current image
    show_image(image_files[st.session_state.current_index])

    # Display the Next button next to the image
    col1, col2 = st.columns([3, 1])
    next_button = col2.button("Next", key='next_button', help="Next Button")

    # Apply custom CSS to the Next button
    next_button_style = """
        <style>
        .next-button {
            background-color: red;
            color: white;
        }
        </style>
        """
    col2.markdown(next_button_style, unsafe_allow_html=True)

    # Update the current index when the Next button is clicked
    if next_button:
        st.session_state.current_index += 1
        if st.session_state.current_index >= len(image_files):
            st.session_state.current_index = 0

    st.markdown(
        "Please enter the necessary information and select the appropriate options to annotate the meme:"
    )

# Main function to run the Streamlit app
def main():
    # Sidebar options
    option = st.sidebar.radio("Select an option", ("Introduction", "Annotation"))

    # Display the selected section
    if option == "Introduction":
        show_introduction()
    elif option == "Annotation":
        show_annotation()

if __name__ == "__main__":
    main()
