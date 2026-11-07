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
            self,
            text= "Izaberi PDF-ove",
            command=self.choose_pdf_files
        )
        self.choose_pdf.pack(pady=10)


    def choose_pdf_files(self) -> None:
        from tkinter import filedialog
        files = filedialog.askopenfilenames(
            parent=self,
            title="Izaberi PDF-ove",
            filetypes=(("PDF fajlovi", "*pdf"),),
        )
        if not files:
            return

        self.pdf_paths = list(files)
        print(self.pdf_paths)
        self.status_label.configure(
        text=f"Izabrano PDF fajlova: {len(self.pdf_paths)}"
        )




def main() -> None:
    app = PdfToolkitApp()
    app.mainloop()


if __name__ == "__main__":
    main()
