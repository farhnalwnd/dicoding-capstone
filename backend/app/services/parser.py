import io
import re

from docx import Document
from pypdf import PdfReader

STOPWORDS = {
    # --- 1. PREPOSISI & KATA HUBUNG STANDARD (English) ---
    "that",
    "this",
    "these",
    "those",
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "for",
    "with",
    "from",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "between",
    "of",
    "to",
    "in",
    "on",
    "at",
    "by",
    "as",
    "job",
    "description",
    "requirement",
    "requirements",
    # --- 2. PREPOSISI & KATA HUBUNG STANDARD (Indonesian) ---
    "yang",
    "dan",
    "di",
    "ke",
    "dari",
    "pada",
    "dengan",
    "untuk",
    "dalam",
    "adalah",
    "sebagai",
    "telah",
    "akan",
    "dapat",
    "tidak",
    "ini",
    "itu",
    "juga",
    "atau",
    "oleh",
    "seperti",
    "sehingga",
    "serta",
    "saat",
    "bagi",
    "kemudian",
    "namun",
    "karena",
    "bisa",
    "harus",
    "ia",
    "kami",
    "saya",
    "deskripsi",
    # --- 3. CV ARTIFACTS & HEADERS (Kata bawaan template dokumen) ---
    "requirements",
    "description",
    "curriculum",
    "vitae",
    "resume",
    "page",
    "summary",
    "profile",
    "contact",
    "about",
    "me",
    "biodata",
    "personal",
    "deskripsi",
    "persyaratan",
    "profil",
    "ringkasan",
    "tentang",
    "saya",
    "halaman",
    "detail",
    "details",
    "information",
    "informasi",
    # --- 4. CORPORATE CLICHES & BUZZWORDS (Pemanis kalimat yang tidak bernilai) ---
    "seeking",
    "looking",
    "forward",
    "passionate",
    "motivated",
    "dynamic",
    "results-oriented",
    "proven",
    "track",
    "record",
    "excellent",
    "strong",
    "good",
    "success",
    "successful",
    "highly",
    "hardworking",
    "talented",
    "mencari",
    "termotivasi",
    "dinamis",
    "berorientasi",
    "hasil",
    "terbukti",
    "baik",
    "sukses",
    "sangat",
    "berbakat",
    "kompeten",
    "professional",
    "responsible",
    # --- 5. SATUAN WAKTU & INFORMASI UMUM (Sering muncul di riwayat kerja) ---
    "years",
    "months",
    "year",
    "month",
    "tahun",
    "bulan",
    "penuh",
    "waktu",
    "magang",
    "kontrak",
    "contract",
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
    "present",
    "current",
    "sekarang",
    "saat",
    "ini",
    # --- 6. ACTION VERBS / KATA KERJA UMUM (Bukan skill) ---
    "have",
    "must",
    "can",
    "able",
    "will",
    "shall",
    "may",
    "being",
    "ensure",
    "assist",
    "contribute",
    "comply",
    "perform",
    "make",
    "do",
    "manage",
    "handle",
    "support",
    "provide",
    "create",
    "develop",
    "berhasil",
    "membantu",
    "mengelola",
    "menangani",
    "melakukan",
    "membuat",
    "menggunakan",
    "menjadi",
    "memiliki",
    "serta",
    "termasuk",
    # --- 7. RECRUITMENT NOUNS (Kata bawaan lowongan kerja, bukan skill) ---
    "skill",
    "skills",
    "knowledge",
    "bachelor",
    "degree",
    "science",
    "proficiency",
    "proficient",
    "basic",
    "fluent",
    "written",
    "verbal",
    "english",
    "indonesia",
    "communication",
    "interpersonal",
    "keren",
    "lulusan",
    "sarjana",
    "pengetahuan",
    "komunikasi",
    # --- 8. KATA KERJA & KATA BENDA GENERIK (Bukan skill spesifik) ---
    "work",
    "working",
    "experience",
    "experienced",
    "experience",
    "team",
    "company",
    "position",
    "candidate",
    "applicants",
    "role",
    "opportunity",
    "responsibilities",
    "duties",
    "tasks",
    "pengalaman",
    "pengalaman kerja",
    "posisi",
    "kandidat",
    # --- 9. GEOGRAFIS / LOKASI (Bukan skill) ---
    "indonesia",
    "medan",
    "bekasi",
    "pangandaran",
    "banten",
    "jakarta",
    "bandung",
    "surabaya",
    "tangerang",
    "depok",
    "bogor",
    "semarang",
    "yogyakarta",
    "makassar",
    "bali",
    "manado",
    "palembang",
    "padang",
    "lampung",
    "aceh",
    "sumatera",
    "kalimantan",
    "sulawesi",
    "jawa",
    "ntt",
    "ntb",
    # --- 10. KATA GENERIK LAINNYA (Kata yang sering salah dianggap skill) ---
    "what",
    "within",
    "well",
    "also",
    "such",
    "like",
    "other",
    "more",
    "all",
    "any",
    "each",
    "every",
    "both",
    "few",
    "own",
    "new",
    "first",
    "last",
    "long",
    "great",
    "little",
    "only",
    "over",
    "here",
    "there",
    "where",
    "when",
    "how",
    "why",
    "berikut",
    "berikut",
    "tersebut",
    "lainnya",
    "serta",
    "solusi",
    "sistem",
    "solutions",
    "system",
    "systems",
    "reporting",
    "presentation",
    "design",
    "terkait",
    "khusus",
    "umum",
    "lain",
    "lebih",
    "e.g.",
    "e.g",
    "eg",
    "i.e.",
    "i.e",
    "ie",
    "etc",
    "dll",
    "dsb",
    "wfo",
    "wfh",
    "database",
    "databases",
    "server",
    "servers",
    "js",
    "web",
    "app",
    "application",
    "applications",
    "framework",
    "library",
    "tool",
    "tools",
    "platform",
    "platforms",
    "data",
    "programming",
    "code",
    "coding",
    "software",
    "hardware",
    "project",
    "projects",
}


