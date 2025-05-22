"""import streamlit as st
from transformers import pipeline, set_seed
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import os

# Download NLTK data
nltk.download('punkt_tab')
nltk.download('stopwords')

st.set_page_config(page_title="🧙‍♀️ AI Dungeon Story Generator", layout="centered")
st.title("🧙‍♀️ AI Dungeon Story Generator")
st.write("Craft immersive, genre-based tales powered by AI. Choose your genre, write an intro, and let the magic unfold.")

# Genre-styled adaptive templates
genre_templates = {
    "Fantasy": "In a realm where {keywords}, ",
    "Mystery": "It all began when {keywords}, ",
    "Sci-Fi": "In a future shaped by {keywords}, ",
    "Horror": "Under the shadow of {keywords}, ",
    "Romance": "As fate entwined {keywords}, "
}

# User input for genre and custom text
genre = st.selectbox("Choose a genre", list(genre_templates.keys()))
user_input = st.text_area("Describe your story idea:", placeholder="Type here", height=100)

# Load GPT-Neo model
@st.cache_resource
def load_model():
    return pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")

generator = load_model()

# Extract keywords
def extract_keywords(text, max_keywords=3):
    tokens = word_tokenize(text.lower())
    words = [word for word in tokens if word.isalpha()]
    filtered = [w for w in words if w not in stopwords.words('english')]
    return ', '.join([word.capitalize() for word in filtered[:max_keywords]]) if filtered else "mystery and wonder"

# Create stronger story prompt
def create_strong_prompt(genre, user_input):
    keywords = extract_keywords(user_input)
    base = genre_templates[genre].format(keywords=keywords)
    structure = (
        f"{base}{user_input.strip()} "
        "But one day, something unexpected happened. "
        "They faced a difficult choice. "
        "What happened next changed everything."
    )
    return structure

# Clean story output
def clean_story(text):
    text = re.sub(r'\[\d+\]', '', text)
    return text.split("...")[0].strip()

# Generate stories
def generate_stories(prompt, num=3):
    set_seed(42)
    raw_outputs = generator(
        prompt,
        max_length=350,
        num_return_sequences=num,
        do_sample=True,
        temperature=0.8,
        top_p=0.92,
        top_k=50,
        repetition_penalty=1.2,
        pad_token_id=50256
    )
    stories = []
    for output in raw_outputs:
        story = clean_story(output['generated_text'])
        stories.append(story)
    return stories

# Trigger generation
if st.button("Generate Story"):
    if not user_input.strip():
        st.warning("Please describe your story idea to generate a continuation.")
    else:
        st.markdown("### ✨ Generated Stories")
        prompt = create_strong_prompt(genre, user_input)
        results = generate_stories(prompt)

        for i, story in enumerate(results):
            st.markdown(f"#### Story #{i+1}")
            st.write(story)

            filename = f"story_{genre.lower()}_{i+1}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(story)

            with open(filename, "rb") as file:
                st.download_button(
                    label=f"📥 Download Story #{i+1}",
                    data=file,
                    file_name=filename,
                    mime="text/plain"
                )"""
import streamlit as st
import random
from transformers import pipeline, set_seed
import nltk
from io import BytesIO
from datetime import datetime

# Ensure necessary nltk data is downloaded
nltk.download('punkt')
nltk.download('stopwords')

# Streamlit page config
st.set_page_config(page_title="🧙‍♀️ AI Dungeon Story Generator", layout="centered")

# Sidebar Instructions
st.sidebar.title("🛠 How to Use")
st.sidebar.markdown("""
1. Choose your genre  
2. Describe your idea  
3. Hit Enter or press Generate  
4. Enjoy your tale 
""")
st.sidebar.markdown("Made with  using GPT-Neo")

# Title and intro
st.title("🧙‍♀️ AI Dungeon Story Generator")
st.markdown("""
Welcome, storyteller! Choose your genre, craft a spark of imagination,  
and let the AI weave the rest. 
""")

# Genre Templates
opening_lines = {
    "Fantasy": "In a land forgotten by time,",
    "Mystery": "It started on a foggy night when",
    "Sci-Fi": "In the year {}, humanity discovered that".format(random.randint(1500, 1959)),
    "Horror": "There was a house no one dared enter, until",
    "Romance": "They met when the rain fell hardest, and"
}

# Load GPT-Neo Model
@st.cache_resource
def load_model():
    return pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")

generator = load_model()

# Improved prompt creation
def create_prompt(genre, user_input):
    intro = opening_lines.get(genre, "Once upon a time,")
    return f"{intro} {user_input.strip().capitalize()} "

# Add an ending to a story

def add_ending(story):
    if "The end" in story:
        return story
    return story.strip() + "\n\nAnd so, the tale finds its close — not with silence, but with echoes in the wind, reminding all who hear it that every story, once begun, must someday be remembered. The end."

# Generate story function

def generate_story(prompt):
    set_seed(42)
    raw_output = generator(
        prompt,
        max_length=350,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.85,
        top_p=0.9,
        top_k=40,
        repetition_penalty=1.15,
        pad_token_id=50256
    )
    story_text = raw_output[0]['generated_text'].strip()
    return add_ending(story_text)

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
    submitted = st.form_submit_button("✨ Generate Story")

# JavaScript to allow Enter key to submit the form
st.markdown("""
    <script>
    const textarea = window.parent.document.querySelector('textarea');
    textarea.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            window.parent.document.querySelector('button[kind="primary"]').click();
        }
    });
    </script>
""", unsafe_allow_html=True)

# Handle story generation
if submitted:
    if not user_input.strip():
        st.warning("Please describe your story idea.")
    else:
        st.markdown("---")
        st.markdown("## 📜 Your Generated Story")
        prompt = create_prompt(genre, user_input)
        story = generate_story(prompt)

        st.markdown(
            f"""
            <div style=\"background-color:#222; padding: 20px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); color: #f9f9f9; font-family: 'Georgia', serif; font-size: 16px; line-height: 1.6;\">
                {story}
            </div>
            """, unsafe_allow_html=True
        )

        buffer = BytesIO()
        buffer.write(story.encode('utf-8'))
        buffer.seek(0)
        filename = f"{genre.lower()}_story_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"

        st.download_button(
            label="📅 Download Story",
            data=buffer,
            file_name=filename,
            mime="text/plain"
        )

