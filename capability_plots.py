import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats
import seaborn as sns

def create_six_pack(analysis_obj, title="Capability Six Pack"):
    """
    Generates a matplotlib figure with the 6-pack charts.
    """
    data = analysis_obj.data
    mean = analysis_obj.mean
    std_within = analysis_obj.std_within
    std_overall = analysis_obj.std_overall
    lsl = analysis_obj.lsl
    usl = analysis_obj.usl

    # Setup Figure
    fig = plt.figure(figsize=(11.69, 8.27)) # A4 Landscape size roughly
    fig.suptitle(title, fontsize=16)

    # GridSpec for layout
    gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1])

    # 1. I Chart
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(data.values, marker='o', linestyle='-', markersize=4)
    ax1.axhline(mean, color='green', linestyle='-')
    # Control limits for I chart are Mean +/- 3 * (MR_mean / d2)
    # which is Mean +/- 3 * std_within
    ucl_i = mean + 3 * std_within
    lcl_i = mean - 3 * std_within
    ax1.axhline(ucl_i, color='red', linestyle='--')
    ax1.axhline(lcl_i, color='red', linestyle='--')
    ax1.set_title("I Chart")
    ax1.set_ylabel("Individual Value")

    # 2. MR Chart
    ax2 = fig.add_subplot(gs[0, 1])
    mrs = analysis_obj.mrs.dropna()
    mr_mean = analysis_obj.mr_mean
    # D4 constant for n=2 is 3.267
    ucl_mr = 3.267 * mr_mean
    lcl_mr = 0 # D3 is 0 for n=2

    ax2.plot(mrs.values, marker='o', linestyle='-', markersize=4)
    ax2.axhline(mr_mean, color='green', linestyle='-')
    ax2.axhline(ucl_mr, color='red', linestyle='--')
    ax2.axhline(lcl_mr, color='red', linestyle='--')
    ax2.set_title("Moving Range Chart")
    ax2.set_ylabel("Moving Range")

    # 3. Run Chart (Last 25)
    ax3 = fig.add_subplot(gs[1, 0])
    last_25 = data.tail(25)
    ax3.plot(range(len(data)-len(last_25), len(data)), last_25.values, marker='o', linestyle='-')
    ax3.axhline(mean, color='green', linestyle='-')
    ax3.set_title("Run Chart (Last 25 obs)")
    ax3.set_xlabel("Observation")

    # 4. Capability Histogram
    ax4 = fig.add_subplot(gs[1, 1])
    # Plot histogram
    sns.histplot(data, stat="density", kde=False, ax=ax4, color='skyblue', edgecolor='black')

    # Plot Overall Normal Curve
    x = np.linspace(min(data.min(), lsl) - 0.5, max(data.max(), usl) + 0.5, 1000)
    pdf_overall = stats.norm.pdf(x, mean, std_overall)
    ax4.plot(x, pdf_overall, color='red', linestyle='--', label='Overall')

    # Plot Within Normal Curve
    pdf_within = stats.norm.pdf(x, mean, std_within)
    ax4.plot(x, pdf_within, 'k-', label='Within')

    # Spec Limits
    ax4.axvline(lsl, color='red', linestyle='-', linewidth=2, label='LSL')
    ax4.axvline(usl, color='red', linestyle='-', linewidth=2, label='USL')
    ax4.set_title("Capability Histogram")
    ax4.legend(fontsize='small')

    # 5. Normal Probability Plot
    ax5 = fig.add_subplot(gs[2, 0])
    stats.probplot(data, dist="norm", plot=ax5)
    ax5.set_title("Normal Probability Plot")

    # 6. Capability Statistics
    ax6 = fig.add_subplot(gs[2, 1])
    ax6.axis('off')

    metrics = analysis_obj.calculate_metrics()

    # Create text summary
    stats_text = (
        f"LSL: {lsl}\n"
        f"Target: {analysis_obj.target if analysis_obj.target else 'N/A'}\n"
        f"USL: {usl}\n\n"
        f"Mean: {mean:.4f}\n"
        f"N: {int(metrics['N'])}\n\n"
        f"StDev (Within): {metrics['StDev (Within)']:.4f}\n"
        f"Cp: {metrics['Cp']:.2f}\n"
        f"Cpk: {metrics['Cpk']:.2f}\n\n"
        f"StDev (Overall): {metrics['StDev (Overall)']:.4f}\n"
        f"Pp: {metrics['Pp']:.2f}\n"
        f"Ppk: {metrics['Ppk']:.2f}"
    )

    ax6.text(0.1, 0.5, stats_text, fontsize=12, va='center', fontfamily='monospace')
    ax6.set_title("Capability Statistics")

    plt.tight_layout()
    return fig

if __name__ == "__main__":
    from capability_logic import CapabilityAnalysis
    import pandas as pd

    df = pd.read_csv("dummy_data.csv")
    col = df.columns[0]
    analysis = CapabilityAnalysis(df[col], lsl=9.5, usl=10.5)
    fig = create_six_pack(analysis, title=f"Six Pack Report: {col}")
    fig.savefig("test_six_pack.png")
    print("Test chart saved to test_six_pack.png")
