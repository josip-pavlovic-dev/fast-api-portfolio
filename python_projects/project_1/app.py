import os
from tkinter import filedialog

import customtkinter as ctk  # type: ignore[import-untyped]


def parsiranje_brojeva_stranica(
    tekst: str | None,
    total_pages: int,
) -> list[int]:
    """Parsiraj i proveri unos stranica, na primer '1, 3-5'."""
    if total_pages < 1:
        raise ValueError("PDF mora da sadrži najmanje jednu stranicu.")
    if tekst is None or not tekst.strip():
        raise ValueError("Unos stranica ne sme biti prazan.")

    brojevi_stranica: list[int] = []

    for deo in tekst.strip().split(","):
        deo = deo.strip()
        if not deo:
            raise ValueError("Unos sadrži prazan deo između zareza.")

        if "-" in deo and not deo.startswith("-"):
            krajevi_opsega = deo.split("-")
            if len(krajevi_opsega) != 2:
                raise ValueError(f"Neispravan opseg stranica: {deo}")

            try:
                start, end = (int(kraj.strip()) for kraj in krajevi_opsega)
            except ValueError as error:
                raise ValueError(f"Neispravan opseg stranica: {deo}") from error

            if start <= 0 or end <= 0:
                raise ValueError("Broj stranice mora biti pozitivan")
            if start > end:
                raise ValueError("Početna stranica ne može biti veća od krajnje")
            if start > total_pages or end > total_pages:
                raise ValueError(
                    f"Brojevi stranica ne mogu biti veći od {total_pages}."
                )

            brojevi_stranica.extend(range(start, end + 1))
        else:
            try:
                broj = int(deo)
            except ValueError as error:
                raise ValueError(f"Neispravan unos: {deo}") from error

            if broj <= 0:
                raise ValueError("Broj stranice mora biti pozitivan")
            if broj > total_pages:
                raise ValueError(f"Broj stranice ne može biti veći od {total_pages}.")

            brojevi_stranica.append(broj)

    return brojevi_stranica


class PdfToolkitApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.pdf_paths: list[str] = []

        self.title("PDF Toolkit")
        self.geometry("720x480")
        self.minsize(560, 360)

        self.title_label = ctk.CTkLabel(
            self,
            text="PDF Toolkit",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        self.title_label.pack(padx=24, pady=(32, 12))

        self.status_label = ctk.CTkLabel(
            self,
            text="Početni prozor je spreman.",
        )
        self.status_label.pack(padx=24, pady=12)

        # Dugme za izbor PDF fajlova
        self.choose_pdf = ctk.CTkButton(
            self, text="Izaberi PDF-ove", command=self.choose_pdf_files
        )
        self.choose_pdf.pack(pady=10)

        # Dugme za spajanje PDF fajlova
        self.merge_pdf = ctk.CTkButton(
            self, text="Spoji PDF-ove", command=self.merge_pdfs
        )
        self.merge_pdf.pack(pady=10)

    # Funkcija za izbor PDF fajlova
    def choose_pdf_files(self) -> None:

        files = filedialog.askopenfilenames(
            parent=self,  # self zato što je ovo glavni prozor aplikacije i želimo da dijalog bude modalno vezan za njega
            title="Izaberi PDF-ove",
            filetypes=(
                ("PDF fajlovi", "*.pdf"),
            ),  # Ograničava dijalog na prikaz samo PDF fajlova
        )
        if not files:
            return

        # Dodaje nove PDF fajlove u listu samo ako već nisu izabrani ranije
        for pdf_path in files:
            if pdf_path not in self.pdf_paths:
                self.pdf_paths.append(pdf_path)

        print(self.pdf_paths)
        self.status_label.configure(text=f"Izabrano PDF fajlova: {len(self.pdf_paths)}")

        # Prikazuje imena izabranih PDF fajlova u status labeli
        if self.pdf_paths:
            file_names = [os.path.basename(path) for path in self.pdf_paths]
            self.status_label.configure(text="\n".join(file_names))

    # Funkcija za spajanje PDF fajlova
    def merge_pdfs(self) -> None:
        from pypdf import PdfWriter

        if len(self.pdf_paths) < 2:
            self.status_label.configure(text="Izaberite najmanje dva PDF fajla.")
            return

        output_path = filedialog.asksaveasfilename(
            parent=self,
            title="Sačuvaj spojeni PDF",
            defaultextension=".pdf",
            filetypes=(("PDF fajlovi", "*.pdf"),),
        )
        if not output_path:
            self.status_label.configure(text="Spajanje PDF-ova otkazano.")
            return

        output_realpath = os.path.normcase(os.path.realpath(output_path))
        input_realpaths = {
            os.path.normcase(os.path.realpath(pdf_path)) for pdf_path in self.pdf_paths
        }
        if output_realpath in input_realpaths:
            self.status_label.configure(
                text="Izaberite izlazni fajl koji nije jedan od ulaznih PDF-ova."
            )
            return

        self.status_label.configure(text="Spajanje PDF-ova u toku...")
        self.update_idletasks()

        writer = PdfWriter()
        for pdf_path in self.pdf_paths:
            writer.append(pdf_path)

        # Čuva spojeni PDF fajl na izabranoj lokaciji
        with open(
            output_path, "wb"
        ) as f:  # "wb" znači write binary, potrebno za PDF fajlove
            writer.write(f)
        self.status_label.configure(text=f"PDF-ovi su spojeni u: {output_path}")


def main() -> None:
    app = PdfToolkitApp()
    app.mainloop()


if __name__ == "__main__":
    main()
