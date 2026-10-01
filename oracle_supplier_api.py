from oracle_api import (
    get_oracle_data,
    get_oracle_file_content,
)


# ============================================================
# GET SUPPLIER BY NAME
# ============================================================

def get_supplier_by_name(supplier_name):

    endpoint = (
        "/fscmRestApi/resources/latest/suppliers"
    )

    params = {
        "q": f'Supplier="{supplier_name}"'
    }

    data = get_oracle_data(
        endpoint,
        params=params
    )

    suppliers = data.get("items", [])

    if not suppliers:
        return None

    return suppliers[0]


# ============================================================
# GET SUPPLIER BY ID
# ============================================================

def get_supplier_by_id(supplier_id):

    endpoint = (
        f"/fscmRestApi/resources/latest/"
        f"suppliers/{supplier_id}"
    )

    return get_oracle_data(endpoint)


# ============================================================
# API 1: BUSINESS CLASSIFICATIONS
# ============================================================

def get_business_classifications(supplier_id):

    endpoint = (
        f"/fscmRestApi/resources/11.13.18.05/"
        f"suppliers/{supplier_id}/"
        f"child/businessClassifications"
    )

    return get_oracle_data(endpoint)


# ============================================================
# API 2: SUPPLIER ATTACHMENTS
# ============================================================

def get_supplier_attachments(supplier_id):

    endpoint = (
        f"/fscmRestApi/resources/11.13.18.05/"
        f"suppliers/{supplier_id}/"
        f"child/attachments"
    )

    return get_oracle_data(endpoint)


# ============================================================
# SUPPLIER DFF
# ============================================================

def get_supplier_dff(supplier_id):

    endpoint = (
        f"/fscmRestApi/resources/11.13.18.05/"
        f"suppliers/{supplier_id}/child/DFF"
    )

    return get_oracle_data(endpoint)

# ============================================================
# FIND TRADE LICENSE ATTACHMENT
# ============================================================

def find_trade_license_attachment(attachments):

    if not attachments:
        return None

    items = attachments.get("items", [])

    for attachment in items:

        filename = attachment.get(
            "FileName",
            ""
        )

        if "trade license" in filename.lower():

            return attachment

    return None


# ============================================================
# API 3: FIND FILE CONTENTS URL
# ============================================================

def find_file_contents_url(attachment):

    if not attachment:
        return None

    links = attachment.get(
        "links",
        []
    )

    for link in links:

        name = link.get(
            "name",
            ""
        )

        rel = link.get(
            "rel",
            ""
        )

        href = link.get(
            "href",
            ""
        )

        # Oracle FileContents enclosure
        if (
            name.lower() == "filecontents"
            and rel.lower() == "enclosure"
            and href
        ):
            return href

    return None


# ============================================================
# API 4: GET FILE CONTENTS
# ============================================================

def get_file_contents(file_contents_url):

    if not file_contents_url:
        return None

    return get_oracle_file_content(
        file_contents_url
    )
# ============================================================
# SUPPLIER ADDRESSES
# ============================================================

def get_supplier_addresses(supplier_id):

    endpoint = (
        f"/fscmRestApi/resources/11.13.18.05/"
        f"suppliers/{supplier_id}/child/addresses"
    )

    return get_oracle_data(endpoint)


# ============================================================
# SUPPLIER CONTACTS
# ============================================================

def get_supplier_contacts(supplier_id):

    endpoint = (
        f"/fscmRestApi/resources/11.13.18.05/"
        f"suppliers/{supplier_id}/child/contacts"
    )

    return get_oracle_data(endpoint)


# ============================================================
# PRODUCTS AND SERVICES
# ============================================================

def get_supplier_products_and_services(supplier_id):

    endpoint = (
        f"/fscmRestApi/resources/11.13.18.05/"
        f"suppliers/{supplier_id}/child/productsAndServices"
    )

    return get_oracle_data(endpoint)