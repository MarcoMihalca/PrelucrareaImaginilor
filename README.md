# Aplicatie de Procesare a Imaginilor

Aceasta este o aplicatie care este dezvoltata strict in Python, pentru procesarea si analizarea imaginilor BMP. Toate functiile sunt implementate manual, fara OpenCV sau orice alta librarie externa.

## Caracteristici Principale
* **Independenta de biblioteci externe**: Citirea fisierelor si algoritmii matematici sunt toti implementati de la zero.

* **Interfata Centrata**: Toate elementele vizuale (imagini, grafice, mesaje) sunt centrate, pentru a asigura o experienta de utilizare consistenta si placuta.

## Cerinte de sistem
* **Python**: 3.6 sau mai nou
* **Biblioteci**: `numpy` (singura dependenta externa, care trebuie instalata)

## Instructiuni pentru rulare

1. **Clonati repository-ul**:
   ```bash
   git clone https://github.com/MarcoMihalca/PrelucrareaImaginilor.git
   ```

2. **Intrati in folderul corect**:
    ```bash
    cd PrelucrareaImaginilor && cd Laborator
    ```

3. **Instalati dependentele necesare**:
    ```bash
    pip install -r requirements.txt
    ```
4. **Rulati codul din fisierul "cod_versiuneLab4_noCV2.py"**

## Demo
Prezentare initiala a catorva functii pe care aceasta aplicatie vi le pune la dispozitie.

## 1. Experienta de Start
La lansarea aplicatiei, utilizatorul este intampinat de un ecran de salut centrat, urmat de interfata principala care ofera instructiuni clare pentru inceput.

| Pagina de Bun Venit | Pagina Principala |
| :--- | :--- |
| ![Bun Venit](Screenshots%20Demo/Demo%20initial/1.%20Pagina%20Bun%20Venit.png) | ![Pagina Principala](Screenshots%20Demo/Demo%20initial/2.%20Pagina%20principala.png) |
| *Salutul initial al aplicatiei* | *Instructiuni pentru utilizator* |

## 2. Navigare si Optiuni
Sistemul de meniu este structurat logic pentru a separa gestionarea fisierelor de uneltele de procesare matematica.

| Meniu File | Meniu Tools |
| :--- | :--- |
| ![Meniu File](Screenshots%20Demo/Demo%20initial/3.%20Meniu%20File.png) | ![Meniu Tools](Screenshots%20Demo/Demo%20initial/4.Meniu%20Tools.png) |
| *Optiuni pentru deschidere si iesire* | *Lista completa a algoritmilor implementati* |

## 3. Exemple de Procesare Digitala
Aplicatia permite vizualizarea rezultatelor procesarii prin diverse metode de conversie si analiza spatiala. Toate imaginile sunt afisate centrat pentru o vizibilitate optima.

### A. Conversie in Alb-Negru (3 Metode)
Aplicatia genereaza simultan trei variante de gri pentru a permite compararea rezultatelor intre media aritmetica, formula Luma si metoda Min-Max.

![Aplicare Alb-Negru](Screenshots%20Demo/Demo%20initial/5.%20Aplicare%20Alb-Negru.png)

### B. Inversarea Culorilor (Negativ)
Vizualizarea negativului imaginii prin descompunerea pe cele trei canale fundamentale: Rosu, Verde si Albastru.

![Inversare Culori](Screenshots%20Demo/Demo%20initial/6.%20Aplicare%20Inversare%20culori.png)

### C. Analiza prin Proiectii
Calcularea si afisarea automata a proiectiilor orizontale si verticale, utile pentru detectarea limitelor obiectelor din imagine.

![Proiectii](Screenshots%20Demo/Demo%20initial/7.%20Proiectii.png)

---