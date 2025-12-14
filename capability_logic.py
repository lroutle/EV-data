import pandas as pd
import numpy as np
import scipy.stats as stats

class CapabilityAnalysis:
    def __init__(self, data_series, lsl, usl, target=None):
        """
        Initialize with a pandas Series of data and specification limits.
        """
        self.data = data_series.dropna()
        self.lsl = lsl
        self.usl = usl
        self.target = target

        # Basic Statistics
        self.mean = self.data.mean()
        self.count = len(self.data)
        self.std_overall = self.data.std()

        # Moving Range and Within Standard Deviation
        self.mrs = abs(self.data.diff())
        self.mr_mean = self.mrs.mean()
        # d2 constant for n=2 is 1.128
        self.d2 = 1.128
        self.std_within = self.mr_mean / self.d2

    def calculate_metrics(self):
        """
        Calculate Cp, Cpk, Pp, Ppk.
        """
        # Pp & Ppk (Overall Performance)
        self.pp = (self.usl - self.lsl) / (6 * self.std_overall)
        self.ppk_upper = (self.usl - self.mean) / (3 * self.std_overall)
        self.ppk_lower = (self.mean - self.lsl) / (3 * self.std_overall)
        self.ppk = min(self.ppk_upper, self.ppk_lower)

        # Cp & Cpk (Potential Capability - Within)
        self.cp = (self.usl - self.lsl) / (6 * self.std_within)
        self.cpk_upper = (self.usl - self.mean) / (3 * self.std_within)
        self.cpk_lower = (self.mean - self.lsl) / (3 * self.std_within)
        self.cpk = min(self.cpk_upper, self.cpk_lower)

        return {
            "Mean": self.mean,
            "N": self.count,
            "StDev (Overall)": self.std_overall,
            "StDev (Within)": self.std_within,
            "Pp": self.pp,
            "Ppk": self.ppk,
            "Cp": self.cp,
            "Cpk": self.cpk
        }

if __name__ == "__main__":
    # Test the logic
    df = pd.read_csv("dummy_data.csv")
    col = df.columns[0]
    analysis = CapabilityAnalysis(df[col], lsl=9.5, usl=10.5)
    metrics = analysis.calculate_metrics()
    print("Metrics for column:", col)
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")
