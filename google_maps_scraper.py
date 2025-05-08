import tkinter as tk
from tkinter import ttk, messagebox
import requests
import csv

class GoogleMapsScraper:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraper de Ruas (1km)")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        self.lat = tk.StringVar()
        self.lon = tk.StringVar()
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto para buscar ruas")
        
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Web Scraper de Ruas (1km)",
                               font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 20))

        input_frame = ttk.LabelFrame(main_frame, text="Coordenadas (Latitude, Longitude)",
                                   padding="10")
        input_frame.pack(fill=tk.X, pady=10)

        lat_label = ttk.Label(input_frame, text="Latitude:")
        lat_label.pack(anchor=tk.W, pady=(0, 5))
        lat_entry = ttk.Entry(input_frame, textvariable=self.lat, width=50)
        lat_entry.pack(fill=tk.X, pady=(0, 10))

        lon_label = ttk.Label(input_frame, text="Longitude:")
        lon_label.pack(anchor=tk.W, pady=(0, 5))
        lon_entry = ttk.Entry(input_frame, textvariable=self.lon, width=50)
        lon_entry.pack(fill=tk.X, pady=(0, 10))

        example_label = ttk.Label(input_frame,
                                 text="Exemplo: -23.55052 (lat), -46.633308 (lon)",
                                 font=("Helvetica", 9, "italic"))
        example_label.pack(anchor=tk.W)

        search_button = ttk.Button(main_frame, text="Buscar Ruas",
                                 command=self.start_scraping)
        search_button.pack(pady=20)

        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)

        status_label = ttk.Label(status_frame, text="Status:")
        status_label.pack(side=tk.LEFT)

        status_info = ttk.Label(status_frame, textvariable=self.status_var)
        status_info.pack(side=tk.LEFT, padx=5)

    def start_scraping(self):
        lat = self.lat.get().strip()
        lon = self.lon.get().strip()

        if not lat or not lon:
            messagebox.showerror("Erro", "Por favor, insira latitude e longitude.")
            return
        try:
            lat_f = float(lat)
            lon_f = float(lon)
        except ValueError:
            messagebox.showerror("Erro", "Latitude e longitude devem ser números válidos.")
            return

        self.status_var.set("Buscando ruas via Overpass API...")
        self.root.update()

        try:
            url = "https://overpass-api.de/api/interpreter"
            query = f"""
            [out:json];
            way["highway"]["name"](around:1000,{lat},{lon});
            out tags;
            """.replace("\n", " ")
            response = requests.post(url, data={'data': query})
            data = response.json()
            street_names = set()
            for element in data.get('elements', []):
                name = element.get('tags', {}).get('name')
                if name:
                    street_names.add(name)
            street_list = sorted(street_names)
            if not street_list:
                messagebox.showinfo("Sem Resultados", "Nenhuma rua encontrada no raio de 1km.")
                self.status_var.set("Nenhuma rua encontrada.")
                return
            self.save_to_csv(street_list)
            self.status_var.set(f"Busca concluída! {len(street_list)} ruas salvas.")
            messagebox.showinfo("Sucesso", f"{len(street_list)} ruas encontradas e salvas em 'ruas_1km.csv'.")
        except Exception as e:
            self.status_var.set("Erro durante a busca!")
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")

    def save_to_csv(self, street_list):
        with open("ruas_1km.csv", "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Nome da Rua"])
            for name in street_list:
                writer.writerow([name])

if __name__ == "__main__":
    root = tk.Tk()
    app = GoogleMapsScraper(root)
    root.mainloop()
