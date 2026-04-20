# Partycje prostopadloscianu n x m x k

Program rozwiazuje problem partycjonowania prostopadloscianu o wymiarach calkowitych `n x m x k` na mniejsze prostopadlosciany o bokach rownoleglych do osi i dlugosciach calkowitych.

Projekt zostal przygotowany wylacznie do celow edukacyjnych na potrzeby przedmiotu "Matematyka Dyskretna".

Wynik to:
- komplet wszystkich poprawnych partycji (jako multizbiory wymiarow),
- liczba partycji,
- przykladowe rzeczywiste ulozenie geometryczne dla kazdej partycji,
- interaktywna wizualizacja 3D (z przekrojami i zoomem).

## Definicja problemu

Partycja `n x m x k` to multizbior mniejszych prostopadloscianow, ktore:
- lacznie maja objetosc `n*m*k`,
- daja sie ulozyc bez nakladania i bez luk, wypelniajac caly blok,
- sa liczone po wymiarach (np. `(1,2,3)` i `(3,1,2)` to ten sam typ bloku).

Dwie partycje uznajemy za identyczne, gdy maja ten sam multizbior wymiarow (ulozenie w przestrzeni moze byc inne).

## Najwazniejsze cechy implementacji

- pelne przeszukiwanie wszystkich mozliwych pokryc,
- weryfikacja geometryczna (nie tylko suma objetosci),
- deduplikacja po kanonicznym multizbiorze wymiarow,
- deterministyczne wypisywanie wynikow,
- interaktywna wizualizacja 3D:
	- transparentne bryly,
	- ciemne krawedzie,
	- osie X/Y/Z,
	- przekroje po osiach X, Y, Z,
	- suwak zoom,
	- przyciski przechodzenia miedzy partycjami.

## Jak dziala algorytm

1. Program generuje wszystkie mozliwe bloki startujace z kazdej komorki siatki 3D.
2. Kazdy blok kodowany jest jako maska bitowa zajetych komorek.
3. Backtracking wybiera pierwsza wolna komorke i probuje legalnie wstawic kazdy pasujacy blok.
4. Pelne pokrycie (wszystkie bity ustawione) oznacza poprawne kafelkowanie.
5. Dla kazdego kafelkowania tworzona jest reprezentacja kanoniczna:
	 - wymiary pojedynczego bloku sa sortowane,
	 - cala lista blokow jest sortowana,
	 - dzieki temu rozne ulozenia geometryczne tej samej partycji sa laczone w jeden wynik.

To podejscie gwarantuje, ze raportowana partycja jest zarowno poprawna objetosciowo, jak i geometrycznie realizowalna.

## Uruchamianie

### 1) Argumenty CLI

```bash
python3 partycje.py n m k
python3 partycje.py 2 2 2
python3 partycje.py 2 2 2 --count-only
```

### 2) Tryb interaktywny

Jesli nie podasz argumentow, program poprosi o wpisanie `n m k` przez `input()`.

## Flagi

- `--count-only` - tylko zliczanie i wypisanie partycji, bez otwierania okna wizualizacji.

## Wymagania

- Python 3.x
- do wizualizacji: `numpy`, `matplotlib`

Instalacja bibliotek:

```bash
pip install numpy matplotlib
```

## Test poprawnosci: 2x2x2

Dla `2x2x2` program powinien znalezc **dokladnie 10 poprawnych partycji**.
To jest podstawowy test zgodnosci z zalozeniami problemu.

Szybka walidacja:

```bash
python3 partycje.py 2 2 2 --count-only
```

Wypisany naglowek powinien zawierac informacje o znalezieniu `10` partycji.

## Obsluga przypadkow brzegowych

- `1x1x1` - jedna trywialna partycja,
- wieksze wartosci - program ostrzega o potencjalnie bardzo dlugim czasie liczenia,
- dla objetosci `>= 60` wymaga potwierdzenia kontynuacji.

## Uwagi praktyczne

- Nazwa pliku w repozytorium to `partycje.py`.
- W docstringu programu przyklady uzywaja nazwy `partycja.py`; przy uruchamianiu nalezy uzyc faktycznej nazwy pliku z repozytorium.