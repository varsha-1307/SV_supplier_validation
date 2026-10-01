# ============================================================
# BUILD ORACLE FORM DATA
# ============================================================


def get_first_item(data):
    """
    Safely return the first item from an Oracle collection response.
    """
    if not data:
        return None

    items = data.get("items", [])

    if not items:
        return None

    return items[0]


def get_trade_license_classification(business_classifications):
    """
    Find the Trade Licence business classification.
    """
    if not business_classifications:
        return None

    items = business_classifications.get("items", [])

    for item in items:
        classification = str(
            item.get("Classification", "")
        ).strip().lower()

        if classification == "trade licence":
            return item

    return None


def build_oracle_form_data(
    supplier,
    addresses=None,
    contacts=None,
    business_classifications=None,
    products_and_services=None,
):
    """
    Build the Oracle-side supplier form data.

    Only values that are actually available from the
    inspected Oracle APIs are mapped.
    """

    addresses = addresses or {}
    contacts = contacts or {}

    business_classifications = (
        business_classifications or {}
    )

    products_and_services = (
        products_and_services or {}
    )

    # --------------------------------------------------------
    # ADDRESS
    # --------------------------------------------------------

    address = get_first_item(addresses)

    # --------------------------------------------------------
    # CONTACT
    # --------------------------------------------------------

    contact = get_first_item(contacts)

    # --------------------------------------------------------
    # TRADE LICENCE CLASSIFICATION
    # --------------------------------------------------------

    trade_license = get_trade_license_classification(
        business_classifications
    )

    # --------------------------------------------------------
    # TRADE LICENSE PHONE / MOBILE
    # --------------------------------------------------------
    #
    # Do not map Oracle supplier address/contact phone
    # numbers to Trade License phone/mobile fields.
    #
    # These are supplier contact details and are not
    # verified Trade License values.
    #
    # Therefore they remain None for Trade License comparison.

    phone = None

    mobile = None

    # --------------------------------------------------------
    # PO BOX
    # --------------------------------------------------------

    po_box = None

    if address:
        # Oracle does not expose a dedicated POBox field
        # in this response.
        #
        # For this supplier, AddressLine1 contains 117564,
        # which is being used as the PO Box value.

        po_box = address.get("AddressLine1")

    # --------------------------------------------------------
    # PRODUCTS AND SERVICES
    # --------------------------------------------------------

    products_services = []

    for item in products_and_services.get(
        "items",
        []
    ):
        category_name = item.get(
            "CategoryName"
        )

        if category_name:
            products_services.append(
                category_name
            )

    # --------------------------------------------------------
    # FORM DATA
    # --------------------------------------------------------

    form_data = {

        # ----------------------------------------------------
        # Supplier identification
        # ----------------------------------------------------

        "supplierName": supplier.get(
            "Supplier"
        ),

        "supplierId": supplier.get(
            "SupplierId"
        ),

        "supplierNumber": supplier.get(
            "SupplierNumber"
        ),

        "status": supplier.get(
            "Status"
        ),

        # ----------------------------------------------------
        # Trade Licence
        # ----------------------------------------------------

        "certificateNumber": (
            trade_license.get("CertificateNumber")
            if trade_license
            else None
        ),

        # These fields are NOT available from the
        # inspected Oracle APIs.

        "issueDate": None,

        "expiryDate": None,

        "companyName": supplier.get(
            "Supplier"
        ),

        "businessName": supplier.get(
            "Supplier"
        ),

        # Do not map SupplierType or TaxOrganizationType
        # directly to legalType because they are not the
        # same semantic field as the document's legal type.

        "legalType": None,

        "mainLicenseNumber": None,

        "dcciNumber": None,

        "registerNumber": None,

        "licenseCategory": None,

        "phone": phone,

        "mobile": mobile,

        "poBox": po_box,

        "parcelId": None,

        # ----------------------------------------------------
        # Additional Oracle supplier information
        # ----------------------------------------------------

       "address": address,

"contact": contact,

# Full Oracle address collection
"addresses": addresses.get(
    "items",
    []
),

# Full Oracle contact collection
"contacts": contacts.get(
    "items",
    []
),

"productsAndServices": products_services,

"businessClassifications": (
    business_classifications.get(
        "items",
        []
    )
),
    }

    return form_data