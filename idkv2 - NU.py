import tkinter as tk
from tkinter import filedialog
import struct
import os
import cv2
import numpy as np

# Aici am refactorizat si imbunatatit codul DAR NU E OK, FOLOSESTE CONTAINER SI NU LE INTELEG!!

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

    def procesare_imagine(self, file_path):
        """Funcție utilitară care citește și redimensionează imaginea indiferent de format"""
        # OpenCV citește automat 8, 24 sau 32 biți
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError("Nu am putut citi fișierul.")

        max_w, max_h = 400, 400
        h, w = img.shape[:2]
        if w > max_w or h > max_h:
            scale = min(max_w / w, max_h / h)
            img = cv2.resize(img, (int(w * scale), int(h * scale)))
        
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def afiseaza_eroare(self, e):
        self.curata_ecranul()
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(container, text=f"Eroare: {e}", fg="red", font=("Arial", 14)).pack()
        self.adauga_buton_inapoi(container)

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
        file_path = filedialog.askopenfilename(filetypes=[("Imagini", "*.bmp *.jpg *.png")])
        if not file_path: return

        try:
            img_rgb = self.procesare_imagine(file_path)
            h, w = img_rgb.shape[:2]
            
            self.img_tk = tk.PhotoImage(width=w, height=h)
            rows = ["{" + " ".join(f"#{r:02x}{g:02x}{b:02x}" for r, g, b in row) + "}" for row in img_rgb]
            self.img_tk.put(" ".join(rows))

            self.curata_ecranul()
            res_container = tk.Frame(self)
            res_container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(res_container, image=self.img_tk).pack()
            tk.Label(res_container, text=f"Imagine Originală: {w}x{h} px", font=("Arial", 12)).pack()
            self.adauga_buton_inapoi(res_container)

        except Exception as e:
            self.afiseaza_eroare(e)

    def submeniu_alb_negru(self):
        self.curata_ecranul()
        tk.Label(self, text="Alege o imagine pentru conversie in alb si negru", font=("Arial", 14)).pack(pady=20)
        tk.Button(self, text="Deschide Imagine", command=self.deschide_imagine_albNegru).pack(pady=10)
        self.adauga_buton_inapoi()

    def deschide_imagine_albNegru(self):
        file_path = filedialog.askopenfilename(filetypes=[("Imagini", "*.bmp *.jpg *.png")])
        if not file_path: return

        try:
            img_rgb = self.procesare_imagine(file_path)
            h, w = img_rgb.shape[:2]

            self.img1, self.img2, self.img3 = tk.PhotoImage(width=w, height=h), tk.PhotoImage(width=w, height=h), tk.PhotoImage(width=w, height=h)
            r1, r2, r3 = [], [], []

            for row in img_rgb:
                l1, l2, l3 = [], [], []
                for r, g, b in row.astype(int):
                    # Formulele tale
                    v1 = (r + g + b) // 3
                    v2 = int(0.299*r + 0.587*g + 0.114*b)
                    v3 = (min(r, g, b) + max(r, g, b)) // 2

                    l1.append(f"#{v1:02x}{v1:02x}{v1:02x}")
                    l2.append(f"#{v2:02x}{v2:02x}{v2:02x}")
                    l3.append(f"#{v3:02x}{v3:02x}{v3:02x}")
                
                r1.append("{" + " ".join(l1) + "}")
                r2.append("{" + " ".join(l2) + "}")
                r3.append("{" + " ".join(l3) + "}")

            self.img1.put(" ".join(r1)); self.img2.put(" ".join(r2)); self.img3.put(" ".join(r3))

            self.curata_ecranul()
            res_container = tk.Frame(self)
            res_container.place(relx=0.5, rely=0.5, anchor="center")

            # Afișare în linie
            img_row = tk.Frame(res_container)
            img_row.pack()

            for img, txt in zip([self.img1, self.img2, self.img3], ["Media (R+G+B)/3", "Luma (0.299R...)", "Min-Max / 2"]):
                f = tk.Frame(img_row); f.pack(side="left", padx=10)
                tk.Label(f, image=img).pack()
                tk.Label(f, text=txt, font=("Arial", 10, "bold")).pack()

            self.adauga_buton_inapoi(res_container)

        except Exception as e:
            self.afiseaza_eroare(e)

if __name__ == "__main__":
    app = Aplicatie()
    app.mainloop()