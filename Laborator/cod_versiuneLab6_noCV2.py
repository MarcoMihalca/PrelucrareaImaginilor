import tkinter as tk
from tkinter import filedialog
import numpy as np
import math
import struct

# Sa refactorizez prin a adauga o functie pentru procesare imagine si afisare de eroare (a doua e optionala)
# Sa centrez toate pe pagina. !!!(sa intreb daca sa folosesc container sau sa folosesc direct place(relx=0.5, rely=0.5, anchor="center") pentru fiecare element).
# Sa fac ideea aia unde imaginea default e afisata in centru, iar cand aplic un filtru, de ex alb negru, este afisata doar pe partea stanga, iar in dreapta este imaginea editata.
# Pe viitor sa adaug buton de comparatie a conversiilor (alb negru, yuv, ycbcr) cu un pop_up care sa te lase sa selectezi care conversii vrei sa fie comparate, iar width sa fie impartit in parti egale, dupa cate selectii de conversii au fost selectate, ca sa fie afisat egal, corespunzator.

class Aplicatie(tk.Tk):
    def __init__(self):
        super().__init__()

        # Setari fereastra
        self.title("Aplicatie Desktop")
        self.geometry("1920x1080")

        # Variabile pentru sistem prag adaptiv
        self.prag_utilizator = None  # Pragul ales de utilizator (None = default)
        self.functie_curenta = None  # Functia care se executa (pentru a o relansa dupa schimbarea pragului)

        self.afiseaza_mesaj_bienvenue()

    def curata_ecranul(self):
        # Sterge toate widget-urile de pe fereastra, EXCEPTIE facand Meniul
        for widget in self.winfo_children():
            # Verificam daca widget-ul NU este un meniu inainte sa il distrugem
            if not isinstance(widget, tk.Menu):
                widget.destroy()

    def ecran_principal(self):
        self.curata_ecranul()
        
        # Titlu ecran (Acum fara butoane, deoarece le avem in meniul de sus)
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(container, text="Foloseste meniul 'File' din stanga-sus pentru a incepe.", font=("Arial", 20, "bold"), fg="gray").pack(pady=30)
        self.creeaza_meniu_sus()

    def creeaza_meniu_sus(self):
        """Creeaza bara de meniu cu ambele optiuni (File si Tools)"""
        
        # 1. Cream O SINGURA bara principala pentru toata fereastra
        bara_principala = tk.Menu(self)

        # ==========================================
        # 2. Construim meniul "File"
        # ==========================================
        file_menu = tk.Menu(bara_principala, tearoff=0)
        file_menu.add_command(label="Deschide Imagine (Simplu)", command=self.deschide_imagine)
        file_menu.add_separator()
        file_menu.add_command(label="Iesire", command=self.quit)
        
        # Il atasam la bara principala
        bara_principala.add_cascade(label="File", menu=file_menu)

        # ==========================================
        # 3. Construim meniul "Tools"
        # ==========================================
        tools_menu = tk.Menu(bara_principala, tearoff=0)
        tools_menu.add_command(label="Convertire Imagine in Alb si Negru", command=self.aplicare_grayscale_3exemplare)
        tools_menu.add_command(label="Convertire RGB in YUV", command=self.aplicare_conversie_RGB_in_YUV)
        tools_menu.add_command(label="Convertire RGB in YCbCr", command=self.aplicare_conversie_RGB_in_YCbCr)
        tools_menu.add_command(label="Imagine inversa (RGB)", command=self.aplicare_inversare_RGB)
        tools_menu.add_command(label="Binarizare", command=self.aplicare_binarizare)
        tools_menu.add_command(label="Calculare centru de masa", command=self.calculare_centru_de_masa)
        tools_menu.add_separator()
        # De implementat pe viitor
        # tools_menu.add_separator()
        # tools_menu.add_command(label="Comparare conversii imagini", command=self.comparare_conversii)
        tools_menu.add_command(label="Convertire RGB in HSV", command=self.aplicare_conversie_RGB_in_HSV)
        tools_menu.add_command(label="Histograma imagine gri", command=self.afisare_histograma)
        tools_menu.add_command(label="Egalizare Histograma (Contrast)", command=self.aplicare_egalizare_histograma)
        tools_menu.add_separator()
        tools_menu.add_command(label="Dilatare", command=self.aplicare_dilatare)
        tools_menu.add_command(label="Eroziune", command=self.aplicare_eroziune)
        tools_menu.add_command(label="Dilatare Repetitiva (Alegere Iteratii)", command=self.aplicare_dilatare_repetitiva)
        tools_menu.add_command(label="Eroziune Repetitiva (Alegere Iteratii)", command=self.aplicare_eroziune_repetitiva)
        tools_menu.add_command(label="Deschidere (Eroziune + Dilatare)", command=self.aplicare_deschidere)
        tools_menu.add_command(label="Inchidere (Dilatare + Eroziune)", command=self.aplicare_inchidere)
        tools_menu.add_separator()
        tools_menu.add_command(label="Moment de ordin 1", command=self.calculare_moment_ordin_1)
        tools_menu.add_command(label="Moment de ordin 2", command=self.calculare_moment_ordin_2)
        tools_menu.add_command(label="Matrice de covarianta", command=self.calculare_matrice_covarianta)
        tools_menu.add_command(label="Proiectii orizontala/verticala", command=self.calculare_proiectii)
        tools_menu.add_separator()
        tools_menu.add_command(label="Afisare etichetare obiecte", command=self.aplicare_etichetare)
        tools_menu.add_command(label="Afisare etichetare obiecte cu selectie", command=self.aplicare_etichetare_cu_selectie)

        
        # Il atasam la ACEEASI bara principala, langa File
        bara_principala.add_cascade(label="Tools", menu=tools_menu)

        # ==========================================
        # 4. Setam bara pe fereastra O SINGURA DATA
        # ==========================================
        self.config(menu=bara_principala)


    def afiseaza_mesaj_bienvenue(self):
        self.curata_ecranul()

        # Cream un container pentru a-l centra perfect pe tot ecranul
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Mesaj mai mare si mai vizibil
        self.label = tk.Label(container, text="Bine ai venit in aplicatie! ;)", font=("Arial", 24, "bold"), fg="#333333")
        self.label.pack()

        # Dupa 3 secunde (3000 ms), trece la ecranul principal
        self.after(3000, self.ecran_principal)

    def adauga_buton_inapoi(self):
        """Adauga un buton standard de revenire in colțul dreapta-jos"""
        buton_frame = tk.Frame(self, bg=self.cget("bg"))
        buton_frame.place(relx=0.95, rely=0.95, anchor="se")
        
        buton = tk.Button(
            buton_frame, 
            text="Înapoi",
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            padx=10,
            pady=5,
            command=self.ecran_principal
        )
        buton.pack(padx=5, pady=5)

    def afiseaza_eroare(self, mesaj_eroare):
        """Afiseaza o pagina cu mesajul de eroare si butonul de revenire"""
        self.curata_ecranul()
        tk.Label(self, text=f"Eroare: {mesaj_eroare}", fg="red", font=("Arial", 12)).pack(pady=20)
        self.adauga_buton_inapoi()

    def read_bmp_24bit(self, file_path):
        """ 
        Reads a 24-bit uncompressed BMP file and returns a 3D list of RGB values. 
        """ 
        with open(file_path, 'rb') as f: 
            # Read BITMAPFILEHEADER (14 bytes) 
            file_header = f.read(14) 
            if len(file_header) < 14: 
                raise ValueError("File too small to be a BMP") 
            signature = file_header[0:2] 
            if signature != b'BM': 
                raise ValueError("Not a BMP file (invalid signature)") 
    
            # Extract file size and pixel data offset 
            file_size = struct.unpack('<I', file_header[2:6])[0] 
            data_offset = struct.unpack('<I', file_header[10:14])[0] 
    
            # Read BITMAPINFOHEADER (40 bytes) 
            info_header = f.read(40) 
            if len(info_header) < 40: 
                raise ValueError("Incomplete BMP info header") 
    
            header_size = struct.unpack('<I', info_header[0:4])[0] 
            width = struct.unpack('<i', info_header[4:8])[0] 
            height = struct.unpack('<i', info_header[8:12])[0] 
            planes = struct.unpack('<H', info_header[12:14])[0] 
            bit_count = struct.unpack('<H', info_header[14:16])[0] 
            compression = struct.unpack('<I', info_header[16:20])[0] 
            image_size = struct.unpack('<I', info_header[20:24])[0] 
    
            # Validate format: must be 24-bit uncompressed 
            if bit_count != 24: 
                raise ValueError(f"Only 24-bit BMP supported, got {bit_count}-bit") 
            if compression != 0:  # BI_RGB 
                raise ValueError("Only uncompressed BMP supported") 
    
            # Height can be positive (bottom-up) or negative (top-down) 
            bottom_up = height > 0 
            abs_height = abs(height) 
    
            # Each row is padded to a multiple of 4 bytes 
            row_size = ((width * 3 + 3) // 4) * 4 
    
            # Seek to the pixel data 
            f.seek(data_offset) 
    
            # Read pixel data row by row 
            pixels = [] 
            for _ in range(abs_height): 
                row_data = f.read(row_size) 
                if len(row_data) < row_size: 
                    raise ValueError("Unexpected end of file") 
                # Convert BGR (BMP order) to RGB, one pixel at a time 
                row_pixels = [] 
                for x in range(width): 
                    b = row_data[x*3] 
                    g = row_data[x*3 + 1] 
                    r = row_data[x*3 + 2] 
                    row_pixels.append([r, g, b]) 
                pixels.append(row_pixels) 
    
            # BMP rows are stored bottom-up (if height > 0). Reverse to get top-to-bottom order. 
            if bottom_up: 
                pixels.reverse() 
    
            return pixels  # matrix[y][x] = [R,G,B]
        
    def read_bmp_8bit(self, file_path):
        """ 
        Citeste un fisier BMP pe 8 biti (folosind paleta de culori) si returneaza o matrice RGB.
        """
        with open(file_path, 'rb') as f:
            file_header = f.read(14)
            data_offset = struct.unpack('<I', file_header[10:14])[0]
            
            info_header = f.read(40)
            header_size = struct.unpack('<I', info_header[0:4])[0]
            width = struct.unpack('<i', info_header[4:8])[0]
            height = struct.unpack('<i', info_header[8:12])[0]
            colors_used = struct.unpack('<I', info_header[32:36])[0]
            
            abs_height = abs(height)
            bottom_up = height > 0
            
            # 1. Citim Paleta de Culori
            num_colors = colors_used if colors_used > 0 else 256
            f.seek(14 + header_size)
            palette = []
            for _ in range(num_colors):
                b, g, r, _ = struct.unpack('BBBB', f.read(4))
                palette.append([r, g, b])
                
            # 2. Citim pixelii (indexurile) si ii mapam la culorile din paleta
            f.seek(data_offset)
            row_size = ((width + 3) // 4) * 4
            pixels = []
            for _ in range(abs_height):
                row_data = f.read(row_size)
                row_pixels = []
                for x in range(width):
                    color_index = row_data[x]
                    row_pixels.append(palette[color_index])
                pixels.append(row_pixels)
                
            if bottom_up:
                pixels.reverse()
                
            return pixels

    def procesare_imagine(self):
        """
        Deschide o imagine, verifica daca e 8 sau 24 de biti, apeleaza functia corecta
        si o incarca in memorie pentru a fi procesata de restul aplicatiei.
        """
        file_path = filedialog.askopenfilename(
            title="Open BMP Image",
            filetypes=[("BMP files", "*.bmp")]
        )

        if not file_path:
            return None

        # 1. Citim rapid doar antetul pentru a afla formatul (cati biti per pixel are)
        with open(file_path, 'rb') as f:
            file_header = f.read(14)
            if file_header[0:2] != b'BM':
                raise ValueError("Fisierul selectat nu este un BMP valid.")
            
            # Ne intereseaza `bit_count` care se afla la byte-ul 14 din info_header 
            # (adica offset-ul 28 fata de inceputul fisierului)
            info_header_start = f.read(16)
            bit_count = struct.unpack('<H', info_header_start[14:16])[0]

        # 2. Apelam functia corespunzatoare
        if bit_count == 8:
            matrix = self.read_bmp_8bit(file_path)
        elif bit_count == 24:
            matrix = self.read_bmp_24bit(file_path)
        else:
            raise ValueError(f"Aplicatia suporta doar imagini pe 8 sau 24 de biti. Imaginea curenta are {bit_count} biti.")

        # 3. Transformam rezultatul in numpy array pentru compatibilitate cu restul functiilor
        self.cv_img_rgb = np.array(matrix, dtype=np.uint8)

        # 4. Redimensionare manuala (daca imaginea e prea mare, sa nu blocheze UI-ul Tkinter)
        max_w, max_h = 500, 400
        h, w = self.cv_img_rgb.shape[:2]
        
        if w > max_w or h > max_h:
            scale = min(max_w / w, max_h / h)
            new_h, new_w = int(h * scale), int(w * scale)
            
            y_indices = np.clip(np.int_(np.arange(new_h) / scale), 0, h - 1)
            x_indices = np.clip(np.int_(np.arange(new_w) / scale), 0, w - 1)
            
            self.cv_img_rgb = self.cv_img_rgb[y_indices[:, None], x_indices]
            h, w = self.cv_img_rgb.shape[:2]
        
        return h, w

    def deschide_imagine(self):
        """
        Deschide o imagine si o afiseaza centrat in mod normal.
        """
        try:
            result = self.procesare_imagine()
            if result is None:
                return
            
            h, w = result
            
            # Cream un obiect PhotoImage gol
            self.img_tk = tk.PhotoImage(width=w, height=h)

            # Transformam matricea intr-un format de text hexazecimal pe care Tkinter il intelege
            rows = []
            for y in range(h):
                row_data = " ".join(f"#{r:02x}{g:02x}{b:02x}" for r, g, b in self.cv_img_rgb[y])
                rows.append(f"{{{row_data}}}")
            
            self.img_tk.put(" ".join(rows))

            # ==========================================
            # AFISARE PE ECRAN (Centrat)
            # ==========================================
            self.curata_ecranul()
            
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")
            
            # Adaugam un titlu optional deasupra imaginii
            tk.Label(container, text="Imagine Originala", font=("Arial", 18, "bold")).pack(pady=10)

            # Afisam imaginea
            img_label = tk.Label(container, image=self.img_tk)
            img_label.pack()
            
            # Afisam dimensiunile dedesubt
            info_text = f"Dimensiuni: {w}x{h} px"
            tk.Label(container, text=info_text, font=("Arial", 12), fg="gray").pack(pady=5)
            
            self.adauga_buton_inapoi()
            
        except Exception as e:
            self.afiseaza_eroare(str(e))

    # De gasit un use la asta

    # def submeniu_alb_negru(self):
    #     self.curata_ecranul()
    #     tk.Label(self, text="Alege o imagine pentru conversie in alb si negru", font=("Arial", 14)).pack(pady=20)
    #     tk.Button(self, text="Deschide Imagine", command=self.deschide_imagine_albNegru).pack(pady=10)
    #     self.adauga_buton_inapoi()

    def aplicare_grayscale_3exemplare(self):
        """
        Aplica 3 metode diferite de conversie in alb si negru pe imaginea din memorie.
        Afiseaza cele 3 rezultate side-by-side, centrate pe ecran.
        """
        try:
            # Verificam daca avem deja o imagine in memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                # Daca nu, deschidem o imagine noua
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Cream 3 obiecte PhotoImage pentru cele 3 rezultate
            self.img1 = tk.PhotoImage(width=w, height=h)
            self.img2 = tk.PhotoImage(width=w, height=h)
            self.img3 = tk.PhotoImage(width=w, height=h)

            rows1, rows2, rows3 = [], [], []

            for y in range(h):
                line1, line2, line3 = [], [], []
                for x in range(w):
                    r, g, b = cv_img_rgb[y, x].astype(float)

                    # Gray 1 (Media)
                    g1 = int((r + g + b) / 3)
                    
                    # Gray 2 (Luma)
                    g2 = int(0.299 * r + 0.587 * g + 0.114 * b)
                    
                    # Gray 3 (Min-Max)
                    g3 = int(min(r, g, b) / 2 + max(r, g, b) / 2)

                    # Adaugam in listele de culori hex
                    line1.append(f"#{g1:02x}{g1:02x}{g1:02x}")
                    line2.append(f"#{g2:02x}{g2:02x}{g2:02x}")
                    line3.append(f"#{g3:02x}{g3:02x}{g3:02x}")

                rows1.append(f"{{{ ' '.join(line1) }}}")
                rows2.append(f"{{{ ' '.join(line2) }}}")
                rows3.append(f"{{{ ' '.join(line3) }}}")

            # "Desenam" imaginile
            self.img1.put(" ".join(rows1))
            self.img2.put(" ".join(rows2))
            self.img3.put(" ".join(rows3))

            # ==========================================
            # AFISARE REZULTATE (Centrat)
            # ==========================================
            self.curata_ecranul()
            
            # Containerul principal centrat pe pagina
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            # Adaugam un titlu pentru aceasta pagina
            tk.Label(container, text="Conversie in Alb-Negru (3 Metode)", font=("Arial", 18, "bold")).pack(pady=10)

            # Cream un sub-container orizontal pentru a pune pozele una langa alta
            row_frame = tk.Frame(container)
            row_frame.pack()

            # Afisam cele 3 variante
            for img, titlu in zip([self.img1, self.img2, self.img3], 
                                  ["Media (R+G+B)/3", "Luma (0.299R...)", "Min-Max / 2"]):
                f = tk.Frame(row_frame)
                f.pack(side="left", padx=10) # Spatiu intre imagini (padx=10)
                tk.Label(f, image=img).pack()
                tk.Label(f, text=titlu, font=("Arial", 12, "bold")).pack()

            # Butonul inapoi (care este deja setat sa fie centrat jos)
            self.adauga_buton_inapoi()

        except Exception as e:
            self.afiseaza_eroare(str(e))

    def aplicare_conversie_RGB_in_YUV(self):
        """
        Aplica conversia RGB -> YUV folosind formulele din laborator.
        """
        try:
            # Verificam daca avem deja o imagine in memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                # Daca nu, deschidem o imagine noua
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Cream obiectul PhotoImage pentru rezultatul YUV
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
                    
                    # Adaugam +128 la U si V pentru a le aduce in intervalul vizibil (0-255)
                    # deoarece diferenta (r - y_val) poate fi un numar negativ!
                    u_val = 0.74 * (r - y_val) + 0.27 * (b - y_val) + 128
                    v_val = 0.48 * (r - y_val) + 0.41 * (b - y_val) + 128

                    # Corectam valorile sa fie strict intre 0 si 255
                    y_int = int(max(0, min(255, y_val)))
                    u_int = int(max(0, min(255, u_val)))
                    v_int = int(max(0, min(255, v_val)))

                    # Asamblam pixelul in format hexazecimal
                    line_yuv.append(f"#{y_int:02x}{u_int:02x}{v_int:02x}")

                # Punem tot randul in formatul cerut de Tkinter
                rows_yuv.append(f"{{{ ' '.join(line_yuv) }}}")

            # "Desenam" imaginea
            self.img_yuv.put(" ".join(rows_yuv))

            # ==========================================
            # AFISARE PE ECRAN (Centrat)
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
        Aplica conversia RGB -> YCbCr (standardul JPEG) folosind formulele din laborator.
        """
        try:
            # Verificam daca avem deja o imagine in memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                # Daca nu, deschidem o imagine noua
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Cream obiectul PhotoImage pentru rezultatul YCbCr
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
                    
                    # Pentru Cb si Cr, offset-ul de 128 este deja inclus direct in formula standard
                    cb_val = -0.1687 * r - 0.3313 * g + 0.498 * b + 128
                    cr_val = 0.498 * r - 0.4187 * g - 0.0813 * b + 128

                    # Corectam valorile sa fie strict intre 0 si 255
                    y_int = int(max(0, min(255, y_val)))
                    cb_int = int(max(0, min(255, cb_val)))
                    cr_int = int(max(0, min(255, cr_val)))

                    # Asamblam pixelul in format hexazecimal
                    line_ycbcr.append(f"#{y_int:02x}{cb_int:02x}{cr_int:02x}")

                # Punem tot randul in formatul cerut de Tkinter
                rows_ycbcr.append(f"{{{ ' '.join(line_ycbcr) }}}")

            # "Desenam" imaginea
            self.img_ycbcr.put(" ".join(rows_ycbcr))

            # ==========================================
            # AFISARE PE ECRAN (Centrat)
            # ==========================================
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(container, image=self.img_ycbcr).pack()
            tk.Label(container, text="Imagine YCbCr (Standard JPEG)", font=("Arial", 14, "bold")).pack(pady=10)

            self.adauga_buton_inapoi()

        except Exception as e:
            self.afiseaza_eroare(str(e))    

    def deschide_dialog_prag(self):
        """
        Deschide o casuta de dialog care permite utilizatorului sa introduce un prag custom.
        Dupa ce introduce pragul, relanseza functia curenta cu noul prag.
        """
        from tkinter import simpledialog
        
        # Calculeaza pragul implicit ca media imaginii
        prag_implicit = int(self.cv_img_rgb.mean()) if hasattr(self, 'cv_img_rgb') and self.cv_img_rgb is not None else 127
        
        # Deschide dialog pentru introducere prag
        val = simpledialog.askinteger(
            "Schimbare Prag",
            f"Introduceți pragul (0-255):\n(Implicit: {prag_implicit})",
            initialvalue=prag_implicit,
            minvalue=0,
            maxvalue=255
        )
        
        # Daca utilizatorul a introdus o valoare, o stocheaza si relanseza functia
        if val is not None:
            self.prag_utilizator = val
            # Relansez functia curenta cu noul prag
            if self.functie_curenta:
                getattr(self, self.functie_curenta)()

    def adauga_butoane_inapoi_cu_prag(self):
        """
        Adauga doua butoane in dreapta jos: "Schimbă Prag" si "Înapoi".
        Trebuie apelata DUPA ce se creeaza container-ul principal.
        """
        # Creez o cutie pentru butoane, poziționată în colțul dreapta-jos
        butoane_frame = tk.Frame(self, bg=self.cget("bg"))
        butoane_frame.place(relx=0.95, rely=0.95, anchor="se")
        
        # Buton pentru schimbare prag
        buton_prag = tk.Button(
            butoane_frame,
            text="Schimbă Prag",
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            padx=10,
            pady=5,
            command=self.deschide_dialog_prag
        )
        buton_prag.pack(side="left", padx=5, pady=5)
        
        # Buton inapoi clasic
        buton_inapoi = tk.Button(
            butoane_frame,
            text="Înapoi",
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            padx=10,
            pady=5,
            command=self.ecran_principal
        )
        buton_inapoi.pack(side="left", padx=5, pady=5)

    def aplicare_inversare_RGB(self):
        """
        Calculeaza imaginea inversa (negativul) si afiseaza cele 3 canale RGB separat.
        """
        try:
            # Verificam daca avem deja o imagine in memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Cream 3 obiecte PhotoImage pentru cele 3 canale inverse
            self.img_inv_r = tk.PhotoImage(width=w, height=h)
            self.img_inv_g = tk.PhotoImage(width=w, height=h)
            self.img_inv_b = tk.PhotoImage(width=w, height=h)

            rows_r, rows_g, rows_b = [], [], []

            for y in range(h):
                line_r, line_g, line_b = [], [], []
                for x in range(w):
                    r, g, b = cv_img_rgb[y, x].astype(int)

                    # 1. Calculam inversul (negativul) pentru fiecare culoare
                    inv_r = 255 - r
                    inv_g = 255 - g
                    inv_b = 255 - b

                    # 2. Construim pixelii pentru fiecare canal in parte
                    # Pentru canalul ROSU, lasam G si B pe zero
                    line_r.append(f"#{inv_r:02x}0000")
                    
                    # Pentru canalul VERDE, lasam R si B pe zero
                    line_g.append(f"#00{inv_g:02x}00")
                    
                    # Pentru canalul ALBASTRU, lasam R si G pe zero
                    line_b.append(f"#0000{inv_b:02x}")

                # Impachetam randurile pentru formatul Tkinter
                rows_r.append(f"{{{ ' '.join(line_r) }}}")
                rows_g.append(f"{{{ ' '.join(line_g) }}}")
                rows_b.append(f"{{{ ' '.join(line_b) }}}")

            # Incarcam datele in imagini
            self.img_inv_r.put(" ".join(rows_r))
            self.img_inv_g.put(" ".join(rows_g))
            self.img_inv_b.put(" ".join(rows_b))

            # ==========================================
            # AFISARE PE ECRAN (Centrat)
            # ==========================================
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(container, text="Canalele Imaginii Inverse (Negative)", font=("Arial", 18, "bold")).pack(pady=10)

            # Folosim un Frame orizontal pentru a pune cele 3 imagini side-by-side
            row_frame = tk.Frame(container)
            row_frame.pack()

            # Afisam imaginile si titlurile lor
            for img, titlu in zip([self.img_inv_r, self.img_inv_g, self.img_inv_b], 
                                  ["Canal Rosu (Invers)", "Canal Verde (Invers)", "Canal Albastru (Invers)"]):
                f = tk.Frame(row_frame)
                f.pack(side="left", padx=10)
                tk.Label(f, image=img).pack()
                tk.Label(f, text=titlu, font=("Arial", 12, "bold")).pack()

            # Adaugam butonul de inapoi
            self.adauga_buton_inapoi()

        except Exception as e:
            self.afiseaza_eroare(str(e))

    def logica_binarizare(self, prag=127):
        """
        Functie auxiliara care binarizeaza imaginea din memorie (self.cv_img_rgb).
        Foloseste aceeasi logica ca aplicare_binarizare().

        Pentru fiecare pixel se calculeaza tonul de gri: gray = (R + G + B) / 3
        Daca gray >= prag -> pixelul este ALB (fond, valoare 0)
        Daca gray < prag  -> pixelul este NEGRU (obiect, valoare 1)

        Returneaza:
        - img_bin: matrice numpy h x w cu valori 0 (fond) sau 1 (obiect)
        """
        cv_img_rgb = self.cv_img_rgb
        h, w = cv_img_rgb.shape[:2]

        # Calculam tonul de gri pentru fiecare pixel (media aritmetica)
        img_bin = np.zeros((h, w), dtype=int)

        for y in range(h):
            for x in range(w):
                r, g, b = cv_img_rgb[y, x].astype(int)
                gray = (r + g + b) // 3

                # Acelasi criteriu ca in aplicare_binarizare:
                # gray >= prag -> alb (fond = 0), gray < prag -> negru (obiect = 1)
                if gray < prag:
                    img_bin[y, x] = 1

        return img_bin

    def aplicare_binarizare(self):
        """
        Transforma imaginea intr-una strict alb-negru (binara) pe baza unui prag.
        """
        try:
            # Verificam daca avem imagine in memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Cream obiectele PhotoImage (Original si Binarizat)
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

                    # --- Pentru imaginea originala (doar reconstruim pixelii) ---
                    line_orig.append(f"#{r:02x}{g:02x}{b:02x}")

                    # --- Pentru Binarizare ---
                    # 1. Gasim valoarea de luminozitate (folosim media aritmetica)
                    gray = (r + g + b) // 3

                    # 2. Aplicam pragul ales de noi
                    if gray >= prag:
                        line_bin.append("#ffffff") # Alb pur
                    else:
                        line_bin.append("#000000") # Negru pur

                # Impachetam randurile pentru formatul Tkinter
                rows_orig.append(f"{{{ ' '.join(line_orig) }}}")
                rows_bin.append(f"{{{ ' '.join(line_bin) }}}")

            # Incarcam datele in imagini
            self.img_original.put(" ".join(rows_orig))
            self.img_binar.put(" ".join(rows_bin))

            # ==========================================
            # AFISARE PE ECRAN (Centrat)
            # ==========================================
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(container, text=f"Binarizare (Prag ales: {prag})", font=("Arial", 18, "bold")).pack(pady=10)

            # Folosim un Frame orizontal pentru a pune pozele side-by-side
            row_frame = tk.Frame(container)
            row_frame.pack()

            # Imaginea Originala (Stanga)
            f_orig = tk.Frame(row_frame)
            f_orig.pack(side="left", padx=15)
            tk.Label(f_orig, image=self.img_original).pack()
            tk.Label(f_orig, text="Imagine Originala", font=("Arial", 12)).pack()

            # Imaginea Binarizata (Dreapta)
            f_bin = tk.Frame(row_frame)
            f_bin.pack(side="left", padx=15)
            tk.Label(f_bin, image=self.img_binar).pack()
            tk.Label(f_bin, text="Imagine Binarizata (Alb/Negru pur)", font=("Arial", 12, "bold")).pack()

            self.adauga_buton_inapoi()

        except Exception as e:
            self.afiseaza_eroare(str(e))

    def calculare_centru_de_masa(self):
        """
        Calculeaza centrul de masa (greutate) al imaginii pe baza luminantei
        si deseneaza un indicator vizual (o cruce rosie) pe acele coordonate.
        """
        try:
            # Verificam daca avem imagine in memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # 1. CALCULUL MATEMATIC AL CENTRULUI DE MASA
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

            # Evitam impartirea la zero in cazul (improbabil) al unei imagini complet negre
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
                    # Desenam o "tinta" (cruce) rosie peste centrul de masa
                    # Daca pixelul curent este pe linia lui cx sau cy
                    if (abs(x - cx) <= 1 and abs(y - cy) <= 20) or (abs(y - cy) <= 1 and abs(x - cx) <= 20):
                        line.append("#ff0000") # Rosu pur
                    else:
                        r, g, b = cv_img_rgb[y, x].astype(int)
                        line.append(f"#{r:02x}{g:02x}{b:02x}")

                rows.append(f"{{{ ' '.join(line) }}}")

            self.img_centru.put(" ".join(rows))

            # ==========================================
            # AFISARE PE ECRAN
            # ==========================================
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(container, text="Centrul de Masa al Imaginii", font=("Arial", 18, "bold")).pack(pady=10)
            
            # Afisam coordonatele calculate
            tk.Label(container, text=f"Coordonate calculate: X = {cx}, Y = {cy}", font=("Arial", 14), fg="blue").pack(pady=5)

            tk.Label(container, image=self.img_centru).pack(pady=10)

            self.adauga_buton_inapoi()

        except Exception as e:
            self.afiseaza_eroare(str(e))

    # ==========================================
    # LABORATOR 5 – Functii noi
    # ==========================================

    def aplicare_conversie_RGB_in_HSV(self):
        """
        Converteste imaginea din spatiul de culoare RGB in spatiul HSV.

        Formulele utilizate (conform laboratorului):
        - Se normalizeaza R, G, B in intervalul [0, 1]: r = R/255, g = G/255, b = B/255
        - M = max(r, g, b), m = min(r, g, b), C = M - m
        - V (Value) = M
        - S (Saturation) = C / V daca V != 0, altfel S = 0
        - H (Hue):
            * Daca C != 0:
                - Daca M == r: H = 60 * (g - b) / C
                - Daca M == g: H = 120 + 60 * (b - r) / C
                - Daca M == b: H = 240 + 60 * (r - g) / C
            * Altfel (grayscale): H = 0
            * Daca H < 0: H = H + 360

        Normalizare pentru afisare pe 8 biti (0-255):
        - H_norm = H * 255 / 360
        - S_norm = S * 255
        - V_norm = V * 255

        Afiseaza 4 imagini: HSV combinat, H, S, V separate.
        """
        try:
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return

            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]

            # Cream 4 obiecte PhotoImage: HSV combinat + H, S, V separate
            self.img_hsv = tk.PhotoImage(width=w, height=h)
            self.img_h_ch = tk.PhotoImage(width=w, height=h)
            self.img_s_ch = tk.PhotoImage(width=w, height=h)
            self.img_v_ch = tk.PhotoImage(width=w, height=h)

            rows_hsv, rows_h, rows_s, rows_v = [], [], [], []

            for y_px in range(h):
                line_hsv, line_h, line_s, line_v = [], [], [], []
                for x_px in range(w):
                    R, G, B = cv_img_rgb[y_px, x_px].astype(float)

                    # Normalizam componentele RGB in intervalul [0, 1]
                    r = R / 255.0
                    g = G / 255.0
                    b = B / 255.0

                    M = max(r, g, b)
                    m = min(r, g, b)
                    C = M - m

                    # Value
                    V = M

                    # Saturation
                    if V != 0:
                        S = C / V
                    else:  # negru
                        S = 0

                    # Hue
                    if C != 0:
                        if M == r:
                            H = 60.0 * (g - b) / C
                        elif M == g:
                            H = 120.0 + 60.0 * (b - r) / C
                        else:  # M == b
                            H = 240.0 + 60.0 * (r - g) / C
                    else:  # grayscale
                        H = 0

                    if H < 0:
                        H = H + 360

                    # Normalizam in intervalul [0, 255] pentru afisare ca imagine 8 biti
                    H_norm = int(max(0, min(255, H * 255.0 / 360.0)))
                    S_norm = int(max(0, min(255, S * 255.0)))
                    V_norm = int(max(0, min(255, V * 255.0)))

                    # HSV combinat (H pe canalul rosu, S pe verde, V pe albastru)
                    line_hsv.append(f"#{H_norm:02x}{S_norm:02x}{V_norm:02x}")
                    # Canale separate in tonuri de gri
                    line_h.append(f"#{H_norm:02x}{H_norm:02x}{H_norm:02x}")
                    line_s.append(f"#{S_norm:02x}{S_norm:02x}{S_norm:02x}")
                    line_v.append(f"#{V_norm:02x}{V_norm:02x}{V_norm:02x}")

                rows_hsv.append(f"{{{ ' '.join(line_hsv) }}}")
                rows_h.append(f"{{{ ' '.join(line_h) }}}")
                rows_s.append(f"{{{ ' '.join(line_s) }}}")
                rows_v.append(f"{{{ ' '.join(line_v) }}}")

            # "Desenam" imaginile
            self.img_hsv.put(" ".join(rows_hsv))
            self.img_h_ch.put(" ".join(rows_h))
            self.img_s_ch.put(" ".join(rows_s))
            self.img_v_ch.put(" ".join(rows_v))

            # AFISARE PE ECRAN
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(container, text="Conversie RGB -> HSV", font=("Arial", 18, "bold")).pack(pady=10)

            row_frame = tk.Frame(container)
            row_frame.pack()

            for img, titlu in zip(
                [self.img_hsv, self.img_h_ch, self.img_s_ch, self.img_v_ch],
                ["HSV Combinat", "H (Hue)", "S (Saturation)", "V (Value)"]
            ):
                f = tk.Frame(row_frame)
                f.pack(side="left", padx=5)
                tk.Label(f, image=img).pack()
                tk.Label(f, text=titlu, font=("Arial", 10, "bold")).pack()

            self.adauga_buton_inapoi()

        except Exception as e:
            self.afiseaza_eroare(str(e))

    def calculeaza_histograma(self, img_rgb):
        """
        Calculeaza histograma unei imagini RGB.
        Functie auxiliara reutilizabila folosita de egalizare_histograma() si afisare_histograma().
        
        Algoritm:
        1. Converteste fiecare pixel RGB la grayscale: gray = (R + G + B) / 3
        2. Calculeaza frecventa fiecarui nivel de gri (0-255)
        
        Parametri:
        - img_rgb: imagine numpy array de dimensiune (h, w, 3)
        
        Returneaza:
        - histogram: array numpy de 256 elemente cu frecventa fiecarui nivel de gri
        """
        h, w = img_rgb.shape[:2]
        
        # Initializam histograma cu 0
        histogram = np.zeros(256, dtype=int)
        
        # Calculam histograma prin parcurgerea tuturor pixelilor
        for y in range(h):
            for x in range(w):
                r, g, b = img_rgb[y, x].astype(int)
                # Convertim pixelul la grayscale (media RGB)
                gray = (r + g + b) // 3
                # Incrementam frecventa nivelului de gri
                histogram[gray] += 1
        
        return histogram

    def afisare_histograma(self):
        """
        Calculeaza si afiseaza histograma unei imagini in tonuri de gri.
        NU se foloseste OpenCV pentru calculul histogramei.

        Algoritmul:
        1. Se converteste fiecare pixel in ton de gri: gray = (R + G + B) / 3
        2. Se initializeaza un array de 256 elemente (cate unul pentru fiecare nivel de gri 0-255)
        3. Se parcurge fiecare pixel si se incrementeaza contorul corespunzator nivelului de gri:
           histogram[gray] += 1
        4. Se deseneaza histograma pe un Canvas Tkinter:
           - Axa X = nivelul de gri (0-255)
           - Axa Y = numarul de pixeli cu acel nivel de gri (scalat la inaltimea canvas-ului)
           - Barele sunt colorate cu nuanta de gri corespunzatoare
        """
        try:
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return

            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]

            # 1. Calculam histograma folosind functia auxiliara
            histogram = self.calculeaza_histograma(cv_img_rgb)

            # 2. Aflam valoarea maxima pentru scalare
            max_val = max(histogram)
            if max_val == 0:
                max_val = 1

            # 3. AFISARE PE ECRAN
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(container, text="Histograma Imaginii (Tonuri de Gri)", font=("Arial", 18, "bold")).pack(pady=10)

            # Dimensiunile canvas-ului
            canvas_w = 512  # 256 niveluri * 2 pixeli per bara
            canvas_h = 300

            canvas = tk.Canvas(container, width=canvas_w, height=canvas_h, bg="white", bd=2, relief="sunken")
            canvas.pack(pady=10)

            # Desenam barele histogramei
            bar_width = canvas_w / 256
            for i in range(256):
                # Inaltimea barei, scalata la dimensiunea canvas-ului
                bar_height = (histogram[i] / max_val) * (canvas_h - 10)

                x0 = i * bar_width
                y0 = canvas_h - bar_height
                x1 = (i + 1) * bar_width
                y1 = canvas_h

                # Culoarea barei
                gray_hex = f"#{i:02x}{i:02x}{i:02x}"
                canvas.create_rectangle(x0, y0, x1, y1, fill=gray_hex, outline="")

            # Afisam statistici
            total_pixeli = h * w
            tk.Label(container, text=f"Total pixeli: {total_pixeli} | Dimensiuni: {w}x{h}",
                     font=("Arial", 12)).pack(pady=5)

            self.adauga_buton_inapoi()

        except Exception as e:
            self.afiseaza_eroare(str(e))

    def egalizare_histograma(self, img_rgb):
        """
        Egalizarea histogramei pentru o imagine RGB.
        Converteste imaginea la grayscale, calculeaza histograma si histograma cumulativa,
        apoi aplica transformarea pentru a obtine o histograma uniforma.
        
        Algoritm:
        1. Convertim imaginea RGB la grayscale (media canalelor)
        2. Calculam histograma: h[i] = frecventa nivelului de gri i
        3. Calculam histograma cumulativa: hc[i] = suma(h[0] la h[i])
        4. Aplicam transformarea: nivel_nou = (hc[nivel_vechi] - hc[0]) * 255 / (width * height - hc[0])
        
        Returneaza:
        - img_out: imagine egalizata (RGB, cu R=G=B pentru a arata grayscale)
        """
        h, w = img_rgb.shape[:2]
        
        # PASUL 1: Convertim la grayscale
        img_gray = np.zeros((h, w), dtype=np.uint8)
        for y in range(h):
            for x in range(w):
                r, g, b = img_rgb[y, x].astype(float)
                # Media RGB-ului
                gray = int((r + g + b) / 3)
                img_gray[y, x] = gray
        
        # PASUL 2: Calculam histograma folosind functia auxiliara
        histogram = self.calculeaza_histograma(img_rgb)
        
        # PASUL 3: Calculam histograma cumulativa
        hc = np.zeros(256, dtype=int)
        hc[0] = histogram[0]
        for i in range(1, 256):
            hc[i] = hc[i-1] + histogram[i]
        
        # PASUL 4: Aplicam transformarea pentru egalizare
        total_pixels = h * w
        img_out = np.zeros((h, w, 3), dtype=np.uint8)
        
        for y in range(h):
            for x in range(w):
                nivel_vechi = img_gray[y, x]
                # Transformarea: T(x) = (hc[x] - hc[0]) * 255 / (total_pixels - hc[0])
                if total_pixels - hc[0] == 0:
                    nivel_nou = 0
                else:
                    nivel_nou = int((hc[nivel_vechi] - hc[0]) * 255 / (total_pixels - hc[0]))
                
                # Asiguram valori intre 0 si 255
                nivel_nou = max(0, min(255, nivel_nou))
                
                # Stocam valoarea egalizata in toate 3 canale (pentru a forma un pixel grayscale)
                img_out[y, x] = [nivel_nou, nivel_nou, nivel_nou]
        
        return img_out

    def aplicare_egalizare_histograma(self):
        """
        Aplica egalizarea histogramei pe imaginea din memorie.
        Afiseaza imaginea originala (convertita la grayscale) si versiunea egalizata side-by-side.
        """
        try:
            # Verificam daca avem deja o imagine in memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                # Daca nu, deschidem o imagine noua
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # 1. Convertim imaginea la grayscale pentru afisare
            img_gray = np.zeros((h, w, 3), dtype=np.uint8)
            for y in range(h):
                for x in range(w):
                    r, g, b = cv_img_rgb[y, x].astype(float)
                    gray = int((r + g + b) / 3)
                    img_gray[y, x] = [gray, gray, gray]
            
            # 2. Aplicam egalizarea
            img_egalizata = self.egalizare_histograma(cv_img_rgb)
            
            # 3. Cream 2 obiecte PhotoImage pentru original si egalizat
            self.img_original = tk.PhotoImage(width=w, height=h)
            self.img_egalizat = tk.PhotoImage(width=w, height=h)
            
            # Construim datele pentru imaginea originala (grayscale)
            rows_original = []
            for y in range(h):
                line = " ".join(f"#{img_gray[y, x][0]:02x}{img_gray[y, x][1]:02x}{img_gray[y, x][2]:02x}" 
                                for x in range(w))
                rows_original.append(f"{{{line}}}")
            self.img_original.put(" ".join(rows_original))
            
            # Construim datele pentru imaginea egalizata
            rows_egalizat = []
            for y in range(h):
                line = " ".join(f"#{img_egalizata[y, x][0]:02x}{img_egalizata[y, x][1]:02x}{img_egalizata[y, x][2]:02x}" 
                                for x in range(w))
                rows_egalizat.append(f"{{{line}}}")
            self.img_egalizat.put(" ".join(rows_egalizat))
            
            # ==========================================
            # AFISARE REZULTATE (Centrat)
            # ==========================================
            self.curata_ecranul()
            
            # Containerul principal centrat pe pagina
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")
            
            # Adaugam un titlu pentru aceasta pagina
            tk.Label(container, text="Egalizare Histograma (Accentuare Contrast)", font=("Arial", 18, "bold")).pack(pady=10)
            
            # Cream un sub-container orizontal pentru a pune pozele una langa alta
            row_frame = tk.Frame(container)
            row_frame.pack()
            
            # Afisam imaginea originala si cea egalizata
            for img, titlu in zip([self.img_original, self.img_egalizat], 
                                  ["Original (Grayscale)", "Egalizata (Contrast Crescut)"]):
                f = tk.Frame(row_frame)
                f.pack(side="left", padx=15)
                tk.Label(f, image=img).pack()
                tk.Label(f, text=titlu, font=("Arial", 12, "bold")).pack(pady=5)
            
            # Butonul inapoi
            self.adauga_buton_inapoi()
            
        except Exception as e:
            self.afiseaza_eroare(str(e))

    def calculare_moment_ordin_1(self):
        """
        Calculeaza momentele de ordin 1 ale unei imagini binarizate.
        NU se foloseste OpenCV.

        Momentele brute calculate:
        - M00 = Σ I(x,y) — suma tuturor valorilor pixelilor (aria obiectului in imagine binara)
        - M10 = Σ x * I(x,y) — momentul de ordin 1 pe axa X
        - M01 = Σ y * I(x,y) — momentul de ordin 1 pe axa Y

        Din aceste momente se calculeaza centroidul (centrul de masa):
        - x_centroid = M10 / M00
        - y_centroid = M01 / M00

        Imaginea este binarizata (alb/negru) cu un prag de 127 pentru a lucra cu
        forme simple (cercuri, dreptunghiuri rotite create in Paint).
        Se deseneaza o cruce rosie pe centroid ca indicator vizual.
        """
        try:
            # Setez functia curenta pentru relansare dupa schimbarea pragului
            self.functie_curenta = 'calculare_moment_ordin_1'
            
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return

            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]

            # 1. Binarizam imaginea folosind functia auxiliara (aceeasi logica ca aplicare_binarizare)
            # Calculaza pragul adaptiv (implicit este 220 pentru a detecta si obiecte colorate, dar poate fi schimbat)
            prag = self.prag_utilizator if self.prag_utilizator is not None else 220
            img_bin = self.logica_binarizare(prag=prag)

            # 2. Calculam momentele de ordin 0 si 1 folosind matricea binarizata
            M00 = 0  # Moment de ordin 0 (aria obiectului)
            M10 = 0  # Moment de ordin 1 pe X
            M01 = 0  # Moment de ordin 1 pe Y

            for y_px in range(h):
                for x_px in range(w):
                    I = img_bin[y_px, x_px]
                    M00 += I
                    M10 += x_px * I
                    M01 += y_px * I

            # 3. Calculam centroidul (centrul de masa)
            if M00 > 0:
                cx = M10 / M00
                cy = M01 / M00
            else:
                cx, cy = w / 2, h / 2

            # 4. Generam imaginea binarizata cu indicator vizual (cruce rosie pe centroid)
            self.img_moment1 = tk.PhotoImage(width=w, height=h)
            rows = []

            for y_px in range(h):
                line = []
                for x_px in range(w):
                    # Desenam crucea rosie pe centroid
                    if (abs(x_px - int(cx)) <= 1 and abs(y_px - int(cy)) <= 20) or \
                       (abs(y_px - int(cy)) <= 1 and abs(x_px - int(cx)) <= 20):
                        line.append("#ff0000")
                    else:
                        # Folosim matricea binarizata pentru afisare
                        if img_bin[y_px, x_px] == 1:
                            line.append("#000000")  # Obiect = negru
                        else:
                            line.append("#ffffff")  # Fond = alb
                rows.append(f"{{{ ' '.join(line) }}}")

            self.img_moment1.put(" ".join(rows))

            # 5. AFISARE PE ECRAN
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(container, text="Momente de Ordin 1", font=("Arial", 18, "bold")).pack(pady=10)

            # Afisam valorile calculate
            info_frame = tk.Frame(container)
            info_frame.pack(pady=5)
            tk.Label(info_frame, text=f"M00 (Aria obiectului) = {M00}", font=("Arial", 12), fg="blue").pack()
            tk.Label(info_frame, text=f"M10 (Moment ordin 1, axa X) = {M10}", font=("Arial", 12), fg="blue").pack()
            tk.Label(info_frame, text=f"M01 (Moment ordin 1, axa Y) = {M01}", font=("Arial", 12), fg="blue").pack()
            tk.Label(info_frame, text=f"Centroid: X = {cx:.2f}, Y = {cy:.2f}",
                     font=("Arial", 14, "bold"), fg="darkgreen").pack(pady=5)

            tk.Label(container, image=self.img_moment1).pack(pady=10)

            # Legenda
            tk.Label(container, text="● Rosu = Centroid (centrul de masa)", fg="red", font=("Arial", 10)).pack()

            self.adauga_butoane_inapoi_cu_prag()

        except Exception as e:
            self.afiseaza_eroare(str(e))

    def calculare_moment_ordin_2(self):
        """
        Calculeaza momentele de ordin 2 ale unei imagini binarizate.
        NU se foloseste OpenCV.

        Momentele brute de ordin 2:
        - M20 = Σ x² * I(x,y) — momentul de ordin 2 pe axa X
        - M02 = Σ y² * I(x,y) — momentul de ordin 2 pe axa Y
        - M11 = Σ x * y * I(x,y) — momentul mixt de ordin 2

        Momentele centrale de ordin 2 (relative la centroid):
        - μ20 = M20 - cx * M10
        - μ02 = M02 - cy * M01
        - μ11 = M11 - cx * M01

        Din momentele de ordin 2 se calculeaza orientarea obiectului:
        - θ = 0.5 * arctan(2 * μ11 / (μ20 - μ02))

        Aceasta reprezinta unghiul axei principale a obiectului.
        Se deseneaza o linie verde pentru axa principala si o cruce rosie pe centroid.
        """
        try:
            # Setez functia curenta pentru relansare dupa schimbarea pragului
            self.functie_curenta = 'calculare_moment_ordin_2'
            
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return

            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]

            # Binarizam imaginea folosind functia auxiliara (aceeasi logica ca aplicare_binarizare)
            # Calculaza pragul adaptiv (implicit este 220 pentru a detecta si obiecte colorate, dar poate fi schimbat)
            prag = self.prag_utilizator if self.prag_utilizator is not None else 220
            img_bin = self.logica_binarizare(prag=prag)

            # Calculam TOATE momentele necesare (ordin 0, 1 si 2) folosind matricea binarizata
            M00, M10, M01 = 0, 0, 0
            M20, M02, M11 = 0, 0, 0

            for y_px in range(h):
                for x_px in range(w):
                    I = img_bin[y_px, x_px]

                    M00 += I
                    M10 += x_px * I
                    M01 += y_px * I
                    M20 += x_px * x_px * I
                    M02 += y_px * y_px * I
                    M11 += x_px * y_px * I

            # Centroid
            if M00 != 0:
                cx = M10 / M00
                cy = M01 / M00
            else:
                cx, cy = w / 2, h / 2

            # Momente centrale de ordin 2
            mu20 = M20 - cx * M10
            mu02 = M02 - cy * M01
            mu11 = M11 - cx * M01

            # Orientarea axei principale (in grade)
            if (mu20 - mu02) != 0:
                theta = 0.5 * math.atan2(2 * mu11, mu20 - mu02)
            else:
                theta = 0
            theta_deg = math.degrees(theta)

            # Generam imaginea cu indicatoare vizuale
            self.img_moment2 = tk.PhotoImage(width=w, height=h)
            rows = []

            # Lungimea liniei axei principale pentru vizualizare
            line_length = min(w, h) // 3

            for y_px in range(h):
                line = []
                for x_px in range(w):
                    dx = x_px - int(cx)
                    dy = y_px - int(cy)

                    # Verificam daca punctul este pe axa principala (linie verde)
                    dist_to_axis = abs(dx * math.sin(theta) - dy * math.cos(theta))
                    dist_from_center = math.sqrt(dx * dx + dy * dy)

                    if dist_to_axis <= 1.5 and dist_from_center <= line_length:
                        line.append("#00ff00")  # Verde pentru axa principala
                    elif (abs(x_px - int(cx)) <= 1 and abs(y_px - int(cy)) <= 15) or \
                         (abs(y_px - int(cy)) <= 1 and abs(x_px - int(cx)) <= 15):
                        line.append("#ff0000")  # Rosu pentru centroid
                    else:
                        # Folosim matricea binarizata pentru afisare
                        if img_bin[y_px, x_px] == 1:
                            line.append("#000000")
                        else:
                            line.append("#ffffff")
                rows.append(f"{{{ ' '.join(line) }}}")

            self.img_moment2.put(" ".join(rows))

            # AFISARE PE ECRAN
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(container, text="Momente de Ordin 2", font=("Arial", 18, "bold")).pack(pady=10)

            info_frame = tk.Frame(container)
            info_frame.pack(pady=5)
            tk.Label(info_frame, text=f"M20 = {M20}", font=("Arial", 12), fg="blue").pack()
            tk.Label(info_frame, text=f"M02 = {M02}", font=("Arial", 12), fg="blue").pack()
            tk.Label(info_frame, text=f"M11 = {M11}", font=("Arial", 12), fg="blue").pack()
            tk.Label(info_frame, text=f"μ20 = {mu20:.2f}", font=("Arial", 12), fg="purple").pack()
            tk.Label(info_frame, text=f"μ02 = {mu02:.2f}", font=("Arial", 12), fg="purple").pack()
            tk.Label(info_frame, text=f"μ11 = {mu11:.2f}", font=("Arial", 12), fg="purple").pack()
            tk.Label(info_frame, text=f"Orientare (θ) = {theta_deg:.2f}°",
                     font=("Arial", 14, "bold"), fg="darkgreen").pack(pady=5)

            tk.Label(container, image=self.img_moment2).pack(pady=10)

            # Legenda
            legend = tk.Frame(container)
            legend.pack()
            tk.Label(legend, text="● Rosu = Centroid", fg="red", font=("Arial", 10)).pack(side="left", padx=10)
            tk.Label(legend, text="● Verde = Axa Principala", fg="green", font=("Arial", 10)).pack(side="left", padx=10)

            self.adauga_butoane_inapoi_cu_prag()

        except Exception as e:
            self.afiseaza_eroare(str(e))

    def calculare_matrice_covarianta(self):
        """
        Calculeaza matricea de covarianta a unei imagini binarizate.

        Matricea de covarianta 2x2 descrie distributia spatiala a pixelilor:

        Cov = | cov_xx  cov_xy |   =   | μ20/M00  μ11/M00 |
              | cov_xy  cov_yy |       | μ11/M00  μ02/M00 |

        unde:
        - μ20 = Σ (x - cx)² * I(x,y)  — variatia pe axa X
        - μ02 = Σ (y - cy)² * I(x,y)  — variatia pe axa Y
        - μ11 = Σ (x - cx)(y - cy) * I(x,y) — corelatia X-Y
        - cx, cy = centroidul imaginii
        """
        try:
            # Setez functia curenta pentru relansare dupa schimbarea pragului
            self.functie_curenta = 'calculare_matrice_covarianta'
            
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return

            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]

            # Binarizam imaginea folosind functia auxiliara (aceeasi logica ca aplicare_binarizare)
            # Calculaza pragul adaptiv (implicit este 220 pentru a detecta si obiecte colorate, dar poate fi schimbat)
            prag = self.prag_utilizator if self.prag_utilizator is not None else 220
            img_bin = self.logica_binarizare(prag=prag)

            # Prima trecere: calculam M00, M10, M01 pentru centroid
            M00, M10, M01 = 0, 0, 0

            for y_px in range(h):
                for x_px in range(w):
                    I = img_bin[y_px, x_px]

                    M00 += I
                    M10 += x_px * I
                    M01 += y_px * I

            if M00 == 0:
                cx, cy = w / 2, h / 2
                M00 = 1  # Evitam impartirea la zero
            else:
                cx = M10 / M00
                cy = M01 / M00

            # A doua trecere: calculam momentele centrale folosind matricea binarizata
            mu20, mu02, mu11 = 0.0, 0.0, 0.0

            for y_px in range(h):
                for x_px in range(w):
                    I = img_bin[y_px, x_px]

                    dx = x_px - cx
                    dy = y_px - cy

                    mu20 += dx * dx * I
                    mu02 += dy * dy * I
                    mu11 += dx * dy * I

            # Matricea de covarianta
            cov_xx = mu20 / M00
            cov_yy = mu02 / M00
            cov_xy = mu11 / M00

            # Calculam valorile proprii (eigenvalues) ale matricei 2x2
            trace = cov_xx + cov_yy
            det = cov_xx * cov_yy - cov_xy * cov_xy
            discriminant = max(0, trace * trace / 4 - det)  # Asiguram >= 0 (erori numerice)

            lambda1 = trace / 2 + math.sqrt(discriminant)
            lambda2 = trace / 2 - math.sqrt(discriminant)

            # AFISARE PE ECRAN
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(container, text="Matricea de Covarianta", font=("Arial", 18, "bold")).pack(pady=10)

            # Afisam centroidul
            tk.Label(container, text=f"Centroid: ({cx:.2f}, {cy:.2f})",
                     font=("Arial", 12), fg="blue").pack(pady=5)

            # Afisam matricea intr-un format vizual
            matrix_frame = tk.Frame(container, bd=2, relief="ridge", padx=20, pady=10)
            matrix_frame.pack(pady=10)

            tk.Label(matrix_frame, text="Matrice de Covarianta:", font=("Arial", 14, "bold")).pack()
            tk.Label(matrix_frame, text=f"| {cov_xx:12.2f}  {cov_xy:12.2f} |",
                     font=("Courier", 14)).pack()
            tk.Label(matrix_frame, text=f"| {cov_xy:12.2f}  {cov_yy:12.2f} |",
                     font=("Courier", 14)).pack()

            # Afisam valorile proprii
            tk.Label(container, text=f"Valoare proprie λ1 = {lambda1:.2f}",
                     font=("Arial", 12), fg="darkgreen").pack(pady=2)
            tk.Label(container, text=f"Valoare proprie λ2 = {lambda2:.2f}",
                     font=("Arial", 12), fg="darkgreen").pack(pady=2)

            # Afisam formula
            tk.Label(container, text="Formula: Cov = [[μ20/M00, μ11/M00], [μ11/M00, μ02/M00]]",
                     font=("Arial", 10), fg="gray").pack(pady=5)

            self.adauga_butoane_inapoi_cu_prag()

        except Exception as e:
            self.afiseaza_eroare(str(e))

    def calculare_proiectii(self):
        """
        Calculeaza si afiseaza proiectiile orizontala si verticala ale imaginii.

        Proiectia orizontala:
        - Pentru fiecare rand y, se calculeaza suma intensitatilor tuturor pixelilor:
          proj_h[y] = Σ_x I(x, y)
        - Se afiseaza ca un grafic de bare orizontale (in dreapta imaginii)

        Proiectia verticala:
        - Pentru fiecare coloana x, se calculeaza suma intensitatilor tuturor pixelilor:
          proj_v[x] = Σ_y I(x, y)
        - Se afiseaza ca un grafic de bare verticale (sub imagine)

        Proiectiile sunt utile pentru:
        - Detectarea limitelor obiectelor
        - Segmentarea textului
        - Analiza formei si pozitiei obiectelor in imagine
        """
        try:
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return

            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]

            # 1. Calculam proiectiile
            proj_h = [0] * h  # Proiectie orizontala (suma intensitatilor pe fiecare rand)
            proj_v = [0] * w  # Proiectie verticala (suma intensitatilor pe fiecare coloana)

            for y_px in range(h):
                for x_px in range(w):
                    r, g, b = cv_img_rgb[y_px, x_px].astype(int)
                    # Folosim tonul de gri ca intensitate
                    gray = (r + g + b) // 3

                    proj_h[y_px] += gray  # Adunam la suma randului
                    proj_v[x_px] += gray  # Adunam la suma coloanei

            # 2. AFISARE PE ECRAN
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")

            tk.Label(container, text="Proiectii Orizontala si Verticala",
                     font=("Arial", 18, "bold")).pack(pady=10)

            # Container principal cu grid layout
            main_frame = tk.Frame(container)
            main_frame.pack()

            # Imaginea originala (in grayscale) - stanga sus
            self.img_proj = tk.PhotoImage(width=w, height=h)
            rows = []
            for y_px in range(h):
                line = []
                for x_px in range(w):
                    r, g, b = cv_img_rgb[y_px, x_px].astype(int)
                    gray = (r + g + b) // 3
                    line.append(f"#{gray:02x}{gray:02x}{gray:02x}")
                rows.append(f"{{{ ' '.join(line) }}}")
            self.img_proj.put(" ".join(rows))

            tk.Label(main_frame, image=self.img_proj).grid(row=0, column=0, padx=5, pady=5)

            # Proiectia orizontala (grafic de bare in dreapta imaginii)
            max_h_val = max(proj_h) if max(proj_h) > 0 else 1
            proj_h_width = 200

            canvas_h_proj = tk.Canvas(main_frame, width=proj_h_width, height=h,
                                      bg="white", bd=1, relief="sunken")
            canvas_h_proj.grid(row=0, column=1, padx=5, pady=5)

            # Desenam barele orizontale (cate una per rand al imaginii)
            for y_px in range(h):
                bar_w = (proj_h[y_px] / max_h_val) * (proj_h_width - 5)
                canvas_h_proj.create_line(0, y_px, bar_w, y_px, fill="#4444ff")

            # Proiectia verticala (grafic de bare sub imagine)
            max_v_val = max(proj_v) if max(proj_v) > 0 else 1
            proj_v_height = 150

            canvas_v_proj = tk.Canvas(main_frame, width=w, height=proj_v_height,
                                      bg="white", bd=1, relief="sunken")
            canvas_v_proj.grid(row=1, column=0, padx=5, pady=5)

            # Desenam barele verticale (cate una per coloana a imaginii)
            for x_px in range(w):
                bar_h = (proj_v[x_px] / max_v_val) * (proj_v_height - 5)
                canvas_v_proj.create_line(x_px, proj_v_height, x_px, proj_v_height - bar_h, fill="#44aa44")

            # Legenda
            legend_frame = tk.Frame(container)
            legend_frame.pack(pady=5)
            tk.Label(legend_frame, text="Albastru = Proiectie Orizontala (suma pe randuri)",
                     fg="#4444ff", font=("Arial", 10)).pack()
            tk.Label(legend_frame, text="Verde = Proiectie Verticala (suma pe coloane)",
                     fg="#44aa44", font=("Arial", 10)).pack()

            self.adauga_buton_inapoi()

        except Exception as e:
            self.afiseaza_eroare(str(e))

    # ==========================================
    # LABORATOR 6 – Etichetarea Componentelor
    # ==========================================

    def aplicare_etichetare(self):
        """
        Realizează etichetarea obiectelor distincte dintr-o imagine binară.
        
        Logica algoritmului (fără OpenCV):
        1. Inițializează o matrice de etichete cu zero.
        2. Parcurge imaginea pixel cu pixel.
        3. Când găsește un pixel de obiect (valoare 0) neetichetat:
           - Incrementează contorul de etichete.
           - Folosește o coadă (Queue) pentru a propaga eticheta la toți vecinii
             conecști (N8), marcând astfel întreg obiectul.
        4. Generează o imagine colorată unde fiecare ID de obiect are o culoare unică.
        """
        try:
            # Setez functia curenta pentru relansare dupa schimbarea pragului
            self.functie_curenta = 'aplicare_etichetare'
            
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None: return

            h, w = self.cv_img_rgb.shape[:2]
            
            # Pasul 0: Obținem imaginea binară (0=obiect, 1=fundal)
            # Adaptăm logica: în codul Java, obiectele sunt 0 (negru).
            # Calculaza pragul adaptiv (implicit este 127, dar poate fi schimbat)
            prag = self.prag_utilizator if self.prag_utilizator is not None else 127
            img_bin = self.logica_binarizare(prag=prag) 
            # Inversăm dacă este necesar pentru a avea obiect=0 conform sursei Java.
            
            # Pasul 1: Inițializare matrice etichete
            self.labels = np.zeros((h, w), dtype=int)
            label_actual = 0
            
            # Pasul 2: Parcurgerea imaginii
            for i in range(h):
                for j in range(w):
                    # Verificăm dacă pixelul este de tip obiect (0) și neetichetat
                    # Nota: logica_binarizare returneaza 1 pentru obiect, adaptam conditia:
                    if img_bin[i, j] == 1 and self.labels[i, j] == 0:
                        label_actual += 1
                        
                        # Pasul 3: Propagarea etichetei folosind o coadă (BFS)
                        queue = [(i, j)]
                        self.labels[i, j] = label_actual
                        
                        while queue:
                            curr_i, curr_j = queue.pop(0)
                            
                            # Verificăm vecinătatea N8 (8-vecini)
                            for k in range(-1, 2):
                                for m in range(-1, 2):
                                    ni, nj = curr_i + k, curr_j + m
                                    
                                    # Verificăm limitele imaginii
                                    if 0 <= ni < h and 0 <= nj < w:
                                        # Dacă vecinul este obiect și neetichetat
                                        if img_bin[ni, nj] == 1 and self.labels[ni, nj] == 0:
                                            self.labels[ni, nj] = label_actual
                                            queue.append((ni, nj))

            self.num_obiecte = label_actual
            self.afisare_rezultat_etichetare(h, w)
            
        except Exception as e:
            self.afiseaza_eroare(str(e))

    def aplicare_etichetare_cu_selectie(self):
        """
        La fel ca aplicare_etichetare, dar apelează afișarea cu posibilitate de selecție.
        """
        try:
            # Setez functia curenta pentru relansare dupa schimbarea pragului
            self.functie_curenta = 'aplicare_etichetare_cu_selectie'
            
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None: return

            h, w = self.cv_img_rgb.shape[:2]
            
            # Calculaza pragul adaptiv (implicit este 127, dar poate fi schimbat)
            prag = self.prag_utilizator if self.prag_utilizator is not None else 127
            img_bin = self.logica_binarizare(prag=prag) 
            
            self.labels = np.zeros((h, w), dtype=int)
            label_actual = 0
            
            for i in range(h):
                for j in range(w):
                    if img_bin[i, j] == 1 and self.labels[i, j] == 0:
                        label_actual += 1
                        queue = [(i, j)]
                        self.labels[i, j] = label_actual
                        
                        while queue:
                            curr_i, curr_j = queue.pop(0)
                            for k in range(-1, 2):
                                for m in range(-1, 2):
                                    ni, nj = curr_i + k, curr_j + m
                                    if 0 <= ni < h and 0 <= nj < w:
                                        if img_bin[ni, nj] == 1 and self.labels[ni, nj] == 0:
                                            self.labels[ni, nj] = label_actual
                                            queue.append((ni, nj))

            self.num_obiecte = label_actual
            # Aici este diferența: apelăm varianta de afișare CU selecție
            self.afisare_rezultat_etichetare_cu_selectie(h, w)
            
        except Exception as e:
            self.afiseaza_eroare(str(e))

    def afisare_rezultat_etichetare(self, h, w):
        """Generează reprezentarea vizuală colorată a obiectelor etichetate (versiune simpla, fara selectie)."""
        import random
        
        # Generăm culori aleatorii pentru fiecare etichetă (ID)
        culori = {0: "#ffffff"} # Fundalul rămâne alb
        for i in range(1, self.num_obiecte + 1):
            r = random.randint(50, 220)
            g = random.randint(50, 220)
            b = random.randint(50, 220)
            culori[i] = f"#{r:02x}{g:02x}{b:02x}"

        self.img_tk_labeled = tk.PhotoImage(width=w, height=h)
        rows = []
        for i in range(h):
            row_colors = [culori[self.labels[i, j]] for j in range(w)]
            rows.append(f"{{{ ' '.join(row_colors) }}}")
        
        self.img_tk_labeled.put(" ".join(rows))

        # Afișare în UI
        self.curata_ecranul()
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(container, text=f"Etichetare finalizată: {self.num_obiecte} obiecte", 
                 font=("Arial", 18, "bold")).pack(pady=10)
        tk.Label(container, image=self.img_tk_labeled).pack()
        
        self.adauga_buton_inapoi()

    def afisare_rezultat_etichetare_cu_selectie(self, h, w):
        """Generează reprezentarea vizuală colorată a obiectelor etichetate cu posibilitate de selecție."""
        import random
        
        # Generăm culori aleatorii pentru fiecare etichetă (ID)
        self.culori_etichete = {0: "#ffffff"} # Fundalul rămâne alb
        for i in range(1, self.num_obiecte + 1):
            r = random.randint(50, 220)
            g = random.randint(50, 220)
            b = random.randint(50, 220)
            self.culori_etichete[i] = f"#{r:02x}{g:02x}{b:02x}"

        self.img_tk_labeled = tk.PhotoImage(width=w, height=h)
        rows = []
        for i in range(h):
            row_colors = [self.culori_etichete[self.labels[i, j]] for j in range(w)]
            rows.append(f"{{{ ' '.join(row_colors) }}}")
        
        self.img_tk_labeled.put(" ".join(rows))

        # Afișare în UI
        self.curata_ecranul()
        self.creeaza_meniu_sus()  # Recreează meniu-ul după curățare
        
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(container, text=f"Etichetare finalizată: {self.num_obiecte} obiecte", 
                 font=("Arial", 18, "bold")).pack(pady=10)
        
        # Stocăm dimensiunile pentru click handler
        self.labeled_h, self.labeled_w = h, w
        
        # Afișare imagine pe Canvas (pentru a putea detecta clicuri)
        canvas_frame = tk.Frame(container)
        canvas_frame.pack(pady=10)
        
        self.canvas_etichete = tk.Canvas(canvas_frame, width=w, height=h, bg="white", bd=2, relief="sunken")
        self.canvas_etichete.create_image(0, 0, image=self.img_tk_labeled, anchor="nw")
        self.canvas_etichete.pack()
        
        # Bind click event pentru selecție
        self.canvas_etichete.bind("<Button-1>", self.selectare_obiect_etichetat)
        
        # Panou informații
        self.info_frame_etichete = tk.Frame(container)
        self.info_frame_etichete.pack(pady=10)
        
        tk.Label(self.info_frame_etichete, text="Faceți clic pe un obiect pentru a vedea statisticile acestuia.", 
                 font=("Arial", 11), fg="gray").pack()
        
        self.adauga_butoane_inapoi_cu_prag()

    def selectare_obiect_etichetat(self, event):
        """Handler pentru clic pe imagine etichetată - selectează și afișează info despre obiect."""
        x, y = event.x, event.y
        
        # Verifică limitele
        if x < 0 or x >= self.labeled_w or y < 0 or y >= self.labeled_h:
            return
        
        # Obține eticheta obiectului pe care s-a făcut clic
        label_clickat = self.labels[y, x]
        
        if label_clickat == 0:
            # S-a făcut clic pe fundal
            self.afiseaza_info_eticheta(None)
            return
        
        # Calculează statistici pentru obiect, INCLUSIV orientarea Sobel
        stats = self.calculeaza_statistici_obiect(label_clickat)
        self.afiseaza_info_eticheta(label_clickat, stats)

    def calculeaza_statistici_obiect(self, label_id):
        """Calculează statistici pentru un obiect etichetat."""
        h, w = self.labeled_h, self.labeled_w
        
        pixeli_obiect = []
        for i in range(h):
            for j in range(w):
                if self.labels[i, j] == label_id:
                    pixeli_obiect.append((j, i))  # (x, y)
        
        if not pixeli_obiect:
            return None
        
        num_pixeli = len(pixeli_obiect)
        
        # Calculează bounding box-ul obiectului
        xs = [p[0] for p in pixeli_obiect]
        ys = [p[1] for p in pixeli_obiect]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        
        # Calculează centroidul
        cx = sum(p[0] for p in pixeli_obiect) / num_pixeli
        cy = sum(p[1] for p in pixeli_obiect) / num_pixeli
        
        # Procentajul obiectului din totalul imaginii
        total_pixeli = h * w
        procent = (num_pixeli / total_pixeli) * 100

        # === APLICARE SOBEL PENTRU DIRECȚIA DE ALUNGIRE ===
        orientare_sobel = self.calculare_orientare_sobel(label_id, x_min, x_max, y_min, y_max)
        
        return {
            'num_pixeli': num_pixeli,
            'x_min': x_min,
            'x_max': x_max,
            'y_min': y_min,
            'y_max': y_max,
            'centroid_x': cx,
            'centroid_y': cy,
            'latime': x_max - x_min + 1,
            'inaltime': y_max - y_min + 1,
            'procent': procent,
            'orientare': orientare_sobel
        }

    def calculare_orientare_sobel(self, label_id, x_min, x_max, y_min, y_max):
        """
        Calculează direcția de alungire a obiectului selectat folosind operatorul Sobel.
        Analizează doar aria din jurul obiectului (bounding box) pentru eficiență.
        """
        import math
        h, w = self.labels.shape
        
        # Extindem marginile cu 1 pixel pentru a permite kernel-ului 3x3 să acționeze complet pe margini
        y_start = max(1, y_min - 1)
        y_end = min(h - 1, y_max + 2)
        x_start = max(1, x_min - 1)
        x_end = min(w - 1, x_max + 2)

        max_mag = -1.0
        orientare_rad = 0.0

        for y in range(y_start, y_end):
            for x in range(x_start, x_end):
                # Mască logică: 1 dacă pixelul curent aparține obiectului selectat, 0 altfel.
                # Aceasta simulează o imagine binară izolată doar cu obiectul nostru.
                p00 = 1 if self.labels[y-1, x-1] == label_id else 0
                p01 = 1 if self.labels[y-1, x] == label_id else 0
                p02 = 1 if self.labels[y-1, x+1] == label_id else 0
                
                p10 = 1 if self.labels[y, x-1] == label_id else 0
                p11 = 1 if self.labels[y, x] == label_id else 0  # Centrul
                p12 = 1 if self.labels[y, x+1] == label_id else 0
                
                p20 = 1 if self.labels[y+1, x-1] == label_id else 0
                p21 = 1 if self.labels[y+1, x] == label_id else 0
                p22 = 1 if self.labels[y+1, x+1] == label_id else 0

                # 1. Aplicăm kernel-ul Gx (Orizontal)
                gx = (-1 * p00) + (0 * p01) + (1 * p02) + \
                     (-2 * p10) + (0 * p11) + (2 * p12) + \
                     (-1 * p20) + (0 * p21) + (1 * p22)

                # 2. Aplicăm kernel-ul Gy (Vertical)
                gy = (-1 * p00) + (-2 * p01) + (-1 * p02) + \
                     (0 * p10)  + (0 * p11)  + (0 * p12)  + \
                     (1 * p20)  + (2 * p21)  + (1 * p22)

                # 3. Calculăm magnitudinea gradientului
                mag = math.sqrt(gx*gx + gy*gy)

                # 4. Actualizăm unghiul doar acolo unde gradientul este MAXIM (adică pe cel mai puternic contur al obiectului)
                if mag > max_mag:
                    max_mag = mag
                    # atan2 returnează unghiul în radiani, în intervalul [-pi, pi]
                    orientare_rad = math.atan2(gy, gx)

        # Returnăm unghiul convertit în grade
        return math.degrees(orientare_rad)

    def afiseaza_info_eticheta(self, label_id, stats=None):
        """Afișează informații despre obiectul selectat (inclusiv direcția Sobel)."""
        # Șterge conținutul anterior
        for widget in self.info_frame_etichete.winfo_children():
            widget.destroy()
        
        if label_id is None:
            tk.Label(self.info_frame_etichete, text="● Ați făcut clic pe fundal (alb).", 
                     font=("Arial", 11), fg="gray").pack()
            return
        
        # Header
        culoare_hex = self.culori_etichete.get(label_id, "#000000")
        tk.Label(self.info_frame_etichete, text=f"● Obiect selectat: Etichetă #{label_id}", 
                 font=("Arial", 12, "bold"), fg="darkblue").pack()
        
        # Indicator de culoare
        color_indicator = tk.Canvas(self.info_frame_etichete, width=20, height=20, bg=culoare_hex, bd=2, relief="sunken")
        color_indicator.pack(pady=5)
        
        if stats:
            # Statistici actualizate cu orientarea Sobel
            stats_text = (
                f"Număr de pixeli: {stats['num_pixeli']}\n"
                f"Centroid: ({stats['centroid_x']:.2f}, {stats['centroid_y']:.2f})\n"
                f"Bounding Box: ({stats['x_min']}, {stats['y_min']}) - ({stats['x_max']}, {stats['y_max']})\n"
                f"Dimensiuni: {stats['latime']} × {stats['inaltime']} pixeli\n"
                f"Procentaj din imagine: {stats['procent']:.2f}%\n\n"
                f"★ Direcția de alungire (Sobel): {stats['orientare']:.2f}°"
            )
            tk.Label(self.info_frame_etichete, text=stats_text, 
                     font=("Arial", 11), justify="left", fg="darkgreen").pack(pady=5)

    def dilatare(self, img_bin, kernel_size=3, iteratii=1):
        """
        Aplica operația de dilatare pe o imagine binară.
        
        Dilatarea expandează obiectele albe (valoare 1).
        Pentru fiecare pixel, dacă VREUN vecin din kernel este 1, pixelul devine 1.
        
        Parametri:
        - img_bin: imagine binară (h, w) cu valori 0 sau 1
        - kernel_size: dimensiunea kernelului (3, 5, 7, etc.) - trebuie să fie impar
        - iteratii: numărul de ori se aplică dilatarea
        
        Returneaza:
        - img_dilated: imagine dilatată cu aceleași dimensiuni
        """
        h, w = img_bin.shape[:2]
        img_out = img_bin.copy()
        offset = kernel_size // 2
        
        for _ in range(iteratii):
            img_temp = np.zeros((h, w), dtype=int)
            
            for y in range(h):
                for x in range(w):
                    # Căutăm dacă vreo vecinătate conține 1
                    has_white = False
                    for dy in range(-offset, offset + 1):
                        for dx in range(-offset, offset + 1):
                            ny, nx = y + dy, x + dx
                            # Verificam daca coordonatele sunt în limita imaginii
                            if 0 <= ny < h and 0 <= nx < w:
                                if img_out[ny, nx] == 1:
                                    has_white = True
                                    break
                        if has_white:
                            break
                    
                    img_temp[y, x] = 1 if has_white else 0
            
            img_out = img_temp
        
        return img_out

    def eroziune(self, img_bin, kernel_size=3, iteratii=1):
        """
        Aplica operația de eroziune pe o imagine binară.
        
        Eroziunea micșorează obiectele albe (valoare 1).
        Pentru fiecare pixel, dacă TOȚI vecinii din kernel sunt 1, pixelul rămâne 1.
        Altfel, pixelul devine 0.
        
        Parametri:
        - img_bin: imagine binară (h, w) cu valori 0 sau 1
        - kernel_size: dimensiunea kernelului (3, 5, 7, etc.) - trebuie să fie impar
        - iteratii: numărul de ori se aplică eroziunea
        
        Returneaza:
        - img_eroded: imagine erodată cu aceleași dimensiuni
        """
        h, w = img_bin.shape[:2]
        img_out = img_bin.copy()
        offset = kernel_size // 2
        
        for _ in range(iteratii):
            img_temp = np.zeros((h, w), dtype=int)
            
            for y in range(h):
                for x in range(w):
                    # Verificam daca TOTI vecinii sunt 1
                    all_white = True
                    for dy in range(-offset, offset + 1):
                        for dx in range(-offset, offset + 1):
                            ny, nx = y + dy, x + dx
                            # Dacă coordonatele sunt în afara imaginii, considerăm ca fond (0)
                            if not (0 <= ny < h and 0 <= nx < w):
                                all_white = False
                                break
                            if img_out[ny, nx] == 0:
                                all_white = False
                                break
                        if not all_white:
                            break
                    
                    img_temp[y, x] = 1 if all_white else 0
            
            img_out = img_temp
        
        return img_out

    def aplicare_dilatare(self):
        """
        Aplica operația de dilatare pe imaginea binarizată din memorie.
        Afișează imaginea originală și versiunile dilatate (1x, 2x, 3x iterații) side-by-side.
        """
        try:
            # Setez functia curenta pentru relansare dupa schimbarea pragului
            self.functie_curenta = 'aplicare_dilatare'
            
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Calculeaza pragul adaptiv (implicit este media imaginii, dar poate fi schimbat)
            prag = self.prag_utilizator if self.prag_utilizator is not None else int(cv_img_rgb.mean())
            
            # Binarizează imaginea
            img_bin = self.logica_binarizare(prag=prag)
            
            # Aplică dilatare cu 1, 2 și 3 iterații
            img_dilat_1 = self.dilatare(img_bin, kernel_size=3, iteratii=1)
            img_dilat_2 = self.dilatare(img_bin, kernel_size=3, iteratii=2)
            img_dilat_3 = self.dilatare(img_bin, kernel_size=3, iteratii=3)
            
            # Cream 4 PhotoImage-uri
            self.img_bin_disp = tk.PhotoImage(width=w, height=h)
            self.img_dilat_1_disp = tk.PhotoImage(width=w, height=h)
            self.img_dilat_2_disp = tk.PhotoImage(width=w, height=h)
            self.img_dilat_3_disp = tk.PhotoImage(width=w, height=h)
            
            # Funcție auxiliară pentru a construi imaginea din matrice binară
            def build_image_from_binary(img_bin_matrix):
                rows = []
                for y in range(h):
                    line = []
                    for x in range(w):
                        if img_bin_matrix[y, x] == 1:
                            line.append("#000000")  # Negru pentru obiect
                        else:
                            line.append("#ffffff")  # Alb pentru fond
                    rows.append(f"{{{ ' '.join(line) }}}")
                return rows
            
            # Construim imaginile
            rows_orig = build_image_from_binary(img_bin)
            rows_dilat_1 = build_image_from_binary(img_dilat_1)
            rows_dilat_2 = build_image_from_binary(img_dilat_2)
            rows_dilat_3 = build_image_from_binary(img_dilat_3)
            
            self.img_bin_disp.put(" ".join(rows_orig))
            self.img_dilat_1_disp.put(" ".join(rows_dilat_1))
            self.img_dilat_2_disp.put(" ".join(rows_dilat_2))
            self.img_dilat_3_disp.put(" ".join(rows_dilat_3))
            
            # AFISARE
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")
            
            tk.Label(container, text="Dilatare (Expandare Obiecte Albe)", font=("Arial", 18, "bold")).pack(pady=10)
            
            row_frame = tk.Frame(container)
            row_frame.pack()
            
            for img, titlu in zip([self.img_bin_disp, self.img_dilat_1_disp, self.img_dilat_2_disp, self.img_dilat_3_disp],
                                  ["Original", "Dilatare 1x", "Dilatare 2x", "Dilatare 3x"]):
                f = tk.Frame(row_frame)
                f.pack(side="left", padx=10)
                tk.Label(f, image=img).pack()
                tk.Label(f, text=titlu, font=("Arial", 10, "bold")).pack(pady=5)
            
            self.adauga_butoane_inapoi_cu_prag()
            
        except Exception as e:
            self.afiseaza_eroare(str(e))

    def aplicare_eroziune(self):
        """
        Aplica operația de eroziune pe imaginea binarizată din memorie.
        Afișează imaginea originală și versiunile erodată (1x, 2x, 3x iterații) side-by-side.
        """
        try:
            # Setez functia curenta pentru relansare dupa schimbarea pragului
            self.functie_curenta = 'aplicare_eroziune'
            
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Calculeaza pragul adaptiv (implicit este media imaginii, dar poate fi schimbat)
            prag = self.prag_utilizator if self.prag_utilizator is not None else int(cv_img_rgb.mean())
            
            # Binarizează imaginea
            img_bin = self.logica_binarizare(prag=prag)
            
            # Aplică eroziune cu 1, 2 și 3 iterații
            img_eroz_1 = self.eroziune(img_bin, kernel_size=3, iteratii=1)
            img_eroz_2 = self.eroziune(img_bin, kernel_size=3, iteratii=2)
            img_eroz_3 = self.eroziune(img_bin, kernel_size=3, iteratii=3)
            
            # Cream 4 PhotoImage-uri
            self.img_bin_disp_e = tk.PhotoImage(width=w, height=h)
            self.img_eroz_1_disp = tk.PhotoImage(width=w, height=h)
            self.img_eroz_2_disp = tk.PhotoImage(width=w, height=h)
            self.img_eroz_3_disp = tk.PhotoImage(width=w, height=h)
            
            # Funcție auxiliară pentru a construi imaginea din matrice binară
            def build_image_from_binary(img_bin_matrix):
                rows = []
                for y in range(h):
                    line = []
                    for x in range(w):
                        if img_bin_matrix[y, x] == 1:
                            line.append("#000000")  # Negru pentru obiect
                        else:
                            line.append("#ffffff")  # Alb pentru fond
                    rows.append(f"{{{ ' '.join(line) }}}")
                return rows
            
            # Construim imaginile
            rows_orig = build_image_from_binary(img_bin)
            rows_eroz_1 = build_image_from_binary(img_eroz_1)
            rows_eroz_2 = build_image_from_binary(img_eroz_2)
            rows_eroz_3 = build_image_from_binary(img_eroz_3)
            
            self.img_bin_disp_e.put(" ".join(rows_orig))
            self.img_eroz_1_disp.put(" ".join(rows_eroz_1))
            self.img_eroz_2_disp.put(" ".join(rows_eroz_2))
            self.img_eroz_3_disp.put(" ".join(rows_eroz_3))
            
            # AFISARE
            self.curata_ecranul()
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")
            
            tk.Label(container, text="Eroziune (Micșorare Obiecte Albe)", font=("Arial", 18, "bold")).pack(pady=10)
            
            row_frame = tk.Frame(container)
            row_frame.pack()
            
            for img, titlu in zip([self.img_bin_disp_e, self.img_eroz_1_disp, self.img_eroz_2_disp, self.img_eroz_3_disp],
                                  ["Original", "Eroziune 1x", "Eroziune 2x", "Eroziune 3x"]):
                f = tk.Frame(row_frame)
                f.pack(side="left", padx=10)
                tk.Label(f, image=img).pack()
                tk.Label(f, text=titlu, font=("Arial", 10, "bold")).pack(pady=5)
            
            self.adauga_butoane_inapoi_cu_prag()
            
        except Exception as e:
            self.afiseaza_eroare(str(e))


# Daca vreo imagien nu este tratata corespunzator, trebuie doar sa setez un prag mai mic, de ex 127.
    def aplicare_dilatare_repetitiva(self):
        """
        Permite utilizatorului să aleagă numărul de iterații pentru dilatare.
        Afișează imaginea originală și versiunea dilatată cu iterații alese.
        """
        try:
            # Setez functia curenta pentru relansare dupa schimbarea pragului
            self.functie_curenta = 'aplicare_dilatare_repetitiva'
            
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Calculeaza pragul adaptiv (implicit este media imaginii, dar poate fi schimbat)
            prag = self.prag_utilizator if self.prag_utilizator is not None else int(cv_img_rgb.mean())
            
            # Binarizează imaginea
            img_bin = self.logica_binarizare(prag=prag)
            
            # Cream interfața pentru alegerea iterațiilor
            self.curata_ecranul()
            
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")
            
            tk.Label(container, text="Dilatare Repetitiva - Alegeți Iterații", font=("Arial", 18, "bold")).pack(pady=20)
            
            # Frame pentru selector
            selector_frame = tk.Frame(container)
            selector_frame.pack(pady=10)
            
            tk.Label(selector_frame, text="Numărul de iterații:", font=("Arial", 12)).pack(side="left", padx=10)
            
            # Spinbox pentru alegerea iterațiilor (1-10)
            iteratii_var = tk.IntVar(value=1)
            spinbox = tk.Spinbox(
                selector_frame,
                from_=1,
                to=10,
                textvariable=iteratii_var,
                font=("Arial", 12),
                width=5
            )
            spinbox.pack(side="left", padx=5)
            
            # Funcția callback pentru a aplica dilatarea
            def aplica_dilatare():
                iteratii = iteratii_var.get()
                
                # Aplică dilatare
                img_dilat = self.dilatare(img_bin, kernel_size=3, iteratii=iteratii)
                
                # Cream PhotoImage-uri
                self.img_bin_rep = tk.PhotoImage(width=w, height=h)
                self.img_dilat_rep = tk.PhotoImage(width=w, height=h)
                
                # Funcție auxiliară
                def build_image_from_binary(img_bin_matrix):
                    rows = []
                    for y in range(h):
                        line = []
                        for x in range(w):
                            if img_bin_matrix[y, x] == 1:
                                line.append("#000000")
                            else:
                                line.append("#ffffff")
                        rows.append(f"{{{ ' '.join(line) }}}")
                    return rows
                
                rows_orig = build_image_from_binary(img_bin)
                rows_dilat = build_image_from_binary(img_dilat)
                
                self.img_bin_rep.put(" ".join(rows_orig))
                self.img_dilat_rep.put(" ".join(rows_dilat))
                
                # AFISARE REZULTATE
                self.curata_ecranul()
                result_container = tk.Frame(self)
                result_container.place(relx=0.5, rely=0.5, anchor="center")
                
                tk.Label(result_container, text=f"Dilatare - {iteratii} Iterații", font=("Arial", 18, "bold")).pack(pady=10)
                
                result_row = tk.Frame(result_container)
                result_row.pack()
                
                # Imaginea originală
                f1 = tk.Frame(result_row)
                f1.pack(side="left", padx=15)
                tk.Label(f1, image=self.img_bin_rep).pack()
                tk.Label(f1, text="Original", font=("Arial", 12, "bold")).pack(pady=5)
                
                # Imaginea dilatată
                f2 = tk.Frame(result_row)
                f2.pack(side="left", padx=15)
                tk.Label(f2, image=self.img_dilat_rep).pack()
                tk.Label(f2, text=f"Dilatare {iteratii}x", font=("Arial", 12, "bold")).pack(pady=5)
                
                self.adauga_butoane_inapoi_cu_prag()
            
            # Buton de aplicare
            buton_aplica = tk.Button(
                container,
                text="Aplica Dilatare",
                font=("Arial", 12, "bold"),
                bg="#4CAF50",
                fg="white",
                padx=20,
                pady=10,
                command=aplica_dilatare
            )
            buton_aplica.pack(pady=20)
            
            self.adauga_buton_inapoi()
            
        except Exception as e:
            self.afiseaza_eroare(str(e))

# Daca vreo imagien nu este tratata corespunzator, trebuie doar sa setez un prag mai mic, de ex 127.
    def aplicare_eroziune_repetitiva(self):
        """
        Permite utilizatorului să aleagă numărul de iterații pentru eroziune.
        Afișează imaginea originală și versiunea erodată cu iterații alese.
        """
        try:
            # Setez functia curenta pentru relansare dupa schimbarea pragului
            self.functie_curenta = 'aplicare_eroziune_repetitiva'
            
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Calculeaza pragul adaptiv (implicit este media imaginii, dar poate fi schimbat)
            prag = self.prag_utilizator if self.prag_utilizator is not None else int(cv_img_rgb.mean())
            
            # Binarizează imaginea
            img_bin = self.logica_binarizare(prag=prag)
            
            # Cream interfața pentru alegerea iterațiilor
            self.curata_ecranul()
            
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")
            
            tk.Label(container, text="Eroziune Repetitiva - Alegeți Iterații", font=("Arial", 18, "bold")).pack(pady=20)
            
            # Frame pentru selector
            selector_frame = tk.Frame(container)
            selector_frame.pack(pady=10)
            
            tk.Label(selector_frame, text="Numărul de iterații:", font=("Arial", 12)).pack(side="left", padx=10)
            
            # Spinbox pentru alegerea iterațiilor (1-10)
            iteratii_var = tk.IntVar(value=1)
            spinbox = tk.Spinbox(
                selector_frame,
                from_=1,
                to=10,
                textvariable=iteratii_var,
                font=("Arial", 12),
                width=5
            )
            spinbox.pack(side="left", padx=5)
            
            # Funcția callback pentru a aplica eroziunea
            def aplica_eroziune():
                iteratii = iteratii_var.get()
                
                # Aplică eroziune
                img_eroz = self.eroziune(img_bin, kernel_size=3, iteratii=iteratii)
                
                # Cream PhotoImage-uri
                self.img_bin_rep_e = tk.PhotoImage(width=w, height=h)
                self.img_eroz_rep = tk.PhotoImage(width=w, height=h)
                
                # Funcție auxiliară
                def build_image_from_binary(img_bin_matrix):
                    rows = []
                    for y in range(h):
                        line = []
                        for x in range(w):
                            if img_bin_matrix[y, x] == 1:
                                line.append("#000000")
                            else:
                                line.append("#ffffff")
                        rows.append(f"{{{ ' '.join(line) }}}")
                    return rows
                
                rows_orig = build_image_from_binary(img_bin)
                rows_eroz = build_image_from_binary(img_eroz)
                
                self.img_bin_rep_e.put(" ".join(rows_orig))
                self.img_eroz_rep.put(" ".join(rows_eroz))
                
                # AFISARE REZULTATE
                self.curata_ecranul()
                result_container = tk.Frame(self)
                result_container.place(relx=0.5, rely=0.5, anchor="center")
                
                tk.Label(result_container, text=f"Eroziune - {iteratii} Iterații", font=("Arial", 18, "bold")).pack(pady=10)
                
                result_row = tk.Frame(result_container)
                result_row.pack()
                
                # Imaginea originală
                f1 = tk.Frame(result_row)
                f1.pack(side="left", padx=15)
                tk.Label(f1, image=self.img_bin_rep_e).pack()
                tk.Label(f1, text="Original", font=("Arial", 12, "bold")).pack(pady=5)
                
                # Imaginea erodată
                f2 = tk.Frame(result_row)
                f2.pack(side="left", padx=15)
                tk.Label(f2, image=self.img_eroz_rep).pack()
                tk.Label(f2, text=f"Eroziune {iteratii}x", font=("Arial", 12, "bold")).pack(pady=5)
                
                self.adauga_butoane_inapoi_cu_prag()
            
            # Buton de aplicare
            buton_aplica = tk.Button(
                container,
                text="Aplica Eroziune",
                font=("Arial", 12, "bold"),
                bg="#FF9800",
                fg="white",
                padx=20,
                pady=10,
                command=aplica_eroziune
            )
            buton_aplica.pack(pady=20)
            
            self.adauga_buton_inapoi()
            
        except Exception as e:
            self.afiseaza_eroare(str(e))

    def aplicare_deschidere(self):
        """
        Deschiderea (Opening) este o operație de eroziune urmată de dilatare.
        Elimină obiecte mici (zgomot) și netezește contururile.
        Permite utilizatorului să aleagă numărul de iterații.
        """
        try:
            # Setez functia curenta pentru relansare dupa schimbarea pragului
            self.functie_curenta = 'aplicare_deschidere'
            
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Calculeaza pragul adaptiv (implicit este media imaginii, dar poate fi schimbat)
            prag = self.prag_utilizator if self.prag_utilizator is not None else int(cv_img_rgb.mean())
            
            # Binarizează imaginea
            img_bin = self.logica_binarizare(prag=prag)
            
            # Cream interfața pentru alegerea iterațiilor
            self.curata_ecranul()
            
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")
            
            tk.Label(container, text="Deschidere - Alegeți Iterații", font=("Arial", 18, "bold")).pack(pady=20)
            
            # Frame pentru selector
            selector_frame = tk.Frame(container)
            selector_frame.pack(pady=10)
            
            tk.Label(selector_frame, text="Numărul de iterații:", font=("Arial", 12)).pack(side="left", padx=10)
            
            # Spinbox pentru alegerea iterațiilor (1-10)
            iteratii_var = tk.IntVar(value=1)
            spinbox = tk.Spinbox(
                selector_frame,
                from_=1,
                to=10,
                textvariable=iteratii_var,
                font=("Arial", 12),
                width=5
            )
            spinbox.pack(side="left", padx=5)
            
            # Funcția callback pentru a aplica deschiderea
            def aplica_deschidere():
                iteratii = iteratii_var.get()
                
                # Aplică eroziune urmată de dilatare (opening)
                img_eroz = self.eroziune(img_bin, kernel_size=3, iteratii=iteratii)
                img_deschidere = self.dilatare(img_eroz, kernel_size=3, iteratii=iteratii)
                
                # Cream PhotoImage-uri
                self.img_bin_deschidere = tk.PhotoImage(width=w, height=h)
                self.img_deschidere_result = tk.PhotoImage(width=w, height=h)
                
                # Funcție auxiliară
                def build_image_from_binary(img_bin_matrix):
                    rows = []
                    for y in range(h):
                        line = []
                        for x in range(w):
                            if img_bin_matrix[y, x] == 1:
                                line.append("#000000")
                            else:
                                line.append("#ffffff")
                        rows.append(f"{{{ ' '.join(line) }}}")
                    return rows
                
                rows_orig = build_image_from_binary(img_bin)
                rows_deschidere = build_image_from_binary(img_deschidere)
                
                self.img_bin_deschidere.put(" ".join(rows_orig))
                self.img_deschidere_result.put(" ".join(rows_deschidere))
                
                # AFISARE REZULTATE
                self.curata_ecranul()
                result_container = tk.Frame(self)
                result_container.place(relx=0.5, rely=0.5, anchor="center")
                
                tk.Label(result_container, text=f"Deschidere (Opening) - {iteratii} Iterații", font=("Arial", 18, "bold")).pack(pady=10)
                
                result_row = tk.Frame(result_container)
                result_row.pack()
                
                # Imaginea originală
                f1 = tk.Frame(result_row)
                f1.pack(side="left", padx=15)
                tk.Label(f1, image=self.img_bin_deschidere).pack()
                tk.Label(f1, text="Original", font=("Arial", 12, "bold")).pack(pady=5)
                
                # Imaginea după deschidere
                f2 = tk.Frame(result_row)
                f2.pack(side="left", padx=15)
                tk.Label(f2, image=self.img_deschidere_result).pack()
                tk.Label(f2, text=f"Deschidere {iteratii}x", font=("Arial", 12, "bold")).pack(pady=5)
                
                self.adauga_butoane_inapoi_cu_prag()
            
            # Buton de aplicare
            buton_aplica = tk.Button(
                container,
                text="Aplica Deschidere",
                font=("Arial", 12, "bold"),
                bg="#9C27B0",
                fg="white",
                padx=20,
                pady=10,
                command=aplica_deschidere
            )
            buton_aplica.pack(pady=20)
            
            self.adauga_buton_inapoi()
            
        except Exception as e:
            self.afiseaza_eroare(str(e))

    def aplicare_inchidere(self):
        """
        Inchiderea (Closing) este o operație de dilatare urmată de eroziune.
        Umple găuri mici în obiecte și netezește contururile.
        Permite utilizatorului să aleagă numărul de iterații.
        """
        try:
            # Setez functia curenta pentru relansare dupa schimbarea pragului
            self.functie_curenta = 'aplicare_inchidere'
            
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Calculeaza pragul adaptiv (implicit este media imaginii, dar poate fi schimbat)
            prag = self.prag_utilizator if self.prag_utilizator is not None else int(cv_img_rgb.mean())
            
            # Binarizează imaginea
            img_bin = self.logica_binarizare(prag=prag)
            
            # Cream interfața pentru alegerea iterațiilor
            self.curata_ecranul()
            
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")
            
            tk.Label(container, text="Inchidere - Alegeți Iterații", font=("Arial", 18, "bold")).pack(pady=20)
            
            # Frame pentru selector
            selector_frame = tk.Frame(container)
            selector_frame.pack(pady=10)
            
            tk.Label(selector_frame, text="Numărul de iterații:", font=("Arial", 12)).pack(side="left", padx=10)
            
            # Spinbox pentru alegerea iterațiilor (1-10)
            iteratii_var = tk.IntVar(value=1)
            spinbox = tk.Spinbox(
                selector_frame,
                from_=1,
                to=10,
                textvariable=iteratii_var,
                font=("Arial", 12),
                width=5
            )
            spinbox.pack(side="left", padx=5)
            
            # Funcția callback pentru a aplica inchiderea
            def aplica_inchidere():
                iteratii = iteratii_var.get()
                
                # Aplică dilatare urmată de eroziune (closing)
                img_dilat = self.dilatare(img_bin, kernel_size=3, iteratii=iteratii)
                img_inchidere = self.eroziune(img_dilat, kernel_size=3, iteratii=iteratii)
                
                # Cream PhotoImage-uri
                self.img_bin_inchidere = tk.PhotoImage(width=w, height=h)
                self.img_inchidere_result = tk.PhotoImage(width=w, height=h)
                
                # Funcție auxiliară
                def build_image_from_binary(img_bin_matrix):
                    rows = []
                    for y in range(h):
                        line = []
                        for x in range(w):
                            if img_bin_matrix[y, x] == 1:
                                line.append("#000000")
                            else:
                                line.append("#ffffff")
                        rows.append(f"{{{ ' '.join(line) }}}")
                    return rows
                
                rows_orig = build_image_from_binary(img_bin)
                rows_inchidere = build_image_from_binary(img_inchidere)
                
                self.img_bin_inchidere.put(" ".join(rows_orig))
                self.img_inchidere_result.put(" ".join(rows_inchidere))
                
                # AFISARE REZULTATE
                self.curata_ecranul()
                result_container = tk.Frame(self)
                result_container.place(relx=0.5, rely=0.5, anchor="center")
                
                tk.Label(result_container, text=f"Inchidere (Closing) - {iteratii} Iterații", font=("Arial", 18, "bold")).pack(pady=10)
                
                result_row = tk.Frame(result_container)
                result_row.pack()
                
                # Imaginea originală
                f1 = tk.Frame(result_row)
                f1.pack(side="left", padx=15)
                tk.Label(f1, image=self.img_bin_inchidere).pack()
                tk.Label(f1, text="Original", font=("Arial", 12, "bold")).pack(pady=5)
                
                # Imaginea după inchidere
                f2 = tk.Frame(result_row)
                f2.pack(side="left", padx=15)
                tk.Label(f2, image=self.img_inchidere_result).pack()
                tk.Label(f2, text=f"Inchidere {iteratii}x", font=("Arial", 12, "bold")).pack(pady=5)
                
                self.adauga_butoane_inapoi_cu_prag()
            
            # Buton de aplicare
            buton_aplica = tk.Button(
                container,
                text="Aplica Inchidere",
                font=("Arial", 12, "bold"),
                bg="#F44336",
                fg="white",
                padx=20,
                pady=10,
                command=aplica_inchidere
            )
            buton_aplica.pack(pady=20)
            
            self.adauga_buton_inapoi()
            
        except Exception as e:
            self.afiseaza_eroare(str(e))

if __name__ == "__main__":
    app = Aplicatie()
    app.mainloop()