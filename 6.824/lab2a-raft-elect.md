# MIT 6.824 分布式系统 | Lab 2A：Raft选举

本文是本人学习`MIT 6.824 Lab 2A`的笔记，包含了我自己的实现和理解。本系列其它文章、及本系列详细说明，请看：[MIT 6.824 分布式系统 | 材料准备和环境搭建](https://zhuanlan.zhihu.com/p/260470258)

本文md源码：[AnBlog](https://github.com/Anarion-zuo/AnBlogs/blob/master/6.824/lab2a-raft-elect.md)

`Lab 2A`实现著名的`Raft`算法。在对应论文中，作者们不断强调，`Raft`算法相较于`Paxos`等其它共识算法`Consensus`的优势在于**可解释性**`Understandable`，方便教学。即便如此，这个实现对我来说算是非常复杂了。我花了一天多，从早到晚不停研究，才终于让代码通过了`Lab 2A`的测试。

`Debug`多线程非常困难，多线程和系统调度自带的**随机性**，让代码有时能通过测试，有时不可以。每次不通过的原因还可能不同，又令我们雪上加霜。当然，正确的代码应该在任何情况下都能够通过。我跑二十多次`Lab 2A`测试，幸运地全部通过了，即便如此，我依然不能保证代码的**正确性**，更不必说**效率**或**优雅**了。我能保证，我的代码**大致**正确。如果你发现了我的错误，请务必提醒我！

我将配合代码、文字、和简单的示意图讲解，整个算法非常复杂，我不能把所有代码全搬到文章里面。文章中呈现的代码应看做**伪代码**，而不是可以直接运行的代码。其中很多部分不会详细展开讲解，一方面是没有必要、避免啰嗦，另一方面要尽量缩减篇幅，你不必过于*刨根问底*。

完整的、可以直接拿来抄的代码，请看[我的GitHub仓库](https://github.com/Anarion-zuo/MIT-6.828)。当然，真的直接抄就没意思了，不自己操作一遍，你的损失特别大！我不想成为剥夺你学习机会的带恶人。

# 准备工作

在开始写代码之前，请务必做好充分准备。这些准备工作很多，请你尽量做充分，准备中的工作量能顶好几倍之后的代码工作量，减少bug出现概率。做`Lab 2A`的准备工作尤为重要，`Lab 2`的其它部分也依赖这部分的知识，我们需要一个好的开始。

准备工作主要包括两部分，先理解`Raft`算法，再看看给好代码的结构。

## 学习`Raft`

讲义中给了很多参考资料，`Raft`算法本身非常复杂，需要花较多精力理解。推荐你按如下顺序阅读这些材料：

1.  [官网简单介绍](https://raft.github.io/)，只需要看到`Raft Visualization`标题之前。
2.  [一个很棒的可视化](http://thesecretlivesofdata.com/raft/)，慢慢把所有动画放完。
3.  [Raft论文](https://pdos.csail.mit.edu/6.824/papers/raft-extended.pdf)，主要看`Figure 2`和`Section 5`。
4.  [6.824助教写的注意事项](https://thesquareplanet.com/blog/students-guide-to-raft/)

还有一些材料可以选择性阅读：

-   [6.824课程视频](https://www.bilibili.com/video/BV1R7411t71W?p=6)
-   [Raft作者博士论文](https://raw.githubusercontent.com/ongardie/dissertation/master/book.pdf)

如果你需要中文材料，可以参考知乎上的这些文章：

-   本文
-   https://www.zhihu.com/question/29597104

-   https://zhuanlan.zhihu.com/p/110168818

请你花长时间，仔细研究以上材料，确保你能独立地在脑海中放出像[一个很棒的可视化](http://thesecretlivesofdata.com/raft/)那样的动画，充分理解`Raft`算法。讲解`Raft`算法不是本文的主要内容，如果以后有兴致，再写一篇文章，下次一定！

## 几句话说说`Raft`原理

还是简单说一些。

`Raft`的目的是在**多个机器**上维持**相同状态**。客户端对`Raft`集群发送**改变状态**的请求，`Raft`算法保证，集群中所有机器的状态保持一致。

`Raft`通过维持一个**操作记录**结构抱保证一致性。通过机器之前交换信息，在所有机器中维护了一个`log`结构。这个结构按顺序记录了客户端向集群发送的所有操作请求，保证这个结构在所有机器上保持一致，就可以保持所有机器进行一致操作，进而保证广泛的**一致性**。

`Raft`算法选中集群中的一个机器作为**领导**`leader`，起到整体调控的作用。这样的**中心化**设计在分布式领域非常常见，让整个开发工作轻松了很多。

![log结构](lab2a-raft-elect.assets/image-20201009223347374.png)

这是[Raft论文](https://pdos.csail.mit.edu/6.824/papers/raft-extended.pdf)中的图，基本解释清楚了。`leader`引导整个流程，将自己的`log`同步到所有`follower`上。有的`follower`没有特别跟上，如第三个。也有完全跟上的，如第二个。方框的颜色表示执行到什么位置，大部分`follower`的执行和`leader`一致，都在执行`x<-2`。第三个`follower`和`leader`执行不一致，之后等它的`log`和`leader`同步之后，它也会执行相同操作，进而和其它机器一致。

无论是`leader`还是`follower`，都有发生错误离线的可能。令整个系统不受错误影响，也是`Raft`的职责。如果`leader`离线，就要重新产生`leader`，这是本文的主要内容。

## 看看代码和任务总览

`Lab 2A`主要代码写在文件`src/raft/raft.go`。目录`src/raft`下的其它文件都是为**测试**服务的，测试主要流程在`test_test.go`。

`Lab 2A`的测试流程主要在`test_test.go`的前两个函数`TestInitialElection2A， TestReElection2A`，主要关于`leader`的**产生**和**重新产生**。`Goland`有对`gotest`的完全支持，请看[官方文档](https://www.jetbrains.com/help/go/testing.html)。使用`Goland`可以方便地运行单个测试，并使用**断点调试**。

测试流程通过一些复杂的手段启动和管理各个`Raft`进程，我们最好通过测试流程`test_test.go`调用`raft.go`中的代码，而不是另外写一个`main.go`。主要调用和管理`Raft`进程的代码主要在`config.go`，调用`raft.go`中提供的函数`Make, Kill, Raft.GetState`，分别对应**创建、销毁、查看**`Raft`进程。

我们需要在`raft.go`中实现**选举**和**心跳信号**，具体表现为两个功能：

1.  一系列调用`Make`创建`Raft`进程后，进程之间选举出一个`leader`。
2.  `leader`相对于其它进程离线后，其它进程在它们中间重新选举一个`leader`。

这两个功能分别对应`TestInitialElection2A, TestReElection2A`，前者相对容易实现，后者需要`Raft`之外的一些设计。

## 在开始写代码之前

按惯例，除了论文还要阅读[Lab 2 Notes](https://pdos.csail.mit.edu/6.824/labs/lab-raft.html)，如果你还没阅读的话。前面没有指出来，是因为[Lab 2 Notes](https://pdos.csail.mit.edu/6.824/labs/lab-raft.html)和**学习Raft**这件事情关系不大。现在指出来，是因为[Lab 2 Notes](https://pdos.csail.mit.edu/6.824/labs/lab-raft.html)里面讲了很多代码介绍和要求，需要你特别注意。在这里归纳出几点：

-   主要编程指引在[Raft论文](https://pdos.csail.mit.edu/6.824/papers/raft-extended.pdf)的`Figure 2`中，必须按照它的逻辑严格执行，最好不自己发挥。
-   使用的`RPC`命名和`Figure 2`中相同，用`RequestVote`**索取选票**，用`AppendEntries`实现**心跳信号**。
-   有一些和**等待**有关的参数需要小心选取。

除此之外，基于我自己写这个`Lab`的经验，再提醒你一下：

-   没有理解清楚算法流程不要硬上，多看看论文，反复琢磨总是能懂的！
-   不要先追求**效率**或**优雅**，很多错误就是这么来的，先追求**正确！**
-   多线程代码不要用**断点调试**了，可以尝试在终端`print`一些信息，像这样：

```
[Peer 1 Leader term 2] sending heartbeat signal to peer 2
[Peer 1 Leader term 2] all heartbeats sent, sleeping for 120 then send heartbeats again
[Peer 0 Follower term 2] got heartbeat message from leader peer 1 at term 2
[Peer 1 Leader term 2] heartbeat response from peer 0 received in 138.851µs success true
[Peer 2 Leader term 1] heartbeat response from peer 0 received in 70.168149ms success true
[Peer 2 Leader term 1] found peer 0 unreachable when sending heartbeats
[Peer 2 Leader term 1] sending heartbeat signal to peer 0
```

-   我的完整实现请看[我的GitHub仓库](https://github.com/Anarion-zuo/MIT-6.828)，**不要照抄！！！**

如果怎样都调不通，可以依次尝试：

1.  调整**等待时间**参数
2.  检查`GetState`方法是否正确
3.  阅读终端输出信息

说了这么多，你可以开始写代码了。在你写好之前，**请不要继续阅读本文**。后文中的一些结论，我花了很长时间才发现，本来一起列在上面了，后来还是觉得不要**剧透**太多，给你留多一点发挥的空间，才能学到更多，不应该把这个机会就这样抢走。我也不想成为剥夺你学习机会的带恶人。

图片之后代码正式开始。

![别偷看哦](lab2a-raft-elect.assets/Anakin-Yellow-Eyes-in-Revenge-of-the-Sith-1602263485314.jpg)

# 复现`Raft`论文

有了[Raft论文](https://pdos.csail.mit.edu/6.824/papers/raft-extended.pdf)的`Figure 2`，我们可以依样画葫芦，亦步亦趋地按照论文中的要求来实现。