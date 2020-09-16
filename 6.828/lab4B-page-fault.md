# MIT 6.828：实现操作系统 | Lab 4B：用户进程的缺页中断

本文为本人实现`6.828 Lab`的笔记，`Lab`其他部分在专栏不定期更新，目录和环境搭建请看第一篇：

[MIT 6.828：实现操作系统 | Lab1：快来引导一个内核吧](https://zhuanlan.zhihu.com/p/166413604)

本文md文档源码链接：[AnBlogs](https://github.com/Anarion-zuo/AnBlogs/blob/master/6.828/lab4B-page-fault.md)

`Lab 4B`部分要求我们实现`fork`系统调用，本文只是前半部分，有关用户进程下的缺页中断`Page Fault`处理。这是实现`fork`非常重要的组件，我们想要实现`Copy On Write`，就不得不使用`Page Fault`机制。

# 中断流程总览

我们已经写了一些`Page Fault`处理流程，在函数`page_fault_handler`下。我们假设内核一定不会出现`Page Fault`，如果出现了，那就是内核有bug。本文完善用户态下的`Page Fault`处理。

和之前一样，任何中断都会进入`trap`函数，`trap`函数通过一次简单的`switch`，将中断分发到相应处理函数。对于`Page Fault`，也就是`page_fault_handler`。目前为止，内核将触发`Page Fault`的进程销毁，这当然不是我们想要的。

`JOS`在内核中做一些准备，然后以用户态进入在文件`lib/pfentry.S`中定义的流程。这个流程跳转到触发`Page Fault`的进程实现定义的一个处理函数，处理完成之后，再进行一些处理，返回到出发`Page Fault`的指令继续执行。`JOS`使用用户态流程处理`Page Fault`，其中需要内核参与的部分，通过`System Call`实现。

具体内核应做哪些准备，如何设置处理函数，如何返回触发中断的指令，就是本文接下来的内容。

# 指定处理函数

这个标题对应`Exercise 8`。

用户进程通过函数`set_pgfault_handler`给自己设置`Page Fault`的处理函数，这个进程触发`Page Fault`之后，会由指定的函数处理。我们需要完善`set_pgfault_handler`。

在写代码之前，首先看看指定处理函数的设计。

在结构体`Env`中，`Lab 4`新拉取的代码多了一个属性`env_pgfault_upcall`，用来指定一个入口。目前为止，我们总是将这个属性设置为函数`_pgfault_upcall`的地址，这个函数代表`lib/pfentry.S`定义的流程，故所有进程发生`Page Fault`之后，都跳转到这个流程。

在`pfentry.S`的开头，这个流程马上跳转到了函数`_pgfault_handler`。这是个全局函数指针，不像`env_pgfault_upcall`总是接受一个固定的值，`_pgfault_handler`函数指针在函数`set_pgfault_handler`中设置为指定的值。这样一来，虽然`env_pgfault_upcall`的值总是固定，我们还是可以为进程定义不同的`Page Fault`处理函数。

有了这个理解，写代码就很容易了。全局函数指针`_pgfault_handler`没有设置初始值，则初始值是`NULL`，这让我们可以对第一次调用进行特殊处理。第一次调用`set_pgfault_handler`，要为中断时使用的栈分配空间。第一次调用之后，`_pgfault_handler`应设置为传入的函数指针，使得配置生效，并将当前进程的结构体通过系统调用`sys_env_set_ogfault_upcall`进行设置。具体代码如下：

```c
void
set_pgfault_handler(void (*handler)(struct UTrapframe *utf))
{
	int r, ret;

	if (_pgfault_handler == 0) {
		// First time through!
		// allocate an exception stack
        ret = sys_page_alloc(thisenv->env_id, (void *)(UXSTACKTOP - PGSIZE), PTE_U | PTE_W);
        if (ret < 0) {
            panic("Allocate user exception stack failed!\n");
        }
    }
    sys_env_set_pgfault_upcall(thisenv->env_id, _pgfault_upcall);

	// Save handler pointer for assembly to call.
	_pgfault_handler = handler;
}
```

# 为处理函数传参

