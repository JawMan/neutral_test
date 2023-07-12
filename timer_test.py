import streamlit as st
import time
from datetime import datetime, timedelta

def save_time_duration(duration):
    with open('time.txt', 'w') as file:
        file.write(str(duration))

def format_duration(duration):
    seconds = int(duration)
    formatted_time = str(timedelta(seconds=seconds))
    return formatted_time

def main():
    session_state = st.session_state
    if 'start_time' not in session_state:
        session_state.start_time = None

    st.title('Timer Example')

    if st.button('Submit 1'):
        if session_state.start_time is None:
            session_state.start_time = time.time()
            st.write('Timer started.')
        else:
            st.warning('Timer is already started.')

    if st.button('Submit 2') and session_state.start_time is not None:
        end_time = time.time()
        duration = round(end_time - session_state.start_time, 2)
        formatted_duration = format_duration(duration)
        st.write(f'Timer stopped. Duration: {formatted_duration}')
        save_time_duration(formatted_duration)
        session_state.start_time = None

if __name__ == '__main__':
    main()
