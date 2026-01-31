import pdfplumber
from docx import Document


def parse_jd(file_path: str) -> str:
    """
    Extract raw text from a Job Description file.
    Supports PDF (text-based), DOCX, and TXT.
    """

    file_path = file_path.lower()

    # ---------- PDF ----------
    if file_path.endswith(".pdf"):
        try:
            with pdfplumber.open(file_path) as pdf:
                text = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)

                if not text:
                    raise ValueError("PDF has no extractable text")

                return "\n".join(text)

        except Exception as e:
            raise ValueError(
                "Failed to parse PDF JD. "
                "Ensure it is a text-based PDF, not scanned."
            ) from e

    # ---------- DOCX ----------
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    # ---------- TXT ----------
    elif file_path.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    else:
        raise ValueError("Unsupported JD file format. Use PDF, DOCX, or TXT.")