def clean_text(text: str) -> str:
    """Clean extracted text from noise, excess whitespaces, HTML tags, and common artifacts while preserving case"""
    if not text:
        return ""

    # 1. Hapus tag HTML jika ada (terutama untuk JD hasil scrape)
    text = re.sub(r"<[^>]*>", " ", text)

    # 3. Hapus URL/Links
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # 4. Hapus Email
    text = re.sub(r"\S+@\S+", " ", text)

    # 5. Hapus Nomor Telepon
    text = re.sub(r"\+?\d[\d -]{8,15}\d", " ", text)

    # 6. Hilangkan karakter tidak perlu kecuali tanda baca dasar dan simbol teknologi (+, #, -, /)
    text = re.sub(r"[^\w\s.,;:\-+/#]", " ", text)

    # 7. Bersihkan spasi/newline berlebih
    text = re.sub(r"\s+", " ", text)

    # 8. Hilangkan header/footer umum CV (case-insensitive)
    noise_patterns = [
        r"(?i)page\s+\d+\s+of\s+\d+",
        r"(?i)curriculum\s+vitae",
        r"(?i)resume",
    ]
    for pattern in noise_patterns:
        text = re.sub(pattern, " ", text)

    return text.strip()


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file.

    Uses PyMuPDF (fitz) as the primary extractor — it handles character-spaced
    PDFs and complex layouts far better than pypdf.  Falls back to pypdf if
    fitz is not installed.
    """
    # --- Primary: PyMuPDF ---
    try:
        import fitz  # noqa: PLC0415

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text())
        raw = "\n".join(pages_text)
        return clean_text(raw)
    except ImportError:
        pass  # fitz not installed — fall through to pypdf
    except Exception:
        pass  # malformed PDF — try pypdf anyway

    # --- Fallback: pypdf ---
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


def extract_candidate_name_from_pdf_bytes(file_bytes: bytes) -> str:
    try:
        import fitz

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        if len(doc) == 0:
            return ""

        page = doc[0]
        blocks = page.get_text("dict").get("blocks", [])

        text_spans = []
        for b in blocks:
            if b.get("type") == 0:  # text block
                for line in b.get("lines", []):
                    line_text = ""
                    max_size = 0.0
                    for s in line.get("spans", []):
                        line_text += s.get("text", "") + " "
                        max_size = max(max_size, s.get("size", 0.0))

                    line_text = line_text.strip()
                    if len(line_text) > 2 and re.search(r"[A-Za-z]", line_text):
                        text_spans.append((max_size, line_text))

        if not text_spans:
            return ""

        # Sort by size descending (largest font = most likely the name)
        text_spans.sort(key=lambda x: x[0], reverse=True)

        ignore_words = [
            "curriculum",
            "vitae",
            "resume",
            "cv",
            "profile",
            "portfolio",
            "contact",
            "about",
            "me",
            "summary",
            "objective",
            "experience",
            "education",
            "skills",
            "personal",
            "information",
            "data diri",
            "riwayat",
            "pengalaman",
            "pendidikan",
        ]

        for size, text in text_spans:
            text_lower = text.lower().strip()
            if not any(w in text_lower for w in ignore_words):
                # Keep letters (including accented/unicode), dots, spaces, hyphens, and apostrophes
                name = re.sub(r"[^a-zA-ZÀ-ÿ\s.\-']", "", text)
                name = re.sub(r"\s+", " ", name).strip()
                words = name.split()
                # A name should have 1-6 words and at least 2 characters total
                if 1 <= len(words) <= 6 and len(name) >= 2:
                    return name.title()

    except ImportError:
        print("PyMuPDF (fitz) is not installed. Falling back to regex name extraction.")
    except Exception as e:
        print(f"Error extracting name from PDF fonts: {e}")

    return ""


def extract_candidate_name(text: str, filename: str, file_bytes: bytes = None) -> str:
    # 1. Try Font Size extraction if it's a PDF and bytes are provided
    if file_bytes and filename.lower().endswith(".pdf"):
        name_from_font = extract_candidate_name_from_pdf_bytes(file_bytes)
        if name_from_font:
            return name_from_font

    # 2. Try regex matches from text content (e.g. "Name: John Doe")
    name_patterns = [
        r"(?i)full\s*name\s*:\s*([A-Za-zÀ-ÿ\s.\-']{2,50})",
        r"(?i)nama\s*lengkap\s*:\s*([A-Za-zÀ-ÿ\s.\-']{2,50})",
        r"(?i)name\s*:\s*([A-Za-zÀ-ÿ\s.\-']{2,50})",
        r"(?i)nama\s*:\s*([A-Za-zÀ-ÿ\s.\-']{2,50})",
    ]
    for pattern in name_patterns:
        match = re.search(pattern, text)
        if match:
            name = match.group(1).strip()
            name = re.sub(r"\s+", " ", name)
            if 1 <= len(name.split()) <= 6:
                return name.title()

    # 3. Try first non-empty lines (heuristic: name is usually the first prominent line)
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    # Words that indicate a section header, NOT a person's name
    skip_words = [
        "curriculum",
        "vitae",
        "resume",
        "cv",
        "page",
        "contact",
        "profile",
        "summary",
        "objective",
        "address",
        "phone",
        "email",
        "http",
        "www",
        "linkedin",
        "@",
        "personal",
        "data diri",
        "riwayat",
        # Common CV section headers (English)
        "professional",
        "experience",
        "education",
        "skills",
        "technical",
        "employment",
        "work",
        "history",
        "references",
        "projects",
        "awards",
        "certifications",
        "languages",
        "interests",
        "achievements",
        # Common CV section headers (Indonesian)
        "pengalaman",
        "pendidikan",
        "keahlian",
        "kemampuan",
        "portofolio",
        "referensi",
        "proyek",
        "penghargaan",
        "sertifikasi",
    ]

    for line in lines[:8]:
        line_lower = line.lower()
        if any(w in line_lower for w in skip_words):
            continue
        if re.search(r"[\d@/|]", line):
            continue
        if re.match(r"^[A-Za-zÀ-ÿ\s.\-']{2,50}$", line):
            words = line.split()
            if 1 <= len(words) <= 6:
                return line.title()

    # 3b. ALL-CAPS name detection — some CVs put the name after the summary block
    #     e.g. "ZAKARIA NOOR RIZKANDIRA" appearing on line 5+
    for line in lines[:15]:
        if re.search(r"[\d@/|\\]", line):
            continue
        # ALL CAPS, 2-5 words, 4-50 chars
        if re.match(r"^[A-Z][A-Z\s.\-']{3,49}$", line):
            words = line.split()
            if 2 <= len(words) <= 5:
                line_lower = line.lower()
                if not any(w in line_lower for w in skip_words):
                    return line.title()

    # 3c. Scan the FLAT text for ALL-CAPS name pattern (handles collapsed newlines from clean_text).
    #     Looks for 2-5 consecutive ALL-CAPS words not in the skip list.
    #     e.g. finds "ZAKARIA NOOR RIZKANDIRA" inside a long single-line string.
    caps_pattern = re.compile(
        r"\b([A-Z][A-Z\'\-\.]{1,}(?:\s+[A-Z][A-Z\'\-\.]{1,}){1,4})\b"
    )
    for match in caps_pattern.finditer(text):
        candidate = match.group(1).strip()
        words = candidate.split()
        if 2 <= len(words) <= 5:
            candidate_lower = candidate.lower()
            if not any(w in candidate_lower for w in skip_words):
                if not re.search(r"[\d@/|]", candidate):
                    return candidate.title()

    # 4. Fallback: derive name from filename (remove extension and clean separators)
    fallback_name = re.sub(r"\.[^.]+$", "", filename)
    # Remove common prefixes like "CV", "Resume", "CV -", etc.
    fallback_name = re.sub(
        r"(?i)^(cv|resume|curriculum\s*vitae)\s*[-_.\s]*", "", fallback_name
    )
    fallback_name = re.sub(r"[-_]", " ", fallback_name)
    # Remove trailing noise like "(1)", "(2)", "copy", "final"
    fallback_name = re.sub(r"\s*\(?\d+\)?\s*$", "", fallback_name)
    fallback_name = re.sub(
        r"\s*(copy|final|rev|v\d+)\s*$", "", fallback_name, flags=re.IGNORECASE
    )
    fallback_name = re.sub(r"\s+", " ", fallback_name).strip()

    if fallback_name:
        return fallback_name.title()

    return "Unknown Candidate"
