import time
import tempfile
from PIL import Image
import streamlit as st
import google.generativeai as genai

# -----------------------------
# Session state
# -----------------------------
if "GOOGLE_API_KEY" not in st.session_state:
    st.session_state.GOOGLE_API_KEY = None

if "last_run" not in st.session_state:
    st.session_state.last_run = 0.0

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.title("ℹ️ Configuration")

    if not st.session_state.GOOGLE_API_KEY:
        api_key = st.text_input(
            "Enter your Google Gemini API Key",
            type="password"
        )
        st.caption("Get your key from https://aistudio.google.com/apikey")
        if api_key:
            st.session_state.GOOGLE_API_KEY = api_key
            st.success("API key saved")
            st.rerun()
    else:
        st.success("API key configured")
        if st.button("Reset API Key"):
            st.session_state.GOOGLE_API_KEY = None
            st.rerun()

    st.warning(
        "⚠ Educational use only. This tool does NOT provide medical diagnoses."
    )

if not st.session_state.GOOGLE_API_KEY:
    st.warning("Please configure your API key to continue.")
    st.stop()

# -----------------------------
# Gemini configuration
# -----------------------------
genai.configure(api_key=st.session_state.GOOGLE_API_KEY)

model = genai.GenerativeModel(
    model_name="models/gemini-2.5-flash"
)


# -----------------------------
# Prompt (safe + token-efficient)
# -----------------------------
PROMPT = """
You are an AI system providing EDUCATIONAL analysis of medical images.
You are NOT a medical professional and must NOT give diagnoses.

Structure your response as:

### 1. Image Type & Region
- Imaging modality
- Anatomical region
- Image quality and limitations

### 2. Key Visual Observations
- Notable visible features
- Location and appearance
- Severity estimate (Normal / Mild / Moderate / Severe)

### 3. Possible Interpretations (Non-Diagnostic)
- Plausible explanations based on appearance
- Differential considerations if appropriate
- Clearly state uncertainty

### 4. Patient-Friendly Explanation
- Simple, non-technical explanation
- Emphasize that this is NOT a diagnosis

### 5. Educational Context
- General educational information only
- No treatment instructions

If image quality limits interpretation, say so clearly.
Be concise and cautious.
"""

# -----------------------------
# UI
# -----------------------------
st.title("🩻 Medical Imaging Analysis (Educational)")
st.write("Upload a medical image for AI-assisted visual analysis.")

uploaded_file = st.file_uploader(
    "Upload image (JPG / PNG)",
    type=["jpg", "jpeg", "png"],
)

if not uploaded_file:
    st.info("Upload an image to begin.")
    st.stop()

# -----------------------------
# Display image (display only)
# -----------------------------
image = Image.open(uploaded_file)

display_image = image.copy()
display_image.thumbnail((600, 600))

st.image(
    display_image,
    caption="Uploaded image (display resized; original used for analysis)",
    use_container_width=True,
)

# -----------------------------
# Analyze
# -----------------------------
if st.button("🔍 Analyze Image", type="primary"):
    now = time.time()
    if now - st.session_state.last_run < 30:
        st.warning("Please wait 30 seconds between analyses.")
        st.stop()

    st.session_state.last_run = now

    with st.spinner("Analyzing image..."):
        try:
            response = model.generate_content(
                [
                    PROMPT,
                    image  # ORIGINAL image, no resizing
                ]
            )

            st.markdown("### 📋 Analysis Result")
            st.markdown(response.text)

        except Exception as e:
            st.error(f"Analysis failed: {e}")

# -----------------------------
# Footer
# -----------------------------
st.caption(
    "AI-generated educational output only. "
    "Always consult qualified healthcare professionals for medical decisions."
)
