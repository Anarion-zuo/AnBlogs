

## 预测分布

回到要解决的问题上来。计算出MLE/MAP中的一个，把估计值带入模型就可以进行预测了。一般的机器学习算法只进行了这个简单的过程。

**直接带入估计值**这种手法存在很多问题，完整的贝叶斯统计分析直接操作后验分布，考虑参数所有的取值可能，而不是只考虑零散的几个值。

在进行统计分析之前，我们假设$\theta$有一个分布：
$$
p(y|x)=\frac{1}{\sqrt{2\pi}\sigma}\exp(-\frac{(y-\theta^Tx)^2}{2\sigma^2})
$$
在得到样本数据之后，我们可以通过**训练好**的模型预测$y$取某值的概率$p(y|x,D)$。其中$|$后的$x$表示一个**输入**的特征，$D$表示在「见过」这些数据的条件下，也就是**经过训练**的意思。根据贝叶斯的标准手法，**输出**应该在参数的后验空间上平滑：
$$
p(y|x,D)=\int d\theta\; p(y|x,\theta)p(\theta|D)
$$
以下我们来算这个积分。
$$
\int d\theta\; p(y|x,\theta)p(\theta|D)\propto
\int d\theta\; \exp(-\frac{\sum_i(y^{(i)}-\sum_j\theta_jx_j^{(i)})^2}{\sigma^2}-
\sum_j\frac{(\theta_j-\mu_j)^2}{2\sigma_j^2})
$$
整理一下：
$$
\exp(-\frac{\sum_i(y^{(i)}-\sum_j\theta_jx_j^{(i)})^2}{\sigma^2}-
\sum_j\frac{(\theta_j-\mu_j)^2}{2\sigma_j^2})=
(\prod_i\exp(-\frac{(y^{(i)}-\sum_j\theta_jx_j^{(i)})^2}{\sigma^2}))
(\prod_j\exp(-\frac{(\theta_j-\mu_j)^2}{2\sigma_j^2}))
$$

$$
(y^{(i)}-\sum_j\theta_jx_j^{(i)})^2=(y^{(i)})^2+(\sum_j\theta_jx_j^{(i)})^2-2y^{(i)}\sum_j\theta_jx_j^{(i)}
$$

