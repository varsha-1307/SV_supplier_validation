import json
import os
import re
import time

from dotenv import load_dotenv
from google import genai


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file."
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


CACHE_DIRECTORY = "extracted_data"

os.makedirs(
    CACHE_DIRECTORY,
    exist_ok=True
)


# ============================================================
# SAFE FILE NAME
# ============================================================

def safe_cache_name(filename):

    name = os.path.basename(
        filename
    )

    name = os.path.splitext(
        name
    )[0]

    name = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        name
    )

    return name


# ============================================================
# DOCUMENT TYPE DETECTION
# ============================================================

def detect_document_type(filename):

    name = filename.lower()

    if (
        "trade" in name
        and "license" in name
    ):
        return "trade_license"

    if (
        "trn" in name
        or "tax" in name
        or "vat" in name
    ):
        return "trn_certificate"

    if "iban" in name:
        return "iban_letter"

    return "unknown"


# ============================================================
# TRADE LICENSE SCHEMA
# ============================================================

TRADE_LICENSE_FIELDS = {
    "certificateNumber": None,
    "issueDate": None,
    "expiryDate": None,
    "companyName": None,
    "businessName": None,
    "legalType": None,
    "mainLicenseNumber": None,
    "dcciNumber": None,
    "registerNumber": None,
    "licenseCategory": None,
    "phone": None,
    "mobile": None,
    "poBox": None,
    "parcelId": None,
}


# ============================================================
# TRN CERTIFICATE SCHEMA
# ============================================================

TRN_CERTIFICATE_FIELDS = {
    "trn": None,
    "companyName": None,
    "businessName": None,
    "taxRegistrationNumber": None,
    "taxRegistrationDate": None,
    "issueDate": None,
    "expiryDate": None,
    "country": None,
    "address": None,
}


# ============================================================
# IBAN LETTER SCHEMA
# ============================================================

IBAN_LETTER_FIELDS = {
    "companyName": None,
    "accountName": None,
    "iban": None,
    "bankName": None,
    "accountNumber": None,
    "currency": None,
    "swiftCode": None,
    "branch": None,
    "address": None,
}


# ============================================================
# GENERIC DOCUMENT SCHEMA
# ============================================================

UNKNOWN_DOCUMENT_FIELDS = {
    "documentName": None,
    "companyName": None,
    "businessName": None,
    "documentNumber": None,
    "issueDate": None,
    "expiryDate": None,
    "country": None,
    "address": None,
    "phone": None,
    "mobile": None,
    "email": None,
}


# ============================================================
# PROMPT BUILDER
# ============================================================

def build_prompt(document_type):

    if document_type == "trade_license":

        fields = TRADE_LICENSE_FIELDS

        document_name = (
            "Trade License"
        )

        additional_rules = """
Important Trade License rules:

1. Extract the value labelled "Date Issue"
   into issueDate.

2. Extract the value labelled "Date Expiry"
   into expiryDate.

3. NEVER swap issueDate and expiryDate.

4. Extract certificateNumber exactly as shown.

5. Extract mainLicenseNumber only if the document
   explicitly contains a separate main license number.

6. Do not assume certificateNumber equals mainLicenseNumber.

7. Do not create values from other fields.
"""

    elif document_type == "trn_certificate":

        fields = TRN_CERTIFICATE_FIELDS

        document_name = (
            "TRN / Tax Registration Certificate"
        )

        additional_rules = """
Important TRN rules:

1. Extract the Tax Registration Number exactly
   as shown.

2. Do not confuse a certificate number with the
   Tax Registration Number.

3. Extract dates only when explicitly present.

4. Extract company name exactly as shown.

5. Extract country and address only when explicitly
   present in the document.
"""

    elif document_type == "iban_letter":

        fields = IBAN_LETTER_FIELDS

        document_name = (
            "IBAN Letter"
        )

        additional_rules = """
Important IBAN rules:

1. Extract IBAN only when explicitly shown.

2. Extract bank name only when explicitly shown.

3. Extract account number only when explicitly shown.

4. Do not create supplier information from assumptions.

5. Do not treat IBAN as a supplier registration number.
"""

    else:

        fields = UNKNOWN_DOCUMENT_FIELDS

        document_name = (
            "Supplier Document"
        )

        additional_rules = """
Extract only information that is explicitly visible
in the document.
"""

    schema = json.dumps(
        fields,
        indent=4
    )

    return f"""
You are a Supplier Document Extraction AI.

Document type:
{document_name}

Extract information ONLY from the provided PDF.

Do NOT guess.
Do NOT infer.
Do NOT calculate.
Do NOT correct values.
Do NOT normalize values.
Do NOT replace missing values with assumptions.

Return ONLY valid JSON.

Use exactly this JSON structure:

{schema}

Rules:

1. Extract values exactly as displayed.

2. If a field does not exist in the document,
   return null.

3. Do not create values from other fields.

4. Do not use outside knowledge.

5. Preserve numbers exactly as displayed.

6. Preserve company names as displayed.

7. Preserve dates exactly as displayed.

8. Do not swap dates.

9. If the document contains multiple possible
   values for a field, select the value whose
   label clearly corresponds to that field.

10. Do not infer that two differently labelled
    fields are the same.

{additional_rules}

Return JSON only.
"""


