import os
import openai
import logging
import re
import streamlit as st

class StreamlitHelper:
    @staticmethod
    def hide_footer():
        hide_streamlit_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    </style>
          
                    """
        
        st.markdown(hide_streamlit_style, unsafe_allow_html=True)
