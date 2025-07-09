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
        # Canvas container
        container = tk.Frame(self)
        container.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.grid(row=0, column=1, sticky='ns')
        canvas.grid(row=0, column=0, sticky='nsew')

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Scrollable content frame
        self.scrollable_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)


        # Add commodity blocks
        columns = 2  # Adjust to 3 if you want tighter boxes   
        row = 0
        col = 0

        for name, symbol in COMMODITIES.items():
            self.create_commodity_block(name, symbol, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

    def create_commodity_block(self, name, symbol, row, col):
        

        frame = tk.Frame(self.scrollable_frame, bg="#1e1e1e", bd=2, relief="groove")
        frame.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")

        # Make columns expand evenly
        self.scrollable_frame.grid_columnconfigure(col, weight=1)

        # Commodity Title Label
        tk.Label(frame, text=name, font=("Segoe UI", 14, "bold"), fg="#ffffff", bg="#1e1e1e").grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))
        frame.grid_columnconfigure(0, weight=1)


        # Fetch historical data
        end = datetime.datetime.now()
        start = end - datetime.timedelta(days=180)
        data = yf.download(symbol, start=start, end=end)
        if data.empty:
            print(f"[WARN] No data for {name}")
            return

        # Ichimoku Cloud Calculation
        high_9 = data['High'].rolling(window=9).max()
        low_9 = data['Low'].rolling(window=9).min()
        tenkan_sen = (high_9 + low_9) / 2

        high_26 = data['High'].rolling(window=26).max()
        low_26 = data['Low'].rolling(window=26).min()
        kijun_sen = (high_26 + low_26) / 2

        senkou_a = ((tenkan_sen + kijun_sen) / 2).shift(26)


        high_52 = data['High'].rolling(window=52).max()
        low_52 = data['Low'].rolling(window=52).min()
        senkou_b = ((high_52 + low_52) / 2).shift(26)



        chikou_span = data['Close'].shift(-26)

        # Plot closing price
        fig, ax = plt.subplots(figsize=(6, 2), dpi=100)
        fig.patch.set_facecolor("#1e1e1e")
        ax.set_facecolor("#2b2b2b")
        data['Close'].plot(ax=ax, color="cyan", linewidth=1.5)

        import pandas as pd  # Ensure this is at the top

        # Build Ichimoku DataFrame and drop NaNs
        ichimoku_df = pd.DataFrame({
            "SenkouA": senkou_a.squeeze(),
            "SenkouB": senkou_b.squeeze()
        }, index=data.index).dropna()


        # Sanity check
        if ichimoku_df.empty:
            print(f"[WARN] Ichimoku data for {name} not sufficient.")
            return
        
        ax.fill_between(
            ichimoku_df.index, ichimoku_df["SenkouA"], ichimoku_df["SenkouB"],
            where=(ichimoku_df["SenkouA"] > ichimoku_df["SenkouB"]),
            color='green', alpha=0.2, interpolate=True
        )

        ax.fill_between(
            ichimoku_df.index, ichimoku_df["SenkouA"], ichimoku_df["SenkouB"],
            where=(ichimoku_df["SenkouA"] < ichimoku_df["SenkouB"]),
            color='red', alpha=0.2, interpolate=True
        )


        ax.plot(tenkan_sen, label='Tenkan-sen', color='magenta', linewidth=0.8)
        ax.plot(kijun_sen, label='Kijun-sen', color='orange', linewidth=0.8)
        ax.plot(senkou_a, label='Senkou A', color='green', linewidth=0.8)
        ax.plot(senkou_b, label='Senkou B', color='red', linewidth=0.8)
        ax.plot(chikou_span, label='Chikou', color='gray', linestyle=':', linewidth=0.8)


        ax.set_title(f"{name} Price", color="white")
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.set_ylabel("USD", color="white")

        #ax.legend(loc='upper left', fontsize='small')

        ax.grid(False)
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=10, pady=5)


        # Display simple stats
        #latest_close = data['Close'].iloc[-1]
        #latest_volume = data['Volume'].iloc[-1]
        #stats = f"Latest Close: {latest_close:.2f} | Volume: {int(latest_volume)}"
        #tk.Label(frame, text=stats).pack(pady=5)

# --- RUN ---
if __name__ == "__main__":
    app = CommodityApp()
    app.mainloop()
