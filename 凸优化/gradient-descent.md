# 梯度下降、随机梯度下降、最速下降、梯度消失

[TOC]

## 线性回归的梯度下降

本文全程以线性回归为例，为了方便简单。如果你还不熟悉线性回归，请看：线性回归

这里对线性回归的梯度下降进行简单复习。

假设训练数据集为$(X,y)$，其中$X=\{x^{(i)}\}$为样本矩阵，$y=\{y^{(i)}\}$为预测目标，每一行$x^{(i)}$对应一个特征，上标带括号为行索引。要使用模型进行预测，输入一个特征$x$，预测值就是$\hat y=\theta^Tx+b$。

线性回归的损失函数和梯度如下：
$$
L^{(i)}=\frac{1}{2}(\theta^Tx^{(i)}+b-y^{(i)})^2,\frac{\partial L^{(i)}}{\partial \theta_j}=(\theta^Tx^{(i)}+b-y^{(i)})x_j^{(i)},\frac{\partial L^{(i)}}{\partial b}=\theta^Tx^{(i)}+b-y^{(i)}
$$
。其中上标仍然表示行索引，对应对一行数据求的损失和梯度。这样计算得到的只使用了一行数据，当然很不完备。实际算法一定要适当选择“使用哪些行”，行选择的不同，对应不同的算法种类。

得到了梯度之后，可以使用梯度不断更新参数$\theta,b$的值，多次迭代后可以得到精确的参数值。
$$
\theta^{(k+1)}=\theta^{(k)}-\eta\nabla L_\theta
$$
其中$\eta$是“学习率”

```pseudocode
# 初始化参数的值
theta = 0
bias = 0
# 不断循环，直到终止条件满足
while [some stopping criterion]:
	# 每次循环，减去对应的梯度分量和学习率的乘积
	theta -= gradient_theta * learning_rate
	bias -= gradient_bias * learning_rate
```

终止条件通常是梯度小到一定程度。每次改变的参数

若损失函数是每一行的损失求平均，$L=\frac{1}{N_D}\sum_iL^{(i)}$，相应梯度也是对每一行的平均，这样的算法叫做Batch Gradient Descent，翻译大概是“大批量”梯度下降。

与“大批量”相对应的是Stochastic Gradient Descent，翻译大概是“随机”梯度下降。