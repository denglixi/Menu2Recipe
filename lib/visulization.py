import matplotlib.pyplot as plt
import numpy as np


def auto_label(labels, bins):
    """
    Attach a text label above each bar displaying its height
    """
    for i, v in enumerate(labels):
        plt.text(bins[i] + 0.015,
                 labels[i] + 2,
                 # v / labels[i] + 100,
                 "{:d}".format(int(labels[i])),
                 fontsize=12)


def draw_hist(data, save_path='Histogram'):
    """
    draw hist with data
    :param data:
    """
    n, bins, patches = plt.hist(x=data, bins='auto', color='#0504aa',
                                alpha=0.7, rwidth=0.85)
    plt.grid(axis='y', alpha=0.75)
    plt.xticks()
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title('Histogram')
    plt.text(23, 45, r'$\mu=15, b=3$')
    maxfreq = n.max()
    # 设置y轴的上限
    plt.ylim(ymax=np.ceil(maxfreq / 10) * 10 if maxfreq % 10 else maxfreq + 10)
    auto_label(n, bins)
    plt.savefig(save_path)
    # plt.show()
