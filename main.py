import tkinter as tk
from tkinter import ttk, messagebox
import time

from logic import load_data, run_genetic_algorithm

df = load_data()

class MenuOptimizerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Optimasi Menu - Desktop")
        self.geometry("640x540")
        self.resizable(False, False)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Card.TLabelframe", background="#f5f5f5")
        style.configure("Card.TLabelframe.Label", font=(None, 11, "bold"))
        style.configure("Accent.TButton", font=(None, 10, "bold"))
        style.configure("Status.TLabel", font=(None, 10, "bold"))

        self._build_input_section()
        self._build_result_section()
        self._build_summary_section()

    def _build_input_section(self):
        frame = ttk.LabelFrame(self, text="Parameter Target", style="Card.TLabelframe")
        frame.pack(fill="x", padx=16, pady=(16, 8))

        self.budget_var = tk.StringVar(value="50000")
        self.cal_var = tk.StringVar(value="2000")
        self.prot_var = tk.StringVar(value="90")

        ttk.Label(frame, text="Budget Harian (Rp):").grid(row=0, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(frame, textvariable=self.budget_var, width=20).grid(row=0, column=1, padx=8, pady=4)

        ttk.Label(frame, text="Target Kalori (kkal):").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(frame, textvariable=self.cal_var, width=20).grid(row=1, column=1, padx=8, pady=4)

        ttk.Label(frame, text="Target Protein (gram):").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        ttk.Entry(frame, textvariable=self.prot_var, width=20).grid(row=2, column=1, padx=8, pady=4)

        ttk.Button(frame, text="Generate Menu", command=self._on_generate, style="Accent.TButton").grid(row=3, column=0, columnspan=2, pady=12)

    def _build_result_section(self):
        result_frame = ttk.LabelFrame(self, text="Rekomendasi Menu", style="Card.TLabelframe")
        result_frame.pack(fill="both", expand=True, padx=16, pady=8)

        columns = ("name", "price", "calories", "proteins")
        self.menu_table = ttk.Treeview(result_frame, columns=columns, show="headings", height=8)
        self.menu_table.heading("name", text="Nama Makanan")
        self.menu_table.heading("price", text="Harga (Rp)")
        self.menu_table.heading("calories", text="Kalori")
        self.menu_table.heading("proteins", text="Protein (g)")
        self.menu_table.column("name", width=240)
        self.menu_table.column("price", width=120, anchor="center")
        self.menu_table.column("calories", width=100, anchor="center")
        self.menu_table.column("proteins", width=120, anchor="center")
        self.menu_table.pack(fill="both", expand=True, padx=8, pady=8)

    def _build_summary_section(self):
        summary_frame = ttk.Frame(self)
        summary_frame.pack(fill="x", padx=16, pady=(0, 16))

        separator = ttk.Separator(summary_frame, orient="horizontal")
        separator.pack(fill="x", pady=4)

        self.total_label = ttk.Label(summary_frame, text="Total biaya: -", font=(None, 10))
        self.total_label.pack(anchor="w", pady=2)

        status_frame = ttk.Frame(summary_frame)
        status_frame.pack(fill="x", pady=2)
        ttk.Label(status_frame, text="Status:", font=(None, 10, "bold")).pack(side="left")
        self.status_label = ttk.Label(status_frame, text="-", style="Status.TLabel")
        self.status_label.pack(side="left", padx=(4, 0))

        self.time_label = ttk.Label(summary_frame, text="Waktu komputasi: -", font=(None, 9))
        self.time_label.pack(anchor="w", pady=2)

    def _on_generate(self):
        try:
            budget = int(self.budget_var.get())
            cal = float(self.cal_var.get())
            prot = float(self.prot_var.get())
        except ValueError:
            messagebox.showerror("Input tidak valid", "Masukkan angka yang benar untuk semua parameter.")
            return

        start = time.time()
        result = run_genetic_algorithm(df, budget, cal, prot)
        elapsed = time.time() - start

        for row in self.menu_table.get_children():
            self.menu_table.delete(row)

        total_price = total_cal = total_prot = 0
        for _, food in result.iterrows():
            self.menu_table.insert("", tk.END, values=(
                food["name"],
                f"{int(food['price']):,}",
                f"{food['calories']:.1f}",
                f"{food['proteins']:.1f}",
            ))
            total_price += food["price"]
            total_cal += food["calories"]
            total_prot += food["proteins"]

        self.total_label.configure(
            text=f"Total biaya Rp {total_price:,.0f} · Kalori {total_cal:.1f} kkal · Protein {total_prot:.1f} g"
        )

        status_text = "MASUK BUDGET" if total_price <= budget else f"OVER BUDGET (Rp {total_price - budget:,.0f})"
        self.status_label.configure(text=status_text, foreground="#2a9d8f" if total_price <= budget else "#e76f51")
        self.time_label.configure(text=f"Waktu komputasi: {elapsed:.4f} detik")


if __name__ == "__main__":
    MenuOptimizerApp().mainloop()
