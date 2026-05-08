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
        self.state('zoomed')  # Maximizeaza fereastra din start

        # Variabile pentru sistem prag adaptiv
        self.prag_utilizator = None  # Pragul ales de utilizator (None = default)
        self.functie_curenta = None  # Functia care se executa (pentru a o relansa dupa schimbarea pragului)

        # Variabile pentru Transformata Fourier (binarizare + tracking)
        self.fourier_use_binarization = False  # Flag pentru a aplica binarizare inainte de DFT
        self.fourier_inverse_active = False    # Track daca inverse Fourier e activa

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
        # 3. Construim meniul "Tools" cu Submenu-uri
        # ==========================================
        tools_menu = tk.Menu(bara_principala, tearoff=0)
        
        # CONVERSII DE CULORI
        conversii_menu = tk.Menu(tools_menu, tearoff=0)
        conversii_menu.add_command(label="Convertire în Alb-Negru", command=self.aplicare_grayscale_3exemplare)
        conversii_menu.add_command(label="RGB → YUV", command=self.aplicare_conversie_RGB_in_YUV)
        conversii_menu.add_command(label="RGB → YCbCr", command=self.aplicare_conversie_RGB_in_YCbCr)
        conversii_menu.add_command(label="RGB → HSV", command=self.aplicare_conversie_RGB_in_HSV)
        tools_menu.add_cascade(label="Conversii Culori", menu=conversii_menu)
        
        # OPERAȚII DE BAZĂ
        operatii_menu = tk.Menu(tools_menu, tearoff=0)
        operatii_menu.add_command(label="Imagine Inversă (RGB)", command=self.aplicare_inversare_RGB)
        operatii_menu.add_command(label="Binarizare", command=self.aplicare_binarizare)
        tools_menu.add_cascade(label="Operații de Bază", menu=operatii_menu)
        
        # STATISTICĂ
        statistica_menu = tk.Menu(tools_menu, tearoff=0)
        statistica_menu.add_command(label="Histograma Imagine Gri", command=self.afisare_histograma)
        statistica_menu.add_command(label="Egalizare Histograma (Contrast)", command=self.aplicare_egalizare_histograma)
        statistica_menu.add_command(label="Calculare Centru de Masă", command=self.calculare_centru_de_masa)
        statistica_menu.add_separator()
        statistica_menu.add_command(label="SNR (o imagine)", command=self.aplicare_snr_o_imagine)
        statistica_menu.add_command(label="SNR (doua imagini)", command=self.aplicare_snr_doua_imagini_ui)
        tools_menu.add_cascade(label="Statistică", menu=statistica_menu)
        
        # FILTRE
        filtre_menu = tk.Menu(tools_menu, tearoff=0)
        filtre_menu.add_command(label="Filtru de Mediere (3x3)", command=self.aplicare_filtru_mediere)
        filtre_menu.add_command(label="Filtru Median (3x3)", command=self.aplicare_filtru_median)
        filtre_menu.add_command(label="Filtru Minim (3x3)", command=self.aplicare_filtru_minim)
        filtre_menu.add_command(label="Filtru Maxim (3x3)", command=self.aplicare_filtru_maxim)
        filtre_menu.add_command(label="Filtru Accentuare (3x3)", command=self.aplicare_filtru_accentuare)
        filtre_menu.add_command(label="Filtru Laplacian", command=self.aplicare_filtru_laplacian)
        filtre_menu.add_command(label="Dithering Floyd-Steinberg", command=self.aplicare_floyd_steinberg)
        filtre_menu.add_separator()
        filtre_menu.add_command(label="Eliminare Zgomot Gaussian", command=self.aplicare_eliminare_zgomot_gaussian)
        tools_menu.add_cascade(label="Filtre", menu=filtre_menu)
        
        # MORFOLOGIE
        morfologie_menu = tk.Menu(tools_menu, tearoff=0)
        morfologie_menu.add_command(label="Dilatare", command=self.aplicare_dilatare)
        morfologie_menu.add_command(label="Eroziune", command=self.aplicare_eroziune)
        morfologie_menu.add_command(label="Dilatare Repetitivă (Alegere Iterații)", command=self.aplicare_dilatare_repetitiva)
        morfologie_menu.add_command(label="Eroziune Repetitivă (Alegere Iterații)", command=self.aplicare_eroziune_repetitiva)
        morfologie_menu.add_command(label="Deschidere (Eroziune + Dilatare)", command=self.aplicare_deschidere)
        morfologie_menu.add_command(label="Inchidere (Dilatare + Eroziune)", command=self.aplicare_inchidere)
        tools_menu.add_cascade(label="Morfologie", menu=morfologie_menu)
        
        # ANALIZĂ FORME
        analiza_menu = tk.Menu(tools_menu, tearoff=0)
        analiza_menu.add_command(label="Moment de Ordin 1", command=self.calculare_moment_ordin_1)
        analiza_menu.add_command(label="Moment de Ordin 2", command=self.calculare_moment_ordin_2)
        analiza_menu.add_command(label="Matrice de Covarianta", command=self.calculare_matrice_covarianta)
        analiza_menu.add_command(label="Proiectii (Orizontală/Verticală)", command=self.calculare_proiectii)
        tools_menu.add_cascade(label="Analiză Forme", menu=analiza_menu)
        
        # DETECTARE OBIECTE
        detectare_menu = tk.Menu(tools_menu, tearoff=0)
        detectare_menu.add_command(label="Afisare Etichetare Obiecte", command=self.aplicare_etichetare)
        detectare_menu.add_command(label="Afisare Etichetare Obiecte cu Selectie", command=self.aplicare_etichetare_cu_selectie)
        tools_menu.add_cascade(label="Detectare Obiecte", menu=detectare_menu)
        
        # TRANSFORMATE FRECVENȚĂ (FOURIER)
        fourier_menu = tk.Menu(tools_menu, tearoff=0)
        fourier_menu.add_command(label="Transformata Fourier (DFT)", command=self.aplicare_fourier_transform)
        fourier_menu.add_command(label="Transformata Fourier Inversă (IDFT)", command=self.aplicare_inverse_fourier_transform)
        tools_menu.add_cascade(label="Fourier", menu=fourier_menu)

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

    def adauga_butoane_fourier(self, is_inverse=False):
        """
        Adauga butoane pentru Fourier/Inverse Fourier: 'Binarizare' si 'Inapoi'
        
        Args:
            is_inverse: True daca e pe ecranul inverse Fourier
        """
        buton_frame = tk.Frame(self, bg=self.cget("bg"))
        buton_frame.place(relx=0.95, rely=0.95, anchor="se")
        
        # Buton pentru binarizare
        buton_binarizare = tk.Button(
            buton_frame,
            text="Binarizare",
            font=("Arial", 10),
            bg="#FF9800",
            fg="white",
            padx=10,
            pady=5,
            command=lambda: self.toggle_fourier_binarization(is_inverse)
        )
        buton_binarizare.pack(side="left", padx=5, pady=5)
        
        # Buton inapoi
        buton_inapoi = tk.Button(
            buton_frame,
            text="Înapoi",
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            padx=10,
            pady=5,
            command=self.reset_fourier_and_return
        )
        buton_inapoi.pack(side="left", padx=5, pady=5)

    def toggle_fourier_binarization(self, is_inverse=False):
        """Comuta flag-ul binarizarii si recomuta functia Fourier activa"""
        self.fourier_use_binarization = not self.fourier_use_binarization
        
        if is_inverse:
            self.aplicare_inverse_fourier_transform()
        else:
            self.aplicare_fourier_transform()

    def reset_fourier_and_return(self):
        """Reseteaza flag-ul binarizarii si se intoarce la meniu principal"""
        self.fourier_use_binarization = False
        self.fourier_inverse_active = False
        self.ecran_principal()

    def binarizeaza_grayscale(self, pixels_gray, prag=127):
        """
        Binarizeaza o imagine in scala de gri.
        
        Args:
            pixels_gray: matrice 2D cu valori de gri
            prag: pragul de binarizare (default 127)
        
        Returns:
            matrice binarizata (0 sau 255)
        """
        return np.where(pixels_gray >= prag, 255, 0).astype(np.uint8)

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

    def aplicare_transformata_fourier(self):
        """Aplica Transformata Fourier Discreta (DFT)."""
        def logica(img):
            # DFT pe grayscale
            gray = np.mean(img, axis=2)
            magn, _ = self.dft_2d(gray)
            # Normalizam magnitudinea pentru afisare (log scale)
            magn_log = np.log(1 + magn)
            magn_norm = (magn_log / np.max(magn_log) * 255).astype(np.uint8)
            return np.stack([magn_norm]*3, axis=-1)

        self.incarcare_si_procesare_imagine(logica, "Transformata Fourier (Magnitudine)", "Original", "Spectru DFT")

    def aplicare_conversie_RGB_in_YUV(self):
        """Converteste imaginea in spatiul YUV."""
        def logica(img):
            h, w = img.shape[:2]
            yuv = np.zeros_like(img, dtype=np.uint8)
            for y in range(h):
                for x in range(w):
                    r, g, b = img[y, x].astype(float)
                    Y = 0.299 * r + 0.587 * g + 0.114 * b
                    U = -0.147 * r - 0.289 * g + 0.436 * b + 128
                    V = 0.615 * r - 0.515 * g - 0.100 * b + 128
                    yuv[y, x] = [np.clip(Y, 0, 255), np.clip(U, 0, 255), np.clip(V, 0, 255)]
            return yuv
        self.incarcare_si_procesare_imagine(logica, "Conversie RGB -> YUV", "Original", "YUV (Y=R, U=G, V=B)")

    def aplicare_conversie_RGB_in_YCbCr(self):
        """Converteste imaginea in spatiul YCbCr."""
        def logica(img):
            h, w = img.shape[:2]
            ycc = np.zeros_like(img, dtype=np.uint8)
            for y in range(h):
                for x in range(w):
                    r, g, b = img[y, x].astype(float)
                    Y = 16 + (65.481 * r + 128.553 * g + 24.966 * b) / 256
                    Cb = 128 + (-37.797 * r - 74.203 * g + 112.0 * b) / 256
                    Cr = 128 + (112.0 * r - 93.786 * g - 18.214 * b) / 256
                    ycc[y, x] = [np.clip(Y, 0, 255), np.clip(Cb, 0, 255), np.clip(Cr, 0, 255)]
            return ycc
        self.incarcare_si_procesare_imagine(logica, "Conversie RGB -> YCbCr", "Original", "YCbCr")

    # ================================================================================================
    # HELPER FUNCTIONS - Reduce DUPLICARE DE COD in functiile de procesare
    # ================================================================================================

    def verificare_daca_exista_imagine_incarcata(self):
        """
        PATTERN REPETAT: Verifica daca avem imagine in memorie, daca nu, o deschide.
        Aceasta functie se foloseste la inceputul aproape fiecarei functii de procesare.
        
        Returns:
            tuple (h, w) dacă are succes, None dacă utilizator anulează
        """
        if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
            result = self.procesare_imagine()
            if result is None:
                return None
        
        h, w = self.cv_img_rgb.shape[:2]
        return h, w

    def matrice_la_imagine(self, image):
        """
        PATTERN REPETAT: Converteste matrice RGB in PhotoImage (se repeta ~20 de ori!)
        
        Args:
            image: matrice numpy de forma (h, w, 3) cu valori 0-255
        
        Returns:
            tuple (photo_image, width, height) gata pentru afisare
        """
        h, w = image.shape[:2]
        photo = tk.PhotoImage(width=w, height=h)
        
        rows = []
        for y in range(h):
            line = []
            for x in range(w):
                r, g, b = image[y, x]
                line.append(f"#{r:02x}{g:02x}{b:02x}")
            rows.append(f"{{{ ' '.join(line) }}}")
        
        photo.put(" ".join(rows))
        return photo, w, h

    def afisare_rezultat_dublu(self, img_orig, img_procesat, titlu, eticheta_orig="Original", eticheta_proc="Procesat"):
        """
        PATTERN REPETAT: Afiseaza 2 imagini side-by-side (se repeta in ~15 functii!)
        Gestioneaza TOTI pasii: curatare ecran, container, layout, butoane
        
        Args:
            img_orig: matrice originala
            img_procesat: matrice procesata
            titlu: titlul fereastrei (string)
            eticheta_orig: eticheta pentru imagine originala
            eticheta_proc: eticheta pentru imagine procesat
        """
        h, w = img_orig.shape[:2]
        
        # Convertim ambele imagini
        photo_orig, w, h = self.matrice_la_imagine(img_orig)
        photo_proc, _, _ = self.matrice_la_imagine(img_procesat)
        
        # Curatam ecranul
        self.curata_ecranul()
        
        # Cream layout
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Titlu
        tk.Label(container, text=titlu, font=("Arial", 18, "bold")).pack(pady=10)
        
        # Frame imagini side-by-side
        img_frame = tk.Frame(container)
        img_frame.pack(pady=10)
        
        # Imagine originala
        label_orig = tk.Label(img_frame, image=photo_orig)
        label_orig.image = photo_orig  # Pastreaza referinta
        label_orig.pack(side="left", padx=10)
        
        # Imagine procesata
        label_proc = tk.Label(img_frame, image=photo_proc)
        label_proc.image = photo_proc  # Pastreaza referinta
        label_proc.pack(side="left", padx=10)
        
        # Etichete
        tk.Label(container, text=eticheta_orig, font=("Arial", 12), fg="gray").pack()
        tk.Label(container, text=eticheta_proc, font=("Arial", 12), fg="gray").pack()
        
        # Buton inapoi
        self.adauga_buton_inapoi()

    def afisare_rezultat_triplu(self, img1, img2, img3, titlu, etichete):
        """
        PATTERN REPETAT: Afiseaza 3 imagini (folosit in grayscale_3exemplare)
        Gestioneaza layout cu 3 imagini alaturi
        
        Args:
            img1, img2, img3: matricele celor 3 imagini
            titlu: titlul fereastrei
            etichete: lista [eticheta1, eticheta2, eticheta3]
        """
        h, w = img1.shape[:2]
        
        photo1, w, h = self.matrice_la_imagine(img1)
        photo2, _, _ = self.matrice_la_imagine(img2)
        photo3, _, _ = self.matrice_la_imagine(img3)
        
        self.curata_ecranul()
        
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(container, text=titlu, font=("Arial", 18, "bold")).pack(pady=10)
        
        # Frame imagini
        img_frame = tk.Frame(container)
        img_frame.pack(pady=10)
        
        # Afiseaza 3 imagini
        for i, (photo, eticheta) in enumerate([(photo1, etichete[0]), (photo2, etichete[1]), (photo3, etichete[2])]):
            frame_col = tk.Frame(img_frame)
            frame_col.pack(side="left", padx=5)
            
            label = tk.Label(frame_col, image=photo)
            label.image = photo
            label.pack()
            
            tk.Label(frame_col, text=eticheta, font=("Arial", 10), fg="gray").pack()
        
        self.adauga_buton_inapoi()

    def incarcare_si_procesare_imagine(self, functie_procesare, titlu, eticheta_orig="Original", eticheta_proc="Procesat"):
        """
        WRAPPER UNIVERSAL: Combina pasii comuni ai ~15 functii de procesare.
        
        Args:
            functie_procesare: functia care proceseaza imaginea (trebuie sa ia imaginea si sa returneze rezultatul)
            titlu: titlul fereastrei de rezultat
            eticheta_orig: eticheta pentru original
            eticheta_proc: eticheta pentru procesat
        
        Exemplu de utilizare:
            def aplicare_filtru_median_simplificat(self):
                try:
                    self.incarcare_si_procesare_imagine(
                        self.filtru_median,
                        "Filtru Median - Before & After",
                        "Original", 
                        "Filtrat"
                    )
                except Exception as e:
                    self.afiseaza_eroare(str(e))
        """
        dims = self.verificare_daca_exista_imagine_incarcata()
        if dims is None:
            return
        
        try:
            img_procesat = functie_procesare(self.cv_img_rgb)
            self.afisare_rezultat_dublu(self.cv_img_rgb, img_procesat, titlu, eticheta_orig, eticheta_proc)
        except Exception as e:
            self.afiseaza_eroare(str(e))

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
        """Transforma imaginea intr-una strict alb-negru (binara) pe baza unui prag."""
        self.functie_curenta = 'aplicare_binarizare'
        dims = self.verificare_daca_exista_imagine_incarcata()
        if dims is None: return
        h, w = dims

        prag = self.prag_utilizator if self.prag_utilizator is not None else 127
        
        img_bin = np.zeros((h, w, 3), dtype=np.uint8)
        for y in range(h):
            for x in range(w):
                gray = int(np.mean(self.cv_img_rgb[y, x]))
                val = 255 if gray >= prag else 0
                img_bin[y, x] = [val, val, val]

        self.afisare_rezultat_dublu(self.cv_img_rgb, img_bin, 
            f"Binarizare (Prag: {prag})", "Original", "Binarizata")
        self.adauga_butoane_inapoi_cu_prag()


    def calculare_centru_de_masa(self):
        """Calcula centrul de masa si deseneaza un indicator vizual pe acele coordonate."""
        dims = self.verificare_daca_exista_imagine_incarcata()
        if dims is None: return
        h, w = dims
        
        suma_x = suma_y = suma_mase = 0
        for y in range(h):
            for x in range(w):
                masa = np.sum(self.cv_img_rgb[y, x].astype(int))
                suma_x += x * masa
                suma_y += y * masa
                suma_mase += masa

        cx, cy = (int(suma_x / suma_mase), int(suma_y / suma_mase)) if suma_mase > 0 else (w // 2, h // 2)

        img_centru = self.cv_img_rgb.copy()
        # Desenam crucea rosie direct in matrice (pe 40 de pixeli lungime)
        for d in range(-20, 21):
            if 0 <= cx+d < w: img_centru[cy, cx+d] = [255, 0, 0]
            if 0 <= cy+d < h: img_centru[cy+d, cx] = [255, 0, 0]

        self.afisare_rezultat_dublu(self.cv_img_rgb, img_centru, f"Centru de Masa: X={cx}, Y={cy}", "Original", "Centru de Masa")

    # ==========================================
    # LABORATOR 5 – Functii noi
    # ==========================================

    def aplicare_conversie_RGB_in_HSV(self):
        """Converteste imaginea in spatiul HSV si afiseaza canalele."""
        dims = self.verificare_daca_exista_imagine_incarcata()
        if dims is None: return
        h, w = dims

        # 1. Calculam matricile pentru fiecare canal
        img_hsv_comb = np.zeros((h, w, 3), dtype=np.uint8)
        img_h = np.zeros((h, w, 3), dtype=np.uint8)
        img_s = np.zeros((h, w, 3), dtype=np.uint8)
        img_v = np.zeros((h, w, 3), dtype=np.uint8)

        for y in range(h):
            for x in range(w):
                r, g, b = self.cv_img_rgb[y, x] / 255.0
                M, m = max(r, g, b), min(r, g, b)
                C = M - m
                V = M
                S = C / V if V != 0 else 0
                if C == 0: H = 0
                elif M == r: H = 60 * ((g - b) / C % 6)
                elif M == g: H = 60 * ((b - r) / C + 2)
                else: H = 60 * ((r - g) / C + 4)
                
                hn, sn, vn = int(H * 255 / 360), int(S * 255), int(V * 255)
                img_hsv_comb[y, x] = [hn, sn, vn]
                img_h[y, x] = [hn, hn, hn]
                img_s[y, x] = [sn, sn, sn]
                img_v[y, x] = [vn, vn, vn]

        # 2. Afisare
        self.curata_ecranul()
        container = tk.Frame(self); container.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(container, text="Conversie RGB -> HSV", font=("Arial", 18, "bold")).pack(pady=10)
        row = tk.Frame(container); row.pack()
        
        for img, t in zip([img_hsv_comb, img_h, img_s, img_v], ["HSV Combinat", "H (Hue)", "S (Saturation)", "V (Value)"]):
            f = tk.Frame(row); f.pack(side="left", padx=5)
            p, _, _ = self.matrice_la_imagine(img)
            lbl = tk.Label(f, image=p); lbl.image = p; lbl.pack()
            tk.Label(f, text=t, font=("Arial", 10, "bold")).pack()
        self.adauga_buton_inapoi()


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
        """Aplica egalizarea histogramei pe imaginea din memorie."""
        def logica(img):
            # Imaginea originala convertita la grayscale (3 canale identice)
            h, w = img.shape[:2]
            img_gray = np.zeros((h, w, 3), dtype=np.uint8)
            for y in range(h):
                for x in range(w):
                    g = int(np.mean(img[y, x]))
                    img_gray[y, x] = [g, g, g]
            return self.egalizare_histograma(img)

        self.incarcare_si_procesare_imagine(logica, "Egalizare Histograma (Contrast)", "Original (Grayscale)", "Egalizata")

    def calculare_moment_ordin_1(self):
        """Calculeaza momentele de ordin 1 si centroidul."""
        self.functie_curenta = 'calculare_moment_ordin_1'
        dims = self.verificare_daca_exista_imagine_incarcata()
        if dims is None: return
        h, w = dims

        prag = self.prag_utilizator if self.prag_utilizator is not None else 220
        img_bin = self.logica_binarizare(prag=prag)

        M00 = np.sum(img_bin)
        indices = np.where(img_bin == 1)
        M10 = np.sum(indices[1])
        M01 = np.sum(indices[0])

        cx, cy = (M10 / M00, M01 / M00) if M00 > 0 else (w/2, h/2)

        # Generam imaginea binarizata cu indicator (R=G=B pentru binara)
        img_res = np.ones((h, w, 3), dtype=np.uint8) * 255
        img_res[img_bin == 1] = [0, 0, 0]
        
        # Desenam crucea rosie
        for d in range(-20, 21):
            if 0 <= int(cx)+d < w: img_res[int(cy), int(cx)+d] = [255, 0, 0]
            if 0 <= int(cy)+d < h: img_res[int(cy)+d, int(cx)] = [255, 0, 0]

        self.curata_ecranul()
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(container, text=f"Momente Ordin 1 - Centroid: ({cx:.2f}, {cy:.2f})", font=("Arial", 18, "bold")).pack(pady=10)
        
        photo, _, _ = self.matrice_la_imagine(img_res)
        lbl = tk.Label(container, image=photo)
        lbl.image = photo
        lbl.pack(pady=10)
        
        self.adauga_butoane_inapoi_cu_prag()


    def calculare_moment_ordin_2(self):
        """Calculeaza momentele de ordin 2 si orientarea."""
        self.functie_curenta = 'calculare_moment_ordin_2'
        dims = self.verificare_daca_exista_imagine_incarcata()
        if dims is None: return
        h, w = dims

        prag = self.prag_utilizator if self.prag_utilizator is not None else 220
        img_bin = self.logica_binarizare(prag=prag)

        M00 = np.sum(img_bin)
        if M00 == 0: return self.afiseaza_eroare("Nu s-au gasit obiecte pentru calcul.")
        
        indices = np.where(img_bin == 1)
        cx, cy = np.mean(indices[1]), np.mean(indices[0])

        mu20 = np.sum((indices[1] - cx)**2)
        mu02 = np.sum((indices[0] - cy)**2)
        mu11 = np.sum((indices[1] - cx) * (indices[0] - cy))

        theta = 0.5 * math.atan2(2 * mu11, mu20 - mu02)
        theta_deg = math.degrees(theta)

        img_res = np.ones((h, w, 3), dtype=np.uint8) * 255
        img_res[img_bin == 1] = [0, 0, 0]
        
        # Desenam axa principala (verde)
        length = min(w, h) // 3
        for r in range(-length, length):
            px = int(cx + r * math.cos(theta))
            py = int(cy + r * math.sin(theta))
            if 0 <= px < w and 0 <= py < h: img_res[py, px] = [0, 255, 0]

        self.curata_ecranul()
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(container, text=f"Orientare: {theta_deg:.2f}°", font=("Arial", 18, "bold")).pack(pady=10)
        
        photo, _, _ = self.matrice_la_imagine(img_res)
        lbl = tk.Label(container, image=photo); lbl.image = photo; lbl.pack()
        self.adauga_butoane_inapoi_cu_prag()


    def calculare_matrice_covarianta(self):
        """Calculeaza matricea de covarianta a unei imagini binarizate."""
        self.functie_curenta = 'calculare_matrice_covarianta'
        dims = self.verificare_daca_exista_imagine_incarcata()
        if dims is None: return
        h, w = dims

        prag = self.prag_utilizator if self.prag_utilizator is not None else 220
        img_bin = self.logica_binarizare(prag=prag)

        M00 = np.sum(img_bin)
        if M00 == 0: return self.afiseaza_eroare("Nu s-au gasit obiecte.")
        
        indices = np.where(img_bin == 1)
        cx, cy = np.mean(indices[1]), np.mean(indices[0])

        mu20 = np.sum((indices[1] - cx)**2)
        mu02 = np.sum((indices[0] - cy)**2)
        mu11 = np.sum((indices[1] - cx) * (indices[0] - cy))

        cov_xx, cov_yy, cov_xy = mu20/M00, mu02/M00, mu11/M00
        trace = cov_xx + cov_yy
        det = cov_xx * cov_yy - cov_xy**2
        lambda1 = trace/2 + math.sqrt(max(0, trace**2/4 - det))
        lambda2 = trace/2 - math.sqrt(max(0, trace**2/4 - det))

        self.curata_ecranul()
        container = tk.Frame(self); container.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(container, text="Matricea de Covarianta", font=("Arial", 18, "bold")).pack(pady=10)
        tk.Label(container, text=f"λ1 = {lambda1:.2f}, λ2 = {lambda2:.2f}", font=("Arial", 14), fg="darkgreen").pack()
        
        m_frame = tk.Frame(container, bd=2, relief="ridge", padx=20, pady=10); m_frame.pack(pady=10)
        tk.Label(m_frame, text=f"| {cov_xx:12.2f}  {cov_xy:12.2f} |", font=("Courier", 14)).pack()
        tk.Label(m_frame, text=f"| {cov_xy:12.2f}  {cov_yy:12.2f} |", font=("Courier", 14)).pack()

        self.adauga_butoane_inapoi_cu_prag()


    def calculare_proiectii(self):
        """Calculeaza si afiseaza proiectiile orizontala si verticala."""
        dims = self.verificare_daca_exista_imagine_incarcata()
        if dims is None: return
        h, w = dims

        img_gray = np.mean(self.cv_img_rgb, axis=2)
        proj_h = np.sum(img_gray, axis=1)
        proj_v = np.sum(img_gray, axis=0)

        self.curata_ecranul()
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(container, text="Proiectii Orizontala si Verticala", font=("Arial", 18, "bold")).pack(pady=10)

        main_frame = tk.Frame(container); main_frame.pack()
        
        # Imaginea in grayscale
        img_gray_3ch = np.stack([img_gray]*3, axis=-1).astype(np.uint8)
        photo, _, _ = self.matrice_la_imagine(img_gray_3ch)
        tk.Label(main_frame, image=photo).grid(row=0, column=0, padx=5, pady=5)
        self.img_proj = photo # Referinta

        # Canvas-uri pentru proiectii
        ph_w, pv_h = 200, 150
        c_h = tk.Canvas(main_frame, width=ph_w, height=h, bg="white", bd=1, relief="sunken")
        c_h.grid(row=0, column=1, padx=5, pady=5)
        max_h = np.max(proj_h) if np.max(proj_h) > 0 else 1
        for y, val in enumerate(proj_h):
            c_h.create_line(0, y, (val/max_h)*ph_w, y, fill="#4444ff")

        c_v = tk.Canvas(main_frame, width=w, height=pv_h, bg="white", bd=1, relief="sunken")
        c_v.grid(row=1, column=0, padx=5, pady=5)
        max_v = np.max(proj_v) if np.max(proj_v) > 0 else 1
        for x, val in enumerate(proj_v):
            c_v.create_line(x, pv_h, x, pv_h - (val/max_v)*pv_h, fill="#44aa44")

        self.adauga_buton_inapoi()


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
        """Aplica operația de dilatare pe imaginea binarizată."""
        self.functie_curenta = 'aplicare_dilatare'
        dims = self.verificare_daca_exista_imagine_incarcata()
        if dims is None: return
        h, w = dims
        
        prag = self.prag_utilizator if self.prag_utilizator is not None else int(self.cv_img_rgb.mean())
        img_bin = self.logica_binarizare(prag=prag)
        
        # Aplică dilatare cu 1, 2 și 3 iterații
        imgs = [img_bin]
        for i in range(1, 4):
            imgs.append(self.dilatare(img_bin, kernel_size=3, iteratii=i))
            
        titluri = ["Original", "Dilatare 1x", "Dilatare 2x", "Dilatare 3x"]
        photos = []
        for img in imgs:
            # Convertim matricea 0/1 în RGB pentru afișare
            img_rgb = np.ones((h, w, 3), dtype=np.uint8) * 255
            img_rgb[img == 1] = [0, 0, 0]
            p, _, _ = self.matrice_la_imagine(img_rgb)
            photos.append(p)
            
        self.curata_ecranul()
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(container, text="Dilatare (Expandare Obiecte)", font=("Arial", 18, "bold")).pack(pady=10)
        
        row_frame = tk.Frame(container); row_frame.pack()
        for p, t in zip(photos, titluri):
            f = tk.Frame(row_frame); f.pack(side="left", padx=10)
            lbl = tk.Label(f, image=p); lbl.image = p; lbl.pack()
            tk.Label(f, text=t, font=("Arial", 10, "bold")).pack(pady=5)
            
        self.adauga_butoane_inapoi_cu_prag()


    def aplicare_eroziune(self):
        """Aplica operația de eroziune pe imaginea binarizată."""
        self.functie_curenta = 'aplicare_eroziune'
        dims = self.verificare_daca_exista_imagine_incarcata()
        if dims is None: return
        h, w = dims
        
        prag = self.prag_utilizator if self.prag_utilizator is not None else int(self.cv_img_rgb.mean())
        img_bin = self.logica_binarizare(prag=prag)
        
        imgs = [img_bin]
        for i in range(1, 4):
            imgs.append(self.eroziune(img_bin, kernel_size=3, iteratii=i))
            
        titluri = ["Original", "Eroziune 1x", "Eroziune 2x", "Eroziune 3x"]
        photos = []
        for img in imgs:
            img_rgb = np.ones((h, w, 3), dtype=np.uint8) * 255
            img_rgb[img == 1] = [0, 0, 0]
            p, _, _ = self.matrice_la_imagine(img_rgb)
            photos.append(p)
            
        self.curata_ecranul()
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(container, text="Eroziune (Micșorare Obiecte)", font=("Arial", 18, "bold")).pack(pady=10)
        
        row_frame = tk.Frame(container); row_frame.pack()
        for p, t in zip(photos, titluri):
            f = tk.Frame(row_frame); f.pack(side="left", padx=10)
            lbl = tk.Label(f, image=p); lbl.image = p; lbl.pack()
            tk.Label(f, text=t, font=("Arial", 10, "bold")).pack(pady=5)
            
        self.adauga_butoane_inapoi_cu_prag()



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

    def aplicare_fourier_transform(self):
        """
        Aplica Transformata Fourier Discreta (DFT) pe imaginea curenta si afiseaza:
        1. Imaginea originala (grayscale) - opțional binarizata
        2. Imaginea reconstruita din IDFT
        3. Spectrul de frecvente (magnitudinea)
        """
        try:
            # Verificam daca avem o imagine in memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return
            
            self.fourier_inverse_active = False  # Marcheaza ca nu e inverse
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Convertim imaginea in scala de gri
            pixels_gray = np.zeros((h, w))
            for y in range(h):
                for x in range(w):
                    r, g, b = cv_img_rgb[y, x].astype(float)
                    # Folosim formula Luma pentru conversie in scala de gri
                    gray = 0.299 * r + 0.587 * g + 0.114 * b
                    pixels_gray[y, x] = gray
            
            # APLICAM BINARIZARE DACA FLAG-UL ESTE ACTIVAT
            if self.fourier_use_binarization:
                pixels_gray = self.binarizeaza_grayscale(pixels_gray)
            
            # Aplicam Transformata Fourier Discreta (DFT) pe intreaga imagine 2D
            dft = self.discrete_fourier_transform_2d(pixels_gray)
            
            # Aplicam Transformata Fourier Inversa (IDFT) pentru a reconstrui imaginea
            reconstructed = self.inverse_discrete_fourier_transform_2d(dft)
            
            # Cream imaginea magnitudinii spectrului de frecvente
            magnitude_image = self.create_magnitude_image(dft, h, w)
            
            # Cream PhotoImage din imaginea originala (grayscale)
            self.img_fourier_original = tk.PhotoImage(width=w, height=h)
            rows_original = []
            for y in range(h):
                line = []
                for x in range(w):
                    color_val = int(pixels_gray[y, x]) % 256
                    line.append(f"#{color_val:02x}{color_val:02x}{color_val:02x}")
                rows_original.append(f"{{{ ' '.join(line) }}}")
            self.img_fourier_original.put(" ".join(rows_original))
            
            # Cream PhotoImage din imaginea reconstruita
            self.img_fourier_reconstructed = tk.PhotoImage(width=w, height=h)
            rows_reconstructed = []
            for y in range(h):
                line = []
                for x in range(w):
                    color_val = int(np.clip(reconstructed[y, x], 0, 255))
                    line.append(f"#{color_val:02x}{color_val:02x}{color_val:02x}")
                rows_reconstructed.append(f"{{{ ' '.join(line) }}}")
            self.img_fourier_reconstructed.put(" ".join(rows_reconstructed))
            
            # Cream PhotoImage din imaginea magnitudinii
            self.img_fourier_spectrum = tk.PhotoImage(width=w, height=h)
            rows_spectrum = []
            for y in range(h):
                line = []
                for x in range(w):
                    color_val = magnitude_image[y, x]
                    line.append(f"#{color_val:02x}{color_val:02x}{color_val:02x}")
                rows_spectrum.append(f"{{{ ' '.join(line) }}}")
            self.img_fourier_spectrum.put(" ".join(rows_spectrum))
            
            # AFISARE REZULTATE (3 imagini)
            self.curata_ecranul()
            
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")
            
            # Titlu cu indicare daca e binarizata
            titlu_text = "Transformata Fourier (DFT -> IDFT)"
            if self.fourier_use_binarization:
                titlu_text += " - BINARIZATA"
            tk.Label(container, text=titlu_text, font=("Arial", 18, "bold")).pack(pady=10)
            
            # Containerul orizontal pentru cele 3 imagini
            row_frame = tk.Frame(container)
            row_frame.pack()
            
            # Afisam cele 3 imagini
            for img, titlu in zip([self.img_fourier_original, self.img_fourier_reconstructed, self.img_fourier_spectrum], 
                                  ["Original (Grayscale)", "Reconstruita (IDFT)", "Spectru de Frecvente"]):
                f = tk.Frame(row_frame)
                f.pack(side="left", padx=10)
                tk.Label(f, image=img).pack()
                tk.Label(f, text=titlu, font=("Arial", 11, "bold")).pack()
            
            info_text = f"Dimensiuni: {w}x{h} px"
            tk.Label(container, text=info_text, font=("Arial", 12), fg="gray").pack(pady=5)
            
            self.adauga_butoane_fourier(is_inverse=False)
            
        except Exception as e:
            self.afiseaza_eroare(str(e))
    
    def discrete_fourier_transform_2d(self, pixels):
        """
        Calculeaza Transformata Fourier Discreta (DFT) in 2D pe o matrice de pixeli.
        Utilizeaza separabilitatea DFT: aplica FFT pe fiecare linie, apoi pe fiecare coloana.
        
        Echivalent cu codul Java:
        - for (int y = 0; y < height; y++) { Complex[] row = transformer.transform(...); }
        - for (int x = 0; x < width; x++) { Complex[] column = transformer.transform(...); }
        
        Args:
            pixels: matrice bidimensionala de pixeli in scala de gri
        
        Returns:
            matrice bidimensionala de numere complexe reprezentand transformata Fourier
        """
        h, w = pixels.shape
        
        # Pas 1: Aplicam FFT pe fiecare linie - echivalent cu DFT.transform(input[y])
        dft_rows = np.zeros((h, w), dtype=complex)
        for y in range(h):
            dft_rows[y, :] = np.fft.fft(pixels[y, :])
        
        # Pas 2: Aplicam FFT pe fiecare coloana a rezultatului anterior - echivalent cu DFT.transform(getColumn(...))
        dft_2d = np.zeros((h, w), dtype=complex)
        for x in range(w):
            dft_2d[:, x] = np.fft.fft(dft_rows[:, x])
        
        return dft_2d
    
    def inverse_discrete_fourier_transform_2d(self, dft):
        """
        Calculeaza Transformata Fourier Inversa (IDFT) in 2D pe transformata Fourier.
        Utilizeaza separabilitatea IDFT: aplica IFFT pe fiecare linie, apoi pe fiecare coloana.
        Echivalent cu DFT inversa dar normalizata.
        
        Echivalent cu codul Java (IDFT):
        - for (int y = 0; y < height; y++) { Complex[] row = transformer.inverseTransform(...); }
        - for (int x = 0; x < width; x++) { Complex[] column = transformer.inverseTransform(...); }
        
        Args:
            dft: matrice bidimensionala de numere complexe (transformata Fourier)
        
        Returns:
            matrice bidimensionala de pixeli reconstruiti (0-255) in scala de gri
        """
        h, w = dft.shape
        
        # Pas 1: Aplicam IFFT pe fiecare linie
        idft_rows = np.zeros((h, w), dtype=complex)
        for y in range(h):
            idft_rows[y, :] = np.fft.ifft(dft[y, :])
        
        # Pas 2: Aplicam IFFT pe fiecare coloana a rezultatului anterior
        idft_2d = np.zeros((h, w), dtype=complex)
        for x in range(w):
            idft_2d[:, x] = np.fft.ifft(idft_rows[:, x])
        
        # Luam doar partea reala si normalizare la 0-255
        reconstructed = np.real(idft_2d)
        reconstructed = np.clip(reconstructed, 0, 255)
        
        return reconstructed
    
    def create_magnitude_image(self, dft, height, width):
        """
        Creeaza o imagine a spectrului de frecvente din transformata Fourier.
        Calculeaza magnitudinea fiecarui element complex si o normalizeaza pentru afisare.
        
        Echivalent cu codul Java:
        - double magnitude = dft[x][y].abs();
        - int color = (int) (255 * magnitude / maxMagnitude);
        
        Args:
            dft: matrice bidimensionala de numere complexe (transformata Fourier)
            height: inaltimea imaginii
            width: latimea imaginii
        
        Returns:
            matrice de pixeli (0-255) reprezentand magnitudinea spectrului
        """
        # Calculam magnitudinea (modulul) fiecarui element complex
        magnitude = np.abs(dft)
        
        # Centram spectrul de frecvente (low frequencies in centru) - mai vizibil
        magnitude_shifted = np.fft.fftshift(magnitude)
        
        # Aplicam logaritmul pentru a face spectrul mai vizibil
        # (high frequencies devine mai vizibil, low frequencies nu domina imaginea)
        magnitude_log = np.log1p(magnitude_shifted)
        
        # Normalizare intre 0 si 255 pentru afisare
        max_log = np.max(magnitude_log)
        if max_log == 0:
            max_log = 1
        
        magnitude_normalized = ((magnitude_log / max_log) * 255).astype(np.uint8)
        
        return magnitude_normalized
    
    def aplicare_inverse_fourier_transform(self):
        """
        Aplica Transformata Fourier Discreta (DFT) pe imaginea curenta, apoi Transformata Inversa (IDFT)
        si afiseaza cele 3 etape:
        1. Imaginea originala (grayscale) - opțional binarizata
        2. Imaginea reconstruita din IDFT
        3. Spectrul de frecvente (magnitudinea)
        
        Demonstreaza ca DFT -> IDFT recupereaza imaginea originala.
        """
        try:
            # Verificam daca avem o imagine in memorie
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return
            
            self.fourier_inverse_active = True  # Marcheaza ca e inverse
            
            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]
            
            # Convertim imaginea in scala de gri
            pixels_gray = np.zeros((h, w))
            for y in range(h):
                for x in range(w):
                    r, g, b = cv_img_rgb[y, x].astype(float)
                    # Folosim formula Luma pentru conversie in scala de gri
                    gray = 0.299 * r + 0.587 * g + 0.114 * b
                    pixels_gray[y, x] = gray
            
            # APLICAM BINARIZARE DACA FLAG-UL ESTE ACTIVAT
            if self.fourier_use_binarization:
                pixels_gray = self.binarizeaza_grayscale(pixels_gray)
            
            # Aplicam Transformata Fourier Discreta (DFT) pe intreaga imagine 2D
            dft = self.discrete_fourier_transform_2d(pixels_gray)
            
            # Aplicam Transformata Fourier Inversa (IDFT) pentru a reconstrui imaginea
            reconstructed = self.inverse_discrete_fourier_transform_2d(dft)
            
            # Cream imaginea magnitudinii spectrului de frecvente
            magnitude_image = self.create_magnitude_image(dft, h, w)
            
            # Cream PhotoImage din imaginea originala (grayscale)
            self.img_inverse_original = tk.PhotoImage(width=w, height=h)
            rows_original = []
            for y in range(h):
                line = []
                for x in range(w):
                    color_val = int(pixels_gray[y, x]) % 256
                    line.append(f"#{color_val:02x}{color_val:02x}{color_val:02x}")
                rows_original.append(f"{{{ ' '.join(line) }}}")
            self.img_inverse_original.put(" ".join(rows_original))
            
            # Cream PhotoImage din imaginea reconstruita
            self.img_inverse_reconstructed = tk.PhotoImage(width=w, height=h)
            rows_reconstructed = []
            for y in range(h):
                line = []
                for x in range(w):
                    color_val = int(np.clip(reconstructed[y, x], 0, 255))
                    line.append(f"#{color_val:02x}{color_val:02x}{color_val:02x}")
                rows_reconstructed.append(f"{{{ ' '.join(line) }}}")
            self.img_inverse_reconstructed.put(" ".join(rows_reconstructed))
            
            # Cream PhotoImage din imaginea magnitudinii
            self.img_inverse_spectrum = tk.PhotoImage(width=w, height=h)
            rows_spectrum = []
            for y in range(h):
                line = []
                for x in range(w):
                    color_val = magnitude_image[y, x]
                    line.append(f"#{color_val:02x}{color_val:02x}{color_val:02x}")
                rows_spectrum.append(f"{{{ ' '.join(line) }}}")
            self.img_inverse_spectrum.put(" ".join(rows_spectrum))
            
            # AFISARE REZULTATE (3 imagini)
            self.curata_ecranul()
            
            container = tk.Frame(self)
            container.place(relx=0.5, rely=0.5, anchor="center")
            
            # Titlu cu indicare daca e binarizata
            titlu_text = "Transformata Fourier Inversa (IDFT -> Reconstituire)"
            if self.fourier_use_binarization:
                titlu_text += " - BINARIZATA"
            tk.Label(container, text=titlu_text, font=("Arial", 18, "bold")).pack(pady=10)
            
            # Containerul orizontal pentru cele 3 imagini
            row_frame = tk.Frame(container)
            row_frame.pack()
            
            # Afisam cele 3 imagini
            for img, titlu in zip([self.img_inverse_original, self.img_inverse_reconstructed, self.img_inverse_spectrum], 
                                  ["Original (Grayscale)", "Reconstruita (IDFT)", "Spectru de Frecvente"]):
                f = tk.Frame(row_frame)
                f.pack(side="left", padx=10)
                tk.Label(f, image=img).pack()
                tk.Label(f, text=titlu, font=("Arial", 11, "bold")).pack()
            
            info_text = f"Dimensiuni: {w}x{h} px"
            tk.Label(container, text=info_text, font=("Arial", 12), fg="gray").pack(pady=5)
            
            self.adauga_butoane_fourier(is_inverse=True)
            
        except Exception as e:
            self.afiseaza_eroare(str(e))
    
    def aplicare_filtru_mediere(self):
        """Aplica filtru de mediere (averaging filter) cu kernel 3x3."""
        self.incarcare_si_procesare_imagine(self.filtru_mediere, "Filtru de Mediere (3x3)", "Original", "Filtrat")

    
    def filtru_mediere(self, image):
        """
        Aplica filtrul de mediere cu kernel 3x3.
        Fiecare pixel este inlocuit cu media ponderata a pixelilor din vecinatate.
        
        Args:
            image: imaginea de intrare (RGB)
        
        Returns:
            imaginea filtrata
        """
        h, w = image.shape[:2]
        result = np.zeros_like(image)
        
        # Kernel de mediere 3x3 - toti coeficientii sunt 1/9
        kernel = np.array([[1/9, 1/9, 1/9],
                          [1/9, 1/9, 1/9],
                          [1/9, 1/9, 1/9]])
        
        # Parcurgem pixelii cu padding (ignoram marginile)
        for i in range(1, w - 1):
            for j in range(1, h - 1):
                # Extraem fereastra 3x3 in jurul pixelului curent
                window = image[j-1:j+2, i-1:i+2]
                
                # Calculam suma ponderata pentru fiecare canal
                r_sum = np.sum(window[:, :, 0] * kernel)
                g_sum = np.sum(window[:, :, 1] * kernel)
                b_sum = np.sum(window[:, :, 2] * kernel)
                
                # Setam pixelul in imagine rezultata
                result[j, i, 0] = np.clip(r_sum, 0, 255).astype(np.uint8)
                result[j, i, 1] = np.clip(g_sum, 0, 255).astype(np.uint8)
                result[j, i, 2] = np.clip(b_sum, 0, 255).astype(np.uint8)
        
        # Copiem marginile din imaginea originala (nu le procesam)
        result[0, :] = image[0, :]
        result[-1, :] = image[-1, :]
        result[:, 0] = image[:, 0]
        result[:, -1] = image[:, -1]
        
        return result
    
    def aplicare_filtru_median(self):
        """Aplica filtru median cu kernel 3x3."""
        self.incarcare_si_procesare_imagine(self.filtru_median, "Filtru Median (3x3)", "Original", "Filtrat")

    
    def filtru_median(self, image):
        """
        Aplica filtrul median cu kernel 3x3.
        Fiecare pixel este inlocuit cu mediana pixelilor din vecinatate.
        Excelent pentru eliminarea zgomotului salt-and-pepper.
        
        Args:
            image: imaginea de intrare (RGB)
        
        Returns:
            imaginea filtrata
        """
        h, w = image.shape[:2]
        result = np.zeros_like(image)
        
        # Parcurgem pixelii cu padding (ignoram marginile)
        for i in range(1, w - 1):
            for j in range(1, h - 1):
                # Extraem fereastra 3x3 in jurul pixelului curent
                window = image[j-1:j+2, i-1:i+2]
                
                # Calculam mediana pentru fiecare canal (R, G, B)
                r_median = np.median(window[:, :, 0])
                g_median = np.median(window[:, :, 1])
                b_median = np.median(window[:, :, 2])
                
                # Setam pixelul in imagine rezultata
                result[j, i, 0] = np.uint8(r_median)
                result[j, i, 1] = np.uint8(g_median)
                result[j, i, 2] = np.uint8(b_median)
        
        # Copiem marginile din imaginea originala (nu le procesam)
        result[0, :] = image[0, :]
        result[-1, :] = image[-1, :]
        result[:, 0] = image[:, 0]
        result[:, -1] = image[:, -1]
        
        return result
    
    def aplicare_filtru_minim(self):
        """Aplica filtru de minim cu kernel 3x3."""
        self.incarcare_si_procesare_imagine(self.filtru_minim, "Filtru de Minim (3x3)", "Original", "Filtrat")

    
    def filtru_minim(self, image):
        """
        Aplica filtrul de minim cu kernel 3x3.
        Fiecare pixel este inlocuit cu valoarea minima din vecinatate.
        Acesta este un filtru de eroziune ce face ca obiectele negre sa se extinda.
        
        Args:
            image: imaginea de intrare (RGB)
        
        Returns:
            imaginea filtrata
        """
        h, w = image.shape[:2]
        result = np.zeros_like(image)
        
        # Parcurgem pixelii cu padding (ignoram marginile)
        for i in range(1, w - 1):
            for j in range(1, h - 1):
                # Extraem fereastra 3x3 in jurul pixelului curent
                window = image[j-1:j+2, i-1:i+2]
                
                # Calculam valoarea minima pentru fiecare canal (R, G, B)
                r_min = np.min(window[:, :, 0])
                g_min = np.min(window[:, :, 1])
                b_min = np.min(window[:, :, 2])
                
                # Setam pixelul in imagine rezultata
                result[j, i, 0] = np.uint8(r_min)
                result[j, i, 1] = np.uint8(g_min)
                result[j, i, 2] = np.uint8(b_min)
        
        # Copiem marginile din imaginea originala (nu le procesam)
        result[0, :] = image[0, :]
        result[-1, :] = image[-1, :]
        result[:, 0] = image[:, 0]
        result[:, -1] = image[:, -1]
        
        return result
    
    def aplicare_filtru_maxim(self):
        """Aplica filtru de maxim cu kernel 3x3."""
        self.incarcare_si_procesare_imagine(self.filtru_maxim, "Filtru de Maxim (3x3)", "Original", "Filtrat")

    
    def filtru_maxim(self, image):
        """
        Aplica filtrul de maxim cu kernel 3x3.
        Fiecare pixel este inlocuit cu valoarea maxima din vecinatate.
        Acesta este un filtru de dilatare ce face ca obiectele luminoase sa se extinda.
        
        Args:
            image: imaginea de intrare (RGB)
        
        Returns:
            imaginea filtrata
        """
        h, w = image.shape[:2]
        result = np.zeros_like(image)
        
        # Parcurgem pixelii cu padding (ignoram marginile)
        for i in range(1, w - 1):
            for j in range(1, h - 1):
                # Extraem fereastra 3x3 in jurul pixelului curent
                window = image[j-1:j+2, i-1:i+2]
                
                # Calculam valoarea maxima pentru fiecare canal (R, G, B)
                r_max = np.max(window[:, :, 0])
                g_max = np.max(window[:, :, 1])
                b_max = np.max(window[:, :, 2])
                
                # Setam pixelul in imagine rezultata
                result[j, i, 0] = np.uint8(r_max)
                result[j, i, 1] = np.uint8(g_max)
                result[j, i, 2] = np.uint8(b_max)
        
        # Copiem marginile din imaginea originala (nu le procesam)
        result[0, :] = image[0, :]
        result[-1, :] = image[-1, :]
        result[:, 0] = image[:, 0]
        result[:, -1] = image[:, -1]
        
        return result
    
    def aplicare_filtru_accentuare(self):
        """Aplica filtru de accentuare cu kernel 3x3."""
        self.incarcare_si_procesare_imagine(self.filtru_accentuare, "Filtru de Accentuare (3x3)", "Original", "Filtrat")

    
    def filtru_accentuare(self, image):
        """
        Aplica filtrul de accentuare cu kernel 3x3.
        Fiecare pixel este inlocuit cu: pixel_original + 0.6 * suma_ponderata_vecini
        
        Kernel-ul folosit:
            [0    -1/4   0  ]
            [-1/4  1    -1/4]
            [0    -1/4   0  ]
        
        Args:
            image: imaginea de intrare (RGB)
        
        Returns:
            imaginea filtrata accentuata
        """
        h, w = image.shape[:2]
        result = np.zeros_like(image, dtype=np.float64)
        
        # Kernel-ul de accentuare
        kernel = np.array([[0,    -1/4,  0   ],
                          [-1/4,   1,   -1/4],
                          [0,    -1/4,  0   ]])
        
        # Parcurgem pixelii cu padding (ignoram marginile)
        for i in range(1, w - 1):
            for j in range(1, h - 1):
                # Extraem fereastra 3x3 in jurul pixelului curent
                window = image[j-1:j+2, i-1:i+2].astype(np.float64)
                
                # Calculam suma ponderata pentru fiecare canal
                for c in range(3):  # R, G, B
                    # Suma ponderata = kernel * window_canal
                    suma = np.sum(kernel * window[:, :, c])
                    
                    # Pixelul original din centrul ferestrei
                    pixel_orig = image[j, i, c]
                    
                    # Aplicam formula: pixel_nou = pixel_orig + 0.6 * suma
                    pixel_nou = pixel_orig + 0.6 * suma
                    
                    # Ajustam valoarea sa fie in intervalul [0, 255]
                    result[j, i, c] = self.adjust_color(pixel_nou)
        
        # Copiem marginile din imaginea originala (nu le procesam)
        result[0, :] = image[0, :]
        result[-1, :] = image[-1, :]
        result[:, 0] = image[:, 0]
        result[:, -1] = image[:, -1]
        
        return result.astype(np.uint8)
    
    def adjust_color(self, value):
        """
        Ajusteaza valoarea de culoare pentru a fi in intervalul [0, 255].
        Clipeaza valorile care depasesc limitele.
        
        Args:
            value: valoarea de culoare (poate fi float)
        
        Returns:
            valoare clipeata in [0, 255]
        """
        return np.clip(value, 0, 255)
    
    def aplicare_floyd_steinberg(self):
        """Aplica algoritmul Floyd-Steinberg de dithering."""
        def logica(img):
            palette = self.create_default_palette()
            return self.floyd_steinberg(img, palette)
            
        self.incarcare_si_procesare_imagine(logica, "Floyd-Steinberg Dithering", "Original", "Floyd-Steinberg")

    
    def create_default_palette(self):
        """
        Creeaza o paleta de culori predefinita pentru dithering.
        Utilizeaza o paleta de 8 culori (cubic palette: 2x2x2 culori).
        
        Returns:
            lista de tuple (R, G, B) reprezentand paletă
        """
        palette = [
            (0, 0, 0),           # Black
            (255, 0, 0),         # Red
            (0, 255, 0),         # Green
            (0, 0, 255),         # Blue
            (255, 255, 0),       # Yellow
            (255, 0, 255),       # Magenta
            (0, 255, 255),       # Cyan
            (255, 255, 255)      # White
        ]
        return palette
    
    def floyd_steinberg(self, image, palette):
        """
        Aplica algoritmul Floyd-Steinberg de dithering pe imagine.
        Reduce paletă de culori si distribuie eroarea de cuantificare.
        
        Ponderile de distribuție a erorii:
                    X    7/16
            3/16    5/16  1/16
        
        Args:
            image: imaginea de intrare (RGB)
            palette: lista de culori disponibile (tuple R,G,B)
        
        Returns:
            imaginea dithered
        """
        h, w = image.shape[:2]
        # Copiem imaginea si lucram cu float pentru a permite distribuția erorii
        img = image.astype(np.float64).copy()
        result = np.zeros_like(image, dtype=np.uint8)
        
        # Parcurgem fiecare pixel
        for y in range(h):
            for x in range(w):
                # Pixelul original
                old_pixel = img[y, x].copy()
                
                # Gasim cea mai apropiata culoare din paleta
                new_pixel = self.get_nearest_color(old_pixel, palette)
                result[y, x] = new_pixel
                
                # Calculam eroarea de cuantificare pentru fiecare canal
                error = old_pixel - new_pixel
                
                # Distribuim eroarea la pixelii vecini conform Floyd-Steinberg
                # Dreapta (x+1, y)
                if x + 1 < w:
                    img[y, x + 1] += error * (7 / 16)
                
                # Stanga-jos (x-1, y+1)
                if x - 1 >= 0 and y + 1 < h:
                    img[y + 1, x - 1] += error * (3 / 16)
                
                # Jos (x, y+1)
                if y + 1 < h:
                    img[y + 1, x] += error * (5 / 16)
                
                # Dreapta-jos (x+1, y+1)
                if x + 1 < w and y + 1 < h:
                    img[y + 1, x + 1] += error * (1 / 16)
        
        return result
    
    def get_nearest_color(self, pixel_rgb, palette):
        """
        Gaseste cea mai apropiata culoare din paleta pentru un pixel dat.
        Utilizeaza distanta Euclidiana in spatiul RGB.
        
        Args:
            pixel_rgb: culoarea pixelului (array R,G,B sau tuple)
            palette: lista de culori disponibile (tuple R,G,B)
        
        Returns:
            tuple (R,G,B) cu cea mai apropiata culoare din paleta
        """
        nearest_color = palette[0]
        nearest_distance = float('inf')
        
        # Clipeaza pixelul la [0, 255] inainte de comparare
        pixel_clipped = np.clip(pixel_rgb, 0, 255)
        
        for color in palette:
            dist = self.euclidean_distance(pixel_clipped, color)
            if dist < nearest_distance:
                nearest_distance = dist
                nearest_color = color
        
        return np.array(nearest_color, dtype=np.uint8)
    
    def euclidean_distance(self, color1, color2):
        """
        Calculeaza distanta Euclidiana intre doua culori in spatiul RGB.
        
        Args:
            color1: tuple sau array (R1, G1, B1)
            color2: tuple sau array (R2, G2, B2)
        
        Returns:
            distanta Euclidiana
        """
        r1, g1, b1 = color1[0], color1[1], color1[2]
        r2, g2, b2 = color2[0], color2[1], color2[2]
        
        dist = math.sqrt((r1 - r2)**2 + (g1 - g2)**2 + (b1 - b2)**2)
        return dist

    # ==========================================
    # LABORATOR 7 - Metode de aplicare (UI)
    # ==========================================

    def aplicare_filtru_laplacian(self):
        """Aplica filtrul Laplacian si afiseaza rezultatul."""
        def logica(img):
            return self.filtru_laplacian(img)
        self.incarcare_si_procesare_imagine(logica, "Filtru Laplacian", "Original", "Laplacian")

    def aplicare_eliminare_zgomot_gaussian(self):
        """Aplica eliminarea zgomotului Gaussian si afiseaza rezultatul."""
        def logica(img):
            return self.eliminare_zgomot_gaussian(img)
        self.incarcare_si_procesare_imagine(logica, "Eliminare Zgomot Gaussian", "Original", "Gaussian Denoised")

    def aplicare_snr_o_imagine(self):
        """Calculeaza SNR pentru o singura imagine si afiseaza rezultatul intr-un popup."""
        from tkinter import messagebox
        result = self.procesare_imagine()
        if result is None:
            return
        snr = self.calculeaza_snr(self.cv_img_rgb)
        messagebox.showinfo("SNR - O Imagine", f"Valoarea SNR: {snr:.4f} dB")

    def aplicare_snr_doua_imagini_ui(self):
        """Calculeaza SNR intre doua imagini si afiseaza rezultatul intr-un popup."""
        from tkinter import messagebox
        messagebox.showinfo("SNR - Doua Imagini", "Selecteaza PRIMA imagine (imaginea originala).")
        result1 = self.procesare_imagine()
        if result1 is None:
            return
        imagine1 = self.cv_img_rgb.copy()

        messagebox.showinfo("SNR - Doua Imagini", "Selecteaza A DOUA imagine (imaginea procesata).")
        result2 = self.procesare_imagine()
        if result2 is None:
            return
        imagine2 = self.cv_img_rgb.copy()

        # Verificam ca imaginile au aceleasi dimensiuni
        if imagine1.shape != imagine2.shape:
            messagebox.showerror("Eroare", "Cele doua imagini trebuie sa aiba aceleasi dimensiuni!")
            return
        snr = self.calculeaza_snr_doua_imagini(imagine1, imagine2)
        messagebox.showinfo("SNR - Doua Imagini", f"Valoarea SNR: {snr:.4f} dB")

    def deschide_imagine_doar_date(self):
        """
        Deschide un dialog pentru selectarea unei imagini si returneaza
        array-ul numpy, fara a o afisa pe ecran.
        """
        result = self.procesare_imagine()
        if result is None:
            return None
        return self.cv_img_rgb

    # ==========================================
    # LABORATOR 7 - Implementari algoritmi
    # ==========================================

    # ------------------------------------
    # Pseudocod - Filtru Laplacian:
    # ------------------------------------
    # FUNCTIE filtru_laplacian(imagine):
    #   Defineste masca Laplaciana 3x3:
    #     [-1, -1, -1]
    #     [-1,  8, -1]
    #     [-1, -1, -1]
    #   Pentru fiecare pixel (x, y) din imagine, ignorand marginile:
    #     Initializeaza suma = 0
    #     Pentru fiecare vecin (m, n) din fereastra 3x3:
    #       Ia valoarea canalului albastru (sau gri) a pixelului vecin
    #       Aduna la suma: masca[m+1][n+1] * valoare_pixel_vecin
    #     Taie suma in intervalul [0, 255]
    #     Seteaza pixelul de iesire ca (suma, suma, suma) => imagine gri
    #   Returneaza imaginea rezultat
    # ------------------------------------
    def filtru_laplacian(self, image):
        """
        Aplica filtrul Laplacian pentru detectarea marginilor.
        Masca folosita: [[-1,-1,-1],[-1,8,-1],[-1,-1,-1]]
        Produce margini de un singur pixel, eliminand mult zgomot.
        """
        h, w = image.shape[:2]
        result = np.zeros_like(image, dtype=np.uint8)

        # Coeficientii mastii Laplaciene
        v = np.array([
            [-1, -1, -1],
            [-1,  8, -1],
            [-1, -1, -1]
        ], dtype=np.float64)

        # Parcurgem pixelii ignorand marginile (ca in modelul Java)
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                suma = 0
                for m in range(-1, 2):
                    for n in range(-1, 2):
                        # Luam canalul albastru (echivalent cu & 0xff din Java)
                        pixel_val = int(image[y + n, x + m, 2])
                        suma += v[m + 1][n + 1] * pixel_val
                # Taiem valoarea in [0, 255]
                suma = int(np.clip(suma, 0, 255))
                result[y, x] = [suma, suma, suma]

        return result

    # ------------------------------------
    # Pseudocod - Eliminare Zgomot Gaussian:
    # ------------------------------------
    # FUNCTIE eliminare_zgomot_gaussian(imagine):
    #   Defineste dimensiunea nucleului = 3, deci raza = 1
    #   Pentru fiecare pixel (x, y) din imagine:
    #     Initializeaza sumele R, G, B = 0
    #     Pentru fiecare vecin (i, j) din fereastra 3x3:
    #       Calculeaza coordonatele vecinului cu clampare la marginile imaginii
    #       Aduna valorile R, G, B ale vecinului la sume
    #     Calculeaza media: R_mediu = sumR / 9, G_mediu = sumG / 9, B_mediu = sumB / 9
    #     Seteaza pixelul de iesire cu valorile medii
    #   Returneaza imaginea rezultat
    # ------------------------------------
    def eliminare_zgomot_gaussian(self, image):
        """
        Elimina zgomotul Gaussian prin medierea pixelilor din vecinatatea 3x3.
        Echivalent cu un filtru de mediere simplu (box filter).
        """
        h, w = image.shape[:2]
        result = np.zeros_like(image, dtype=np.uint8)

        kernel_size = 3
        half_kernel = kernel_size // 2

        for y in range(h):
            for x in range(w):
                sum_r, sum_g, sum_b = 0, 0, 0

                # Calculam media intensitatilor pixelilor din jur
                for i in range(-half_kernel, half_kernel + 1):
                    for j in range(-half_kernel, half_kernel + 1):
                        # Clampam coordonatele la marginile imaginii (ca Math.min/max din Java)
                        offset_x = min(max(x + i, 0), w - 1)
                        offset_y = min(max(y + j, 0), h - 1)

                        sum_r += int(image[offset_y, offset_x, 0])
                        sum_g += int(image[offset_y, offset_x, 1])
                        sum_b += int(image[offset_y, offset_x, 2])

                # Calculam media valorilor pixelilor
                nr_pixeli = kernel_size * kernel_size
                avg_r = sum_r // nr_pixeli
                avg_g = sum_g // nr_pixeli
                avg_b = sum_b // nr_pixeli

                result[y, x] = [avg_r, avg_g, avg_b]

        return result

    # ------------------------------------
    # Pseudocod - SNR Varianta 1 (o singura imagine):
    # ------------------------------------
    # FUNCTIE calculeaza_snr(imagine):
    #   Pentru fiecare pixel din imagine:
    #     Ia valoarea canalului rosu ca semnal
    #     Calculeaza zgomotul = |255 - semnal|
    #     Aduna semnalul si zgomotul la sumele totale
    #   Calculeaza media semnalului = suma_semnal / nr_pixeli
    #   Calculeaza media zgomotului = suma_zgomot / nr_pixeli
    #   SNR = 10 * log10( media_semnal^2 / media_zgomot^2 )
    #   Returneaza SNR
    # ------------------------------------
    def calculeaza_snr(self, image):
        """
        Calculeaza raportul semnal-zgomot (SNR) pentru o singura imagine.
        Foloseste canalul rosu ca semnal si diferenta fata de 255 ca zgomot.
        """
        h, w = image.shape[:2]
        signal_sum = 0
        noise_sum = 0

        for y in range(h):
            for x in range(w):
                # Canalul rosu ca semnal (ca in Java: color.getRed())
                semnal = int(image[y, x, 0])
                # Zgomotul = diferenta intre valoarea maxima si valoarea semnalului
                zgomot = abs(255 - semnal)
                signal_sum += semnal
                noise_sum += zgomot

        nr_pixeli = w * h
        signal_mean = signal_sum / nr_pixeli
        noise_mean = noise_sum / nr_pixeli

        # Evitam impartirea la zero
        if noise_mean == 0:
            return float('inf')

        snr = 10 * math.log10((signal_mean ** 2) / (noise_mean ** 2))
        return snr

    # ------------------------------------
    # Pseudocod - SNR Varianta 2 (doua imagini):
    # ------------------------------------
    # FUNCTIE calculeaza_snr_doua_imagini(imagine1, imagine2):
    #   Pentru fiecare pixel (x, y):
    #     Ia valoarea RGB a pixelului din imagine1 si imagine2
    #     semnal = |valoare_rgb1 - valoare_rgb2| (diferenta dintre imagini)
    #     zgomot = |valoare_rgb1| (valoarea absoluta a primei imagini)
    #     Aduna la sume totale
    #   Calculeaza media semnalului si a zgomotului
    #   SNR = 10 * log10( media_semnal^2 / media_zgomot^2 )
    #   Returneaza SNR
    # ------------------------------------
    def calculeaza_snr_doua_imagini(self, image1, image2):
        """
        Calculeaza raportul semnal-zgomot (SNR) comparand doua imagini.
        Semnalul = diferenta dintre imagini, zgomotul = imaginea originala.
        Util pentru a masura cat de mult a afectat un filtru imaginea.
        """
        h, w = image1.shape[:2]
        signal_sum = 0
        noise_sum = 0

        for y in range(h):
            for x in range(w):
                # Convertim canalele R, G, B intr-un singur intreg (ca getRGB() din Java)
                r1, g1, b1 = int(image1[y, x, 0]), int(image1[y, x, 1]), int(image1[y, x, 2])
                r2, g2, b2 = int(image2[y, x, 0]), int(image2[y, x, 1]), int(image2[y, x, 2])

                rgb1 = (r1 << 16) | (g1 << 8) | b1
                rgb2 = (r2 << 16) | (g2 << 8) | b2

                semnal = abs(rgb1 - rgb2)
                zgomot = abs(rgb1)

                signal_sum += semnal
                noise_sum += zgomot

        nr_pixeli = w * h
        signal_mean = signal_sum / nr_pixeli
        noise_mean = noise_sum / nr_pixeli

        # Evitam impartirea la zero
        if noise_mean == 0:
            return float('inf')

        snr = 10 * math.log10((signal_mean ** 2) / (noise_mean ** 2))
        return snr


if __name__ == "__main__":
    app = Aplicatie()
    app.mainloop()