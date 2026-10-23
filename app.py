import io
import re
from difflib import SequenceMatcher

import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="AI Plagiarism Checker", page_icon="🔎", layout="wide")

st.title("🔎 AI Plagiarism Checker")
st.caption("Compare a document with reference material and review potentially matching passages.")

with st.sidebar:
    st.header("How it works")
    st.write(
        "This prototype compares your text with reference files you provide. "
        "It does not search the entire internet and a similarity score is not proof of plagiarism."
    )
    threshold = st.slider("Passage match threshold", 0.30, 0.95, 0.60, 0.05)
    st.markdown("---")
    st.caption("Supported reference formats: TXT, PDF, DOCX")

def extract_text(uploaded_file):
    name = uploaded_file.name.lower()
    raw = uploaded_file.getvalue()
    if name.endswith(".txt"):
        return raw.decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(raw))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as exc:
            return f"[Could not read PDF: {exc}]"
    if name.endswith(".docx"):
        try:
            from docx import Document
            doc = Document(io.BytesIO(raw))
            return "\n".join(p.text for p in doc.paragraphs)
        except Exception as exc:
            return f"[Could not read DOCX: {exc}]"
    return ""

def sentences(text):
    chunks = re.split(r'(?<=[.!?])\s+|\n+', text.strip())
    return [c.strip() for c in chunks if len(c.strip().split()) >= 5]

def similarity(a, b):
    try:
        matrix = TfidfVectorizer(stop_words="english", ngram_range=(1, 2)).fit_transform([a, b])
        return float(cosine_similarity(matrix[0:1], matrix[1:2])[0, 0])
    except ValueError:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

left, right = st.columns([1, 1])
with left:
    st.subheader("Text to check")
    pasted_text = st.text_area("Paste your text here", height=260, placeholder="Paste an essay, report, or assignment...")
    uploaded_target = st.file_uploader("Or upload the document to check", type=["txt", "pdf", "docx"], key="target")
with right:
    st.subheader("Reference sources")
    reference_files = st.file_uploader(
        "Upload documents to compare against (you can select multiple)",
        type=["txt", "pdf", "docx"],
        accept_multiple_files=True,
        key="references"
    )
    extra_reference = st.text_area("Or paste reference text", height=170, placeholder="Paste text from a permitted reference source...")

target_text = pasted_text.strip()
if uploaded_target is not None:
    extracted = extract_text(uploaded_target)
    if extracted and not extracted.startswith("[Could not"):
        target_text = extracted
    else:
        st.error(extracted)

if st.button("Analyze text", type="primary", use_container_width=True):
    refs = []
    for f in reference_files or []:
        content = extract_text(f)
        if content and not content.startswith("[Could not"):
            refs.append((f.name, content))
    if extra_reference.strip():
        refs.append(("Pasted reference", extra_reference.strip()))

    if not target_text:
        st.warning("Paste or upload the text you want to check.")
    elif not refs:
        st.warning("Add at least one reference document or paste reference text. This prototype compares only against sources you provide.")
    else:
        target_sentences = sentences(target_text)
        if not target_sentences:
            st.warning("Not enough text to analyze. Add a longer passage.")
        else:
            reference_sentences = []
            for source_name, content in refs:
                for sentence in sentences(content):
                    reference_sentences.append((source_name, sentence))

            matched = []
            for sent in target_sentences:
                best_score, best_source, best_sentence = 0.0, "", ""
                for source_name, ref_sentence in reference_sentences:
                    score = similarity(sent, ref_sentence)
                    if score > best_score:
                        best_score, best_source, best_sentence = score, source_name, ref_sentence
                if best_score >= threshold:
                    matched.append({
                        "text": sent,
                        "score": best_score,
                        "source": best_source,
                        "reference": best_sentence
                    })

            words = re.findall(r"\b[\w'-]+\b", target_text)
            matched_words = sum(len(re.findall(r"\b[\w'-]+\b", item["text"])) for item in matched)
            ratio = min(100, round(100 * matched_words / max(1, len(words))))
            c1, c2, c3 = st.columns(3)
            c1.metric("Estimated matching text", f"{ratio}%")
            c2.metric("Potentially matching passages", len(matched))
            c3.metric("Reference sources", len(refs))

            st.progress(ratio / 100)
            st.subheader("Potential matches")
            if not matched:
                st.success("No passages crossed the selected threshold against the provided references.")
            else:
                for i, item in enumerate(sorted(matched, key=lambda x: x["score"], reverse=True), 1):
                    with st.expander(f"Match {i} · {item['score']:.0%} similarity · {item['source']}"):
                        st.markdown("**Text being checked**")
                        st.write(item["text"])
                        st.markdown("**Closest reference passage**")
                        st.write(item["reference"])

            st.info(
                "Interpretation: this is a screening aid, not a definitive plagiarism verdict. "
                "Common phrases, quotations, references, and correctly cited material may match. "
                "Paraphrased copying may not match. Review passages and citations manually."
            )
