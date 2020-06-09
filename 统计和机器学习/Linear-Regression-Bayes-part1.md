# 线性回归和贝叶斯的线性回归

本文源码地址：[AnBlogs]()

## 问题是什么

这个h2标题令人疑惑，不就是线性回归么，高中就会啦。
$$
y=\theta^Tx+b
$$
或者也写成这样：
$$
y=\theta^Tx,x_0=1
$$
用一个$x$的分量代表偏置项$b$，为了方便表述，以下都使用这个记号。

线性回归的目标是，**用线性的函数描述任何数据，使得误差最小**。误差就是这样：
$$
L^{(i)}=||y^{(i)}-(\theta^Tx^{(i)})||_2^2
$$
这样好像理所当然。

这样直观的理解固然没什么毛病，为了理解更深入，必须有**概率解释**(probablistic perspective)做支撑。

统计学在做的事情是拟合概率密度函数，也就是当看见一个**输入**特征$x$的时候，要得到**预测值**$y$取值的概率分布，然后取最有可能的预测值**输出**。翻译成数学语言，就是要求$p(y|x)$。

对于线性回归问题来说，我们是在做这样的假设：**对于一个特征$x$，真实值$y$应该和$\theta^Tx$相去不远**。这个描述很宽泛，有很多概率分布可能符合这个描述。对于连续取值的变量，我们喜欢正态分布：
$$
p(y|x)=\frac{1}{\sqrt{2\pi}\sigma}\exp(-\frac{(y-\theta^Tx)^2}{2\sigma^2})
$$
这是在假设要预测的$y$服从一个以$\theta^Tx$为**均值**、$\sigma^2$为**方差**的正态分布。

这样一来，问题就不再是**最小化误差**，而是**估计参数$\theta,\sigma$**。

## 估计过程

估计参数的过程应该怎样用概率描述呢？我们都知道模型训练的过程是**给定一些样本数据$D$，用这些来估计参数**，说得更“数学”一点，就是**对于给定的样本数据$D$，参数的概率密度函数是什么？**。对于上面的情况，就是要求：
$$
p(\theta,\sigma|D)
$$
这是**后验**(posteri)分布。展开成(贝叶斯)统计喜欢的形式：
$$
p(\theta,\sigma|D)\propto p(\theta,\sigma)p(D|\theta,\sigma)
$$
线性系数$\theta$和$\sigma$通常相互独立，或者说我们喜欢把它们假设成相互独立的：
$$
p(\theta,\sigma|D)\propto p(\theta)p(\sigma)p(D|\theta,\sigma)
$$
接下来的任务是计算**似然**(likelihood)$p(D|\theta,\sigma)$和假设**先验**(priori)$p(\theta),p(\sigma)$。

## 似然

### 表达似然

我们假设每个样本$x^{(i)},y^{(i)}$之间都是相互独立的：
$$
p(D|\theta,\sigma)=\prod_ip(x^{(i)},y^{(i)}|\theta,\sigma)
$$
对于一行来说，这一行数据出现的概率：
$$
p(x^{(i)},y^{(i)}|\theta,\sigma)=\frac{1}{\sqrt{2\pi}\sigma}\exp(-\frac{(y^{(i)}-\theta^Tx^{(i)})^2}{2\sigma^2})
$$
总的似然：
$$
p(D|\theta,\sigma)=\prod_ip(x^{(i)},y^{(i)}|\theta,\sigma)=\frac{1}{(\sqrt{2\pi}\sigma)^{N_D}}\exp(-\frac{\sum_i(y^{(i)}-\theta^Tx^{(i)})^2}{2\sigma^2})
$$
其中，计数变量$N_D$表示样本个数(行数)。

这样计算的似然还是挺简单的！

### 最大似然估计 (MLE)

最大似然估计是频率学派常用的手法，就是对$\theta,\sigma$求似然的最大值，把此时参数的取值作为估计值。这种手法不一定足够令人满意，但能满足绝大多数情况。

