# 把玩正态分布

本文把深入研究正态分布的方方面面，为统计学计算提供基础参考。

本文的md源码链接：

## 习惯使用的记号

本人习惯称之为「正态分布」而不是「高斯分布」，使用英文时习惯称之为 *Gaussian Distribution* 而不是 *Normal Distribution*。

单变量正态分布的概率密度函数如下：
$$
N(x|\mu,\sigma)=\frac{1}{\sqrt{2\pi\sigma^2}}\exp(\frac{(x-\mu)^2}{2\sigma^2})
$$
表达的含义是，随机变量$x$，服从一个分布，这个分布由参数$\mu,\sigma$描述。

如果你经过考研，或是其他类型的考试训练，你可能习惯于这样的记号:
$$
X\sim N(\mu,\sigma^2),f_X(x)=\frac{1}{\sqrt{2\pi\sigma^2}}\exp(\frac{(x-\mu)^2}{2\sigma^2})
$$
表达的是相同含义，前者更加简洁，故使用前者。

多变量/向量的正态分布概率密度函数如下：
$$
N(\vec x|\vec\mu,\Sigma)=\frac{1}{(2\pi)^{D/2}|\Sigma|^{1/2}}\exp(-\frac{1}{2}(\vec x-\vec\mu)^T\Sigma^{-1}(\vec x-\vec\mu))
$$
$\mu$是「均值」，$\Sigma$是「协方差矩阵」，$D$是「维数」，也就是$\vec x$的维数。这里提醒你，$\mu,\Sigma$是人为指定的参数，而不是计算得到的，以防你习惯于认为均值和方差是计算出来的。当然，如果计算这个分布的均值和协方差矩阵，就会得到$\mu,\Sigma$。

可以很容易验证，单变量下的表达式是它的特殊情况。

一下记号均省略$\vec{}$，方便打字。

## 似然

有一系列样本$\{x^{(i)}\}$，也就是一系列测量得到的$\vec x$。这个样本对应一个似然：
$$
\prod_iN(x^{(i)}|\vec\mu,\Sigma)=(2\pi)^{-DN/2}|\Sigma|^{-N/2}\exp(-\frac{1}{2}\prod_i(\vec x^{(i)}-\vec\mu)^T\Sigma^{-1}(\vec x^{(i)}-\vec\mu))
$$

## 两个随机向量的条件分布

### 结论

把一个完整的向量看成两个，把原来的分布看成这两个向量的联合分布，这两个随机向量$x_1,x_2$都分别服从正态分布，参数为$\mu_1,\mu_2,\Sigma_{11},\Sigma_{22}$。

这些新的参数由原来的参数拆分而成：
$$
\mu=\begin{pmatrix}\mu_1\\\mu_2\end{pmatrix},\Sigma=\begin{pmatrix}\Sigma_{11}&\Sigma_{12}\\\Sigma_{21}&\Sigma_{22}\end{pmatrix}
$$
给协方差矩阵的逆矩阵起个名字：
$$
\Lambda=\Sigma^{-1}=\begin{pmatrix}\Lambda_{11}&\Lambda_{12}\\\Lambda_{21}&\Lambda_{22}\\\end{pmatrix}
$$
两个随机向量的分布：
$$
p(x_1)=N(x_1|\mu_1,\Sigma_{11}),p(x_2)=N(x_2|\mu_2,\Sigma_{22})
$$
最重要的，条件分布：
$$
p(x_1|x_2)=N(x_1|\mu_{1|2},\Sigma_{1|2})
$$
参数：
$$
\mu_{1|2}=\mu_1+\Sigma_{12}\Sigma_{22}^{-1}(x_2-\mu_2)=\Sigma_{1|2}(\Lambda_{11}\mu_1-\Lambda_{12}(x_2-\mu_2))\\ \Sigma_{1|2}=\Sigma_{11}-\Sigma_{12}\Sigma_{22}^{-1}\Sigma_{21}=\Lambda_{11}^{-1}
$$
这是个极端重要的结论！很复杂，以下慢慢推导。

