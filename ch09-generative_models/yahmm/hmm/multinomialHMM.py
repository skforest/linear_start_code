# -*- coding: UTF-8 -*-
"""
此脚本用于实现multinomial HMM
"""


# 保证脚本与Python3兼容
from __future__ import print_function

import numpy as np
import scipy as sp
from scipy.misc import logsumexp
from sklearn.utils.extmath import safe_sparse_dot
try:
    from hmm.utils.viterbi import viterbi
except:
    import sys
    # 在Windows下运行此脚本需确保Windows下的命令提示符(cmd)能显示中文
    print(
        """
        Python的运行速度不快。为了提高运算速度，请使用
        'python setup.py build_ext --inplace'生成相应的C扩展
        """,
        file=sys.stdout)
    from hmm.utils.viterbipy import viterbi


class MultinomialHMM(object):
    """
    多项式HMM(First-order hidden Markov model with multinomial event model)

    参数
    ----
    alpha : double, 平滑项（Laplace/Lidstone smoothing）
    """
    def __init__(self, alpha=1.):
        self.alpha = alpha

    def fit(self, X, Y, lengths):
        """
        训练模型

        参数
        ----
        X : {np.array 或者scipy.sparse.csr_matrix}，维度为(样本数，特征数)
            数据的特征矩阵

        y : {np.array}，维度为(样本数)，标签数据，每个样本的隐藏状态

        lengths : {np.array[int]}，表示每个句子的长度。它的和应等于样本数

        返回
        ----
        self : MultinomialHMM
        """
        alpha = self.alpha
        assert alpha > 0, "The alpha must be > 0"
        if sp.sparse.issparse(X):
            pass
        else:
            X = np.atleast_2d(X)
        assert np.sum(lengths) == X.shape[0],\
            "The sum of lengths must equal to num of samples"
        classes, Y = np.unique(Y, return_inverse=True)
        Y = Y.reshape(-1, 1) == np.arange(len(classes))
        lengths = np.array(lengths)
        start, end = self._get_start_end(lengths)
        # 计算状态的初始分布
        init_prob = np.log(Y[start].sum(axis=0) + alpha)
        init_prob -= logsumexp(init_prob)
        # 计算状态间的转移矩阵
        trans_prob = np.log(self._compute_trans_prob(Y, end, len(classes)) + alpha)
        trans_prob -= logsumexp(trans_prob, axis=1)[:, np.newaxis]
        # 计算在状态已知的情况下，各特征的条件概率
        emit_prob = np.log(safe_sparse_dot(Y.T, X) + alpha)
        emit_prob -= logsumexp(emit_prob, axis=1)[:, np.newaxis]
        self.init_prob_ = init_prob
        self.trans_prob_ = trans_prob
        self.emit_prob_ = emit_prob
        self.classes_ = classes
        return self

    def _compute_trans_prob(self, Y, end, class_num):
        """
        计算各状态间的转移次数
        """
        trans = np.zeros((class_num, class_num), dtype=np.intp)
        YY = np.split(Y, end)
        for i in YY:
            for j in range(i.shape[0] - 1):
                trans[i[j], i[j+1]] += 1
        return trans

    def _get_start_end(self, lengths):
        """
        计算每个句子的起始点和终点
        """
        end = np.cumsum(lengths)
        start = end - lengths
        return start, end

    def predict(self, X, lengths=None):
        """
        对未知数据做预测

        参数
        ----
        X : {np.array 或者scipy.sparse.csr_matrix}，维度为(样本数，特征数)
            数据的特征矩阵

        lengths : {np.array[int]}，表示每个句子的长度。它的和应等于样本数
            若为单个句子，此值可为空(默认情况)

        返回
        ----
        y : {np.array}，维度为(样本数)，最终结果，表示每个样本的隐藏状态
        """
        if sp.sparse.issparse(X):
            pass
        else:
            X = np.atleast_2d(X)
        if lengths is None:
            _, y = viterbi(X, self.init_prob_, self.trans_prob_, self.emit_prob_)
        else:
            assert(np.sum(lengths) == X.shape[0])
            start, end = self._get_start_end(lengths)
            y = [viterbi(X[start[i]: end[i]], self.init_prob_,
                         self.trans_prob_, self.emit_prob_)[1] for i in range(start.shape[0])]
            y = np.hstack(y)
        return self.classes_[y]
