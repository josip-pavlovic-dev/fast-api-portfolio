import os
from tkinter import filedialog

import customtkinter as ctk  # type: ignore[import-untyped]


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
            parent=self,
            title="Izaberi PDF-ove",
            filetypes=(("PDF fajlovi", "*.pdf"),),
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
