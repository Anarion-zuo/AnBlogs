#! https://zhuanlan.zhihu.com/p/228812106
# MIT 6.828：实现操作系统 | Lab 3B：中断处理函数和系统调用

本文为本人实现`6.828 Lab`的笔记，接续上一篇：

[MIT 6.828：实现操作系统 | Lab 3A：中断初始化](https://zhuanlan.zhihu.com/p/213873367)

`Lab`其他部分在专栏不定期更新，环境搭建请看第一篇：

[MIT 6.828：实现操作系统 | Lab1：快来引导一个内核吧](https://zhuanlan.zhihu.com/p/166413604)

在`Lab 4 Part A`中，我们完成了中断初始化。现在，每当中断发生，处理器就会进入`trap`函数，进行一系列处理，返回到中断发生之前的指令恢复执行。

目前为止，我们还没有写任何中断处理函数，只是写了中断入口。本文来写处理函数，大量使用了前一篇文章的内容，请你务必理解清楚前一篇文章的有关操作。本文非常简短，如果你感受到一些操作有困难，可能是由于之前的内容没有理解清楚，建议你倒回去复习一下。

本文md文档源码链接：[AnBlogs](https://github.com/Anarion-zuo/AnBlogs/blob/master/6.828/lab3B-syscall.md)

# 分发中断

函数`trap`调用了`trap_dispatch`，在这个函数中，根据`Trapframe`结构体中的信息，选择一个处理函数。处理函数执行完成之后，返回到`trap`函数，再返回到原先执行的状态。

代码非常简单：

```c
switch (tf->tf_trapno) {
    case T_DIVIDE:
        //return;
        break;
    case T_DEBUG:
        debug_breakpoint_handler(tf);
        return ;
    case T_BRKPT:
        debug_breakpoint_handler(tf);
        return;
    case T_PGFLT:
        page_fault_handler(tf);
        return;
    case T_SYSCALL:
        handle_syscall(tf);
        return;
    default:
        //            cprintf("trap caught! number %u\n", tf->tf_trapno);
        break;
}
```

`Exercise 5`要求我们实现`page_fault_handler`，让相应中断发生时，正确地分发到函数`page_fault_handler`，也就是向上面那样。

`Exercise 6`要求我们实现断点调试的中断。**断点**是3号中断，通过指令`int $3`触发。在`trap_init`中已经配置好了入口：

```c
DECLARE_INTENTRY(t_debug, T_DEBUG, 3)
DECLARE_TRAPENTRY(t_brkpt, T_BRKPT, 3)
```

注意这里的`DPL`设置为3，从而允许在用户态下通过指令进入中断入口。若设置为0，触发3号中断会进而触发13号中断，也就是`General Protection Fault`，和权限保护有关。

# 分发系统调用

系统调用通过`int 0x30`触发，也就是48号中断，这是我们自己规定的，因为这个中断序号没有使用。在`JOS`中，用户进程调用`lib/syscall.c`中的`syscall`函数触发这个中断，并传递参数。

用户调用的`syscall`函数接受7个参数。第一个是**系统调用序号**，告诉内核要使用那个处理函数，进入寄存器`eax`。后5个是传递给内核中的处理函数的参数，进入剩下的寄存器`edx, ecx, ebx, edi, esi`。这些寄存器都在中断产生时被压栈了，可以通过`Trapframe`访问到。

在函数`trap_dispatch`中，被分发到函数`handle_syscall`。在`handle_syscall`中调用真正的`syscall`函数，进行二次分发和运行。内核调用的函数`syscall`和用户调用的不同，前者在`kern/syscall.c`中，根据`syscallno`选择处理函数执行，如下：

```c
int32_t
syscall(uint32_t syscallno, uint32_t a1, uint32_t a2, uint32_t a3, uint32_t a4, uint32_t a5)
{
	switch (syscallno) {
        case SYS_cputs:
            sys_cputs((const char *)a1, a2);
            return 0;
        case SYS_getenvid:
            return sys_getenvid();
        case SYS_env_destroy:
            return sys_env_destroy(sys_getenvid());
        case NSYSCALLS:
        default:
            return -E_INVAL;
	}
}
```

这是后几个`Lab`写的`syscall`函数，根据不同的**系统调用序号**，选择了不同的`sys_*`函数。你的代码目前为止只需要写`SYS_cputs`就可以了。

我们再来看看`syscall`函数是如何在`handle_syscall`中调用的。讲义告诉我们，用户调用的`syacall`函数的返回值应该存放在寄存器`eax`中，故内核应将`syscall`返回值放在`Trapframe`结构体中存放寄存器`eax`的地方。同时，`Trapframe`结构体中存储的其它寄存器的值应该当作参数传给`syscall`函数。

```c
static void handle_syscall(struct Trapframe *tf) {
    // this function extracts registers from Trapframe and passes them onto real syscall dispatcher
    struct PushRegs *pushRegs = &tf->tf_regs;
    pushRegs->reg_eax = syscall(pushRegs->reg_eax, pushRegs->reg_edx, pushRegs->reg_ecx, pushRegs->reg_ebx, pushRegs->reg_edi, pushRegs->reg_esi);
}
```

现在你可以试着运行一下`user/hello.c`，也就是在函数`i386_init`中将`ENV_CREATE`的宏参数改为`hello`。你应该看到打印了`hello, world`，并进入了一个`Page Fault`。这是因为用户环境还没配置好，我们接下来配置。要是没有成功输出`hello, world`，就要检查一下哪里写错了。

# 用户环境准备

每个进程都有一个指针`thisenv`指向本进程对应的`Env`结构体，现在还没有配置这个指针，所以上面通过这个指针访问地址会触发`Page Fault`。现在在进程启动时配置这个结构体指针。

用户进程从`lib/libmain.c`中的函数`libmain`开始执行，这个函数进而调用`umain`，也就是用户写的程序入口。

在函数`libmain`的开头，我们通过系统调用配置`thisenv`指针：

```c
envid_t envid = sys_getenvid();
thisenv = &envs[ENVX(envid)];
```

我们还需要写这个系统调用。这个系统调用返回当前进程的`envid`，通过这个返回值拿到`envs`数组的索引，也就得到了`thisenv`的正确数值。

系统调用函数非常简单，也就是返回当前进程的`id`：

```c
static envid_t
sys_getenvid(void)
{
	return curenv->env_id;
}
```

`curenv`就是被中断的进程。

这时候，`user/hello.c`下的代码应该可以正常执行，不会再出发`Page Fault`。