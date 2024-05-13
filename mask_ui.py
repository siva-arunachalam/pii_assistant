from textwrap import dedent
import streamlit as st
import streamlit.components.v1 as components
from mask_utils import highlight_text, mask_text
from style import text_box_style
from masking_agent import PIITagger

def tag_pii(model_choice: str, input_text: str) -> None:
    """
    Masks the PII in the given input text using the specified model and updates the session state.
    
    Args:
        model_choice (str): The name of the model to use for masking.
        input_text (str): The input text to mask.
    """
    try:
        pii_tagger = PIITagger()
        response = pii_tagger.tag_pii_elements(model_choice, input_text)
        tagged_text = response['transformed_data'].tagged_text
        identifiers = response['transformed_data'].identifiers
        
        st.session_state.tagged_text = tagged_text
        st.session_state.highlighted_text = highlight_text(tagged_text=tagged_text)
        st.session_state.identifiers = identifiers
    except Exception as e:
        st.error(f"Error tagging PII for the input text: {str(e)}")


def mask_pii():
    try:
        tagged_text = st.session_state.tagged_text
        identifiers_dict = st.session_state.identifiers.dict()
        st.session_state.masked_text, st.session_state.masked_text_with_highlights = mask_text(tagged_text, identifiers_dict)
    except Exception as e:
        st.error(f"Error masking PII elements: {str(e)}")


demo_text = dedent(
    """It was a pleasant evening. John Doe was walking along Michigan Ave, gazing at the high-rise buildings on either side of the stream. He could not believe all of this was constructed in the early 1900s in the city of Chicago. As he continued his walk, he met Emily Johnson, an old college friend who now worked at Goldman Sachs in New York City. They decided to grab a coffee at the nearby Starbucks and reminisce about their university days.
    As they chatted, Emily mentioned her recent trip to Paris where she visited the Louvre and admired the city's beautiful architecture. John shared his experiences from a business trip to Tokyo, highlighting how the city's blend of modern and traditional elements fascinated him. He mentioned a meeting he had with executives from Sony and Toyota, discussing potential business ventures.
    """
)

# @st.cache_data()
# def load_css():
#     return open("mask/style.css", 'r').read()

st.set_page_config(
    page_title="Masking Demo", 
    page_icon=":alien:", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# import style
# css_content = load_css()
# st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)

if 'tagged_text' not in st.session_state:
    st.session_state.tagged_text = "Not Yet"
    st.session_state.identifiers = None
    st.session_state.highlighted_text = "No highlighted text yet"

st.title("Masking PII using LLMs")

col1, col2 = st.columns(2)
with col1:
    input_text = st.text_area("Original Text", value=demo_text, height=300)
    if not st.session_state.identifiers:
        model_choice = st.radio("Select LLM:", options=["GPT 3.5", "GPT 4"], horizontal=True)
        mask = st.button("Tag PII", on_click=tag_pii, args=[model_choice, input_text])

if st.session_state.identifiers: 
    with col2:
        st.write('<p style="font-weight: bold;">Output from LLM with Tags</p>', unsafe_allow_html=True)
        boxed_text = f'''<div {text_box_style}>{st.session_state.highlighted_text}</div>'''
        # st.markdown(body=boxed_text, unsafe_allow_html=True)
        components.html(boxed_text, height=600, scrolling=True)
        st.write("\n")
        mask = st.button("Mask PII", on_click=mask_pii)
    # st.subheader("Identified PII Elements")
    # st.write(st.session_state.identifiers.dict())
    # st.text_area("Tagged Text", st.session_state.tagged_text, height=400)
    if "masked_text" in st.session_state:
        st.subheader("Masked Text")
        # formatted_masked_text = f'<div style="border: 1px solid black; border-radius: 10px; background-color: #f0f0f0; padding: 10px; font-family: Helvetica; font-size: 10">{st.session_state.masked_text_with_highlights}</div>'
        formatted_masked_text = f'''<div {text_box_style}>{st.session_state.masked_text_with_highlights}</div>'''
        components.html(formatted_masked_text, height=400, scrolling=True)
