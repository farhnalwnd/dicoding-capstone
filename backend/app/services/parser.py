import io
import re
from pypdf import PdfReader
from docx import Document

STOPWORDS = {
    # --- 1. PREPOSISI & KATA HUBUNG STANDARD (English) ---
    "that", "this", "these", "those", "the", "a", "an", "and", "or", "but",
    "for", "with", "from", "into", "through", "during", "before", "after",
    "above", "below", "between", "of", "to", "in", "on", "at", "by", "as", "and"
    
    # --- 2. PREPOSISI & KATA HUBUNG STANDARD (Indonesian) ---
    "yang", "dan", "di", "ke", "dari", "pada", "dengan", "untuk", "dalam",
    "adalah", "sebagai", "telah", "akan", "dapat", "tidak", "ini", "itu",
    "juga", "atau", "oleh", "seperti", "sehingga", "serta", "saat", "bagi",
    "kemudian", "namun", "karena", "bisa", "harus", "ia", "kami", "saya",

    # --- 3. CV ARTIFACTS & HEADERS (Kata bawaan template dokumen) ---
    "requirements", "description", "curriculum", "vitae", "resume", "page", 
    "summary", "profile", "contact", "about", "me", "biodata", "personal",
    "deskripsi", "persyaratan", "profil", "ringkasan", "tentang", "saya",
    "halaman", "detail", "details", "information", "informasi",

    # --- 4. CORPORATE CLICHES & BUZZWORDS (Pemanis kalimat yang tidak bernilai) ---
    "seeking", "looking", "forward", "passionate", "motivated", "dynamic",
    "results-oriented", "proven", "track", "record", "excellent", "strong",
    "good", "success", "successful", "highly", "hardworking", "talented",
    "mencari", "termotivasi", "dinamis", "berorientasi", "hasil", "terbukti",
    "baik", "sukses", "sangat", "berbakat", "kompeten", "professional",

    # --- 5. SATUAN WAKTU & INFORMASI UMUM (Sering muncul di riwayat kerja) ---
    "years", "months", "year", "month",
    "tahun", "bulan", "penuh", "waktu", "magang", "kontrak", "contract",
    "january", "february", "march", "april", "may", "june", "july", "august", 
    "september", "october", "november", "december", "present", "current",
    "sekarang", "saat", "ini"
}

def clean_text(text: str) -> str:
    """Clean extracted text from noise, excess whitespaces, and common artifacts"""
    # Remove non-alphanumeric characters except basic punctuation
    text = text.lower()
    
    text = re.sub(r'[^\w\s.,;:()\-+/#]', ' ', text)
    # Remove multiple spaces/newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove common CV headers/footers
    noise_patterns = [
        r'(?i)page\s+\d+\s+of\s+\d+',
        r'(?i)curriculum\s+vitae',
        r'(?i)resume'
    ]
    for pattern in noise_patterns:
        text = re.sub(pattern, ' ', text)
    return text.strip()

def extract_text_from_pdf(file_bytes: bytes) -> str:
    pdf = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf.pages:
        text += page.extract_text() or ""
    return clean_text(text)

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    text = []
    for para in doc.paragraphs:
        text.append(para.text)
    return clean_text("\n".join(text))

def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.split(".")[-1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext in ["docx", "doc"]:
        return extract_text_from_docx(file_bytes)
    return clean_text(file_bytes.decode("utf-8", errors="ignore"))

def extract_candidate_name(text: str, filename: str) -> str:
    # Fallback name from filename (remove extension and replace separators)
    fallback_name = re.sub(r"\.[^.]+$", "", filename)
    fallback_name = re.sub(r"[-_]", " ", fallback_name).title().strip()
    
    # Try regex matches
    name_patterns = [
        r"(?i)name\s*:\s*([A-Za-z\s.]{2,50})",
        r"(?i)full\s*name\s*:\s*([A-Za-z\s.]{2,50})",
        r"(?i)nama\s*:\s*([A-Za-z\s.]{2,50})"
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            name = match.group(1).strip()
            name = re.sub(r"\s+", " ", name)
            if len(name.split()) <= 4:
                return name.title()
                
    # Try first non-empty lines
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    for line in lines[:3]:
        # Clean from common CV words
        if re.match(r"^[A-Za-z\s.]{2,30}$", line) and not any(w in line.lower() for w in ["curriculum", "vitae", "resume", "cv", "page", "contact", "profile"]):
            return line.title()
            
    return fallback_name
