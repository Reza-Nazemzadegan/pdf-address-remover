import os
import shutil
from datetime import datetime
import streamlit as st
import aspose.pdf as ap
from PyPDF2 import PdfReader, PdfWriter

# Predefined replacements
PREDEFINED_REPLACEMENTS = [
    ("Return Address", " "),
    ("Vapeforest Ltd", " "),
    ("34 Trafalgar House", " "),
    ("Dickens Yard", " "),
    ("London", " "),
    ("W5 2TJ", " ")
]

def replace_text_in_pdf(pdf_path, replacements):
    document = ap.Document(pdf_path)
    snippets = []

    for search_text, replace_text in replacements:
        txtAbsorber = ap.text.TextFragmentAbsorber(search_text)

        # Iterate through all pages
        for page in document.pages:
            page.accept(txtAbsorber)
            textFragmentCollection = txtAbsorber.text_fragments

            if textFragmentCollection:
                for txtFragment in textFragmentCollection:
                    snippets.append(txtFragment.text)
                    txtFragment.text = replace_text

    output_path = pdf_path.replace(".pdf", "_edited.pdf")
    document.save(output_path)
    return snippets, output_path

def split_pdf(pdf_path, max_pages=4):
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    segments = []

    for start in range(0, total_pages, max_pages):
        writer = PdfWriter()
        end = min(start + max_pages, total_pages)

        for page_number in range(start, end):
            writer.add_page(reader.pages[page_number])

        segment_path = f"segment_{start // max_pages}.pdf"
        with open(segment_path, "wb") as segment_file:
            writer.write(segment_file)

        segments.append(segment_path)

    return segments

def merge_pdfs(paths, output_path):
    writer = PdfWriter()

    for path in paths:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)

    with open(output_path, "wb") as output_file:
        writer.write(output_file)

def process_pdf(pdf_path, replacements):
    segments = split_pdf(pdf_path)
    processed_segments = []

    for segment in segments:
        _, edited_segment = replace_text_in_pdf(segment, replacements)
        processed_segments.append(edited_segment)
        os.remove(segment)

    merge_pdfs(processed_segments, "final_output.pdf")
    for segment in processed_segments:
        os.remove(segment)

st.title("Address Remover")

# File uploader
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
if uploaded_file is not None:
    with open("temp_upload.pdf", "wb") as f:
        f.write(uploaded_file.getvalue())

# Replace Button
if st.button("Replace"):
    if uploaded_file:
        # Use predefined replacements
        replacements = PREDEFINED_REPLACEMENTS
        process_pdf("temp_upload.pdf", replacements)
        st.success("Replacements Applied")
    else:
        st.error("Please select a PDF file first")

# Save As Button
if st.button("Download The File"):
    with open("final_output.pdf", "rb") as file:
        btn = st.download_button(
             label="Download PDF",
             data=file,
             file_name="edited_pdf.pdf",
             mime="application/octet-stream"
        )
