#! https://zhuanlan.zhihu.com/p/146934905

# 「伯努利分布+朴素贝叶斯」分类器

在神经网络技术还不成熟的时候，朴素贝叶斯分类器(NBC)是文档分类的利器。即便是在神经网络满地走的今天，朴素贝叶斯模型依然有很大的价值。进行文档分类时，这个模型只需要进行几次简单的循环，就可以给出结果，在一些对结果要求不是特别高、对性能要求很高的场景下，具有很大的价值。

这篇文章以文档分类问题引出，重点将特征的伯努利分布(Bernoulli)带入朴素贝叶斯模型，熟悉贝叶斯统计的流程和计算。

本文的md源码在这里：[AnBlog/统计和机器学习](https://github.com/Anarion-zuo/AnBlogs/blob/master/统计和机器学习/Ber-NBC.md)

@[TOC](目录)

## 可以解决的问题

在进行文档分类之前，需要对文本进行一些处理。对于这个模型来说，最关键的一步是建立一个特征(feature)向量，向量的每个分量(entry)对应文本中可能出现的一个单词，取值$0,1$，表示存在/不存在。

这样的一个分量用伯努利分布描述，参数为$\theta$：
$$
p(x=1|\theta)=\theta,p(x=0|\theta)=1-\theta
$$
在其他问题中，这个分布可能取正态分布，或其他分布，但过程的其他部分大同小异。

建立这样的一个从「单词」到「$0,1$」的映射，可以通过简单的哈希表实现。一段文本中可能出现各种各样的单词，为了保证完备，一段文本对应的特征可能特别多，可能包含所有的英语单词、中文字符，以及世界上的各种其他语言！一定存在一些更省空间的优化，但这不是这篇文章的重点。

模型的目标由需求决定，通常是个二分类问题，判断邮件是/不是垃圾邮件。这篇文章讨论多类分类问题，目标$y$服从多项的伯努利分布(Multinoulli)，参数为$\pi$：
$$
p(y|\pi)=\prod_c\pi_c^{I(y=c)},\sum_c\pi_c=1
$$
解决问题的过程，就是根据现有的数据$D$，估计参数$\theta,\pi$，从而求目标$y$未来取某值的概率$p(y=…)$。

## 「朴素」的意思

「朴素」指的是假设对象的特征都相互独立，这当然不是一个完美的假设，所以才「朴素」(naive)。也就是说，对象特征$\vec x$的概率分布函数，是各个特征$x_j$的概率分布函数的乘积：
$$
p(\vec x)=\prod_{j=1}^Dp(x_j)
$$
## 具体要算什么

假设一个多类分类问题，在具有数据集合$D$的时候，看见一些特征$\vec x$时，目标$y$应取何值。目标$y$由概率分布描述：
$$
p(y=c|\vec x,D)
$$
用这个模型进行预测：
$$
p(y=c|\vec x,D)\propto p(y=c|D)p(\vec x|y=c,D)=p(y=c|D)\prod_jp(x_j|y=c,D)
$$
模型的目标是分别表达出$p(y=c|D),p(x_j|y=c,D)$。

## 数据情况和分布假设

假设特征$x$都只能取得两个离散的值$0,1$，表示「是否存在」，可以用伯努利分布描述这样的数据：
$$
p(x_j|\theta_j)=\theta_j^{x_j}(1-\theta_j)^{1-x_j}
$$
$x$当然可以取其他的值和分布，取值连续时可以取正态分布，取值为多个离散值时可以是多项伯努利分布。

为了让模型具备更多数据，参数$\theta$和目标分类$c$发生依赖，不同的$c$对应不同的参数$\theta$，则要估计的参数$\theta$是一个矩阵$\theta_{jc}$：
$$
p(x_j|y=c,\theta_{jc})=\theta_{jc}^{x_j}(1-\theta_{jc})^{1-x_j}
$$
还未完成的是表达$p(\theta_{jc}|D)$。

$y$可以取离散的多个不同值，$y|D$和特征$x$无关，可以通过多项伯努利分布描述：
$$
p(y|\pi)=\prod_c\pi_c^{I(y=c)},\sum_c\pi_c=1
$$
参数$\pi$也需要估计。

写出联合后验分布：
$$
p(\theta,\pi|D)\propto p(\theta,\pi)p(D|\theta,\pi)=p(\theta)p(\pi)p(D|\theta,\pi)
$$


## 似然 (Likelihood)

接上式似然：
$$
p(D|\theta,\pi)=\prod_ip(x^{(i)},y^{(i)}|\theta,\pi)=\prod_ip(x^{(i)}|\theta,\pi)p(y^{(i)} |\theta,\pi)=\prod_ip(x^{(i)}｜\theta)p(y^{(i)} |\pi)
$$
其中，对每个特征$j$：
$$
p(x^{(i)}|\theta)=\prod_{j=1}^Dp(x_j^{(i)}|\theta_j)
$$
为不同的分类设置不同的参数$\theta$以增加模型的复杂度：
$$
p(x_j^{(i)}|\theta_{jc})=\prod_cp(x_j^{(i)}|\theta_{jc})^{I(y^{(i)}=c)},p(x_j^{(i)}|\theta_{jc})=\theta_{jc}^{x_j^{(i)}}(1-\theta_{jc})^{1-x_j^{(i)}}
$$


## 最大似然估计 (MLE)

取对数：
$$
\ln p(D|\theta,\pi)=\ln \prod_ip(x^{(i)},y^{(i)}|\theta,\pi)=\sum_i(\ln p(y^{(i)}|\pi)+\sum_j\ln p(x^{(i)}_j|\theta_j))
$$
$y$部分：
$$
\sum_i\ln p(y^{(i)}|\pi)=\sum_i\sum_cI(y^{(i)}=c)\times\ln\pi_c=\sum_cN_c\ln\pi_c
$$
$x$部分：
$$
\sum_i\sum_j\ln p(x^{(i)}_j|\theta_j)=\sum_j\sum_c\sum_{i:y^{(i)}=c}(x_j^{(i)}\ln\theta_{jc}+(1-x_j^{(i)})\ln(1-\theta_{jc}))
$$

边界条件：
$$
\sum_c\pi_c=1
$$
以上确定了最大似然估计的最优化问题，以下分别求参数值。

目标函数：
$$
L(\theta,\pi)=\sum_j\sum_c\sum_{i:y^{(i)}=c}(x_j^{(i)}\ln\theta_{jc}+(1-x_j^{(i)})\ln(1-\theta_{jc}))+\sum_cN_c\ln\pi_c-\lambda(\sum_c\pi_c-1)
$$
计数记号：
$$
N_c=\sum_iI(y^{(i)}=c),N_D=\#rows=\sum_c N_c=\sum_i1
$$


参数$\pi$：
$$
\frac{\partial}{\partial \pi_c}L(\theta,\pi)=\frac{N_c}{\pi_c}-\lambda=0\Rightarrow N_c=\lambda\pi_c
$$
带入边界条件：
$$
N_D=\sum_cN_c=\lambda\sum_c\pi_c=\lambda
$$
也就是说：
$$
\hat\pi_c=\frac{N_c}{N_D}
$$
参数$\theta$:
$$
\frac{\partial}{\partial \theta_{jc}}L(\theta,\pi)=\sum_{i:y^{(i)}=c}(\frac{x_j^{(i)}}{\theta_{jc}}-\frac{1-x_j^{(i)}}{1-\theta_{jc}})
$$

求和：
$$
\sum_{i:y^{(i)}=c}(\frac{x_j^{(i)}}{\theta_{jc}}-\frac{1-x_j^{(i)}}{1-\theta_{jc}})=\frac{\sum_{i:y^{(i)}=c}x_j^{(i)}}{\theta_{jc}}-\frac{N_c-\sum_{i:y^{(i)}=c}x_j^{(i)}}{1-\theta_{jc}}
$$
引入新的计数变量，带入：
$$
\sum_{i:y^{(i)}=c}x_j^{(i)}=N_{jc},\sum_{i:y^{(i)}=c}(\frac{x_j^{(i)}}{\theta_{jc}}-\frac{1-x_j^{(i)}}{1-\theta_{jc}})=\frac{N_{jc}}{\theta_{jc}}-\frac{N_c-N_{jc}}{1-\theta_{jc}}
$$
算一下：
$$
\hat\theta_{jc}=\frac{N_{jc}}{N_c}
$$
结果惊人的简单！只要简单地遍历整个样本矩阵，就可以完成训练。

最大似然估计在大多数情况下可以满足需求，以下继续走贝叶斯统计的流程。

## 先验和后验

以下是锦上添花，如果前面已经看晕了最好先缓缓。

### 先验 (Priori)

假设先验具有相同形式：
$$
p(\theta_{jc})\propto\theta_{jc}^{a_{jc}-1}(1-\theta_{jc})^{b_{jc}-1},p(\pi)\propto\prod_c\pi_c^{\beta_c-1}
$$
先验也可以是其他形式，为了方便，此处及以下使用与似然相同的形式。

### 后验 (Posteri)

后验表达式：
$$
p(\theta,\pi|D)\propto p(D|\theta,\pi)p(\theta)p(\pi)=p(\theta)p(\pi)\prod_ip(x^{(i)}|\theta)p(y^{(i)} |\pi)
$$
参数$\pi$:
$$
p(\pi|D)\propto p(\pi)\prod_ip(y^{(i)}|\pi)=\prod_c\pi_c^{N_c+\beta_c-1}
$$
归一化系数：
$$
\frac{1}{Z_\pi}=\int\prod_c\pi_c^{N_c+\beta_c-1}d\pi=\prod_c\int_0^1\pi_c^{N_c+\beta_c-1}d\pi_c=\prod_c\frac{1}{N_c+\beta_c}
$$
算一下：
$$
Z_\pi=\prod_c(N_c+\beta_c)
$$
参数$\theta$:
$$
p(\theta_{jc}|D)\propto\theta_{jc}^{N_{jc}+a_{jc}-1}(1-\theta_{jc})^{N_c-N_{jc}+b_{jc}-1}
$$
归一化系数：
$$
\frac{1}{Z_{\theta_{jc}}}=
\int_0^1 d\theta_{jc}\,\theta_{jc}^{N_{jc}+a_{jc}-1}(1-\theta_{jc})^{N_c-N_{jc}+b_{jc}-1}=
B(N_{jc}+a_{jc},N_c-N_{jc}+b_{jc})
$$
Beta函数：
$$
B(x,y)=\frac{\Gamma(x)\Gamma(y)}{\Gamma(x+y)}
$$
娱乐算一下均值，后面可能要用：
$$
E[\theta_{jc}|D]=Z_{\theta_{jc}}\int_0^1 d\theta_{jc}\,\theta_{jc}\theta_{jc}^{N_{jc}+a_{jc}-1}(1-\theta_{jc})^{N_c-N_{jc}+b_{jc}-1}=\frac{B(N_{jc}+a_{jc}+1,N_c-N_{jc}+b_{jc})}{B(N_{jc}+a_{jc},N_c-N_{jc}+b_{jc})}
$$
带入$\Gamma$函数的性质：
$$
\frac{B(N_{jc}+a_{jc}+1,N_c-N_{jc}+b_{jc})}{B(N_{jc}+a_{jc},N_c-N_{jc}+b_{jc})}=\frac{\Gamma(N_{jc}+a_{jc}+1)\Gamma(N_c-N_{jc}+b_{jc})}{\Gamma(N_{jc}+a_{jc})\Gamma(N_c-N_{jc}+b_{jc})}\frac{\Gamma(N_c+a_{jc}+b_{jc})}{\Gamma(N_c+a_{jc}+b_{jc}+1)}=\frac{N_{jc}+a_{jc}}{N_{jc}+a_{jc}+b_{jc}}
$$
同样算一下共轭的均值(这样是叫共轭吗？)：
$$
E[1-\theta_{jc}|D]=E[1|D]-E[\theta_{jc}|D]=\frac{b_{jc}}{N_{jc}+a_{jc}+b_{jc}}
$$
这样得到的均值也可以作为一个估计值，类似于最大似然估计。

## 最大后验估计(MAP)

取对数：
$$
\ln p(\theta,\pi|D)=\ln p(\theta)+\ln p(\pi)+\sum_i(\ln p(x^{(i)}|\theta)+\ln p(y^{(i)}|\pi))
$$
先验对数：
$$
\ln p(\theta)=Const+(a_{jc}-1)\ln\theta_{jc}+(b_{jc}-1)\ln(1-\theta_{jc}),\ln p(\pi)=Const+\sum_c(\beta_c-1)\ln\pi_c
$$


目标函数：
$$
L(\theta,\pi)=(a_{jc}-1)\ln\theta_{jc}+(b_{jc}-1)\ln(1-\theta_{jc})+\sum_c(\beta_c-1)\ln\pi_c+\sum_j\sum_c\sum_{i:y^{(i)}=c}(x_j^{(i)}\ln\theta_{jc}+(1-x_j^{(i)})\ln(1-\theta_{jc}))+\sum_cN_c\ln\pi_c-\lambda(\sum_c\pi_c-1)
$$
参数$\pi$：
$$
\frac{\partial}{\partial \pi_c}L(\theta,\pi)=\frac{\beta_c-1}{\pi_c}+\frac{N_c}{\pi_c}-\lambda=0\Rightarrow N_c+\beta_c-1=\lambda\pi_c
$$
带入边界条件：
$$
N+\sum_c\beta_c-N_D=\lambda\Rightarrow\hat\pi_c=\frac{N_c+\beta_c-1}{N+\sum_c\beta_c-N_D}
$$
参数$\theta$:
$$
\frac{\partial}{\partial \theta_{jc}}L(\theta,\pi)=\frac{a_{jc}-1}{\theta_{jc}}-\frac{b_{jc}-1}{1-\theta_{jc}}+\sum_{i:y^{(i)}=c}(\frac{x_j^{(i)}}{\theta_{jc}}-\frac{1-x_j^{(i)}}{1-\theta_{jc}})=\frac{N_{jc}+a_{jc}-1}{\theta_{jc}}-\frac{N_c-N_{jc}+b_{jc}-1}{1-\theta_{jc}}
$$

求出来：
$$
\hat\theta_{jc}=\frac{N_{jc}+a_{jc}-1}{N_c+a_{jc}+b_{jc}-2}
$$
设置先验为均匀分布(uninformative)，即$a=1,b=1,\beta=1$，获得和最大似然估计相同的结果！

先验的参数$a,b$是超参数，类似于其他模型的「正则」系数，这些参数是人工指定的，不能通过训练模型获得。如果采用最大后验估计作为「训练」的过程，也只需要遍历整个$\theta_{jc}$矩阵、带入$a,b$即可。

## 预测

### 带入估计值

有了最大似然估计(MLE)或最大后验估计(MAP)的结果$\hat\theta_{jc},\hat\pi_c$，直接带入概率密度函数，就可以求相对的概率大小。
$$
p(y=c|\vec x)\propto p(y=c)\prod_jp(x_j|y=c)
$$
上式右边不需要得到归一化系数，带入参数估计值，就可以比较$y$取不同值时候的相对大小。概率最大时对应的分类就是模型的输出。

直接带入最大似然估计(MLE)或最大后验估计(MAP)的结果，都可能造成「过拟合」，并不是有超参数的模型就不会过拟合。「过拟合」只是个相对的概念，以下介绍贝叶斯统计的常用手法，在大多数情况下比直接带入某种估计的结果，都能更好地避免过拟合。当然，这样的计算要复杂很多，在大多数情况下，MLE/MAP就可以满足需求。

### 在参数空间上平滑

预测目标的分布(predictive distribution)，像上面一样:
$$
p(y=c|\vec x,D)\propto p(y=c|D)\prod_jp(x_j|y=c,D)
$$
「参数空间」就是由参数$\theta,\pi$张成的空间，微元是它们的概率密度函数加权之后的：
$$
p(\pi|D)p(\theta_{jc}|D)d\pi d\theta
$$
注意到$\theta,\pi$相互独立，这一个空间可以当成两个空间看待：
$$
p(\pi_c|D)d\pi_c,p(\theta_{jc}|D)d\theta_{jc}
$$
目标的分布的两个部分分别在这两个空间上做积分：
$$
p(y=c|D)=\int d\pi\,p(y=c|\pi)p(\pi|D),p(x_j|y=c,D)=\int d\theta_{jc}\, p(x_j|y=c,\theta_{jc})p(\theta_{jc}|D)
$$
计算$\pi$的空间:
$$
p(y=c|D)=\int d\pi\,\pi_c Z_\pi\prod_{c'}\pi_{c'}^{N_{c'}+\beta_{c'}-1}=Z_\pi(\int_0^1d\pi_c\,\pi_c^{N_c+\beta_c})(\prod_{c'\ne c}\int_0^1d\pi_{c'}\,\pi_{c'}^{N_{c'}+\beta_{c'}-1})=Z_\pi\frac{1}{N_c+\beta_c+1}\prod_{c'\ne c}\frac{1}{N_{c'}+\beta_{c'}}=1-\frac{1}{N_c+\beta_c+1}
$$
计算$\theta$的空间:
$$
p(x_j|y=c,D)=
Z_{\theta_{jc}}\int_0^1 d\theta_{jc}\,\theta_{jc}^{x_j}(1-\theta_{jc})^{1-x_j}\theta_{jc}^{N_{jc}+a_{jc}-1}(1-\theta_{jc})^{N_c-N_{jc}+b_{jc}-1}=\frac{B(x_j+N_{jc}+a_{jc},1-x_j+N_c-N_{jc}+b_{jc})}{B(N_{jc}+a_{jc},N_c-N_{jc}+b_{jc})}
$$
上式过于庞杂，考虑到$x_j$取值十分有限，可以简化一下，分别计算。

$x_j=1$时，是在求均值，刚才算过了：
$$
p(x_j=1|y=c,D)=\int_0^1 d\theta_{jc}\,\theta_{jc}p(\theta_{jc}|D)=E[\theta_{jc}|D]
$$
$x_j=0$时，还是在求均值：
$$
p(x_j=0|y=c,D)=\int_0^1 d\theta_{jc}\,(1-\theta_{jc})p(\theta_{jc}|D)=E[1-\theta_{jc}|D]
$$
简洁地合并以上两种情况：
$$
p(x_j|y=c,D)=E[\theta_{jc}|D]^{I(x_j=1)}E[1-\theta_{jc}|D]^{I(x_j=0)}
$$
带入连乘：
$$
\prod_jp(x_j|y=c,D)=E[\theta_{jc}|D]^{N_{j1}}E[1-\theta_{jc}|D]^{N_{j0}},N_{j1}+N_{j0}=N_D
$$
这样就完成了所有步骤。最终结果：
$$
p(y=c|\vec x,D)\propto p(y=c|D)\prod_jp(x_j|y=c,D)=(1-\frac{1}{N_c+\beta_c+1})E[\theta_{jc}|D]^{N_{j1}}E[1-\theta_{jc}|D]^{N_{j0}}
$$
这个概率密度函数要比直接带入MLE/MAP复杂得多，求解过程更是千回百转。然而，算法求解过程依然只需要遍历整个样本矩阵，并带入参数。这就是「朴素」的魅力！