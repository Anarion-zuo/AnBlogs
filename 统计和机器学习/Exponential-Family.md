#! https://zhuanlan.zhihu.com/p/148776108
# 统一分布：指数模型家族

本文讲解和「指数分布族」有关的统计计算。机器学习中应用的诸多概率模型都可以统一到「指数族分布」下，这样的统一省去了一些不必要的重复，也为「广义线性模型」(GLM) 奠定了基础。

本文md源码地址：[AnBlog/统计和机器学习](https://github.com/Anarion-zuo/AnBlogs/blob/master/统计和机器学习/Exponential-Family.md)

[TOC]

## 是什么

很多分布的概率密度函数可以写成如下形式：
$$
p(x|\theta)=\frac{1}{Z(\theta)}h(x)\exp(\theta^T\phi(x))
$$
其中$\theta,x,\phi$等都是「向量」。也许公式很复杂，但是思想很简单，*分布函数可以写成相同形式，使用相同的处理方法*。

### 字母的含义

表达式字母有点多，这里详细介绍一下。

$\theta$代表「自然参数」，$x$代表「特征」。模型训练阶段应该「估计参数」，使用模型进行预测时应该给模型「输入特征」。

$\exp$指数中的函数$\phi$，把样本特征$x$映射到另一个空间，以获得更强的拟合能力。如$\phi(x)=[x_1^2,x_1x_2,x_2^2]$，把$x$映射到了“二次”的空间。常用的映射是不映射，$\phi(x)=x$。函数的结果一定要可以和$\theta$「内积」，一定要返回维度相同的向量。

$\exp$指数中的$\theta$，是把原分布中的参数映射后的结果。如伯努利分布常把参数$\theta$这样映射$\theta=[\ln\mu,\ln(1-\mu)]$。在后面的例子中有更详细体现。

$h(x)$是可能出现的「缩放常数」(Scaling Constant)，在把原分布函数化成指数形式的时候，按需出现，写在这里提醒可能出现的情况，由于不涉及参数，训练时具体意义小。

$Z(\theta)$是参数的归一化系数，称为「分配函数」(Partition Function)，涉及到参数，十分重要！

归一化系数可以通过积分求得：
$$
Z(\theta)=\int dx\;h(x)\exp(\eta(\theta)^T\phi(x))
$$
我们更喜欢它的对数$A(\theta)=\ln Z(\theta)$，称为「分配函数对数」(Log Partition Function)。使用$A$而不使用$Z$，原来的概率密度函数的统一形式写成：
$$
p(x|\theta)=h(x)\exp(\eta(\theta)^T\phi(x)-A(\theta))
$$
有时候还不写倒数形式：
$$
g(\theta)=\frac{1}{Z(\theta)}
$$


## 把一些分布的概率密度函数化成指数分布族形式

这里举例把一些分布函数化成指数族的形式，同一个分布可能有不同的写法。

### 伯努利分布

原分布函数：
$$
p(x|\mu)=\mu^x(1-\mu)^{1-x}
$$
取对数：
$$
\ln p(x|\mu)=x\ln\mu+(1-x)\ln(1-\mu)
$$
取指数：
$$
p(x|\mu)=\exp(x\ln\mu+(1-x)\ln(1-\mu))=\exp(\theta^T\phi(x)),\theta=[\ln\mu,\ln(1-\mu)],\phi(x)=[x,1-x]
$$
这个形式「冗余」了，$\mu$和$1-\mu$「不是相互独立」的。由于$\mu+(1-\mu)=1$，不需要二维的向量也可以表达伯努利分布，只需要修改「取对数」：
$$
\ln p(x|\mu)=x\ln\mu+(1-x)\ln(1-\mu)=x\ln\frac{\mu}{1-\mu}+\ln(1-\mu)
$$
再取指数：
$$
p(x|\mu)=(1-\mu)\exp(x\ln\frac{\mu}{1-\mu}),\frac{1}{Z}=1-\mu,\phi(x)=x,\theta=\ln\frac{\mu}{1-\mu}
$$
这里的$\theta$用原有参数$\mu$表达，就是把原分布的参数映射成了$\theta$。模型训练后，得到参数$\theta$，可以通过参数$\theta$得到参数$\mu$:
$$
\mu=\frac{1}{1+e^{-\theta}}
$$
带入$A$:
$$
A=-\ln(1-\mu)=\ln(1+e^\theta)
$$

如果你对伯努利分布的实际应用感兴趣，请看：[Logistic回归]()

### 多项伯努利分布 (Multinoulli)

原分布函数：
$$
p(x|\mu)=\prod_c\mu_c^{x_c}
$$
其中$x_c=I(x=c)$，表示$x$是否取某个离散的值。

取对数：
$$
\ln p(x|\mu)=\sum_cx_c\ln\mu_c
$$
取指数：
$$
p(x|\mu)=\exp(\sum_cx_c\ln\mu_c),\theta=\ln\mu,\phi(x)=x
$$
这个形式也冗余了。由于$\sum_c\mu_c=1$，可将其中一个参数用其他表示，做如下修改：
$$
\mu_C=1-\sum_{c=1}^{C-1}\mu_c,\ln p(x|\mu)=\sum_{c=1}^{C-1}x_c\ln\mu_c+(1-\sum_{c=1}^{C-1}x_c)\ln(1-\sum_{c=1}^{C-1}\mu_c)=\sum_{c=1}^{C-1}x_c\ln\mu_c+(1-\sum_{c=1}^{C-1}x_c)\ln\mu_C
$$
提出$\sum_{c=1}^{C-1}x_c$：
$$
\ln p(x|\mu)=\ln\mu_C+\sum_{c=1}^{C-1}x_c\ln\frac{\mu_c}{\mu_C}
$$
取指数：
$$
p(x|\mu)=\mu_C\exp(\sum_{c=1}^{C-1}x_c\ln\frac{\mu_c}{\mu_C})
$$
带入指数形式$\exp(\theta^T\phi(x)-A(\theta))$，各个部分：
$$
\theta=[\ln\frac{\mu_1}{\mu_C},...,\ln\frac{\mu_{C-1}}{\mu_C}],\phi(x)=[I(x=1),...,I(x=C-1)],A(\theta)=-\ln\mu_C
$$
从$\theta$变回$\mu$:
$$
\mu_c=\frac{e^{\theta_c}}{1+\sum_{c'=1}^{C-1}e^{\theta_{c'}}},\mu_C=1-\frac{\sum_{c=1}^{C-1}e^{\theta_c}}{1+\sum_{c=1}^{C-1}e^{\theta_c}}=\frac{1}{1+\sum_{c=1}^{C-1}e^{\theta_c}}
$$
带入$A$:
$$
A(\theta)=\ln(1+\sum_{c=1}^{C-1}e^{\theta_c})
$$

