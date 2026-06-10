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

try:
    import tkinter as tk
    from tkinter import messagebox
except ImportError:
    tk = None
    messagebox = None

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


def collect_dimensions_gui():
    if tk is None:
        return None

    root = tk.Tk()
    root.title("Partycja - dane wejściowe")
    root.resizable(False, False)
    root.configure(padx=16, pady=16)

    title = tk.Label(root, text="Podaj wymiary prostopadłościanu", font=("Segoe UI", 13, "bold"))
    title.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

    description = tk.Label(
        root,
        text="Wpisz dodatnie liczby całkowite dla osi X, Y i Z.",
        justify="left",
    )
    description.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))

    x_var = tk.StringVar(value="2")
    y_var = tk.StringVar(value="2")
    z_var = tk.StringVar(value="2")
    error_var = tk.StringVar(value="")

    tk.Label(root, text="X:").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=4)
    tk.Entry(root, textvariable=x_var, width=12).grid(row=2, column=1, sticky="w", pady=4)

    tk.Label(root, text="Y:").grid(row=3, column=0, sticky="e", padx=(0, 8), pady=4)
    tk.Entry(root, textvariable=y_var, width=12).grid(row=3, column=1, sticky="w", pady=4)

    tk.Label(root, text="Z:").grid(row=4, column=0, sticky="e", padx=(0, 8), pady=4)
    tk.Entry(root, textvariable=z_var, width=12).grid(row=4, column=1, sticky="w", pady=4)

    tk.Label(root, textvariable=error_var, fg="#b00020").grid(row=5, column=0, columnspan=2, sticky="w", pady=(8, 0))

    result = {"dims": None}

    def submit():
        try:
            n = int(x_var.get().strip())
            m = int(y_var.get().strip())
            k = int(z_var.get().strip())
            if n <= 0 or m <= 0 or k <= 0:
                raise ValueError
        except Exception:
            error_var.set("Podaj trzy dodatnie liczby całkowite.")
            return

        result["dims"] = (n, m, k)
        root.destroy()

    def cancel():
        root.destroy()

    button_frame = tk.Frame(root)
    button_frame.grid(row=6, column=0, columnspan=2, sticky="e", pady=(12, 0))
    tk.Button(button_frame, text="Anuluj", command=cancel).pack(side="right", padx=(8, 0))
    tk.Button(button_frame, text="Uruchom", command=submit).pack(side="right")

    root.bind("<Return>", lambda event: submit())
    root.bind("<Escape>", lambda event: cancel())
    root.mainloop()
    return result["dims"]


def launch_visualizer(n, m, k, partitions):
    try:
        import numpy as np
        import matplotlib.pyplot as plt
        from matplotlib.widgets import Button, Slider
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    except ImportError:
        if messagebox is not None:
            messagebox.showerror(
                "Brak bibliotek",
                "Nie odnaleziono biblioteki matplotlib/numpy. Widok 3D jest niedostępny."
            )
        return

    class PartitionVisualizer:
        def __init__(self, n, m, k, partitions):
            self.n, self.m, self.k = n, m, k
            self.partitions = partitions
            self.current_idx = 0

            self.fig = plt.figure(figsize=(12, 8))
            self.fig.canvas.manager.set_window_title(f"Partycje {n}x{m}x{k}")
            self.ax = self.fig.add_axes([0.05, 0.25, 0.8, 0.7], projection='3d')

            self.ax_z_slider = plt.axes([0.15, 0.15, 0.5, 0.03])
            self.slider_z = Slider(self.ax_z_slider, 'Przekrój Z', -1, self.k-1, valinit=-1, valstep=1)
            self.slider_z.on_changed(self.update_plot)

            self.ax_y_slider = plt.axes([0.15, 0.10, 0.5, 0.03])
            self.slider_y = Slider(self.ax_y_slider, 'Przekrój Y', -1, self.m-1, valinit=-1, valstep=1)
            self.slider_y.on_changed(self.update_plot)

            self.ax_x_slider = plt.axes([0.15, 0.05, 0.5, 0.03])
            self.slider_x = Slider(self.ax_x_slider, 'Przekrój X', -1, self.n-1, valinit=-1, valstep=1)
            self.slider_x.on_changed(self.update_plot)

            self.ax_zoom = plt.axes([0.9, 0.25, 0.03, 0.5])
            self.slider_zoom = Slider(self.ax_zoom, 'Zoom', 0.1, 3.0, valinit=1.0, orientation='vertical')
            self.slider_zoom.on_changed(self.update_plot)

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

            zoom = self.slider_zoom.val
            cx, cy, cz = self.n/2, self.m/2, self.k/2
            rx, ry, rz = self.n/(2*zoom), self.m/(2*zoom), self.k/(2*zoom)

            self.ax.set_xlim(cx - rx, cx + rx)
            self.ax.set_ylim(cy - ry, cy + ry)
            self.ax.set_zlim(cz - rz, cz + rz)
            self.ax.set_box_aspect((self.n, self.m, self.k))

            _, placement = self.partitions[self.current_idx]
            z_cut, y_cut, x_cut = int(self.slider_z.val), int(self.slider_y.val), int(self.slider_x.val)

            for i, (x, y, z, dx, dy, dz) in enumerate(placement):
                if z_cut >= 0 and not (z <= z_cut < z + dz):
                    continue
                if y_cut >= 0 and not (y <= y_cut < y + dy):
                    continue
                if x_cut >= 0 and not (x <= x_cut < x + dx):
                    continue

                color = self.colors[i % len(self.colors)]
                self.draw_cuboid(x, y, z, dx, dy, dz, color)

            self.fig.canvas.draw_idle()

        def draw_cuboid(self, x, y, z, dx, dy, dz, color):
            v = np.array([
                [x, y, z], [x+dx, y, z], [x+dx, y+dy, z], [x, y+dy, z],
                [x, y, z+dz], [x+dx, y, z+dz], [x+dx, y+dy, z+dz], [x, y+dy, z+dz]
            ])
            faces = [
                [v[0], v[1], v[2], v[3]], [v[4], v[5], v[6], v[7]],
                [v[0], v[1], v[5], v[4]], [v[2], v[3], v[7], v[6]],
                [v[1], v[2], v[6], v[5]], [v[0], v[3], v[7], v[4]]
            ]

            poly3d = Poly3DCollection(faces, alpha=0.35, facecolors=color, linewidths=1.5, edgecolors='k')
            self.ax.add_collection3d(poly3d)

    PartitionVisualizer(n, m, k, partitions)


