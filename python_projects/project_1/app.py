import customtkinter as ctk  # type: ignore[import-untyped]


class PdfToolkitApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

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


def main() -> None:
    app = PdfToolkitApp()
    app.mainloop()


if __name__ == "__main__":
    main()
