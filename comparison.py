from datetime import datetime
import re


# ============================================================
# HELPERS
# ============================================================

def is_empty(value):
    return value is None or (
        isinstance(value, str) and not value.strip()
    )


def normalize_text(value):
    if is_empty(value):
        return None

    value = str(value).strip().lower()
    value = re.sub(r"[\s\-_\,./\\]+", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_company_name(value):
    if is_empty(value):
        return None

    value = str(value).strip().lower()

    # Normalize LLC variations
    value = re.sub(
        r"\bl\s*[\W_]\s*l\s*[\W_]\s*c\b",
        " llc ",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\blimited\s+liability\s+company\b",
        " llc ",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(
        r"\bllc\b",
        " llc ",
        value,
        flags=re.IGNORECASE,
    )

    value = re.sub(r"[^a-z0-9\s]", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_number(value):
    if is_empty(value):
        return None

    return re.sub(r"[^0-9]", "", str(value))


def normalize_phone(value):
    if is_empty(value):
        return None

    return re.sub(r"[^0-9]", "", str(value))


def normalize_date(value):
    if is_empty(value):
        return None

    value = str(value).strip()

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    return None


def get_first_value(data, fields):
    """
    Return the first non-empty value from a dictionary.
    """
    if not isinstance(data, dict):
        return None

    for field in fields:
        if field in data:
            value = data.get(field)

            if not is_empty(value):
                return value

    return None


def get_items(data):
    """
    Safely extract items from Oracle API responses.

    Supports:
        {"items": [...]}
        [...]
        None
    """

    if isinstance(data, dict):
        items = data.get("items", [])

        if isinstance(items, list):
            return items

        return []

    if isinstance(data, list):
        return data

    return []


def normalize_key(value):
    if value is None:
        return ""

    return re.sub(
        r"[\s\-_]+",
        " ",
        str(value).strip().lower(),
    )


# ============================================================
# COMPARISON TYPE
# ============================================================

def get_comparison_type(field_name):
    field = str(field_name).lower()

    if (
        "date" in field
        or "expiry" in field
        or "issue" in field
    ):
        return "date"

    if (
        "certificate" in field
        or "license_number" in field
        or "licence_number" in field
        or "dcci" in field
        or "register" in field
        or "number" in field
        or "po_box" in field
        or "parcel" in field
    ):
        return "number"

    if (
        "phone" in field
        or "mobile" in field
    ):
        return "phone"

    if (
        "name" in field
        or "company" in field
        or "business" in field
    ):
        return "company"

    return "text"


def compare_values(
    form_value,
    document_value,
    field_name,
):
    """
    Compare Oracle Fusion value with Trade Licence
    document value.

    No supplier-specific values are used.
    """

    if is_empty(form_value) and is_empty(document_value):
        return "NOT_APPLICABLE"

    if is_empty(form_value):
        return "FAIL"

    if is_empty(document_value):
        return "FAIL"

    comparison_type = get_comparison_type(field_name)

    if comparison_type == "company":

        return (
            "PASS"
            if normalize_company_name(form_value)
            == normalize_company_name(document_value)
            else "FAIL"
        )

    if comparison_type == "number":

        return (
            "PASS"
            if normalize_number(form_value)
            == normalize_number(document_value)
            else "FAIL"
        )

    if comparison_type == "phone":

        return (
            "PASS"
            if normalize_phone(form_value)
            == normalize_phone(document_value)
            else "FAIL"
        )

    if comparison_type == "date":

        form_date = normalize_date(form_value)
        document_date = normalize_date(document_value)

        if form_date is None or document_date is None:
            return "FAIL"

        return (
            "PASS"
            if form_date == document_date
            else "FAIL"
        )

    return (
        "PASS"
        if normalize_text(form_value)
        == normalize_text(document_value)
        else "FAIL"
    )


# ============================================================
# COMMENTS
# ============================================================

def form_check_comment(
    description,
    value,
    status,
):
    if status == "PASS":
        return (
            f"{description} is entered in Oracle Fusion."
        )

    if status == "NOT_APPLICABLE":
        return (
            f"{description} is not available in Oracle Fusion."
        )

    return (
        f"{description} is not entered in Oracle Fusion."
    )


def comparison_comment(
    description,
    form_value,
    document_value,
    status,
):
    if status == "NOT_APPLICABLE":
        return (
            f"{description}: "
            "Oracle form value and Trade Licence "
            "document value are not available."
        )

    if is_empty(form_value):
        return (
            f"{description}: "
            "Oracle form value is not available."
        )

    if is_empty(document_value):
        return (
            f"{description}: "
            "Trade Licence document value is not available."
        )

    if status == "PASS":
        return (
            f"{description}: "
            "Oracle value and Trade Licence document "
            "value match after normalization."
        )

    return (
        f"{description}: "
        "Oracle value and Trade Licence document "
        "value do not match."
    )


# ============================================================
# CLASSIFICATION SEARCH
# ============================================================

def find_classification(
    classifications,
    classification_name,
):
    target = normalize_text(classification_name)

    for item in classifications:

        if not isinstance(item, dict):
            continue

        classification = get_first_value(
            item,
            [
                "Classification",
                "classification",
                "ClassificationName",
                "classificationName",
            ],
        )

        if (
            normalize_text(classification)
            == target
        ):
            return item

    return None


# ============================================================
# PRODUCT / SERVICE VALUE
# ============================================================

def get_product_service_value(item):
    if not isinstance(item, dict):
        return item

    return get_first_value(
        item,
        [
            "CategoryName",
            "categoryName",
            "Product",
            "product",
            "Service",
            "service",
            "Name",
            "name",
            "Classification",
            "classification",
        ],
    )


# ============================================================
# CONTACT NAME
# ============================================================

def get_contact_name(contact):
    if not isinstance(contact, dict):
        return None

    first_name = get_first_value(
        contact,
        [
            "FirstName",
            "firstName",
        ],
    )

    last_name = get_first_value(
        contact,
        [
            "LastName",
            "lastName",
        ],
    )

    full_name = " ".join(
        part
        for part in [
            first_name,
            last_name,
        ]
        if not is_empty(part)
    ).strip()

    return full_name or None


# ============================================================
# FIND CONTACT BY ROLE
# ============================================================

def find_contact_by_role(
    contacts,
    keywords,
):
    for contact in contacts:

        if not isinstance(contact, dict):
            continue

        job_title = get_first_value(
            contact,
            [
                "JobTitle",
                "jobTitle",
            ],
        )

        if is_empty(job_title):
            continue

        title = str(job_title).lower()

        if any(
            keyword.lower() in title
            for keyword in keywords
        ):
            return contact

    return None


# ============================================================
# TRADE LICENCE DOCUMENT
# ============================================================

def find_trade_license_document(documents):

    if not isinstance(documents, dict):
        return None

    for key, value in documents.items():

        key_normalized = normalize_key(key)

        if (
            "trade license" in key_normalized
            or "trade licence" in key_normalized
        ):
            return value

    return None


def get_trade_license_data(documents):

    trade_license = find_trade_license_document(
        documents
    )

    if isinstance(trade_license, dict):
        return trade_license

    if isinstance(trade_license, list):

        for item in trade_license:

            if isinstance(item, dict):
                return item

    return {}


# ============================================================
# ADD CHECK
# ============================================================

def add_check(
    checks,
    check_no,
    section,
    description,
    form_value,
    document_value,
    status,
    applicable,
    decision,
    ai_comment,
    trigger_type="FORM_VALIDATION",
):
    checks.append(
        {
            "checkNo": check_no,
            "section": section,
            "description": description,
            "formValue": form_value,
            "documentValue": document_value,
            "status": status,
            "applicable": applicable,
            "triggerType": trigger_type,
            "aiComment": ai_comment,
        }
    )


# ============================================================
# BUILD VALIDATION RESULT
# ============================================================

def build_validation_result(
    oracle_supplier,
    oracle_form,
    documents,
):
    """
    Main validation function.

    This function is called by main.py:

        build_validation_result(
            oracle_supplier=supplier,
            oracle_form=oracle_form,
            documents=documents,
        )

    All variables are local to this function.
    No module-level supplier/API variables are used.
    """

    # ========================================================
    # RESET CHECKS FOR EVERY RUN
    # ========================================================

    checks = []

    # ========================================================
    # NORMALIZE INPUTS
    # ========================================================

    supplier = (
        oracle_supplier
        if isinstance(oracle_supplier, dict)
        else {}
    )

    form = (
        oracle_form
        if isinstance(oracle_form, dict)
        else {}
    )

    document_collection = (
        documents
        if isinstance(documents, dict)
        else {}
    )

    # ========================================================
    # GET ORACLE DATA
    # ========================================================

    business_classifications = get_items(
        form.get("businessClassifications")
        or form.get("business_classifications")
        or form.get("BusinessClassifications")
    )

    addresses = get_items(
        form.get("addresses")
        or form.get("Addresses")
        or form.get("supplierAddresses")
    )

    contacts = get_items(
        form.get("contacts")
        or form.get("Contacts")
        or form.get("supplierContacts")
    )

    products_services = get_items(
        form.get("productsAndServices")
        or form.get("products_and_services")
        or form.get("ProductsAndServices")
    )

    # ========================================================
    # FALLBACK:
    #
    # Some versions of oracle_form_data.py may store data
    # under different keys. Search common alternatives.
    # ========================================================

    if not business_classifications:

        business_classifications = get_items(
            form.get("business_classification")
            or form.get("business_classification_data")
        )

    if not addresses:

        addresses = get_items(
            form.get("address")
            or form.get("address_data")
        )

    if not contacts:

        contacts = get_items(
            form.get("contact")
            or form.get("contact_data")
        )

    if not products_services:

        products_services = get_items(
            form.get("products_services")
            or form.get("products_services_data")
        )

    # ========================================================
    # CLASSIFICATIONS
    # ========================================================

    vat_class = find_classification(
        business_classifications,
        "*Attach VAT Registration Certificate",
    )

    auth_class = find_classification(
        business_classifications,
        "*Identification of the Authorized Signatory - Emirates ID / Passport Copy",
    )

    moa_class = find_classification(
        business_classifications,
        "Attach Power of Attorney / Memorandum of Association Certificate",
    )

    trade_class = find_classification(
        business_classifications,
        "Trade Licence",
    )

    # ========================================================
    # CHECK 1
    # ========================================================

    value = (
        get_first_value(
            vat_class,
            [
                "Classification",
                "classification",
            ],
        )
        if vat_class
        else None
    )

    status = (
        "PASS"
        if vat_class
        else "FAIL"
    )

    add_check(
        checks,
        1,
        "Business_Classification",
        "Classification",
        value,
        None,
        status,
        True,
        "Approved"
        if status == "PASS"
        else "Resubmission Required",
        form_check_comment(
            "VAT Registration Classification",
            value,
            status,
        ),
    )

    # ========================================================
    # CHECK 2
    # ========================================================

    value = (
        get_first_value(
            auth_class,
            [
                "Classification",
                "classification",
            ],
        )
        if auth_class
        else None
    )

    status = (
        "PASS"
        if auth_class
        else "FAIL"
    )

    add_check(
        checks,
        2,
        "Business_Classification",
        "Classification",
        value,
        None,
        status,
        True,
        "Approved"
        if status == "PASS"
        else "Resubmission Required",
        form_check_comment(
            "Authorized Signatory Classification",
            value,
            status,
        ),
    )

    # ========================================================
    # CHECK 3
    # ========================================================

    value = (
        get_first_value(
            moa_class,
            [
                "Classification",
                "classification",
            ],
        )
        if moa_class
        else None
    )

    status = (
        "PASS"
        if moa_class
        else "FAIL"
    )

    add_check(
        checks,
        3,
        "Business_Classification",
        "Classification",
        value,
        None,
        status,
        True,
        "Approved"
        if status == "PASS"
        else "Resubmission Required",
        form_check_comment(
            "Power of Attorney / MOA Classification",
            value,
            status,
        ),
    )

    # ========================================================
    # CHECK 4
    # ========================================================

    value = (
        get_first_value(
            trade_class,
            [
                "Classification",
                "classification",
            ],
        )
        if trade_class
        else None
    )

    status = (
        "PASS"
        if trade_class
        else "FAIL"
    )

    add_check(
        checks,
        4,
        "Business_Classification",
        "Classification",
        value,
        None,
        status,
        True,
        "Approved"
        if status == "PASS"
        else "Resubmission Required",
        form_check_comment(
            "Trade Licence Classification",
            value,
            status,
        ),
    )

    # ========================================================
    # ADDRESS
    # ========================================================

    address = (
        addresses[0]
        if addresses
        and isinstance(addresses[0], dict)
        else None
    )

    # ========================================================
    # CHECK 5 — ADDRESS NAME
    # ========================================================

    address_name = get_first_value(
        address,
        [
            "AddressName",
            "addressName",
        ],
    )

    status = (
        "PASS"
        if not is_empty(address_name)
        else "NOT_APPLICABLE"
    )

    add_check(
        checks,
        5,
        "Address_Check",
        "AddressName",
        address_name,
        None,
        status,
        status != "NOT_APPLICABLE",
        "Approved",
        form_check_comment(
            "AddressName",
            address_name,
            status,
        ),
    )

    # ========================================================
    # CHECK 6 — FORMATTED ADDRESS
    # ========================================================

    formatted_address = get_first_value(
        address,
        [
            "FormattedAddress",
            "formattedAddress",
        ],
    )

    status = (
        "PASS"
        if not is_empty(formatted_address)
        else "NOT_APPLICABLE"
    )

    add_check(
        checks,
        6,
        "Address_Check",
        "FormattedAddress",
        formatted_address,
        None,
        status,
        status != "NOT_APPLICABLE",
        "Approved",
        form_check_comment(
            "FormattedAddress",
            formatted_address,
            status,
        ),
    )

    # ========================================================
    # CHECK 7 — COUNTRY
    # ========================================================

    country = get_first_value(
        address,
        [
            "Country",
            "country",
            "CountryName",
        ],
    )

    status = (
        "PASS"
        if not is_empty(country)
        else "NOT_APPLICABLE"
    )

    add_check(
        checks,
        7,
        "Address_Check",
        "Country",
        country,
        None,
        status,
        status != "NOT_APPLICABLE",
        "Approved",
        form_check_comment(
            "Country",
            country,
            status,
        ),
    )

    # ========================================================
    # CHECK 8 — PHONE
    # ========================================================

    phone = get_first_value(
        address,
        [
            "PhoneNumber",
            "phoneNumber",
        ],
    )

    status = (
        "PASS"
        if not is_empty(phone)
        else "NOT_APPLICABLE"
    )

    add_check(
        checks,
        8,
        "Address_Check",
        "PhoneNumber",
        phone,
        None,
        status,
        status != "NOT_APPLICABLE",
        "Approved",
        form_check_comment(
            "PhoneNumber",
            phone,
            status,
        ),
    )

    # ========================================================
    # CHECK 9 — EMAIL
    # ========================================================

    email = get_first_value(
        address,
        [
            "Email",
            "email",
            "EmailAddress",
        ],
    )

    status = (
        "PASS"
        if not is_empty(email)
        else "NOT_APPLICABLE"
    )

    add_check(
        checks,
        9,
        "Address_Check",
        "Email",
        email,
        None,
        status,
        status != "NOT_APPLICABLE",
        "Approved",
        form_check_comment(
            "Email",
            email,
            status,
        ),
    )

    # ========================================================
    # CHECK 10 — ADDRESS PURPOSE
    # ========================================================

    purpose_fields = [
        "AddressPurposeOrderingFlag",
        "AddressPurposeRemitToFlag",
        "AddressPurposeRFQOrBiddingFlag",
        "OrderingFlag",
        "RemitToFlag",
        "RFQOrBiddingFlag",
    ]

    purpose_values = []

    if address:

        for field in purpose_fields:

            if field in address:
                value = address.get(field)

                if value is not None:
                    purpose_values.append(value)

    purpose_available = bool(
        purpose_values
    )

    purpose_selected = any(
        str(value).lower()
        in {
            "true",
            "yes",
            "y",
            "1",
        }
        or value is True
        for value in purpose_values
    )

    if purpose_available:

        status = (
            "PASS"
            if purpose_selected
            else "FAIL"
        )

        purpose_value = purpose_selected

    else:

        status = "NOT_APPLICABLE"
        purpose_value = None

    add_check(
        checks,
        10,
        "Address_Check",
        "Address_Purpose_Selected",
        purpose_value,
        None,
        status,
        status != "NOT_APPLICABLE",
        "Approved"
        if status == "PASS"
        else (
            "Resubmission Required"
            if status == "FAIL"
            else "Approved"
        ),
        (
            "At least one address purpose is selected."
            if status == "PASS"
            else (
                "Address purpose information is available "
                "but no purpose is selected."
                if status == "FAIL"
                else
                "Address purpose information is not available."
            )
        ),
    )

    # ========================================================
    # CHECK 11 — FIRST PRODUCT / SERVICE
    # ========================================================

    first_level_value = None

    if products_services:

        first_level_value = get_product_service_value(
            products_services[0]
        )

    status = (
        "PASS"
        if not is_empty(first_level_value)
        else "NOT_APPLICABLE"
    )

    add_check(
        checks,
        11,
        "Products_Services",
        "first_level",
        first_level_value,
        None,
        status,
        status != "NOT_APPLICABLE",
        "Approved",
        form_check_comment(
            "First-level product/service",
            first_level_value,
            status,
        ),
    )

    # ========================================================
    # CHECK 12 — SECOND PRODUCT / SERVICE
    # ========================================================

    second_level_value = None

    if len(products_services) > 1:

        second_level_value = get_product_service_value(
            products_services[1]
        )

    status = (
        "PASS"
        if not is_empty(second_level_value)
        else "NOT_APPLICABLE"
    )

    add_check(
        checks,
        12,
        "Products_Services",
        "second_level",
        second_level_value,
        None,
        status,
        status != "NOT_APPLICABLE",
        "Approved",
        form_check_comment(
            "Second-level product/service",
            second_level_value,
            status,
        ),
    )

    # ========================================================
    # CONTACT DATA
    # ========================================================

    contact = (
        contacts[0]
        if contacts
        and isinstance(contacts[0], dict)
        else None
    )

    # ========================================================
    # CHECK 13 — CEO NAME
    # ========================================================

    ceo_name = get_first_value(
        supplier,
        [
            "ChiefExecutiveName",
            "chiefExecutiveName",
        ],
    )

    status = (
        "PASS"
        if not is_empty(ceo_name)
        else "NOT_APPLICABLE"
    )

    add_check(
        checks,
        13,
        "contact_details",
        "ceo_name",
        ceo_name,
        None,
        status,
        status != "NOT_APPLICABLE",
        "Approved",
        form_check_comment(
            "CEO name",
            ceo_name,
            status,
        ),
    )

    # ========================================================
    # CHECK 14 — CEO EMAIL
    # ========================================================

    ceo_contact = find_contact_by_role(
        contacts,
        [
            "ceo",
            "chief executive",
            "chief executive officer",
        ],
    )

    ceo_email = None

    if ceo_contact:

        ceo_email = get_first_value(
            ceo_contact,
            [
                "Email",
                "email",
                "EmailAddress",
            ],
        )

    status = (
        "PASS"
        if not is_empty(ceo_email)
        else "NOT_APPLICABLE"
    )

    add_check(
        checks,
        14,
        "contact_details",
        "ceo_email",
        ceo_email,
        None,
        status,
        status != "NOT_APPLICABLE",
        "Approved",
        form_check_comment(
            "CEO email",
            ceo_email,
            status,
        ),
    )

    # ========================================================
    # CHECK 15 — CEO PHONE
    # ========================================================

    ceo_phone = None

    if ceo_contact:

        ceo_phone = get_first_value(
            ceo_contact,
            [
                "PhoneNumber",
                "phoneNumber",
                "MobileNumber",
                "mobileNumber",
            ],
        )

    status = (
        "PASS"
        if not is_empty(ceo_phone)
        else "NOT_APPLICABLE"
    )

    add_check(
        checks,
        15,
        "contact_details",
        "ceo_phone_number",
        ceo_phone,
        None,
        status,
        status != "NOT_APPLICABLE",
        "Approved",
        form_check_comment(
            "CEO phone number",
            ceo_phone,
            status,
        ),
    )

    # ========================================================
    # CHECK 16 — BD MANAGER
    # ========================================================

    bd_contact = find_contact_by_role(
        contacts,
        [
            "business development",
            "bd manager",
            "business development manager",
        ],
    )

    bd_manager = get_contact_name(
        bd_contact
    )

    status = (
        "PASS"
        if not is_empty(bd_manager)
        else "NOT_APPLICABLE"
    )

    add_check(
        checks,
        16,
        "contact_details",
        "bd_manager",
        bd_manager,
        None,
        status,
        status != "NOT_APPLICABLE",
        "Approved",
        form_check_comment(
            "Business development manager",
            bd_manager,
            status,
        ),
    )

    # ========================================================
    # CHECK 17 — ACCOUNT
    # ========================================================

    account_contact = find_contact_by_role(
        contacts,
        [
            "account",
            "account manager",
            "accounts",
        ],
    )

    account = get_contact_name(
        account_contact
    )

    status = (
        "PASS"
        if not is_empty(account)
        else "NOT_APPLICABLE"
    )

    add_check(
        checks,
        17,
        "contact_details",
        "account",
        account,
        None,
        status,
        status != "NOT_APPLICABLE",
        "Approved",
        form_check_comment(
            "Account contact",
            account,
            status,
        ),
    )

    # ========================================================
    # CHECK 18 — FINANCE MANAGER
    # ========================================================

    finance_contact = find_contact_by_role(
        contacts,
        [
            "finance",
            "financial",
            "finance manager",
        ],
    )

    finance_manager = get_contact_name(
        finance_contact
    )

    status = (
        "PASS"
        if not is_empty(finance_manager)
        else "NOT_APPLICABLE"
    )

    add_check(
        checks,
        18,
        "contact_details",
        "finance_manager",
        finance_manager,
        None,
        status,
        status != "NOT_APPLICABLE",
        "Approved",
        form_check_comment(
            "Finance manager",
            finance_manager,
            status,
        ),
    )

    # ========================================================
    # TRADE LICENCE DOCUMENT
    # ONLY TRADE LICENCE IS USED
    # ========================================================

    trade_document = get_trade_license_data(
        document_collection
    )

    # ========================================================
    # ORACLE TRADE LICENCE DATA
    # ========================================================

    oracle_trade = (
        trade_class
        if isinstance(trade_class, dict)
        else {}
    )

    # ========================================================
    # TRADE LICENCE FIELD RULES
    # ========================================================

    trade_license_fields = [
        {
            "section": "Certificate_Number",
            "description": "Trade Licence vs Certificate_Number",
            "oracle_fields": [
                "CertificateNumber",
                "certificateNumber",
            ],
            "document_fields": [
                "certificateNumber",
                "CertificateNumber",
            ],
        },
        {
            "section": "Issue_Date",
            "description": "Trade Licence vs Issue_Date",
            "oracle_fields": [
                "StartDate",
                "IssueDate",
                "issueDate",
            ],
            "document_fields": [
                "issueDate",
                "IssueDate",
            ],
        },
        {
            "section": "Expiry_Date",
            "description": "Trade Licence vs Expiry_Date",
            "oracle_fields": [
                "EndDate",
                "ExpiryDate",
                "expiryDate",
            ],
            "document_fields": [
                "expiryDate",
                "ExpiryDate",
            ],
        },
        {
            "section": "Company_Name",
            "description": "Trade Licence vs Company_Name",
            "oracle_fields": [
                "Supplier",
                "supplierName",
                "SupplierName",
                "CompanyName",
            ],
            "document_fields": [
                "companyName",
                "CompanyName",
            ],
        },
        {
            "section": "Business_Name",
            "description": "Trade Licence vs Business_Name",
            "oracle_fields": [
                "Supplier",
                "supplierName",
                "SupplierName",
                "BusinessName",
            ],
            "document_fields": [
                "businessName",
                "BusinessName",
            ],
        },
        {
            "section": "Legal_Type",
            "description": "Trade Licence vs Legal_Type",
            "oracle_fields": [
                "LegalType",
                "legalType",
            ],
            "document_fields": [
                "legalType",
                "LegalType",
            ],
        },
        {
            "section": "Main_License_Number",
            "description": "Trade Licence vs Main_License_Number",
            "oracle_fields": [
                "MainLicenseNumber",
                "mainLicenseNumber",
            ],
            "document_fields": [
                "mainLicenseNumber",
                "MainLicenseNumber",
            ],
        },
        {
            "section": "DCCI_Number",
            "description": "Trade Licence vs DCCI_Number",
            "oracle_fields": [
                "DCCINumber",
                "dcciNumber",
            ],
            "document_fields": [
                "dcciNumber",
                "DCCINumber",
            ],
        },
        {
            "section": "Register_Number",
            "description": "Trade Licence vs Register_Number",
            "oracle_fields": [
                "RegisterNumber",
                "registerNumber",
            ],
            "document_fields": [
                "registerNumber",
                "RegisterNumber",
            ],
        },
        {
            "section": "License_Category",
            "description": "Trade Licence vs License_Category",
            "oracle_fields": [
                "LicenseCategory",
                "licenseCategory",
            ],
            "document_fields": [
                "licenseCategory",
                "LicenseCategory",
            ],
        },
        {
            "section": "Phone",
            "description": "Trade Licence vs Phone",
            "oracle_fields": [
                "Phone",
                "PhoneNumber",
                "phone",
            ],
            "document_fields": [
                "phone",
                "Phone",
            ],
        },
        {
            "section": "Mobile",
            "description": "Trade Licence vs Mobile",
            "oracle_fields": [
                "Mobile",
                "MobileNumber",
                "mobile",
            ],
            "document_fields": [
                "mobile",
                "Mobile",
            ],
        },
        {
            "section": "PO_Box",
            "description": "Trade Licence vs PO_Box",
            "oracle_fields": [
                "POBox",
                "poBox",
            ],
            "document_fields": [
                "poBox",
                "POBox",
            ],
        },
        {
            "section": "Parcel_ID",
            "description": "Trade Licence vs Parcel_ID",
            "oracle_fields": [
                "ParcelId",
                "ParcelID",
                "parcelId",
            ],
            "document_fields": [
                "parcelId",
                "ParcelId",
                "ParcelID",
            ],
        },
    ]

    # ========================================================
    # CREATE TRADE LICENCE CHECKS
    # ========================================================

    next_check_no = 19

    for rule in trade_license_fields:

        oracle_value = get_first_value(
            oracle_trade,
            rule["oracle_fields"],
        )

        # Company/business name can come from the main
        # supplier API if not present in the classification.
        if (
            is_empty(oracle_value)
            and rule["section"]
            in {
                "Company_Name",
                "Business_Name",
            }
        ):

            oracle_value = get_first_value(
                supplier,
                [
                    "Supplier",
                    "supplierName",
                    "SupplierName",
                ],
            )

        document_value = get_first_value(
            trade_document,
            rule["document_fields"],
        )

        status = compare_values(
            oracle_value,
            document_value,
            rule["description"],
        )

        applicable = (
            status != "NOT_APPLICABLE"
        )

        decision = (
            "Approved"
            if status == "PASS"
            else (
                "Resubmission Required"
                if status == "FAIL"
                else "Approved"
            )
        )

        add_check(
            checks,
            next_check_no,
            rule["section"],
            rule["description"],
            oracle_value,
            document_value,
            status,
            applicable,
            decision,
            comparison_comment(
                rule["description"],
                oracle_value,
                document_value,
                status,
            ),
            "TRADE_LICENSE",
        )

        next_check_no += 1

    # ========================================================
    # TRADE LICENCE DATE VALUES
    # ========================================================

    issue_date_value = get_first_value(
        trade_document,
        [
            "issueDate",
            "IssueDate",
        ],
    )

    expiry_date_value = get_first_value(
        trade_document,
        [
            "expiryDate",
            "ExpiryDate",
        ],
    )

    issue_date = normalize_date(
        issue_date_value
    )

    expiry_date = normalize_date(
        expiry_date_value
    )

    # ========================================================
    # ISSUE DATE FORMAT
    # ========================================================

    if issue_date_value and issue_date:

        add_check(
            checks,
            next_check_no,
            "Document_Validity",
            "Trade License Issue Date Format",
            None,
            issue_date_value,
            "PASS",
            True,
            "Approved",
            "Trade License contains a valid issue date.",
            "TRADE_LICENSE_DATE",
        )

    elif issue_date_value:

        add_check(
            checks,
            next_check_no,
            "Document_Validity",
            "Trade License Issue Date Format",
            None,
            issue_date_value,
            "FAIL",
            True,
            "Resubmission Required",
            "Trade License issue date could not be parsed.",
            "TRADE_LICENSE_DATE",
        )

    else:

        add_check(
            checks,
            next_check_no,
            "Document_Validity",
            "Trade License Issue Date Format",
            None,
            None,
            "NOT_APPLICABLE",
            False,
            "Approved",
            "Trade License issue date is not available.",
            "TRADE_LICENSE_DATE",
        )

    next_check_no += 1

    # ========================================================
    # CURRENT VALIDITY
    # ========================================================

    today = datetime.now().date()

    if expiry_date:

        validity_status = (
            "PASS"
            if expiry_date >= today
            else "FAIL"
        )

        validity_comment = (
            "Trade License is currently valid."
            if validity_status == "PASS"
            else "Trade License has expired."
        )

        add_check(
            checks,
            next_check_no,
            "Document_Validity",
            "Trade License Current Validity",
            today.isoformat(),
            expiry_date_value,
            validity_status,
            True,
            (
                "Approved"
                if validity_status == "PASS"
                else "Resubmission Required"
            ),
            validity_comment,
            "TRADE_LICENSE_DATE",
        )

    elif expiry_date_value:

        add_check(
            checks,
            next_check_no,
            "Document_Validity",
            "Trade License Current Validity",
            today.isoformat(),
            expiry_date_value,
            "FAIL",
            True,
            "Resubmission Required",
            "Trade License expiry date could not be parsed.",
            "TRADE_LICENSE_DATE",
        )

    else:

        add_check(
            checks,
            next_check_no,
            "Document_Validity",
            "Trade License Current Validity",
            today.isoformat(),
            None,
            "NOT_APPLICABLE",
            False,
            "Approved",
            "Trade License expiry date is not available.",
            "TRADE_LICENSE_DATE",
        )

    next_check_no += 1

    # ========================================================
    # ISSUE / EXPIRY CHRONOLOGY
    # ========================================================

    if issue_date and expiry_date:

        chronology_status = (
            "PASS"
            if issue_date <= expiry_date
            else "FAIL"
        )

        chronology_comment = (
            "Trade License dates are chronologically valid."
            if chronology_status == "PASS"
            else "Trade License issue date is after the expiry date."
        )

        add_check(
            checks,
            next_check_no,
            "Document_Validity",
            "Trade License Issue and Expiry Chronology",
            issue_date_value,
            expiry_date_value,
            chronology_status,
            True,
            (
                "Approved"
                if chronology_status == "PASS"
                else "Resubmission Required"
            ),
            chronology_comment,
            "TRADE_LICENSE_DATE",
        )

    else:

        add_check(
            checks,
            next_check_no,
            "Document_Validity",
            "Trade License Issue and Expiry Chronology",
            issue_date_value,
            expiry_date_value,
            "NOT_APPLICABLE",
            False,
            "Approved",
            "Trade License issue and expiry dates are not both available.",
            "TRADE_LICENSE_DATE",
        )

    # ========================================================
    # SCORE
    # ========================================================

    passed = sum(
        1
        for check in checks
        if check["status"] == "PASS"
    )

    failed = sum(
        1
        for check in checks
        if check["status"] == "FAIL"
    )

    warnings = sum(
        1
        for check in checks
        if check["status"] == "WARNING"
    )

    not_applicable = sum(
        1
        for check in checks
        if check["status"] == "NOT_APPLICABLE"
    )

    applicable = (
        passed
        + failed
        + warnings
    )

    percentage = (
        round(
            (passed / applicable) * 100
        )
        if applicable
        else 0
    )

    # ========================================================
    # OVERALL STATUS
    #
    # 90–100 = PASS
    # 70–89  = WARNING
    # <70    = FAIL
    # ========================================================

    if percentage >= 90:

        overall_status = "PASS"

    elif percentage >= 70:

        overall_status = "WARNING"

    else:

        overall_status = "FAIL"

    # ========================================================
    # SUPPLIER INFORMATION
    # ========================================================

    supplier_name = get_first_value(
        supplier,
        [
            "Supplier",
            "supplierName",
            "SupplierName",
        ],
    )

    supplier_id = get_first_value(
        supplier,
        [
            "SupplierId",
            "supplierId",
        ],
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    result = {
        supplier_name: {
            "supplierName": supplier_name,
            "supplierId": supplier_id,

            "score": {
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "notApplicable": not_applicable,
                "applicable": applicable,
                "percentage": percentage,
                "status": overall_status,
            },

            "decision": overall_status,

            "reviewedBy": "AI Validation Engine",

            "reviewedAt": datetime.now().strftime(
                "%Y-%m-%dT%H:%M:%S"
            ),

            "reviewerComments": (
                "Validation generated dynamically from "
                "Oracle Fusion supplier data and the "
                "Trade Licence PDF only."
            ),

            "checks": checks,
        }
    }

    return result