def show_results_gui(n, m, k, results, allow_visualization=True):
    if tk is None:
        return False

    root = tk.Tk()
    root.title(f"Partycja {n}x{m}x{k} - wyniki")
    root.geometry("860x620")

    header = tk.Frame(root, padx=12, pady=12)
    header.pack(fill="x")

    title = tk.Label(header, text=f"Znaleziono {len(results)} poprawnych partycji", font=("Segoe UI", 15, "bold"))
    title.pack(anchor="w")

    subtitle = tk.Label(header, text=f"Dla wymiarów {n} x {m} x {k}")
    subtitle.pack(anchor="w", pady=(4, 0))

    body = tk.Frame(root, padx=12, pady=8)
    body.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(body)
    scrollbar.pack(side="right", fill="y")

    text = tk.Text(body, wrap="word", yscrollcommand=scrollbar.set)
    text.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=text.yview)

    text.insert("end", f"Partycja {n}x{m}x{k}\n")
    text.insert("end", f"Liczba poprawnych partycji: {len(results)}\n\n")

    for idx, (canon, _) in enumerate(results, start=1):
        text.insert("end", f"{idx:3d}. {{ {format_part(canon)} }}\n")

    text.config(state="disabled")

    footer = tk.Frame(root, padx=12, pady=12)
    footer.pack(fill="x")

    def open_visualization():
        launch_visualizer(n, m, k, results)

    if allow_visualization:
        tk.Button(footer, text="Otwórz wizualizację 3D", command=open_visualization).pack(side="left")

    tk.Button(footer, text="Zamknij", command=root.destroy).pack(side="right")
    root.mainloop()
    return True

def run():
    parser = argparse.ArgumentParser(description="Partycja prostopadłościanu n x m x k na podzbiory.")
    parser.add_argument('n', type=int, nargs='?', help='Rozmiar w osi X')
    parser.add_argument('m', type=int, nargs='?', help='Rozmiar w osi Y')
    parser.add_argument('k', type=int, nargs='?', help='Rozmiar w osi Z')
    parser.add_argument('--count-only', action='store_true', help='Tylko policz bez włączania grafiki 3D')
    
    args = parser.parse_args()
    
    if args.n is None or args.m is None or args.k is None:
        dims = collect_dimensions_gui()
        if dims is None:
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
            n, m, k = dims
    else:
        n, m, k = args.n, args.m, args.k

    V = n * m * k
    if V >= 60:
        if tk is not None:
            proceed = messagebox.askyesno(
                "Ostrzeżenie",
                f"Całkowita objętość to {V}. Czas poszukiwań może być bardzo długi.\nCzy na pewno kontynuować?"
            )
            if not proceed:
                return
        else:
            print(f"\n[!!!] UWAGA: Całkowita objętość to {V}. Czas poszukiwań może być kosmicznie długi!")
            ans = input("Czy na pewno kontynuować? (T/N): ")
            if ans.lower() not in ('t', 'tak', 'y', 'yes'):
                return

    results = find_partitions(n, m, k)

    if tk is not None:
        shown = show_results_gui(n, m, k, results, allow_visualization=not args.count_only)
        if shown:
            return

    print(f"\nGenerowanie wszystkich unikalnych partycji figur dla {n}x{m}x{k}...")
    print(f"====================================")
    print(f" ZNALEZIONO {len(results)} POPRAWNYCH PARTYCJI\n")

    for idx, (canon, _) in enumerate(results):
        print(f" {idx+1:3d}. {{ {format_part(canon)} }}")

    print(f"====================================\n")

    if args.count_only:
        return

    launch_visualizer(n, m, k, results)
if __name__ == '__main__':
    run()