如果你对多项伯努利分布的实际应用感兴趣，请看：[朴素贝叶斯分类器]()

### 单变量的正态分布

正态分布本身就具有指数形式，比较方便：
$$
p(x|\mu,\sigma^2)=\frac{1}{\sqrt{2\pi\sigma^2}}\exp(-\frac{1}{2\sigma^2}(x-\mu)^2)=\frac{1}{\sqrt{2\pi\sigma^2}}\exp(-\frac{1}{2\sigma^2}x^2+\frac{\mu}{\sigma^2}x-\frac{1}{2\sigma^2}\mu^2)
$$
可以直接看出结果：
$$
\theta=[\frac{\mu}{\sigma^2},-\frac{1}{2\sigma^2}],\phi(x)=[x,x^2],A(\theta)=\frac{1}{2\sigma^2}\mu^2+\frac{1}{2}\ln2\pi\sigma^2
$$
从$\theta$到$\mu,\sigma$:
$$
\sigma^2=-\frac{2}{\theta_2},\mu=\theta_1\sigma^2=-\frac{2\theta_1}{\theta_2}
$$
带回$A$:
$$
A(\theta)=\frac{1}{2}\theta_1\mu+\frac{1}{2}\ln2\pi(-\frac{2}{\theta_2})=-\frac{\theta^2_1}{\theta_2}+\frac{1}{2}\ln4\pi-\frac{1}{2}\ln(-\theta_2)
$$

### 操作总结

以上操作非常固定：

1. 取对数，化简。
2. 利用参数已经存在的依赖关系进一步化简。
3. 取指数，从指数形式中看出$\theta,\phi,A$。
4. 求从$\theta$到原参数的映射，带回$A$。

### 举个反例

反例有很多，这里用「单变量的均匀分布」。

