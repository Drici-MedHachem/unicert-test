
from pathlib import Path

from pyhanko import stamp
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers
from pyhanko.sign.fields import SigFieldSpec,SigSeedSubFilter

# Input and output files
INPUT_PDF = Path("input.pdf")
OUTPUT_PDF = Path("signed.pdf")

# Signing credentials
PRIVATE_KEY = Path("dmh.key")
SIGNER_CERT = Path("dmh.crt")
INTERMEDIATE_CERT = Path("unicert_intermediate_ca.crt")
ROOT_CERT = Path("unicert_root_ca.crt")


# Document verification URL
VERIFY_URL = "https://www.univ-eloued.dz/ar/" # I have to edit this one to match the UPM style of ?get=DOCID

# Visible signature information (both will be changed to become dynamically stored)
SIGNER_NAME = "Drici Mohammed Hachem" 
SIGNER_ROLE = "Student CS Dept"


def sign_pdf():
    for path in (INPUT_PDF, PRIVATE_KEY, SIGNER_CERT):
        if not path.is_file():
            raise FileNotFoundError(f"Required file not found: {path}")

    # 2. Load the signer's certificate and private key.
    chain_files = (
        (str(INTERMEDIATE_CERT),str(ROOT_CERT),)
        if INTERMEDIATE_CERT.is_file() and ROOT_CERT.is_file()
        else ()
    )

    signer = signers.SimpleSigner.load(
        key_file=str(PRIVATE_KEY),
        cert_file=str(SIGNER_CERT),
        ca_chain_files=chain_files,
        key_passphrase=None,
    )

    with INPUT_PDF.open("rb") as pdf_in:
        writer = IncrementalPdfFileWriter(pdf_in)

        signature_field = SigFieldSpec(
            sig_field_name="UniversityOfElOuedSignature",
            on_page=6,
            box=(300, 50, 550, 150),
        )

        metadata = signers.PdfSignatureMetadata(
            field_name="UniversityOfElOuedSignature",
            md_algorithm="sha256",
            subfilter=SigSeedSubFilter.PADES,
        )

        appearance = stamp.QRStampStyle(
            stamp_text=(
                "Digitally signed by %(signer)s\n"
                "Role: %(role)s\n"
                "Time: %(ts)s\n"
                "Scan the QR code to verify this document."
            )
        )

        pdf_signer = signers.PdfSigner(
            signature_meta=metadata,
            signer=signer,
            stamp_style=appearance,
            new_field_spec=signature_field,
        )

        with OUTPUT_PDF.open("wb") as pdf_out:
            pdf_signer.sign_pdf(
                writer,
                output=pdf_out,
                appearance_text_params={
                    "url": VERIFY_URL,
                    "signer": SIGNER_NAME,
                    "role": SIGNER_ROLE,
                },
            )

    print(f"Signed PDF created: {OUTPUT_PDF.resolve()}")


if __name__ == "__main__":
    sign_pdf()