# ============================================================
# CACHE PATH
# ============================================================

def get_cache_path(pdf_path):

    filename = os.path.basename(
        pdf_path
    )

    safe_name = safe_cache_name(
        filename
    )

    return os.path.join(
        CACHE_DIRECTORY,
        f"{safe_name}.json"
    )


# ============================================================
# LOAD CACHE
# ============================================================

def load_cached_extraction(pdf_path):

    cache_path = get_cache_path(
        pdf_path
    )

    if not os.path.exists(
        cache_path
    ):
        return None

    try:

        with open(
            cache_path,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(
                file
            )

        print(
            "Using cached extraction:"
        )

        print(
            cache_path
        )

        return data

    except Exception:

        return None


# ============================================================
# SAVE CACHE
# ============================================================

def save_cached_extraction(
    pdf_path,
    document_type,
    data
):

    cache_path = get_cache_path(
        pdf_path
    )

    output = {
        "sourceFile": os.path.basename(
            pdf_path
        ),
        "documentType": document_type,
        "extractedData": data,
    }

    with open(
        cache_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(
        "Extraction cached:"
    )

    print(
        cache_path
    )


# ============================================================
# NORMALIZE OLD CACHE
# ============================================================

def normalize_cached_data(data):

    # New cache format
    if (
        isinstance(data, dict)
        and "extractedData" in data
    ):
        return data["extractedData"]

    # Old Trade License cache format
    return data


# ============================================================
# GEMINI EXTRACTION
# ============================================================

def extract_document(
    pdf_path,
    force_refresh=False
):

    if not os.path.exists(
        pdf_path
    ):
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    document_type = detect_document_type(
        os.path.basename(pdf_path)
    )

    # --------------------------------------------------------
    # CACHE
    # --------------------------------------------------------

    if not force_refresh:

        cached_data = (
            load_cached_extraction(
                pdf_path
            )
        )

        if cached_data is not None:

            return normalize_cached_data(
                cached_data
            )

    print()
    print(
        "=" * 70
    )

    print(
        "GEMINI DOCUMENT EXTRACTION"
    )

    print(
        "=" * 70
    )

    print(
        "File:",
        pdf_path
    )

    print(
        "Document type:",
        document_type
    )

    # --------------------------------------------------------
    # PROMPT
    # --------------------------------------------------------

    prompt = build_prompt(
        document_type
    )

    # --------------------------------------------------------
    # UPLOAD
    # --------------------------------------------------------

    print(
        "Uploading PDF to Gemini..."
    )

    uploaded_file = client.files.upload(
        file=pdf_path
    )

    # --------------------------------------------------------
    # GENERATE
    # --------------------------------------------------------

    max_retries = 3

    response = None

    for attempt in range(
        max_retries
    ):

        try:

            print(
                f"Gemini attempt "
                f"{attempt + 1}/{max_retries}"
            )

            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=[
                    uploaded_file,
                    prompt
                ]
            )

            break

        except Exception as error:

            error_text = str(
                error
            )

            if "429" in error_text:

                print()
                print(
                    "Gemini API quota exceeded."
                )

                raise

            if "503" in error_text:

                if (
                    attempt
                    == max_retries - 1
                ):

                    raise

                wait_time = (
                    10 * (attempt + 1)
                )

                print(
                    "Gemini temporarily "
                    "unavailable."
                )

                print(
                    f"Retrying in "
                    f"{wait_time} seconds..."
                )

                time.sleep(
                    wait_time
                )

                continue

            raise

    if response is None:

        raise RuntimeError(
            "Gemini did not return a response."
        )

    # --------------------------------------------------------
    # PARSE RESPONSE
    # --------------------------------------------------------

    result = (
        response.text
        .strip()
    )

    if result.startswith(
        "```json"
    ):

        result = result[
            len("```json"):
        ]

    if result.endswith(
        "```"
    ):

        result = result[
            :-3
        ]

    result = result.strip()

    try:

        extracted_data = json.loads(
            result
        )

    except json.JSONDecodeError:

        print()
        print(
            "Gemini returned invalid JSON:"
        )

        print(
            result
        )

        raise

    # --------------------------------------------------------
    # SAVE CACHE
    # --------------------------------------------------------

    save_cached_extraction(
        pdf_path,
        document_type,
        extracted_data
    )

    return extracted_data


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def extract_trade_license(
    pdf_path
):

    return extract_document(
        pdf_path
    )