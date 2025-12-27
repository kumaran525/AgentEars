from pathlib import Path

# Get the path of the current script, resolve it to an absolute path,
# and then access its parent's parent.
root = Path(__file__).resolve().parent.parent

# Join the path to the desired subdirectory
data_path = Path(root / "data")
transcript_path = Path(root / "data/transcript")
db_path = Path(root / "data/agentears.db")
config_path = Path(root / "config")

PII_PATTERNS = [
    # === Identity Numbers ===
    r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b",  # SSN (with variations: 123-45-6789, 123 45 6789)
    r"\b\d{9}\b",  # SSN without separators
    r"\b\d{2}-\d{7}\b",  # EIN (Employer Identification Number)
    # === Financial Account Numbers ===
    r"\b\d{16}\b",  # Credit card (16 digits)
    r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # Credit card with separators
    r"\b\d{13,19}\b",  # Credit/debit card (13-19 digits)
    r"\b\d{10,18}\b",  # Bank account number
    r"\b\d{9}\b",  # Routing number (9 digits)
    r"\bACCT[-\s]?#?[-\s]?\d{8,18}\b",  # Account number with prefix
    r"\bACC(?:OU)?NT[-\s]?(?:NUMBER|NO|#)?[-\s]?\d{8,18}\b",  # Account variations
    r"\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b",  # IBAN
    r"\b[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?\b",  # SWIFT/BIC code
    # === Payment Card Info ===
    r"\b(?:CVV|CVC|CSC|CVN)[-\s]?\d{3,4}\b",  # CVV/CVC code
    r"\b\d{2}/\d{2,4}\b",  # Expiration date (MM/YY or MM/YYYY)
    r"\b(?:0[1-9]|1[0-2])/\d{2,4}\b",  # Expiration date validated
    r"\b(?:EXP|EXPIR(?:Y|ATION)?)[-\s]?(?:DATE)?[-\s]?\d{2}/\d{2,4}\b",
    # === Contact Information ===
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",  # Email
    r"\b\d{10}\b",  # Phone (10 digits)
    r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b",  # Phone with separators
    r"\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b",  # International phone
    r"\b1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",  # US/Canada phone
    r"\b\(\d{3}\)\s?\d{3}-\d{4}\b",  # Phone format: (123) 456-7890
    # === Address Information ===
    r"\b\d{1,5}\s+([A-Z][a-z]+\s+){1,3}(Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way|Circle|Cir|Place|Pl)\b",  # Street address
    r"\b\d{5}(?:-\d{4})?\b",  # ZIP code
    r"\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b",  # Canadian postal code
    r"\b(?:P\.?O\.?\s?BOX|PO\s?BOX)\s+\d+\b",  # PO Box
    # === Government IDs ===
    r"\b[A-Z]\d{8}\b",  # Passport number (simplified)
    r"\b[A-Z]{1,2}\d{6,8}\b",  # Driver's license (varies by state)
    r"\b\d{2}-\d{7}\b",  # Tax ID
    r"\bITIN[-\s]?\d{2}-\d{7}\b",  # Individual Taxpayer Identification Number
    # === Personal Information ===
    r"\b(?:DOB|DATE\s+OF\s+BIRTH)[-:\s]+\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",  # Date of birth
    r"\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b",  # Date format (may catch DOB)
    r"\b(?:19|20)\d{2}[-/]\d{1,2}[-/]\d{1,2}\b",  # Date format YYYY-MM-DD
    # === Banking-Specific ===
    r"\b(?:PIN|PERSONAL\s+ID(?:ENTIFICATION)?\s+NUMBER)[-:\s]+\d{4,6}\b",  # PIN
    r"\b(?:LOAN|MORTGAGE)\s+(?:NUMBER|NO|#)?[-\s]?\d{8,15}\b",  # Loan number
    r"\b(?:CHECK|CHEQUE)\s+(?:NUMBER|NO|#)?[-\s]?\d{4,10}\b",  # Check number
    r"\b(?:WIRE|TRANSFER)\s+(?:REFERENCE|REF|#)?[-\s]?\w{8,20}\b",  # Wire reference
    r"\b(?:DEBIT|CREDIT)\s+CARD\s+(?:NUMBER|NO)?[-\s]?\d{13,19}\b",
    r"\b(?:MOTHER(?:'S)?|MAIDEN)\s+NAME[-:\s]+[A-Z][a-z]+\b",  # Security questions
    # === Biometric & Security ===
    r"\b(?:PASSWORD|PASSPHRASE|PASSCODE)[-:\s]+\S+\b",  # Passwords
    r"\b(?:SECURITY\s+)?(?:QUESTION|ANSWER)[-:\s]+.{3,}\b",  # Security Q&A
    r"\b(?:OTP|ONE[-\s]?TIME[-\s]?PASSWORD)[-:\s]+\d{4,8}\b",  # OTP codes
    r"\b(?:TOKEN|AUTH(?:ENTICATION)?)\s+CODE[-:\s]+\w{6,}\b",  # Auth tokens
    # === Medical/Insurance ===
    r"\b\d{3}-\d{2}-\d{4}\b(?=.*(?:MEDICARE|MEDICAID|HEALTH))",  # Medicare/Medicaid
    r"\b(?:POLICY|MEMBER|GROUP)\s+(?:NUMBER|NO|ID|#)?[-\s]?\w{6,15}\b",  # Insurance policy
    # === Vehicle/Property ===
    r"\b[A-Z0-9]{17}\b",  # VIN (Vehicle Identification Number)
    r"\b\d{3}-\d{2}-\d{4}\b(?=.*(?:PROPERTY|PARCEL))",  # Property tax ID
    # === Employment ===
    r"\b(?:EMPLOYEE|EMP)\s+(?:ID|NUMBER|NO|#)?[-\s]?\d{5,10}\b",  # Employee ID
    r"\b\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?\b",  # Salary/income amounts
    # === Names (contextual) ===
    r"\b(?:MY|HIS|HER)\s+NAME\s+IS\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b",  # Name disclosure
    r"\b(?:I'M|I\s+AM|THIS\s+IS)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b",  # Caller introduction
    # === Common Verbal Patterns in Transcripts ===
    r"\b(?:THE\s+LAST\s+FOUR\s+(?:DIGITS|NUMBERS))[-:\s]+\d{4}\b",  # Last 4 digits
    r"\b(?:CONFIRM|VERIFY)\s+(?:YOUR|THE)?\s*\d{4,16}\b",  # Verification requests
    r"\b(?:ENDING\s+IN|ENDS\s+IN)[-:\s]+\d{4}\b",  # Card ending in
]
