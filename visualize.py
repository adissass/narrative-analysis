import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

conn = sqlite3.connect("data_store.db")
df = pd.read_sql_query("SELECT character, chapter, delta FROM impact_log", conn)

# convert to numeric, just in case
df["chapter"] = pd.to_numeric(df["chapter"], errors="coerce")
df["delta"] = pd.to_numeric(df["delta"], errors="coerce")

# compute average delta per character per chapter
trend = df.groupby(["character", "chapter"])["delta"].mean().reset_index()


# plot
colors = {
    "Monkey D. Luffy": "red",
    "Roronoa Zoro": "green",
    "Sanji": "gold",
    "Jinbe": "lightblue",
    "Nico Robin": "darkblue",
    "Jewelry Bonney": "hotpink",
    "Buggy": "firebrick",
}

plt.figure(figsize=(8,5))
for char, color in colors.items():
    sub = trend[trend["character"] == char].sort_values("chapter")
    sub["cumulative"] = sub["delta"].cumsum()
    plt.plot(sub["chapter"], sub["cumulative"], marker="o", color=color, label=char)
    
plt.axhline(0, color="gray", linestyle="--", linewidth=0.8)
plt.title("Cumulative Agenda Value by Chapter")
plt.xlabel("Chapter")
plt.ylabel("Cumulative Δ (Agenda)")
plt.grid(alpha=0.3, linestyle=":")
plt.axhline(0, color="gray", linestyle="--", linewidth=0.8)
plt.legend(frameon=False, fontsize=9)
plt.tight_layout()
plt.show()
