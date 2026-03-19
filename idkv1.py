import tkinter as tk
from tkinter import filedialog
import struct
import os
import cv2
import numpy as np

# Sa refactorizez prin a adauga o functie pentru procesare imagine si afisare de eroare (a doua e optionala)
# Sa centrez toate pe pagina.
# Sa fac ideea aia unde imaginea default e afisata in centru, iar cand aplic un filtru, de ex alb negru, este afisata doar pe partea stanga, iar in dreapta este imaginea editata.

class Aplicatie(tk.Tk):
    def __init__(self):
        super().__init__()

        # Setări fereastră
        self.title("Aplicație Desktop")
        self.geometry("1920x1080")

        self.afiseaza_mesaj_bienvenue()

    def curata_ecranul(self):
        # Șterge toate widget-urile de pe fereastră, EXCEPȚIE făcând Meniul
        for widget in self.winfo_children():
            # Verificăm dacă widget-ul NU este un meniu înainte să îl distrugem
            if not isinstance(widget, tk.Menu):
                widget.destroy()

    def ecran_principal(self):
        self.curata_ecranul()
        
        # Titlu ecran (Acum fără butoane, deoarece le avem în meniul de sus)
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(container, text="Folosește meniul 'File' din stânga-sus pentru a începe.", font=("Arial", 20, "bold"), fg="gray").pack(pady=30)
        self.creeaza_meniu_sus()

    def creeaza_meniu_sus(self):
        """Creează bara de meniu cu ambele opțiuni (File și Tools)"""
        
        # 1. Creăm O SINGURĂ bară principală pentru toată fereastra
        bara_principala = tk.Menu(self)

        # ==========================================
        # 2. Construim meniul "File"
        # ==========================================
        file_menu = tk.Menu(bara_principala, tearoff=0)
        file_menu.add_command(label="Deschide Imagine (Simplu)", command=self.deschide_imagine)
        file_menu.add_separator()
        file_menu.add_command(label="Ieșire", command=self.quit)
        
        # Îl atașăm la bara principală
        bara_principala.add_cascade(label="File", menu=file_menu)

        # ==========================================
        # 3. Construim meniul "Tools"
        # ==========================================
        tools_menu = tk.Menu(bara_principala, tearoff=0)
        tools_menu.add_command(label="Convertire Imagine in Alb si Negru", command=self.deschide_imagine_albNegru)
        
        # Îl atașăm la ACEEAȘI bară principală, lângă File
        bara_principala.add_cascade(label="Tools", menu=tools_menu)

        # ==========================================
        # 4. Setăm bara pe fereastră O SINGURĂ DATĂ
        # ==========================================
        self.config(menu=bara_principala)


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

    def afiseaza_eroare(self, mesaj_eroare):
        """Afișează o pagină cu mesajul de eroare și butonul de revenire"""
        self.curata_ecranul()
        tk.Label(self, text=f"Eroare: {mesaj_eroare}", fg="red", font=("Arial", 12)).pack(pady=20)
        tk.Button(self, text="Înapoi", command=self.ecran_principal).pack()

    def procesare_imagine(self):
        """
        Deschide o imagine și o încarcă în memorie.
        Returnează dimensiunile (h, w) dacă reuși, altfel raises Exception.
        """
        file_path = filedialog.askopenfilename(
            title="Open BMP Image",
            filetypes=[("BMP files", "*.bmp"), ("All files", "*.*")]
        )

        if not file_path:
            return None

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

        # Salvăm imaginea în memorie
        self.cv_img_rgb = cv_img_rgb
        
        return h, w

    def deschide_imagine(self):
        """
        Deschide o imagine și o afișează în mod normal.
        """
        try:
            result = self.procesare_imagine()
            if result is None:
                return
            
            h, w = result
            
            # CONVERSIE NATIVĂ (Fără PIL)
            # Creăm un obiect PhotoImage gol
            self.img_tk = tk.PhotoImage(width=w, height=h)

            # Transformăm matricea într-un format de text hexazecimal pe care Tkinter îl înțelege
            rows = []
            for y in range(h):
                row_data = " ".join(f"#{r:02x}{g:02x}{b:02x}" for r, g, b in self.cv_img_rgb[y])
                rows.append(f"{{{row_data}}}")
            
            self.img_tk.put(" ".join(rows))

            # Afișăm în interfață
            self.curata_ecranul()
            img_label = tk.Label(self, image=self.img_tk)
            img_label.pack(pady=10)
            
            info_text = f"Dimensiuni: {w}x{h} px"
            tk.Label(self, text=info_text, font=("Arial", 12)).pack()
            
            self.adauga_buton_inapoi()
            
        except Exception as e:
            self.afiseaza_eroare(str(e))

    def submeniu_alb_negru(self):
        self.curata_ecranul()
        tk.Label(self, text="Alege o imagine pentru conversie in alb si negru", font=("Arial", 14)).pack(pady=20)
        tk.Button(self, text="Deschide Imagine", command=self.deschide_imagine_albNegru).pack(pady=10)
        self.adauga_buton_inapoi()

    def aplicare_albNegru(self):
        """
        Aplică 3 metode diferite de conversie în alb și negru pe imaginea din memorie.
        Afișează cele 3 rezultate side-by-side.
        """
        try:
            # Verificăm dacă avem o imagine în memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                raise ValueError("Nu există nicio imagine în memorie")
            
            cv_img_rgb = self.cv_img_rgb
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

            # AFIȘARE REZULTATE
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
            self.afiseaza_eroare(str(e))

    def deschide_imagine_albNegru(self):
        """
        Deschide o imagine și aplică efectul alb și negru.
        Dacă există deja o imagine în memorie, o folosește direct.
        """
        try:
            # Verificăm dacă avem deja o imagine în memorie
            if hasattr(self, 'cv_img_rgb') and self.cv_img_rgb is not None:
                # Dacă da, aplicăm direct efectul alb și negru
                self.aplicare_albNegru()
            else:
                # Dacă nu, deschidem o imagine nouă
                result = self.procesare_imagine()
                if result is None:
                    return
                
                # După încărcarea imaginii, o procesăm
                self.aplicare_albNegru()
            
        except Exception as e:
            self.afiseaza_eroare(str(e))

if __name__ == "__main__":
    app = Aplicatie()
    app.mainloop()