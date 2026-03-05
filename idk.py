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
            title="Open BMP Image",
            filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")]
        )

        if file_path:
            try:
                # 1. Citim cu OpenCV
                cv_img = cv2.imread(file_path)
                if cv_img is None:
                    raise ValueError("Nu pot citi imaginea")

                # 2. Redimensionăm dacă este prea mare (pentru a nu bloca interfața)
                max_w, max_h = 500, 400
                h, w = cv_img.shape[:2]
                if w > max_w or h > max_h:
                    scale = min(max_w / w, max_h / h)
                    cv_img = cv2.resize(cv_img, (int(w * scale), int(h * scale)))
                    h, w = cv_img.shape[:2]

                # 3. OpenCV folosește BGR, Tkinter vrea RGB
                cv_img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)

                # 4. CONVERSIE NATIVĂ (Fără PIL)
                # Creăm un obiect PhotoImage gol
                self.img_tk = tk.PhotoImage(width=w, height=h)

                # Transformăm matricea într-un format de text hexazecimal pe care Tkinter îl înțelege
                # Format: { #RRGGBB #RRGGBB ... } { #RRGGBB ... }
                rows = []
                for y in range(h):
                    row_data = " ".join(f"#{r:02x}{g:02x}{b:02x}" for r, g, b in cv_img_rgb[y])
                    rows.append(f"{{{row_data}}}")
                
                self.img_tk.put(" ".join(rows))

                # 5. Afișăm în interfață
                self.curata_ecranul()
                img_label = tk.Label(self, image=self.img_tk)
                img_label.pack(pady=10)
                
                info_text = f"Dimensiuni: {w}x{h} px"
                tk.Label(self, text=info_text, font=("Arial", 12)).pack()
                
                tk.Button(self, text="Înapoi", command=self.ecran_principal).pack(pady=10)
                
            except Exception as e:
                self.curata_ecranul()
                tk.Label(self, text=f"Eroare: {e}", fg="red").pack(pady=20)
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
    
def cv2_to_tk_image(cv_image, max_width=400, max_height=250):
    """Converteaza imagine OpenCV in PhotoImage pentru tkinter"""
    # Redimensionează dacă e prea mare
    height, width = cv_image.shape[:2]
    if width > max_width or height > max_height:
        scale = min(max_width / width, max_height / height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        cv_image = cv2.resize(cv_image, (new_width, new_height))
    
    # Convertește din BGR (OpenCV) în RGB pentru tkinter
    cv_image_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    
    # Convertește în PIL Image
    pil_image = Image.fromarray(cv_image_rgb)
    
    return ImageTk.PhotoImage(pil_image)

if __name__ == "__main__":
    app = Aplicatie()
    app.mainloop()