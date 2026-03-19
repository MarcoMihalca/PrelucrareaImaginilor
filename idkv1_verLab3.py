import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np

# Sa refactorizez prin a adauga o functie pentru procesare imagine si afisare de eroare (a doua e optionala)
# Sa centrez toate pe pagina. !!!(sa intreb daca sa folosesc container sau sa folosesc direct place(relx=0.5, rely=0.5, anchor="center") pentru fiecare element).
# Sa fac ideea aia unde imaginea default e afisata in centru, iar cand aplic un filtru, de ex alb negru, este afisata doar pe partea stanga, iar in dreapta este imaginea editata.
# Pe viitor sa adaug buton de comparatie a conversiilor (alb negru, yuv, ycbcr) cu un pop_up care sa te lase sa selectezi care conversii vrei sa fie comparate, iar width sa fie impartit in parti egale, dupa cate selectii de conversii au fost selectate, ca sa fie afisat egal, corespunzator.

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
        tools_menu.add_command(label="Convertire Imagine in Alb si Negru", command=self.aplicare_albNegru)
        tools_menu.add_command(label="Convertire RGB in YUV", command=self.aplicare_conversie_RGB_in_YUV)
        tools_menu.add_command(label="Convertire RGB in YCbCr", command=self.aplicare_conversie_RGB_in_YCbCr)
        tools_menu.add_command(label="Imagine inversa (RGB)", command=self.aplicare_inversare_RGB)
        tools_menu.add_command(label="Binarizare", command=self.aplicare_binarizare)
        tools_menu.add_command(label="Calculare centru de masa", command=self.calculare_centru_de_masa)
        # De implementat pe viitor
        # tools_menu.add_separator()
        # tools_menu.add_command(label="Comparare conversii imagini", command=self.comparare_conversii)

        
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
        self.adauga_buton_inapoi()

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

    # De gasit un use la asta

    # def submeniu_alb_negru(self):
    #     self.curata_ecranul()
    #     tk.Label(self, text="Alege o imagine pentru conversie in alb si negru", font=("Arial", 14)).pack(pady=20)
    #     tk.Button(self, text="Deschide Imagine", command=self.deschide_imagine_albNegru).pack(pady=10)
    #     self.adauga_buton_inapoi()

    def aplicare_albNegru(self):
        """
        Aplică 3 metode diferite de conversie în alb și negru pe imaginea din memorie.
        Afișează cele 3 rezultate side-by-side.
        """
        try:
            # Verificăm dacă avem deja o imagine în memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                # Dacă nu, deschidem o imagine nouă
                result = self.procesare_imagine()
                if result is None:
                    return
            
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

            self.adauga_buton_inapoi()

        except Exception as e:
            self.afiseaza_eroare(str(e))

    def aplicare_conversie_RGB_in_YUV(self):
        """
        Aplică conversia RGB -> YUV folosind formulele din laborator.
        """
        try:
            # Verificăm dacă avem deja o imagine în memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                # Dacă nu, deschidem o imagine nouă
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Creăm obiectul PhotoImage pentru rezultatul YUV
            self.img_yuv = tk.PhotoImage(width=w, height=h)

            rows_yuv = []

            for y in range(h):
                line_yuv = []
                for x in range(w):
                    r, g, b = cv_img_rgb[y, x].astype(float)

                    # ==========================================
                    # FORMULE YUV
                    # ==========================================
                    y_val = 0.299 * r + 0.587 * g + 0.114 * b
                    
                    # Adăugăm +128 la U și V pentru a le aduce în intervalul vizibil (0-255)
                    # deoarece diferența (r - y_val) poate fi un număr negativ!
                    u_val = 0.74 * (r - y_val) + 0.27 * (b - y_val) + 128
                    v_val = 0.48 * (r - y_val) + 0.41 * (b - y_val) + 128

                    # Corectăm valorile să fie strict între 0 și 255
                    y_int = int(max(0, min(255, y_val)))
                    u_int = int(max(0, min(255, u_val)))
                    v_int = int(max(0, min(255, v_val)))

                    # Asamblăm pixelul în format hexazecimal
                    line_yuv.append(f"#{y_int:02x}{u_int:02x}{v_int:02x}")

                # Punem tot rândul în formatul cerut de Tkinter
                rows_yuv.append(f"{{{ ' '.join(line_yuv) }}}")

            # "Desenăm" imaginea
            self.img_yuv.put(" ".join(rows_yuv))

            # ==========================================
            # AFIȘARE PE ECRAN (Centrat)
            # ==========================================
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(container, image=self.img_yuv).pack()
            tk.Label(container, text="Imagine YUV", font=("Arial", 14, "bold")).pack(pady=10)

            self.adauga_buton_inapoi()

        except Exception as e:
            self.afiseaza_eroare(str(e))

    def aplicare_conversie_RGB_in_YCbCr(self):
        """
        Aplică conversia RGB -> YCbCr (standardul JPEG) folosind formulele din laborator.
        """
        try:
            # Verificăm dacă avem deja o imagine în memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                # Dacă nu, deschidem o imagine nouă
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Creăm obiectul PhotoImage pentru rezultatul YCbCr
            self.img_ycbcr = tk.PhotoImage(width=w, height=h)

            rows_ycbcr = []

            for y in range(h):
                line_ycbcr = []
                for x in range(w):
                    r, g, b = cv_img_rgb[y, x].astype(float)

                    # ==========================================
                    # FORMULE YCbCr (Standard JPEG)
                    # ==========================================
                    y_val = 0.299 * r + 0.587 * g + 0.114 * b
                    
                    # Pentru Cb și Cr, offset-ul de 128 este deja inclus direct în formula standard
                    cb_val = -0.1687 * r - 0.3313 * g + 0.498 * b + 128
                    cr_val = 0.498 * r - 0.4187 * g - 0.0813 * b + 128

                    # Corectăm valorile să fie strict între 0 și 255
                    y_int = int(max(0, min(255, y_val)))
                    cb_int = int(max(0, min(255, cb_val)))
                    cr_int = int(max(0, min(255, cr_val)))

                    # Asamblăm pixelul în format hexazecimal
                    line_ycbcr.append(f"#{y_int:02x}{cb_int:02x}{cr_int:02x}")

                # Punem tot rândul în formatul cerut de Tkinter
                rows_ycbcr.append(f"{{{ ' '.join(line_ycbcr) }}}")

            # "Desenăm" imaginea
            self.img_ycbcr.put(" ".join(rows_ycbcr))

            # ==========================================
            # AFIȘARE PE ECRAN (Centrat)
            # ==========================================
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(container, image=self.img_ycbcr).pack()
            tk.Label(container, text="Imagine YCbCr (Standard JPEG)", font=("Arial", 14, "bold")).pack(pady=10)

            self.adauga_buton_inapoi()

        except Exception as e:
            self.afiseaza_eroare(str(e))    

    def aplicare_inversare_RGB(self):
        """
        Calculează imaginea inversă (negativul) și afișează cele 3 canale RGB separat.
        """
        try:
            # Verificăm dacă avem deja o imagine în memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Creăm 3 obiecte PhotoImage pentru cele 3 canale inverse
            self.img_inv_r = tk.PhotoImage(width=w, height=h)
            self.img_inv_g = tk.PhotoImage(width=w, height=h)
            self.img_inv_b = tk.PhotoImage(width=w, height=h)

            rows_r, rows_g, rows_b = [], [], []

            for y in range(h):
                line_r, line_g, line_b = [], [], []
                for x in range(w):
                    r, g, b = cv_img_rgb[y, x].astype(int)

                    # 1. Calculăm inversul (negativul) pentru fiecare culoare
                    inv_r = 255 - r
                    inv_g = 255 - g
                    inv_b = 255 - b

                    # 2. Construim pixelii pentru fiecare canal în parte
                    # Pentru canalul ROȘU, lăsăm G și B pe zero (00)
                    line_r.append(f"#{inv_r:02x}0000")
                    
                    # Pentru canalul VERDE, lăsăm R și B pe zero (00)
                    line_g.append(f"#00{inv_g:02x}00")
                    
                    # Pentru canalul ALBASTRU, lăsăm R și G pe zero (00)
                    line_b.append(f"#0000{inv_b:02x}")

                # Împachetăm rândurile pentru formatul Tkinter
                rows_r.append(f"{{{ ' '.join(line_r) }}}")
                rows_g.append(f"{{{ ' '.join(line_g) }}}")
                rows_b.append(f"{{{ ' '.join(line_b) }}}")

            # Încărcăm datele în imagini
            self.img_inv_r.put(" ".join(rows_r))
            self.img_inv_g.put(" ".join(rows_g))
            self.img_inv_b.put(" ".join(rows_b))

            # ==========================================
            # AFIȘARE PE ECRAN (Centrat)
            # ==========================================
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(container, text="Canalele Imaginii Inverse (Negative)", font=("Arial", 18, "bold")).pack(pady=10)

            # Folosim un Frame orizontal pentru a pune cele 3 imagini side-by-side
            row_frame = tk.Frame(container)
            row_frame.pack()

            # Afișăm imaginile și titlurile lor folosind o buclă elegantă
            for img, titlu in zip([self.img_inv_r, self.img_inv_g, self.img_inv_b], 
                                  ["Canal Roșu (Invers)", "Canal Verde (Invers)", "Canal Albastru (Invers)"]):
                f = tk.Frame(row_frame)
                f.pack(side="left", padx=10)
                tk.Label(f, image=img).pack()
                tk.Label(f, text=titlu, font=("Arial", 12, "bold")).pack()

            # Adăugăm butonul tău de înapoi
            self.adauga_buton_inapoi()

        except Exception as e:
            self.afiseaza_eroare(str(e))

    def aplicare_binarizare(self):
        """
        Transformă imaginea într-una strict alb-negru (binară) pe baza unui prag.
        """
        try:
            # Verificăm dacă avem imagine în memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Creăm obiectele PhotoImage (Original și Binarizat)
            self.img_original = tk.PhotoImage(width=w, height=h)
            self.img_binar = tk.PhotoImage(width=w, height=h)

            rows_orig, rows_bin = [], []
            
            # STABILIREA PRAGULUI (Threshold)
            # Folosim mijlocul intervalului (255 / 2 = ~127)
            prag = 127 

            for y in range(h):
                line_orig, line_bin = [], []
                for x in range(w):
                    r, g, b = cv_img_rgb[y, x].astype(int)

                    # --- Pentru imaginea originală (doar reconstruim pixelii) ---
                    line_orig.append(f"#{r:02x}{g:02x}{b:02x}")

                    # --- Pentru Binarizare ---
                    # 1. Găsim valoarea de luminozitate (folosim media aritmetică)
                    gray = (r + g + b) // 3

                    # 2. Aplicăm pragul ales de noi
                    if gray >= prag:
                        line_bin.append("#ffffff") # Alb pur
                    else:
                        line_bin.append("#000000") # Negru pur

                # Împachetăm rândurile pentru formatul Tkinter
                rows_orig.append(f"{{{ ' '.join(line_orig) }}}")
                rows_bin.append(f"{{{ ' '.join(line_bin) }}}")

            # Încărcăm datele în imagini
            self.img_original.put(" ".join(rows_orig))
            self.img_binar.put(" ".join(rows_bin))

            # ==========================================
            # AFIȘARE PE ECRAN (Centrat)
            # ==========================================
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(container, text=f"Binarizare (Prag ales: {prag})", font=("Arial", 18, "bold")).pack(pady=10)

            # Folosim un Frame orizontal pentru a pune pozele side-by-side
            row_frame = tk.Frame(container)
            row_frame.pack()

            # Imaginea Originală (Stânga)
            f_orig = tk.Frame(row_frame)
            f_orig.pack(side="left", padx=15)
            tk.Label(f_orig, image=self.img_original).pack()
            tk.Label(f_orig, text="Imagine Originală", font=("Arial", 12)).pack()

            # Imaginea Binarizată (Dreapta)
            f_bin = tk.Frame(row_frame)
            f_bin.pack(side="left", padx=15)
            tk.Label(f_bin, image=self.img_binar).pack()
            tk.Label(f_bin, text="Imagine Binarizată (Alb/Negru pur)", font=("Arial", 12, "bold")).pack()

            self.adauga_buton_inapoi()

        except Exception as e:
            self.afiseaza_eroare(str(e))

    def calculare_centru_de_masa(self):
        """
        Calculează centrul de masă (greutate) al imaginii pe baza luminanței
        și desenează un indicator vizual (o cruce roșie) pe acele coordonate.
        """
        try:
            # Verificăm dacă avem imagine în memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # 1. CALCULUL MATEMATIC AL CENTRULUI DE MASĂ
            suma_x = 0
            suma_y = 0
            suma_mase = 0

            # Parcurgem imaginea pentru a aduna "masele"
            for y in range(h):
                for x in range(w):
                    r, g, b = cv_img_rgb[y, x].astype(int)
                    # "Masa" pixelului este intensitatea lui (putem folosi suma RGB sau media)
                    masa = r + g + b 
                    
                    suma_x += x * masa
                    suma_y += y * masa
                    suma_mase += masa

            # Evităm împărțirea la zero în cazul (improbabil) al unei imagini complet negre
            if suma_mase == 0:
                cx, cy = w // 2, h // 2
            else:
                cx = int(suma_x / suma_mase)
                cy = int(suma_y / suma_mase)

            # 2. GENERAREA IMAGINII CU INDICATORUL VIZUAL
            self.img_centru = tk.PhotoImage(width=w, height=h)
            rows = []

            for y in range(h):
                line = []
                for x in range(w):
                    # Desenăm o "țintă" (cruce) roșie peste centrul de masă
                    # Dacă pixelul curent este pe linia lui cx sau cy (cu o grosime/lungime limitată)
                    if (abs(x - cx) <= 1 and abs(y - cy) <= 20) or (abs(y - cy) <= 1 and abs(x - cx) <= 20):
                        line.append("#ff0000") # Roșu pur
                    else:
                        r, g, b = cv_img_rgb[y, x].astype(int)
                        line.append(f"#{r:02x}{g:02x}{b:02x}")

                rows.append(f"{{{ ' '.join(line) }}}")

            self.img_centru.put(" ".join(rows))

            # ==========================================
            # AFIȘARE PE ECRAN
            # ==========================================
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(container, text="Centrul de Masă al Imaginii", font=("Arial", 18, "bold")).pack(pady=10)
            
            # Afișăm coordonatele calculate ca dovadă pentru profesor
            tk.Label(container, text=f"Coordonate calculate: X = {cx}, Y = {cy}", font=("Arial", 14), fg="blue").pack(pady=5)

            tk.Label(container, image=self.img_centru).pack(pady=10)

            self.adauga_buton_inapoi()

        except Exception as e:
            self.afiseaza_eroare(str(e))
        

if __name__ == "__main__":
    app = Aplicatie()
    app.mainloop()