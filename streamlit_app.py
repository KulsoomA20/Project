import streamlit as st
from transformers import pipeline, set_seed
import nltk
from io import BytesIO
from datetime import datetime
import random
import os
os.environ["STREAMLIT_WATCH_USE_POLLING"] = "true"



nltk.download('punkt_tab')
nltk.download('stopwords')

# Streamlit page config
st.set_page_config(page_title=" AI Dungeon Story Generator", layout="centered")

# Sidebar Instructions
st.sidebar.title("🛠 How to Use")
st.sidebar.markdown("""
1. Choose your genre  
2. Describe your idea  
3. Hit Enter or press Generate  
4. Enjoy your tale 
""")
st.sidebar.markdown("Made with using GPT-Neo")

# Title and intro
st.title(" AI Dungeon Story Generator")
st.markdown("""
Welcome, storyteller! Choose your genre, craft a spark of imagination,  
and let the AI weave the rest. 
""")

# Genre Templates
opening_lines = {
    "Fantasy": "In a land forgotten by time, in the year {}...".format(random.randint(1000, 1959)),
    "Mystery": "It started on a foggy night when",
    "Sci-Fi": "In the year {}, humanity discovered that".format(random.randint(1000, 1959)),
    "Horror": "There was a house no one dared enter, until",
    "Romance": "They met when the rain fell hardest, and"
}

#  GPT-Neo Model
@st.cache_resource
def load_model():
    return pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")

generator = load_model()


def create_prompt(genre, user_input):
    intro = opening_lines.get(genre, "Once upon a time,")
    return f"{intro} {user_input.strip().capitalize()} "

#ending to a story

def add_ending(story):
    if "The end" in story:
        return story
    return story.strip() + "\n\nAnd so, the tale finds its close — not with silence, but with echoes in the wind, reminding all who hear it that every story, once begun, must someday be remembered. The end."

# multiple stories

def generate_stories(prompt, num_stories=3):
    set_seed(42)
    outputs = generator(
        prompt,
        max_length=350,
        num_return_sequences=num_stories,
        do_sample=True,
        temperature=0.85,
        top_p=0.9,
        top_k=40,
        repetition_penalty=1.15,
        pad_token_id=50256
    )
    return [add_ending(output['generated_text'].strip()) for output in outputs]

# Main form UI with Enter-to-submit and attractive text input
with st.form("story_form", clear_on_submit=False):
    col1, col2 = st.columns([1, 2])
    with col1:
        genre = st.selectbox("🎭 Choose a genre", list(opening_lines.keys()))
    with col2:
        user_input = st.text_area(
            "📝 Describe your story idea:",
            placeholder="An elf finds a mysterious amulet near a cursed forest...",
            height=120,
            key="story_input"
        )
    submitted = st.form_submit_button("✨ Generate Stories")


st.markdown("""
    <script>
    const textarea = window.parent.document.querySelector('textarea');
    textarea.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            window.parent.document.querySelector('button[kind=\"primary\"]').click();
        }
    });
    </script>
""", unsafe_allow_html=True)

# story generation
if submitted:
    if not user_input.strip():
        st.warning("Please describe your story idea.")
    else:
        st.markdown("---")
        st.markdown("## 📜 Your Generated Stories")
        prompt = create_prompt(genre, user_input)
        stories = generate_stories(prompt)

        for i, story in enumerate(stories, 1):
            st.markdown(f"### ✨ Story {i}")
            st.markdown(
                f"""
                <div style=\"background-color:#222; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); color: #f9f9f9; font-family: 'Georgia', serif; font-size: 16px; line-height: 1.6;\">
                    {story}
                </div>
                """, unsafe_allow_html=True
            )

        buffer = BytesIO()
        full_text = "\n\n".join(stories)
        buffer.write(full_text.encode('utf-8'))
        buffer.seek(0)
        filename = f"{genre.lower()}_stories_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

        st.download_button(
            label="📅 Download Stories",
            data=buffer,
            file_name=filename,
            mime="text/plain"
        )
