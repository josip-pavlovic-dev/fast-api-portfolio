import os

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

        self.choose_pdf = ctk.CTkButton(
            self, text="Izaberi PDF-ove", command=self.choose_pdf_files
        )
        self.choose_pdf.pack(pady=10)

        self.marge_pdf = ctk.CTkButton(
            self, text="Spoji PDF-ove", command=self.merge_pdfs
        )
        self.marge_pdf.pack(pady=10)

    def merge_pdfs(self) -> None:
        from pypdf import PdfWriter

        writer = PdfWriter()

        if not self.pdf_paths:
            self.status_label.configure(text="Nema izabranih PDF-ova za spajanje.")
            return

        for pdf_path in self.pdf_paths:
            writer.append(pdf_path)

    def choose_pdf_files(self) -> None:
        from tkinter import filedialog

        files = filedialog.askopenfilenames(
            parent=self,
            title="Izaberi PDF-ove",
            filetypes=(("PDF fajlovi", "*pdf"),),
        )
        if not files:
            return

        for pdf_path in files:
            if pdf_path not in self.pdf_paths:
                self.pdf_paths.append(pdf_path)

        print(self.pdf_paths)
        self.status_label.configure(text=f"Izabrano PDF fajlova: {len(self.pdf_paths)}")

        if self.pdf_paths:
            file_names = [os.path.basename(path) for path in self.pdf_paths]
            self.status_label.configure(text="\n".join(file_names))


def main() -> None:
    app = PdfToolkitApp()
    app.mainloop()


if __name__ == "__main__":
    main()
