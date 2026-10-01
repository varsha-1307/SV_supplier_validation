import json
import os


from oracle_supplier_api import (
    get_supplier_by_id,
    get_supplier_addresses,
    get_supplier_contacts,
    get_supplier_products_and_services,
    get_business_classifications,
)


from comparison import (
    compare_business_classifications,
    compare_address,
    compare_products_services,
    compare_contact_details,
    compare_trade_license,
    compare_company_name,
    build_validation_result,
)


# ============================================================
# SUPPLIER ID
# ============================================================

supplier_id = input(
    "Enter Supplier ID: "
).strip()


# ============================================================
# GET SUPPLIER
# ============================================================

supplier = get_supplier_by_id(
    supplier_id
)


if not supplier:

    raise ValueError(
        "Supplier not found."
    )


# ============================================================
# VALIDATE SUPPLIER ID
# ============================================================

returned_supplier_id = str(
    supplier.get(
        "SupplierId"
    )
)


if returned_supplier_id != str(
    supplier_id
):

    raise ValueError(
        "Oracle returned a different SupplierId. "
        "Processing stopped to prevent supplier substitution."
    )


# ============================================================
# SUPPLIER INFORMATION
# ============================================================

print()
print(
    "============================================================"
)
print(
    "SUPPLIER IDENTIFICATION"
)
print(
    "============================================================"
)

print(
    f"Supplier Name: "
    f"{supplier.get('Supplier')}"
)

print(
    f"Supplier ID: "
    f"{supplier.get('SupplierId')}"
)

print(
    f"Supplier Number: "
    f"{supplier.get('SupplierNumber')}"
)

print(
    f"Status: "
    f"{supplier.get('Status')}"
)


# ============================================================
# GET ORACLE DATA
# ============================================================

print()
print(
    "============================================================"
)
print(
    "ORACLE FUSION DATA"
)
print(
    "============================================================"
)


business_classifications = (
    get_business_classifications(
        supplier_id
    )
)


addresses = (
    get_supplier_addresses(
        supplier_id
    )
)


contacts = (
    get_supplier_contacts(
        supplier_id
    )
)


products_and_services = (
    get_supplier_products_and_services(
        supplier_id
    )
)


print(
    "Business Classifications:"
)

print(
    len(
        business_classifications.get(
            "items",
            []
        )
    )
)


print(
    "Addresses:"
)

print(
    len(
        addresses.get(
            "items",
            []
        )
    )
)


print(
    "Contacts:"
)

print(
    len(
        contacts.get(
            "items",
            []
        )
    )
)


print(
    "Products & Services:"
)

print(
    len(
        products_and_services.get(
            "items",
            []
        )
    )
)


# ============================================================
# LOAD CACHED GEMINI DOCUMENT
# ============================================================

pdf_path = "trade_license.pdf"

cache_directory = "extracted_data"

cache_file = os.path.join(
    cache_directory,
    "Samsotech_LLC_trade_license.json"
)


print()
print(
    "============================================================"
)
print(
    "GEMINI DOCUMENT EXTRACTION"
)
print(
    "============================================================"
)


if os.path.exists(
    cache_file
):

    print(
        "Cached Gemini extraction found."
    )

    print(
        "Using saved JSON."
    )

    with open(
        cache_file,
        "r",
        encoding="utf-8"
    ) as file:

        document_data = json.load(
            file
        )


else:

    from gemini_extractor import (
        extract_trade_license
    )

    print(
        "No cached extraction found."
    )

    print(
        "Calling Gemini..."
    )

    document_data = (
        extract_trade_license(
            pdf_path
        )
    )

    os.makedirs(
        cache_directory,
        exist_ok=True
    )

    with open(
        cache_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            document_data,
            file,
            indent=4
        )


# ============================================================
# BUILD ALL CHECKS
# ============================================================

checks = []


# ------------------------------------------------------------
# 1. BUSINESS CLASSIFICATION
# ------------------------------------------------------------

checks.extend(
    compare_business_classifications(
        business_classifications
    )
)


# ------------------------------------------------------------
# 2. ADDRESS
# ------------------------------------------------------------

checks.extend(
    compare_address(
        addresses
    )
)


# ------------------------------------------------------------
# 3. PRODUCTS AND SERVICES
# ------------------------------------------------------------

checks.extend(
    compare_products_services(
        products_and_services
    )
)


# ------------------------------------------------------------
# 4. CONTACT DETAILS
# ------------------------------------------------------------

checks.extend(
    compare_contact_details(
        contacts
    )
)


# ============================================================
# BUILD ORACLE FORM DATA FOR TRADE LICENSE
# ============================================================

from oracle_form_data import (
    build_oracle_form_data
)


oracle_form_data = (
    build_oracle_form_data(
        supplier=supplier,
        addresses=addresses,
        contacts=contacts,
        business_classifications=(
            business_classifications
        ),
        products_and_services=(
            products_and_services
        ),
    )
)


# ------------------------------------------------------------
# 5. TRADE LICENSE
# ------------------------------------------------------------

checks.extend(
    compare_trade_license(
        oracle_form_data,
        document_data
    )
)


# ------------------------------------------------------------
# 6. COMPANY NAME
# ------------------------------------------------------------

checks.extend(
    compare_company_name(
        oracle_form_data,
        document_data
    )
)


# ============================================================
# FINAL RESULT
# ============================================================

final_result = (
    build_validation_result(
        supplier,
        checks
    )
)


# ============================================================
# DISPLAY FINAL JSON
# ============================================================

print()
print(
    "============================================================"
)

print(
    "FINAL SUPPLIER VALIDATION RESULT"
)

print(
    "============================================================"
)

print(
    json.dumps(
        final_result,
        indent=4,
        ensure_ascii=False
    )
)


# ============================================================
# SAVE FINAL JSON
# ============================================================

output_directory = (
    "validation_results"
)


os.makedirs(
    output_directory,
    exist_ok=True
)


output_file = os.path.join(
    output_directory,
    f"{supplier.get('Supplier')}"
    "_validation.json"
)


with open(
    output_file,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        final_result,
        file,
        indent=4,
        ensure_ascii=False
    )


print()
print(
    "Validation result saved to:"
)

print(
    output_file
)