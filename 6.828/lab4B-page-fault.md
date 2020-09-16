# MIT 6.828：实现操作系统 | Lab 4B：用户进程的缺页中断

本文为本人实现`6.828 Lab`的笔记，`Lab`其他部分在专栏不定期更新，目录和环境搭建请看第一篇：

[MIT 6.828：实现操作系统 | Lab1：快来引导一个内核吧](https://zhuanlan.zhihu.com/p/166413604)

本文md文档源码链接：[AnBlogs](https://github.com/Anarion-zuo/AnBlogs/blob/master/6.828/lab4B-page-fault.md)

`Lab 4B`部分要求我们实现`fork`系统调用，本文只是前半部分，有关用户进程下的缺页中断`Page Fault`处理。这是实现`fork`非常重要的组件，我们想要实现`Copy On Write`，就不得不借用`Page Fault`机制。

# 用户中断流程

我们已经写了一些`Page Fault`处理流程，在函数`page_fault_handler`下。我们假设内核一定不会出现`Page Fault`，如果出现了，那就是内核有bug。这里完善用户态下的`Page Fault`处理。

和之前一样，任何中断都会进入`trap`函数，`trap`将中断分发到相应处理函数。对于`Page Fault`，也就是`page_fault_handler`。目前为止，内核将触发`Page Fault`的进程销毁，这当然不是我们想要的。

`JOS`要将这个中断进一步分发，到事先指定好的`upcall`，进行具体的处理。分离出这个所谓`upcall`概念，就是想对不同情况绑定不同的处理函数，从而让处理更加灵活而优雅。

用户态下发生`Page Fault`后，内核将这个中断有关的信息分发到一个用户态环境，在用户态下执行事先指定的`upcall`，这个`upcall`可以获得中断有关的信息。`upcall`执行结束后，处理器直接跳转回触发中断的指令，不再进入内核。



# 向`upcall`传递结构体