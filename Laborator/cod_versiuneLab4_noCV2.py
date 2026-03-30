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
        tools_menu.add_command(label="Moment de ordin 1", command=self.calculare_moment_ordin_1)
        tools_menu.add_command(label="Moment de ordin 2", command=self.calculare_moment_ordin_2)
        tools_menu.add_command(label="Matrice de covarianta", command=self.calculare_matrice_covarianta)
        tools_menu.add_command(label="Proiectii orizontala/verticala", command=self.calculare_proiectii)

        
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
        """Adauga un buton standard de revenire la meniul principal, centrat jos"""
        buton = tk.Button(
            self, 
            text="⬅ Inapoi la pagina principala", 
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",  # O culoare discreta
            padx=10, pady=5, # Padding interior
            command=self.ecran_principal
        )
        
        # Il plasam mereu centrat pe orizontala (relx=0.5) 
        # si jos pe pagina (rely=0.92), ca sa nu se suprapuna cu imaginile
        buton.place(relx=0.5, rely=0.92, anchor="center")

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

            # 1. Calculam histograma, manual
            histogram = [0] * 256

            for y_px in range(h):
                for x_px in range(w):
                    r, g, b = cv_img_rgb[y_px, x_px].astype(int)
                    # Media aritmetica pentru tonul de gri
                    gray = (r + g + b) // 3
                    # Incrementarea corespunzatoare a valorii in histograma
                    histogram[gray] += 1

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
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return

            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]

            # 1. Binarizam imaginea folosind functia auxiliara (aceeasi logica ca aplicare_binarizare)
            # Pragul este 220 pentru a detecta si obiecte colorate (nu doar negre) pe fond alb
            img_bin = self.logica_binarizare(prag=220)

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

            # 3. Calculam centroidul
            if M00 != 0:
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

            self.adauga_buton_inapoi()

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
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return

            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]

            # Binarizam imaginea folosind functia auxiliara (aceeasi logica ca aplicare_binarizare)
            # Pragul este 220 pentru a detecta si obiecte colorate (nu doar negre) pe fond alb, precum am mentionat la functia de ordin 1
            img_bin = self.logica_binarizare(prag=220)

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

            self.adauga_buton_inapoi()

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
            if not hasattr(self, 'cv_img_rgb') or self.cv_img_rgb is None:
                result = self.procesare_imagine()
                if result is None:
                    return

            cv_img_rgb = self.cv_img_rgb
            h, w = cv_img_rgb.shape[:2]

            # Binarizam imaginea folosind functia auxiliara (aceeasi logica ca aplicare_binarizare)
            # Pragul este 220 pentru a detecta si obiecte colorate (nu doar negre) pe fond alb, precum am mentionat la functiile de ordin 1 si 2
            img_bin = self.logica_binarizare(prag=220)

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

            self.adauga_buton_inapoi()

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


if __name__ == "__main__":
    app = Aplicatie()
    app.mainloop()