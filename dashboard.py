import sys
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QComboBox, QTabWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ---- Generate sample real estate dataset ----
np.random.seed(42)
cities = ["New York", "Los Angeles", "Chicago", "Houston", "Miami"]
property_types = ["Apartment", "House", "Condo", "Townhouse"]
years = list(range(2018, 2026))

data = []
for _ in range(500):
    city = np.random.choice(cities)
    ptype = np.random.choice(property_types)
    year = np.random.choice(years)
    base_price = {"New York": 800000, "Los Angeles": 700000, "Chicago": 350000,
                  "Houston": 300000, "Miami": 450000}[city]
    price = base_price * (1 + (year - 2018) * 0.05) * np.random.uniform(0.7, 1.3)
    data.append([city, ptype, year, round(price, 2)])

df = pd.DataFrame(data, columns=["City", "PropertyType", "Year", "Price"])


class MplCanvas(FigureCanvas):
    def __init__(self, width=6, height=4):
        fig = Figure(figsize=(width, height))
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real Estate Market Dashboard")
        self.setGeometry(100, 100, 1000, 700)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()
        central.setLayout(main_layout)

        # --- Filters ---
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by City:"))
        self.city_combo = QComboBox()
        self.city_combo.addItem("All")
        self.city_combo.addItems(cities)
        self.city_combo.currentTextChanged.connect(self.update_charts)
        filter_layout.addWidget(self.city_combo)

        filter_layout.addWidget(QLabel("Filter by Property Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItem("All")
        self.type_combo.addItems(property_types)
        self.type_combo.currentTextChanged.connect(self.update_charts)
        filter_layout.addWidget(self.type_combo)

        main_layout.addLayout(filter_layout)

        # --- Tabs for different charts ---
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.canvas_trend = MplCanvas()
        self.canvas_city = MplCanvas()
        self.canvas_type = MplCanvas()

        self.tabs.addTab(self.canvas_trend, "Price Trend Over Time")
        self.tabs.addTab(self.canvas_city, "Avg Price by City")
        self.tabs.addTab(self.canvas_type, "Avg Price by Property Type")

        self.update_charts()

    def get_filtered_data(self):
        filtered = df.copy()
        city = self.city_combo.currentText()
        ptype = self.type_combo.currentText()
        if city != "All":
            filtered = filtered[filtered["City"] == city]
        if ptype != "All":
            filtered = filtered[filtered["PropertyType"] == ptype]
        return filtered

    def update_charts(self):
        filtered = self.get_filtered_data()

        # Chart 1: Price trend over time
        self.canvas_trend.axes.clear()
        trend = filtered.groupby("Year")["Price"].mean()
        self.canvas_trend.axes.plot(trend.index, trend.values, marker='o', color='#2563eb')
        self.canvas_trend.axes.set_title("Average Price Over Time")
        self.canvas_trend.axes.set_xlabel("Year")
        self.canvas_trend.axes.set_ylabel("Average Price ($)")
        self.canvas_trend.draw()

        # Chart 2: Avg price by city
        self.canvas_city.axes.clear()
        by_city = df.groupby("City")["Price"].mean().sort_values()
        self.canvas_city.axes.barh(by_city.index, by_city.values, color='#16a34a')
        self.canvas_city.axes.set_title("Average Price by City")
        self.canvas_city.axes.set_xlabel("Average Price ($)")
        self.canvas_city.draw()

        # Chart 3: Avg price by property type
        self.canvas_type.axes.clear()
        by_type = filtered.groupby("PropertyType")["Price"].mean()
        self.canvas_type.axes.bar(by_type.index, by_type.values, color='#dc2626')
        self.canvas_type.axes.set_title("Average Price by Property Type")
        self.canvas_type.axes.set_ylabel("Average Price ($)")
        self.canvas_type.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Dashboard()
    window.show()
    sys.exit(app.exec_())