import tkinter as tk
from tkinter import filedialog
import struct
import os
import cv2
import numpy as np

class Aplicatie(tk.Tk):
    def __init__(self):
        super().__init__()

        # Setări fereastră
        self.title("Aplicație Desktop")
        self.geometry("500x400")

        self.afiseaza_mesaj_bienvenue()

    def curata_ecranul(self):
        #Șterge toate widget-urile de pe fereastră
        for widget in self.winfo_children():
            widget.destroy()

    def ecran_principal(self):
        self.curata_ecranul()
        
        # Titlu ecran
        self.label = tk.Label(self, text="Meniu Principal", font=("Arial", 20, "bold"))
        self.label.pack(pady=30)

        self.button_deschidere_imagine = tk.Button(self, text="Deschide Imagine", font=("Arial", 14), command=self.deschide_imagine)
        self.button_deschidere_imagine.pack(pady=10)

    def afiseaza_mesaj_bienvenue(self):
        self.curata_ecranul()
        
        # Mesaj nou
        self.label = tk.Label(self, text="Bine ai venit în aplicație! ;)", font=("Arial", 18))
        self.label.pack(pady=40)

        self.after(3000, self.ecran_principal)  # După 3 secunde, trece la ecranul principal

    def deschide_imagine(self):
        file_path = filedialog.askopenfilename(
            title="Selectează un fișier BMP pe 24 biți",
            filetypes=[("BMP files", "*.bmp")]
        )

        if file_path:
            try:
                # 1. Folosim funcția ta de citire manuală
                self.img_matrix = read_bmp_24bit(file_path)
                
                h = len(self.img_matrix)
                w = len(self.img_matrix[0])

                # 2. Creăm un PhotoImage gol în Tkinter
                self.img_tk = tk.PhotoImage(width=w, height=h)

                # 3. Conversie Matrice -> Formatul Tkinter (Hexadecimal)
                # Construim rândurile de pixeli sub formă de text formatat: { #color #color }
                img_data = ""
                for row in self.img_matrix:
                    # Transformăm fiecare [R, G, B] în #rrggbb
                    row_hex = " ".join(f"#{r:02x}{g:02x}{b:02x}" for r, g, b in row)
                    img_data += "{" + row_hex + "} "
                
                # "Injectăm" toate datele în obiectul imagine
                self.img_tk.put(img_data)

                # 4. Afișăm rezultatul
                self.curata_ecranul()
                
                # Punem imaginea într-un Label
                img_label = tk.Label(self, image=self.img_tk)
                img_label.pack(pady=10)
                
                info_text = f"Imagine încărcată: {w}x{h} px"
                tk.Label(self, text=info_text, font=("Arial", 12)).pack()
                
                tk.Button(self, text="Înapoi", command=self.ecran_principal).pack(pady=10)

            except Exception as e:
                self.curata_ecranul()
                tk.Label(self, text=f"Eroare la citire: {e}", fg="red").pack(pady=20)
                tk.Button(self, text="Înapoi", command=self.ecran_principal).pack()

    

# AICI AVEM LOGICA PENTRU DESCHIDEREA IMAGINII
def read_bmp_24bit(file_path):
    with open(file_path, 'rb') as f:
        file_header = f.read(14)
        if len(file_header) < 14:
            raise ValueError("File too small to be a BMP")
        signature = file_header[0:2]
        if signature != b'BM':
            raise ValueError("Not a BMP file (invalid signature)")

        file_size = struct.unpack('<I', file_header[2:6])[0]
        data_offset = struct.unpack('<I', file_header[10:14])[0]

        info_header = f.read(40)
        if len(info_header) < 40:
            raise ValueError("Incomplete BMP info header")

        header_size = struct.unpack('<I', info_header[0:4])[0]
        width = struct.unpack('<i', info_header[4:8])[0]
        height = struct.unpack('<i', info_header[8:12])[0]
        bit_count = struct.unpack('<H', info_header[14:16])[0]
        compression = struct.unpack('<I', info_header[16:20])[0]

        if bit_count != 24:
            raise ValueError(f"Only 24‑bit BMP supported, got {bit_count}‑bit")
        if compression != 0:
            raise ValueError("Only uncompressed BMP supported")

        bottom_up = height > 0
        abs_height = abs(height)
        row_size = ((width * 3 + 3) // 4) * 4

        f.seek(data_offset)
        pixels = []
        for _ in range(abs_height):
            row_data = f.read(row_size)
            if len(row_data) < row_size:
                raise ValueError("Unexpected end of file")
            row_pixels = []
            for x in range(width):
                b = row_data[x*3]
                g = row_data[x*3 + 1]
                r = row_data[x*3 + 2]
                row_pixels.append([r, g, b])
            pixels.append(row_pixels)

        if bottom_up:
            pixels.reverse()

        return pixels

if __name__ == "__main__":
    app = Aplicatie()
    app.mainloop()