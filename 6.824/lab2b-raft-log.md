#! https://zhuanlan.zhihu.com/p/266901448
# MIT 6.824 分布式系统 | Lab 2B：Raft同步

本文是本人学习`MIT 6.824 Lab 2B`的笔记，包含了我自己的实现和理解。本系列其它文章、及本系列详细说明，请看：[MIT 6.824 分布式系统 | 材料准备和环境搭建](https://zhuanlan.zhihu.com/p/260470258)

本文md源码：[AnBlog](https://github.com/Anarion-zuo/AnBlogs/blob/master/6.824/lab2b-raft-log.md)

上一篇是[MIT 6.824 分布式系统 | Lab 2A：Raft选举](https://zhuanlan.zhihu.com/p/264448558)，如果你还没有阅读，请先阅读上一篇。上一篇给了一些学习`Raft`的建议，并实现了一部分`Raft`算法。要做如此复杂的分布式算法，你当然不想从中间乱入的。

从现在我编辑这个文档的时候，距离上一次更新这个系列已经过去8天。这是因为我在`Lab 2B`部分花了很多时间，最终的效果也不算很好。

[我的GitHub仓库](https://github.com/Anarion-zuo/MIT-6.824)里面写的代码不能通过测试`TestBackup2B`，而我自认为已经穷尽所能，检查过多次，没有发现什么严重的错误。输出的`Debug`信息显示，各个`Raft`进程进入了一个错误状态，但这个错误在之后的同步机制中会自动更正，只需要等待测试逻辑进入下一个状态。测试逻辑捕捉到了这个错误，并认定这个错误不可接受。最终只能下结论，是测试逻辑不恰当，责任不在我。我很不愿意下这个结论，但是也是真没办法。

在[Lab 1 MapReduce](https://zhuanlan.zhihu.com/p/260752052)中，我犯了一个很严重的错误，在评论区被指出来了，而这个错误没有在测试中被发现。由此判断，由于`Raft`算法和分布式架构自身的复杂性，`6.824`课程给出的测试不能包罗万象。

当然，我也可能犯错了，这要等到后面的`Lab`才能够发现。这里写写我的设计，没有端出很多源代码。对于学习者来说，太细太细的地方不是特别重要了，设计的过程更加可贵。我也要改改我的固执，不能舍本逐末，一直纠结在这些细枝末节。

如果好心的你不嫌弃，使劲翻了[我的GitHub仓库](https://github.com/Anarion-zuo/MIT-6.824)里面的代码，使劲`Debug`，找到了我的错误，请一定告诉我！

# 学习Raft同步机制

和上一篇[MIT 6.824 分布式系统 | Lab 2A：Raft选举](https://zhuanlan.zhihu.com/p/264448558)一样，我们还是需要阅读[Raft论文](https://pdos.csail.mit.edu/6.824/papers/raft-extended.pdf)，需要重点关注上一篇中没有关注的**Log同步机制**。上一篇中提到的其它材料，你也可以再看看。

除了[Raft论文](https://pdos.csail.mit.edu/6.824/papers/raft-extended.pdf)，[6.824助教写的注意事项](https://thesquareplanet.com/blog/students-guide-to-raft/)也很重要。里面讲到了一些可能的错误，可以帮助你节约很多时间。

# 重构设计

写上一篇[MIT 6.824 分布式系统 | Lab 2A：Raft选举](https://zhuanlan.zhihu.com/p/264448558)的时候，我的代码非常原始、粗糙，很难说有什么**设计**可言。写`2B`部分的时候，我意识到，`Raft`算法的复杂不允许如此轻视的态度，要想在这个`Lab`系列走得更远，必须有好的代码结构。

我重构之后的代码在[我的GitHub仓库](https://github.com/Anarion-zuo/MIT-6.824)中，如果你想看重构之前的版本，可以`revert commit`到`2212f03e07d87d69796c79f002e1d8ff6dd3428a`，也就是在`2020.10.8`提交信息含`refactored`的前一个提交`lab2b all tests passed save backup`。当然，你没必要这么做。

## 拆分流程

我把一个`Raft`进程的运行拆成几部分。

-   第一个部分执行由`Raft`当前所处状态决定，称为**角色流程**。如`leader`不断向其它进程发送`AppendEntries RPC`。
-   第二个部分执行各个`RPC`返回之后的回调函数，称为**回调流程**。如`leader`得到`AppendEntries`返回的`reply`结构体，并对这个结构体包含的信息进行处理。`RPC`的调用和回调函数的执行都发生在另一个线程，从而不阻塞**角色流程**。
-   最后的部分由收到的`RPC`产生，称为**异步流程**。如`follower`收到一个`AppendEntries`信号，并对这个`RPC`携带的信息进行处理。这个流程的执行和其它两个流程的关联很小，可以说不受影响，随机出现。

对于不同的流程，我们需要不同的**同步机制**，也就是**加锁**。

## 同步机制

我个人并发编程经验不足，这可能是我第一次完全独立地设计这样的多线程系统。如果我的代码有错误，那么一定是在这里了。

同步机制的目的是：

-   一次**角色流程**执行时，`Raft`角色不变。也就是在发送`RequestVote`时，改变角色为`follower`的效果一定要在发送完成之后产生，不能在中途变化。
-   进程往往一次性发送多个`RPC`，对应一次**角色流程**的执行。它们产生多个**回调流程**，每个对应一个其它进程。对应同一个**角色流程**的**回调流程**不能同时执行。如进程收到多个**投票**，应该**依次**处理这些投票，而不是同时处理。
-   **异步流程**由一个`RPC`处理函数产生之后，被放入一个队列中。一个线程专门从这个队列中取出流程来执行，这些异步流程也就按照一定顺序**同步**地执行了。`RPC`处理函数等到这个**线程**执行完成相应异步流程之后再返回给`RPC`的发送者。
-   在其它情况下，必须保证`Raft`结构体所有属性的**原子性**操作。

以上是一段概括性描述，我自己也不敢说已经全面贯彻执行了。要提醒你的是，切不可为了**效率**而不愿意**加锁**，或是为了效率尝试一些可能不正确的**加锁**方式。加锁不正确，将直接导致最终的不正确，而不只是**运行得慢一些**，而且这样的错误非常难解决。

## 类设计

这里具体落实到我的代码，按各个流程来看。你可以对照[我的GitHub仓库](https://github.com/Anarion-zuo/MIT-6.824)来看。

**角色流程**是个死循环，利用**多态**机制，根据`Raft`进程当前所处角色，执行不同代码。

```go
func (rf *Raft) RunStateProcedure() {
   rf.printInfo("state procedure runner thread started")
   for {
      // run indefinitely
      rf.LockPeerState()
      rf.MyState.Run()
      rf.UnlockPeerState()
   }
}
```

其中，`MyState`是个接口，实现类的`Run`方法不同。改变`MyState`属性，就可以改变每次循环的行为。

**回调流程**嵌入在**发送RPC**的工具类`AsyncRpcCallInterface`中，不同种类的`RPC`需要实现这个接口的`callback`方法。接口的其它方法和流程的退出和统计有关，这里也就不展开了。

**异步流程**由接口`RaftTask`定义。不同种类`RPC`对应的不同**异步流程**，实现不同的`execute`方法。当收到一个`RPC`时，处理函数产生一个`RaftTask`实现类对象，并将它放入队列，等待它执行完成。

```go
func (rf *Raft) AppendEntries(args *AppendEntriesArgs, reply *AppendEntriesReply) {
   RunTask(NewAppendEntriesTask(rf, args, reply), rf.taskQueue)
   return
}

func RunTask(rt RaftTask, queue *RaftTaskQueue) {
	queue.Push(rt)
	rt.WaitForDone()
}
```

另外单独准备一个线程，专门执行进入这个队列的`RaftTask`。

```go
func (rf *Raft) RunAsyncProcedure() {
   rf.printInfo("async procedure runner thread started")
   for {
      rf.taskQueue.RunOne()
   }
}

func (rtq *RaftTaskQueue) RunOne() {
	task := rtq.pop()
	task.execute()
	task.SetDone()
}
```

这基本上就是我的设计，其它实现和具体`Raft`算法行为有关，也就不具体展开了。

