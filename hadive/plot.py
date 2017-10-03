import os
import time
import calmap
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def df_to_pickle(df, filename, results_path):
    pkl_folder = os.path.join(results_path, "pkl")
    if not os.path.isdir(pkl_folder):
        os.mkdir(pkl_folder)
    df.to_pickle(os.path.join(pkl_folder, filename))


def plot_live_time(hadive_path, saved_data=True):
    if not saved_data:
        results_path = os.path.join(hadive_path, "data", "results")
        data_path = os.path.join(results_path, "hadive-data.feather")
        df = pd.read_feather(data_path).set_index("date").resample("D").size()
        df_to_pickle(df, "live-time.pkl", results_path)
    else:
        df = pd.read_pickle(os.path.join(results_path, "pkl", "live-time.pkl"))

    fig, [ax] = calmap.calendarplot(df[df != 0], cmap="viridis_r",
                                    fig_kws=dict(figsize=(10,2)))

    ax.set_ylabel("")
    ax.set_xlim(6*4, 10*4)
    ax.tick_params(axis="both", which="both", labelsize=12)
    ax.set_title("Data Collection To Date", fontsize=16, y=1.02)

    plots_path = os.path.join(hadive_path, "outputs", "plots")
    plot_path = os.path.join(plots_path, "data_collection.png")
    fig.savefig(plot_path, bbox_inches='tight')

    fig.tight_layout()
    plt.show()
