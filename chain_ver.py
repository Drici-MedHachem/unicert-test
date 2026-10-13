from pyhanko.pdf_utils.reader import PdfFileReader

with open("signed.pdf", "rb") as pdf_file:
    reader = PdfFileReader(pdf_file)

    for embedded_signature in reader.embedded_signatures:
        print("Signature field:", embedded_signature.field_name)

        embedded_certs = embedded_signature.other_embedded_certs

        print("Additional embedded certificates:", len(embedded_certs))

        for cert in embedded_certs:
            print(cert.subject.human_friendly)
            print("  Issuer:", cert.issuer.human_friendly)