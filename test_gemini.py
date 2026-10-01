from gemini_extractor import extract_trade_license


pdf_path = "trade_license.pdf"


print("========== GEMINI TRADE LICENSE EXTRACTION ==========")

result = extract_trade_license(
    pdf_path
)


print("Extraction completed.")
print()


for key, value in result.items():

    print(f"{key}: {value}")