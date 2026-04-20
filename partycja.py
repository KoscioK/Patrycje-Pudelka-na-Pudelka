#!/usr/bin/env python3
"""
Rozwiązywanie problemu partycjonowania prostopadłościanu n x m x k na mniejsze bloki
całkowitoliczbowe. Obejmuje przeliczanie wszystkich możliwych multisets oraz 
ich wizualizację na trójwymiarowym rzucie (transparentne bryły).

Użycie:
  python partycja.py [n] [m] [k]
  python partycja.py 2 2 2
  python partycja.py 2 2 2 --count-only
"""

import sys
import argparse
from collections import Counter

def find_partitions(n, m, k):
    """
    Znajduje wszystkie partycje prostopadłościanu dla wymiarów (n, m, k).
    Zwraca słownik: wynik[znormalizowana_krotka_multizbioru] = przykladowe_ulozenie.
    Używa maski bitowej do bardzo wydajnego i dokładnego pokrycia.
    """
    V = n * m * k
    
    # Inicjalizacja tablicy dopuszczalnych wstawień dla każdej komórki z osobna
    moves_from_cell = [[] for _ in range(V)]
    
    for x in range(n):
        for y in range(m):
            for z in range(k):
                idx = x * m * k + y * k + z
                # Szukamy do jakich maksymalnych wymiarów możemy się rozszerzyć z danej komórki
                for dx in range(1, n - x + 1):
                    for dy in range(1, m - y + 1):
                        for dz in range(1, k - z + 1):
                            mask = 0
                            # Budujemy maskę zajętości dla danego ułożenia bloku
                            for cx in range(x, x + dx):
                                for cy in range(y, y + dy):
                                    for cz in range(z, z + dz):
                                        c_idx = cx * m * k + cy * k + cz
                                        mask |= (1 << c_idx)
                            # Zapis: (wymiary, geometria, maska_zajetych_obszarow)
                            moves_from_cell[idx].append(((dx, dy, dz), (x, y, z, dx, dy, dz), mask))
                            
    results = {}
    
    def backtrack(current_mask, current_blocks, current_placement):
        # Kiedy maska jest w pełni zapalona (cała przestrzeń n*m*k zajęta)
        if current_mask == (1 << V) - 1:
            # Sortujemy wszystkie użyte wymiary, co usunie duplikaty ułożeń 
            # składających się z tych samych wielkości prostopadłościanowych.
            canon = tuple(sorted([tuple(sorted(b)) for b in current_blocks]))
            if canon not in results:
                # Zamrażamy jednio poprawne ułożenie dla wizualizacji
                results[canon] = list(current_placement)
            return
            
        # Znajdź indeks pierwszej (najmniej znaczącej) fałszywej(pustej) komórki bitowej
        # Wynika to z operacji dwójkowych: ~maska & (maska + 1) izoluje najniższy wolny bit
        idx = (~current_mask & (current_mask + 1)).bit_length() - 1
        
        for bdim, placement, placement_mask in moves_from_cell[idx]:
            # Jeżeli pole włożenia nowego elementu nie pokrywa się z dotychczas zajętymi...
            if (current_mask & placement_mask) == 0:
                current_blocks.append(bdim)
                current_placement.append(placement)
                # Schodzimy o jeden poziom niżej w drzewie
                backtrack(current_mask | placement_mask, current_blocks, current_placement)
                # Powrót - czyszczenie
                current_placement.pop()
                current_blocks.pop()

    # Początek drzewa
    backtrack(0, [], [])
    
    # Aby ułożenia były zawsze złączne (deterministyczne wizualizacje)
    sorted_results = sorted(results.items(), key=lambda x: str(x[0]))
    return sorted_results


def format_part(canon):
    c = Counter(["{x}x{y}x{z}".format(x=b[0], y=b[1], z=b[2]) for b in canon])
    return ", ".join(f"{k} (\u00D7{v})" for k, v in dict(sorted(c.items())).items())