概率密度函数：
$$
p(x|l,r)=\frac{1}{r-l}
$$
概率密度函数和$x$无关，故无法化成完整指数形式。

这个分布的参数对数据极端敏感，最大似然估计的结果是$l=\min x^{(i)},r=\max x^{(i)}$。数据最值改变时，参数的估计随最值变化，这样的变化不能用「初等函数」的组合表达。

## 分配函数 (Partition Function)

此处推导分配函数的重要性质：

> 对分配函数的对数求导，得到统计累计量 (Cumulant)。

所以分配函数又叫「累计量生成函数」。直观地说，就是分配函数的一阶导数（梯度）是「均值」，二阶导数（厄米矩阵）是「协方差矩阵」。对于多变量情况，得到二阶导数后，通常不再继续求导了。

### 计算

求一阶导数：
$$
\begin{align}\frac{dA}{d\theta}=&\frac{\frac{d}{d\theta}\int dx\;h(x)\exp(\theta^T\phi(x))}{\int dx\;h(x)\exp(\theta^T\phi(x))}\\=&\frac{\int dx\;h(x)\phi(x)\exp(\theta^T\phi(x))}{\exp(A(\theta))}\\=&\int dx\;h(x)\phi(x)\exp(\theta^T\phi(x)-A(\theta))\\=&\int dx\;\phi(x)p(x)=E[\phi(x)]\end{align}
$$
求二阶导数，求导的$\theta$是同一个，得到协方差矩阵的对角线上元素：
$$
\begin{align}\frac{d^2A}{d\theta^2}=&\int dx\;(\phi(x)h(x)\exp(\theta^T\phi(x)-A(\theta))(\phi(x)-A'(\theta)))\\=&\int dx\;\phi(x)p(x)(\phi(x)-A'(\theta))\\=&\int dx\;\phi(x)p(x)(\phi(x)-E(\phi(x)))\\=&\int dx\;\phi(x)^2p(x)-E[\phi(x)]\int dx\;\phi(x)p(x)\\=&E[\phi^2(x)]-E[\phi(x)]^2=var[\phi(x)]\end{align}
$$
当两次求导的$\theta$不是同一个，得到非对角线元素:
$$
\frac{\partial^2A}{\partial\theta_i\partial\theta_j}=E[\phi_i(x)\phi_j(x)]-E[\phi_i(x)]E[\phi_j(x)]=cov(\phi(x))
$$
以上分别计算了对角线和非对角线情况，只是为了更清晰地讲解，可以直接计算一般情况。建议自己算一遍，练习一下简单的加减乘除微积分。

### 伯努利分布举个例子

一阶导数：
$$
\frac{dA}{d\theta}=\frac{d}{d\theta}\ln(1+e^\theta)=\frac{e^\theta}{1+e^\theta}=\frac{1}{1+e^{-\theta}}=\mu
$$
二阶导数：
$$
\frac{d^2A}{d\theta^2}=\frac{e^\theta(1+e^\theta)-e^\theta\cdot e^\theta}{(1+e^\theta)^2}=\frac{1}{1+e^\theta}\cdot\frac{e^{\theta}}{1+e^\theta}=\frac{1}{1+e^{-\theta}}\cdot\frac{e^{-\theta}}{1+e^{-\theta}}=\mu(1-\mu)
$$
还是建议自己算一遍，练习一下简单的加减乘除微积分。

## 似然

### 表达似然

把所有概率乘起来：
$$
p(D|\theta)=g(\theta)^N(\prod_ih(x^{(i)}))\exp(\theta^T\sum_i\phi(x^{(i)}))
$$
向量加法可以写成分量加法，并用新记号代替：
$$
\sum_i\phi(x^{(i)})=[\sum_i\phi_1(x^{(i)}),...,\sum_i\phi_D(x^{(i)})]=\phi(D)
$$
取对数：
$$
l(\theta)=\ln p(D|\theta)=N\ln g(\theta)+\theta^T\phi(D)+\sum_i\ln h(x^{(i)})=-NA(\theta)+\theta^T\phi(D)+\sum_i\ln h(x^{(i)})
$$

### 最大似然估计

求导：
$$
\nabla l=-N\nabla A+\phi(D)=-NE(\phi(x))+\phi(D)
$$
结果惊人地简单：
$$
E(\phi(x))=\frac{1}{N}\phi(D)=\frac{1}{N}\sum_i\phi(x^{(i)})
$$
只要分布的均值确定，就可以输入数据，获得最大似然估计。求均值$E[\phi(x)]$不是统计学过程，是概率论过程，和样本数据无关。

### 伯努利分布举个例子

伯努利分布的特征变换：
$$
\phi(x)=x\Rightarrow E[\phi(x)]=E[x]=\mu
$$
参数的最大似然估计：
$$
\mu=\frac{1}{N}\sum_i\phi(x^{(i)})=\frac{1}{N}\sum_ix^{(i)}
$$
就是我们熟悉的！

### 多项伯努利分布举个例子

多项伯努利分布的特征变换：
$$
\phi(x)=[I(x=1),...,I(x=C-1)]
$$
求均值：
$$
E(\phi(x))=[E[I(x=1)],...,E[I(x=C-1)]]
$$
求分量，带入概率论中求均值的公式：
$$
E[I(x=c)]=\sum_{x=1}^C(I(x=c)(\prod_{c'}\mu_{c'}^{I(x=c)}))=\mu_c
$$
带入最大似然估计：
$$
\mu_c=\frac{1}{N}\sum_iI(x^{(i)}=c)=\frac{N_c}{N}
$$
就是我们熟悉的！

## 先验和后验

### 假设先验

选取和似然具有相同形式的先验。
$$
p(\theta|\nu_0,\tau_0)\propto g(\theta)^{\nu_0}\exp(\theta^T\tau_0)
$$
此处$g(\theta)$和之前的相同。比较在似然中的变量位置，标量$\nu_0$为「初始数据个数」，向量$\tau_0$为「初始数据」。

### 求解后验

似然中$\phi(D)$是一系列的求和。为了强调这一点，我们采用记号，表示从$1$到$N$的$\phi$求和，这是个向量求和，结果还是向量。
$$
s_N=\sum_{i=1}^N\phi(x^{(i)})
$$
将具有相同形式的先验，和似然相乘，得到后验：
$$
p(\theta|D)\propto p(\theta|\nu_0,\tau_0)p(D|\theta)\propto g(\theta)^{\nu_0+N}(\prod_ih(x^{(i)}))\exp(\theta^T(\tau_0+\sum_i\phi(x^{(i)})))
$$
直接看出后验的形式：
$$
\begin{align}p(\theta|D)=&p(\theta|\nu_0+N,\tau_0+s_N)\\=&\frac{1}{Z(\nu_0,\tau_0,s_N)}g(\theta)^{\nu_0+N}(\prod_ih(x^{(i)}))\exp(\theta^T(\tau_0+s_N))\\=&(\prod_ih(x^{(i)}))\frac{1}{Z(\nu_N,\tau_N)}g(\theta)^{\nu_N}\exp(\theta^T\tau_N)\end{align}
$$
先验、后验都具有和指数分布族相同的形式，上面的书写省略了一些归一化系数。先验参数$\nu_0,\tau_0$的意义也更加明确了。

### 最大后验估计

求最大后验估计的过程和求最大似然估计的过程相同。

取对数：
$$
l(\theta)=\ln p(\theta|D)=-\ln Z+\nu_N\ln g(\theta)+\theta^T\tau_N=-\ln Z-\nu_NA(\theta)+\theta^T\tau_N
$$
求导：
$$
\nabla l(\theta)=-\nu_NE[\tau_0+\phi(x)]+\tau_N=\tau_N-\nu_N(\tau_0+E[\phi(x)])
$$
注意$E[]$中的是「随机变量」，外面的$\tau_0,\tau_N$是由样本数据和超参数决定的「常数」。

最终给出结果：
$$
E[\phi(x^{(i)})]=\frac{\tau_N}{\nu_N}-\tau_0=\frac{\tau_0+\sum_i\phi(x^{(i)})}{\nu_0+N}-\tau_0
$$
取特殊情况$\nu_0=0,\tau_0=0$，就是最大似然估计的结果！

### 预测分布

$$
p(x|D)=\int d\theta\;p(x|\theta)p(\theta|D)=\int d\theta\;\frac{1}{Z(\theta)}h(x)\exp(\theta^T\phi(x))(\prod_ih(x^{(i)}))\frac{1}{Z(\nu_N,\tau_N)}g(\theta)^{\nu_N}\exp(\theta^T\tau_N)
$$

进一步求解需要带入具体分布和数值。