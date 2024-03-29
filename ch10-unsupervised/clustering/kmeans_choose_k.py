# -*- coding: UTF-8 -*-
"""
此脚本用于展示如何选择KMeans里面的类别个数k
"""


import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.datasets.samples_generator import make_blobs


def generate_data(n):
    """
    生成随机的聚类数据，聚类中心为3个
    """
    centers = [[1, 1], [-1, -1], [1, -1]]
    X, _ = make_blobs(n_samples=n, centers=centers, cluster_std=0.5)
    return X


def train_model(data, cluster_num):
    """
    使用KMeans对数据进行聚类
    """
    model = KMeans(n_clusters=cluster_num)
    model.fit(data)
    return model


def compute_SSE(model, data):
    """
    计算聚类结果的误差平方和
    """
    wdist = model.transform(data).min(axis=1)
    sse = np.sum(wdist ** 2)
    return sse


def visualize_SSE(sse, cluster_num):
    """
    展示不同聚类个数的误差平方和
    """
    fig = plt.figure(figsize=(6, 6), dpi=80)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(cluster_num, sse, 'k--', marker="o", markerfacecolor="r", markeredgecolor="k")
    ax.set_xlim([min(cluster_num) - 1, max(cluster_num) + 1])


def _visualize(ax, data, labels, centers):
    """
    将聚类结果可视化
    """
    colors = ["#BAE7FC", "#3CAFFA", "#82CCFC", "#0C5FFA", "k"]
    ax.scatter(data[:, 0], data[:, 1], c=[colors[i] for i in labels], marker="o", alpha=0.8)
    ax.scatter(centers[:, 0], centers[:, 1], marker="*", c=colors, edgecolors="white",
               s=600., linewidths=2)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)


def run(data):
    """
    程序的入口
    """
    # 创建一个图形框
    fig = plt.figure(figsize=(10, 10), dpi=80)
    sse = []
    for i in range(2, 6):
        ax = fig.add_subplot(2, 2, i-1)
        model = train_model(data, i)
        sse.append(compute_SSE(model, data))
        _visualize(ax, data, model.labels_, model.cluster_centers_)
    visualize_SSE(sse, range(2, 6))
    plt.show()


if __name__ == "__main__":
    np.random.seed(13003)
    data = generate_data(1000)
    run(data)
