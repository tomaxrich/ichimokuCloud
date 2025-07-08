import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import yfinance as yf
import datetime

# --- CONFIG ---
COMMODITIES = {
    "Gold": "GC=F",
    "Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
    "Silver": "SI=F",
    "Corn": "ZC=F",
}

# --- MAIN APP ---
class CommodityApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📊 Commodity Analysis Engine")
        self.geometry("1200x800")

        # Scrollable Frame Setup
        canvas = tk.Canvas(self)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add commodity blocks
        for name, symbol in COMMODITIES.items():
            self.create_commodity_block(name, symbol)

    def create_commodity_block(self, name, symbol):
        frame = ttk.LabelFrame(self.scrollable_frame, text=name, padding=10)
        frame.pack(fill="x", padx=10, pady=10)

        # Fetch historical data
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=180)
        data = yf.download(symbol, start=start, end=end)

        # Plot closing price
        fig, ax = plt.subplots(figsize=(6, 2), dpi=100)
        data['Close'].plot(ax=ax, title=f"{name} Price")
        ax.set_ylabel("USD")

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x")

        # Display simple stats
        #latest_close = data['Close'].iloc[-1]
        #latest_volume = data['Volume'].iloc[-1]
        #stats = f"Latest Close: {latest_close:.2f} | Volume: {int(latest_volume)}"
        #tk.Label(frame, text=stats).pack(pady=5)

# --- RUN ---
if __name__ == "__main__":
    app = CommodityApp()
    app.mainloop()
