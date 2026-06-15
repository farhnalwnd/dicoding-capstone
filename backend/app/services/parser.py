import io
import re
from pypdf import PdfReader
from docx import Document

STOPWORDS = {
    # --- 1. PREPOSISI & KATA HUBUNG STANDARD (English) ---
    "that", "this", "these", "those", "the", "a", "an", "and", "or", "but",
    "for", "with", "from", "into", "through", "during", "before", "after",
    "above", "below", "between", "of", "to", "in", "on", "at", "by", "as",
    "job", "description", "requirement", "requirements",
    
    # --- 2. PREPOSISI & KATA HUBUNG STANDARD (Indonesian) ---
    "yang", "dan", "di", "ke", "dari", "pada", "dengan", "untuk", "dalam",
    "adalah", "sebagai", "telah", "akan", "dapat", "tidak", "ini", "itu",
    "juga", "atau", "oleh", "seperti", "sehingga", "serta", "saat", "bagi",
    "kemudian", "namun", "karena", "bisa", "harus", "ia", "kami", "saya",
    "deskripsi",

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
    "baik", "sukses", "sangat", "berbakat", "kompeten", "professional", "responsible"

    # --- 5. SATUAN WAKTU & INFORMASI UMUM (Sering muncul di riwayat kerja) ---
    "years", "months", "year", "month",
    "tahun", "bulan", "penuh", "waktu", "magang", "kontrak", "contract",
    "january", "february", "march", "april", "may", "june", "july", "august", 
    "september", "october", "november", "december", "present", "current",
    "sekarang", "saat", "ini",

    # --- 6. ACTION VERBS / KATA KERJA UMUM (Bukan skill) ---
    "have", "must", "can", "able", "will", "shall", "may", "being",
    "ensure", "assist", "contribute", "comply", "perform", "make", "do",
    "manage", "handle", "support", "provide", "create", "develop",
    "berhasil", "membantu", "mengelola", "menangani", "melakukan", "membuat",
    "menggunakan", "menjadi", "memiliki", "serta", "termasuk",

    # --- 7. RECRUITMENT NOUNS (Kata bawaan lowongan kerja, bukan skill) ---
    "skill", "skills", "knowledge", "bachelor", "degree", "science",
    "proficiency", "proficient", "basic", "fluent", "written", "verbal",
    "english", "indonesia", "communication", "interpersonal",
    "keren", "lulusan", "sarjana", "pengetahuan", "komunikasi",

    # --- 8. KATA KERJA & KATA BENDA GENERIK (Bukan skill spesifik) ---
    "work", "working", "experience", "experienced", "experience",
    "team", "company", "position", "candidate", "applicants",
    "role", "opportunity", "responsibilities", "duties", "tasks",
    "pengalaman", "pengalaman kerja", "posisi", "kandidat",

    # --- 9. GEOGRAFIS / LOKASI (Bukan skill) ---
    "indonesia", "medan", "bekasi", "pangandaran", "banten",
    "jakarta", "bandung", "surabaya", "tangerang", "depok",
    "bogor", "semarang", "yogyakarta", "makassar", "bali",
    "manado", "palembang", "padang", "lampung", "aceh",
    "sumatera", "kalimantan", "sulawesi", "jawa", "ntt", "ntb",

    # --- 10. KATA GENERIK LAINNYA (Kata yang sering salah dianggap skill) ---
    "what", "within", "well", "also", "such", "like", "other",
    "more", "all", "any", "each", "every", "both", "few", "own",
    "new", "first", "last", "long", "great", "little", "only",
    "over", "here", "there", "where", "when", "how", "why",
    "berikut", "berikut", "tersebut", "lainnya", "serta",
    "solusi", "sistem", "solutions", "system", "systems",
    "reporting", "presentation", "design",
    "terkait", "khusus", "umum", "lain", "lebih",
    "e.g.", "e.g", "eg", "i.e.", "i.e", "ie", "etc", "dll", "dsb", "wfo", "wfh",
    "database", "databases", "server", "servers", "js", "web", "app", "application",
    "applications", "framework", "library", "tool", "tools", "platform", "platforms",
    "data", "programming", "code", "coding", "software", "hardware", "project", "projects",
}

def clean_text(text: str) -> str:
    """Clean extracted text from noise, excess whitespaces, HTML tags, and common artifacts while preserving case"""
    if not text:
        return ""
        
    # 1. Hapus tag HTML jika ada (terutama untuk JD hasil scrape)
    text = re.sub(r'<[^>]*>', ' ', text)

    # 3. Hapus URL/Links
    text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
    
    # 4. Hapus Email
    text = re.sub(r'\S+@\S+', ' ', text)
    
    # 5. Hapus Nomor Telepon
    text = re.sub(r'\+?\d[\d -]{8,15}\d', ' ', text)

    # 6. Hilangkan karakter tidak perlu kecuali tanda baca dasar dan simbol teknologi (+, #, -, /)
    text = re.sub(r'[^\w\s.,;:\-+/#]', ' ', text)
    
    # 7. Bersihkan spasi/newline berlebih
    text = re.sub(r'\s+', ' ', text)
    
    # 8. Hilangkan header/footer umum CV (case-insensitive)
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