取对数：
$$
L(\theta,\sigma)=\ln p(D|\theta,\sigma)=
\sum_i\ln p(x^{(i)},y^{(i)}|\theta,\sigma)=
-N_D\ln\sigma-N_D\ln\sqrt{2\pi}-\frac{\sum_i(y^{(i)}-\theta^Tx^{(i)})^2}{2\sigma^2}
$$
参数$\sigma$：
$$
\frac{\partial}{\partial \sigma}L=-\frac{N_D}{\sigma}+\frac{\sum_i(y^{(i)}-\theta^Tx^{(i)})^2}{\sigma^3}=-\frac{N_D\sigma^2-\sum_i(y^{(i)}-\theta^Tx^{(i)})^2}{\sigma^3}
$$
算出来：
$$
\hat\sigma^2=\frac{\sum_i(y^{(i)}-\theta^Tx^{(i)})^2}{N_D}
$$
参数$\theta$:
$$
\frac{\partial}{\partial\theta_j}L=\frac{1}{\sigma^2}\sum_i(y^{(i)}-\theta^Tx^{(i)})x^{(i)}_j
$$
算出来：
$$
\sum_i(y^{(i)}-\hat\theta^Tx^{(i)})x^{(i)}_j=0
$$
矩阵形式可以简化：
$$
\sum_iy^{(i)}x^{(i)}_j=y^Tx_j,\sum_ix^{(i)}x_j^{(i)}=Xx
\Rightarrow
y^Tx_j=\theta^TXx
$$
可以通过解这个线性方程组直接得出训练结果。

方差$\sigma$的估计结果不能用于模型的预测，故常常省略。

## 后验 (Posteri)

后验解释了「正则」的意义，更是贝叶斯统计分析中不可或缺的一环。

从这里开始，为了简化计算，我们省略掉对方差$\sigma$的估计，并将它当作「超参数」。这是因为$\sigma$不参与最大似然估计和(之后讲到的)最大后验估计，而主流的实现只关注这两种方式。当然，要完成完整的贝叶斯分析，一定要考虑$\sigma$。

### 先验假设

假设先验和似然有相同形式：
$$
p(\theta_j)=\frac{1}{\sqrt{2\pi}\sigma_j}\exp(-\frac{(\theta_j-\mu_j)^2}{2\sigma_j^2})
$$
这个正态分布中的参数$\mu_j,\sigma_j$也可以通过一些方式估计(Hierarchical Bayes)，但这不是这篇文章的重点。这里姑且假设他们是不能直接通过训练得到的「超参数」。

### 表达后验

把似然乘上刚才写的先验：
$$
p(\theta,\sigma|D)\propto
\frac{1}{(\sqrt{2\pi}\sigma)^{N_D}\sqrt{2\pi}\sigma_j}
\exp(-\frac{\sum_i(y^{(i)}-\theta^Tx^{(i)})^2}{2\sigma^2}-
\sum_j\frac{(\theta_j-\mu_j)^2}{2\sigma_j^2})
$$

### 最大后验估计(MAP)

取对数，省略一些不必要的项：
$$
L(\theta)=\ln p(\theta,\sigma|D)=
-\frac{\sum_i(y^{(i)}-\theta^Tx^{(i)})^2}{2\sigma^2}
-\sum_j\frac{(\theta_j-\mu_j)^2}{2\sigma_j^2}
$$
求导：
$$
\frac{\partial}{\partial\theta_j}L=\frac{1}{\sigma^2}\sum_i(y^{(i)}-\theta^Tx^{(i)})x^{(i)}_j-\sum_j\frac{\theta_j-\mu_j}{\sigma_j^2}
$$
写成矩阵形式：
$$
\lambda_j=\frac{1}{\sigma_j^2},\sum_j\frac{\theta_j-\mu_j}{\sigma_j^2}=\lambda^T(\theta-\mu)
$$
矩阵形式的方程：
$$
y^Tx_j-\theta^TXx-\lambda^T(\theta-\mu)=0
$$
依旧是一个可解的线性方程组。

注意到，这里的$\lambda$就是我们常说的「正则」项系数。一般的「岭回归」目标函数和我们取最大后验估计的目标函数具有相同形式：
$$
L(\theta)=\frac{1}{2}\sum_i(y^{(i)}-\theta^Tx^{(i)})^2+\frac{\lambda}{2}\theta^2
$$
「岭回归」只是我们这个例子的一个特殊情况：

1. 岭回归假设所有$\sigma_j$相同，用一个单独的超参数$\lambda$表示。
2. 岭回归直接假设$\mu=0$。

我们也就可以更新一下对正则的理解。

### 正则项

从损失函数的角度理解「正则项」：

- 要求参数$\theta$和某个指定值$\mu$相差不远，防止一些特别的数据过分影响模型。
- 超参数$\lambda$控制上一条的「力度」，$\lambda$越大，$\theta$偏移得到的「惩罚」就越大。

从先验的角度理解「正则项」：

- 假设参数$\theta$的取值和某个值$\mu$相去不远，用$\lambda=\frac{1}{\sigma^2}$描述到底相去多远。
- 正态分布符合上条描述。

这样就完成训练啦。