def run():
    parser = argparse.ArgumentParser(description="Partycja prostopadłościanu n x m x k na podzbiory.")
    parser.add_argument('n', type=int, nargs='?', help='Rozmiar w osi X')
    parser.add_argument('m', type=int, nargs='?', help='Rozmiar w osi Y')
    parser.add_argument('k', type=int, nargs='?', help='Rozmiar w osi Z')
    parser.add_argument('--count-only', action='store_true', help='Tylko policz bez włączania grafiki 3D')
    
    args = parser.parse_args()
    
    if args.n is None or args.m is None or args.k is None:
        try:
            print("---------------------------------")
            print("Witaj w generatorze Partycji! ")
            print("Podaj pełne wymiary początkowego wielościanu.")
            print("Wpisz liczby n, m, k (oddzielone spacją), na przykład '2 2 2':")
            inputs = input(">>> ").strip().split()
            if len(inputs) != 3:
                print("Błąd: Musisz podać dokładnie 3 liczby całkowite.")
                return
            n, m, k = map(int, inputs)
        except KeyboardInterrupt:
            return
        except Exception:
            print("Niepoprawny format.")
            return
    else:
        n, m, k = args.n, args.m, args.k

    V = n * m * k
    if V >= 60:
        print(f"\n[!!!] UWAGA: Całkowita objętość to {V}. Czas poszukiwań może być kosmicznie długi!")
        ans = input("Czy na pewno kontynuować? (T/N): ")
        if ans.lower() not in ('t', 'tak', 'y', 'yes'):
            return

    print(f"\nGenerowanie wszystkich unikalnych partycji figur dla {n}x{m}x{k}...")
    results = find_partitions(n, m, k)
    print(f"====================================")
    print(f" ZNALEZIONO {len(results)} POPRAWNYCH PARTYCJI\n")
    
    for idx, (canon, _) in enumerate(results):
        print(f" {idx+1:3d}. {{ {format_part(canon)} }}")
        
    print(f"====================================\n")

    if args.count_only:
        return

    # Przerywamy obieg jeśli z bibliotekami GUI jest kłopot
    try:
        import numpy as np
        import matplotlib.pyplot as plt
        from matplotlib.widgets import Button, Slider
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    except ImportError:
        print("Nie odnaleziono biblioteki matplotlib/numpy. Widok 3D jest niedostępny.")
        return

    print("Ładowanie modułu Matplotlib. Zamknij nowe okno, aby zakończyć program...")

    class PartitionVisualizer:
        def __init__(self, n, m, k, partitions):
            self.n, self.m, self.k = n, m, k
            self.partitions = partitions
            self.current_idx = 0
            
            # Główna figura i podział
            self.fig = plt.figure(figsize=(12, 8))
            self.fig.canvas.manager.set_window_title(f"Partycje {n}x{m}x{k}")
            self.ax = self.fig.add_axes([0.05, 0.25, 0.8, 0.7], projection='3d')
            
            # Suwaki rzutów perspektyw i przekrojów
            self.ax_z_slider = plt.axes([0.15, 0.15, 0.5, 0.03])
            self.slider_z = Slider(self.ax_z_slider, 'Przekrój Z', -1, self.k-1, valinit=-1, valstep=1)
            self.slider_z.on_changed(self.update_plot)
    
            self.ax_y_slider = plt.axes([0.15, 0.10, 0.5, 0.03])
            self.slider_y = Slider(self.ax_y_slider, 'Przekrój Y', -1, self.m-1, valinit=-1, valstep=1)
            self.slider_y.on_changed(self.update_plot)
            
            self.ax_x_slider = plt.axes([0.15, 0.05, 0.5, 0.03])
            self.slider_x = Slider(self.ax_x_slider, 'Przekrój X', -1, self.n-1, valinit=-1, valstep=1)
            self.slider_x.on_changed(self.update_plot)
            
            # Suwak przybliżenia
            self.ax_zoom = plt.axes([0.9, 0.25, 0.03, 0.5])
            self.slider_zoom = Slider(self.ax_zoom, 'Zoom', 0.1, 3.0, valinit=1.0, orientation='vertical')
            self.slider_zoom.on_changed(self.update_plot)

            # Przełączniki strzałkowe przód / tył
            self.ax_prev = plt.axes([0.7, 0.1, 0.1, 0.05])
            self.btn_prev = Button(self.ax_prev, '<< Poprzednia')
            self.btn_prev.on_clicked(self.prev_part)
            
            self.ax_next = plt.axes([0.82, 0.1, 0.1, 0.05])
            self.btn_next = Button(self.ax_next, 'Następna >>')
            self.btn_next.on_clicked(self.next_part)

            self.colors = self.generate_colors()
            self.draw_partition()
            plt.show()

        def generate_colors(self):
            # Odcienie niebieskiego tworzące wizualizację lekką i estetyczną
            return [
                '#add8e6', '#87ceeb', '#87cefa', '#00bfff', 
                '#1e90ff', '#00ffff', '#40e0d0', '#48d1cc'
            ]

        def prev_part(self, event):
            self.current_idx = (self.current_idx - 1) % len(self.partitions)
            self.draw_partition()
            
        def next_part(self, event):
            self.current_idx = (self.current_idx + 1) % len(self.partitions)
            self.draw_partition()
            
        def update_plot(self, val):
            self.draw_partition()

        def draw_partition(self):
            self.ax.clear()

            title_info = format_part(self.partitions[self.current_idx][0])
            self.ax.set_title(
                f"Partycja {self.current_idx + 1} z {len(self.partitions)}\nSkład: [ {title_info} ]", 
                pad=20, fontsize=12
            )
            self.ax.set_xlabel('Oś X')
            self.ax.set_ylabel('Oś Y')
            self.ax.set_zlabel('Oś Z')
            
            # Ratyfikacja zoomu poprzez limitowanie osi i pola widzenia
            zoom = self.slider_zoom.val
            cx, cy, cz = self.n/2, self.m/2, self.k/2
            rx, ry, rz = self.n/(2*zoom), self.m/(2*zoom), self.k/(2*zoom)
            
            self.ax.set_xlim(cx - rx, cx + rx)
            self.ax.set_ylim(cy - ry, cy + ry)
            self.ax.set_zlim(cz - rz, cz + rz)
            self.ax.set_box_aspect((self.n, self.m, self.k)) # Skala rzeczywista 1-1-1

            # Renderowanie odpowiednich sześcianików wewnątrz boxu
            _, placement = self.partitions[self.current_idx]
            z_cut, y_cut, x_cut = int(self.slider_z.val), int(self.slider_y.val), int(self.slider_x.val)
            
            for i, (x, y, z, dx, dy, dz) in enumerate(placement):
                # Mechanika cross-sectioningu: wyłącz bryłę jeśli nie przecina się na wskazanej osi
                if z_cut >= 0 and not (z <= z_cut < z + dz): continue
                if y_cut >= 0 and not (y <= y_cut < y + dy): continue
                if x_cut >= 0 and not (x <= x_cut < x + dx): continue
                
                color = self.colors[i % len(self.colors)]
                self.draw_cuboid(x, y, z, dx, dy, dz, color)
                
            self.fig.canvas.draw_idle()

        def draw_cuboid(self, x, y, z, dx, dy, dz, color):
            # Współrzędne ułożenia każdego narożnika
            v = np.array([
                [x, y, z], [x+dx, y, z], [x+dx, y+dy, z], [x, y+dy, z],
                [x, y, z+dz], [x+dx, y, z+dz], [x+dx, y+dy, z+dz], [x, y+dy, z+dz]
            ])
            # Łączenia tworzące bloki ścian wielościanów
            faces = [
                [v[0], v[1], v[2], v[3]], [v[4], v[5], v[6], v[7]],
                [v[0], v[1], v[5], v[4]], [v[2], v[3], v[7], v[6]],
                [v[1], v[2], v[6], v[5]], [v[0], v[3], v[7], v[4]]
            ]
            
            poly3d = Poly3DCollection(faces, alpha=0.35, facecolors=color, linewidths=1.5, edgecolors='k')
            self.ax.add_collection3d(poly3d)
    app = PartitionVisualizer(n, m, k, results)
if __name__ == '__main__':
    run()
