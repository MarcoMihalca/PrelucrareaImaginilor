import tkinter as tk
from tkinter import filedialog
import struct
import os
import cv2
import numpy as np

# Sa refactorizez prin a adauga o functie pentru procesare imagine si afisare de eroare (a doua e optionala)

class Aplicatie(tk.Tk):
    def __init__(self):
        super().__init__()

        # Setări fereastră
        self.title("Aplicație Desktop")
        self.geometry("1920x1080")

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

        self.button_deschidere_imagine = tk.Button(self, text="Deschide Imagine (Simplu)", font=("Arial", 14), command=self.deschide_imagine)
        self.button_deschidere_imagine.pack(pady=10)

        self.button_deschidere_imagine_alb_negru = tk.Button(self, text="Convertire Imagine in Alb si Negru", font=("Arial", 14), command=self.deschide_imagine_albNegru)
        self.button_deschidere_imagine_alb_negru.pack(pady=10)

    

    def afiseaza_mesaj_bienvenue(self):
        self.curata_ecranul()

        # Mesaj nou
        self.label = tk.Label(self, text="Bine ai venit în aplicație! ;)", font=("Arial", 18))
        self.label.pack(pady=40)

        self.after(3000, self.ecran_principal)  # După 3 secunde, trece la ecranul principal

    def adauga_buton_inapoi(self):
        """Adaugă un buton standard de revenire la meniul principal"""
        buton = tk.Button(
            self, 
            text="⬅ Înapoi la Meniu", 
            font=("Arial", 10),
            bg="#f0f0f0",  # Opțional: o culoare discretă
            command=self.ecran_principal
        )
        buton.pack(pady=20)

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
                
                self.adauga_buton_inapoi()
                
            except Exception as e:
                self.curata_ecranul()
                tk.Label(self, text=f"Eroare: {e}", fg="red").pack(pady=20)
                tk.Button(self, text="Înapoi", command=self.ecran_principal).pack()

    def submeniu_alb_negru(self):
        self.curata_ecranul()
        tk.Label(self, text="Alege o imagine pentru conversie in alb si negru", font=("Arial", 14)).pack(pady=20)
        tk.Button(self, text="Deschide Imagine", command=self.deschide_imagine_albNegru).pack(pady=10)
        self.adauga_buton_inapoi()

    def deschide_imagine_albNegru(self):
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

                # 4. LOGICA DE CONVERSIE (Cele 3 variante de Gray)
                h, w = cv_img_rgb.shape[:2]
                
                # Creăm 3 obiecte PhotoImage pentru cele 3 rezultate
                self.img1 = tk.PhotoImage(width=w, height=h)
                self.img2 = tk.PhotoImage(width=w, height=h)
                self.img3 = tk.PhotoImage(width=w, height=h)

                rows1, rows2, rows3 = [], [], []

                for y in range(h):
                    line1, line2, line3 = [], [], []
                    for x in range(w):
                        r, g, b = cv_img_rgb[y, x].astype(float)

                        # Sau puteam sa pun r, g, b = int(r), int(g), int(b) in loc de .astype(float) deasupra.

                        # Gray 1
                        g1 = int((r + g + b) / 3)
                        
                        # Gray 2
                        g2 = int(0.299 * r + 0.587 * g + 0.114 * b)
                        
                        # Gray 3
                        g3 = int(min(r, g, b) / 2 + max(r, g, b) / 2)

                        # Adăugăm în listele de culori hex
                        line1.append(f"#{g1:02x}{g1:02x}{g1:02x}")
                        line2.append(f"#{g2:02x}{g2:02x}{g2:02x}")
                        line3.append(f"#{g3:02x}{g3:02x}{g3:02x}")

                    rows1.append(f"{{{ ' '.join(line1) }}}")
                    rows2.append(f"{{{ ' '.join(line2) }}}")
                    rows3.append(f"{{{ ' '.join(line3) }}}")

                # "Desenăm" imaginile
                self.img1.put(" ".join(rows1))
                self.img2.put(" ".join(rows2))
                self.img3.put(" ".join(rows3))

                # 5. AFIȘARE REZULTATE
                self.curata_ecranul()
                container = tk.Frame(self)
                container.pack(pady=10)

                # Afișăm cele 3 variante una lângă alta
                for img, titlu in zip([self.img1, self.img2, self.img3], 
                                      ["Media (R+G+B)/3", "Luma (0.299R...)", "Min-Max / 2"]):
                    f = tk.Frame(container)
                    f.pack(side="left", padx=5)
                    tk.Label(f, image=img).pack()
                    tk.Label(f, text=titlu, font=("Arial", 10, "bold")).pack()

                tk.Button(self, text="Înapoi", command=self.ecran_principal).pack(pady=10)

            except Exception as e:
                self.curata_ecranul()
                tk.Label(self, text=f"Eroare: {e}", fg="red").pack(pady=20)
                tk.Button(self, text="Înapoi", command=self.ecran_principal).pack()

if __name__ == "__main__":
    app = Aplicatie()
    app.mainloop()