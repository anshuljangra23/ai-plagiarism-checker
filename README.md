# AI Plagiarism Checker

A beginner-friendly Python/Streamlit project that compares submitted text against reference files provided by the user.

## Features
- Paste text or upload a TXT, PDF, or DOCX document.
- Upload multiple reference documents or paste a reference passage.
- Compare sentences with TF-IDF word/phrase similarity.
- Show a screening percentage and highlight likely matching passages.
- Adjust the match threshold.
- Keep processing local when run on your own computer.

## Important limitations
- This prototype compares only with reference material you provide. It does not crawl Google or the wider internet.
- Similarity is not proof of plagiarism. Quotations and common phrases may match.
- Semantic paraphrases can be missed. For a production system, consider adding embeddings, a licensed source-search API, citation detection, and privacy controls.
- Do not upload confidential or sensitive documents to a hosted instance unless you understand its data handling.

## Run locally

1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment (recommended).

   Windows:
   ```bash
   python -m venv .venv
   .venv\\Scripts\\activate
   ```

   macOS/Linux:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   streamlit run app.py
   ```

Streamlit will show a local URL, usually `http://localhost:8501`.

## Suggested future upgrades
- Export reports to PDF or CSV.
- Use sentence-transformer embeddings for semantic similarity.
- Add a database for saved reports and users.
- Add a source-search provider with proper licensing.
- Add sentence-level highlighting in the full document.
