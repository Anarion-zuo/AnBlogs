#! https://zhuanlan.zhihu.com/p/192886969
# MIT 6.828：实现操作系统 | Lab 3A：虚拟地址映射实现总结

本文是本人实现`6.828 Lab 3A`的笔记，将`Lab 2 Part 3`也合并到本文。接续上一篇：

https://zhuanlan.zhihu.com/p/183974374

其他Lab笔记在专栏不定期更新，环境搭建请看：

https://zhuanlan.zhihu.com/p/166413604

本文md文档源码链接：[AnBlogs](https://github.com/Anarion-zuo/AnBlogs/blob/master/6.828/lab2-3A-address.md)

前面的Lab实现了内存管理有关的组件，分配器和`Page Table`。我们还没有正式使用起来这些组件，本文对应的`Lab`内容就是建立真正的`Page Table`的过程。

知乎最近不能发图片，本文不包含图片，要是将来知乎修好了，我再补点图片，如果到时候还记得的话。

# `Page Table`组织总结

在`Lab 2`中，我们让代码跑过了各种`check_*`函数，但是没有对其中的原理充分深究，只是莫得感情地把功能实现了。这里总结一下。

内核的内存管理是以`page`为单位的，称为一个`Page Frame`，一个`page`的大小是`4096Bytes`，也就是`4KB`。内核使用`free list`链表的方式管理尚未分配的空间，实现非常简单。

要使用内存，必须建立**虚拟地址映射**。无论是C代码还是汇编代码，要访问内存，都是通过**虚拟地址**。C代码中，所有指针的值都必须为**虚拟地址**，代码才能正确执行，否则`*`访问不到想要的地址。

**虚拟地址映射**是通过一个**二级`table`**实现的，两个层级分别被称为`Page Directory`和`Page Table`。两者在结构上没有区别，只是相同结构的相互嵌套。虚拟地址不包含任何`table`的地址，只包含`table`的索引。必须事先指定好`Page Directory`的地址，利用这个地址得到`Page Directory Entry`，从而得到`Page Table`地址，从而得到`Page Frame`地址，需要且仅需要指定`Page Directory`地址。`Page Directory`地址是寄存器`cr3`，设置`cr3`的行为会导致硬件执行切换`Page Directory`配套的一系列操作。

在函数`mem_init`之前，内核加载时简单地初始化了一个`Page Directory`，将`0xf0000000`开始的一段地址映射到`0x0`开始的一段地址，以方便正式初始化**虚拟地址映射**之前的操作。在`mem_init`函数的最后，我们需要初始化一个真正的`kern_pgdir`，并将寄存器`cr3`设置为它的地址。

最终得到的**虚拟地址布局**为文件`memlayout.h`中的注释：

```c
/*
 * Virtual memory map:                                Permissions
 *                                                    kernel/user
 *
 *    4 Gig -------->  +------------------------------+
 *                     |                              | RW/--
 *                     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 *                     :              .               :
 *                     :              .               :
 *                     :              .               :
 *                     |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~| RW/--
 *                     |                              | RW/--
 *                     |   Remapped Physical Memory   | RW/--
 *                     |                              | RW/--
 *    KERNBASE, ---->  +------------------------------+ 0xf0000000      --+
 *    KSTACKTOP        |     CPU0's Kernel Stack      | RW/--  KSTKSIZE   |
 *                     | - - - - - - - - - - - - - - -|                   |
 *                     |      Invalid Memory (*)      | --/--  KSTKGAP    |
 *                     +------------------------------+                   |
 *                     |     CPU1's Kernel Stack      | RW/--  KSTKSIZE   |
 *                     | - - - - - - - - - - - - - - -|                 PTSIZE
 *                     |      Invalid Memory (*)      | --/--  KSTKGAP    |
 *                     +------------------------------+                   |
 *                     :              .               :                   |
 *                     :              .               :                   |
 *    MMIOLIM ------>  +------------------------------+ 0xefc00000      --+
 *                     |       Memory-mapped I/O      | RW/--  PTSIZE
 * ULIM, MMIOBASE -->  +------------------------------+ 0xef800000
 *                     |  Cur. Page Table (User R-)   | R-/R-  PTSIZE
 *    UVPT      ---->  +------------------------------+ 0xef400000
 *                     |          RO PAGES            | R-/R-  PTSIZE
 *    UPAGES    ---->  +------------------------------+ 0xef000000
 *                     |           RO ENVS            | R-/R-  PTSIZE
 * UTOP,UENVS ------>  +------------------------------+ 0xeec00000
 * UXSTACKTOP -/       |     User Exception Stack     | RW/RW  PGSIZE
 *                     +------------------------------+ 0xeebff000
 *                     |       Empty Memory (*)       | --/--  PGSIZE
 *    USTACKTOP  --->  +------------------------------+ 0xeebfe000
 *                     |      Normal User Stack       | RW/RW  PGSIZE
 *                     +------------------------------+ 0xeebfd000
 *                     |                              |
 *                     |                              |
 *                     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 *                     .                              .
 *                     .                              .
 *                     .                              .
 *                     |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|
 *                     |     Program Data & Heap      |
 *    UTEXT -------->  +------------------------------+ 0x00800000
 *    PFTEMP ------->  |       Empty Memory (*)       |        PTSIZE
 *                     |                              |
 *    UTEMP -------->  +------------------------------+ 0x00400000      --+
 *                     |       Empty Memory (*)       |                   |
 *                     | - - - - - - - - - - - - - - -|                   |
 *                     |  User STAB Data (optional)   |                 PTSIZE
 *    USTABDATA ---->  +------------------------------+ 0x00200000        |
 *                     |       Empty Memory (*)       |                   |
 *    0 ------------>  +------------------------------+                 --+
 *
 * (*) Note: The kernel ensures that "Invalid Memory" is *never* mapped.
 *     "Empty Memory" is normally unmapped, but user programs may map pages
 *     there if desired.  JOS user programs map pages temporarily at UTEMP.
 */
```

# 建立映射的函数们

我们已经写好了很多函数，在把它们用起来之前，再浏览一遍它们的目的。

首先是分配器，对未分配的物理内存进行管理。在初始化函数`mem_init`中调用`page_init`初始化了这个分配器，之后通过`page_alloc, page_free`获取和释放`page`。

要正确建立映射，首先需要正确方便地索引`Page Directory, Page Table`。函数`pgdir_walk`，根据指定`Page Directory`索引出`Page Table Entry`。函数`page_lookup`基于`pgdir_walk`，进一步得到这个`Page Table Entry`对应的物理地址。

地址映射可以建立或移除，我们都写好了方便的函数。函数`boot_map_region`用于给内核做映射，只处理`0xf0000000`以上虚拟空间。函数`page_insert, page_remove`处理其他空间的映射，分别建立映射、移除映射。

其他函数对以上起辅助作用。

# 为内核建立虚拟地址映射

`Lab 2 Part 3`要求我们补全函数`mem_init`后面的部分，也就是给内核配置好`kern_pgdir`，并设置寄存器`cr3`。在这里使用的函数都是`boot_map_region`。

还是建议你先自己琢磨。如果看`Hints`不明所以，可以看看测试函数`check_kern_pgdir`，也就知道正确的映射是什么样子了。

首先是分配器的`pages`数组，`Hints`中告诉我们这应该是对用户只读，并映射到`UPAGES`地址去。

```c
boot_map_region(kern_pgdir, UPAGES, PTSIZE, PADDR(pages), PTE_U);
```

然后是内核的栈，用户不可读写，映射到`bootstack`地址。

```c
boot_map_region(kern_pgdir, KSTACKTOP - KSTKSIZE, KSTKSIZE, PADDR(bootstack), PTE_W);
```

其余的地址全部映射到`KERNBASE`上，无论物理内存是否有这么大。用户不可读写。

```c
boot_map_region(kern_pgdir, KERNBASE, 0x100000000 - KERNBASE, 0, PTE_U);
```

跑过了`check_kern_pgdir`，说明你的代码大体上是正确的。需要注意的是，权限位可能设置不正确，包括我上面的几行。要是不想权限称为后续开发的麻烦，可以先把权限设置的大一些，可以干脆把所有权限都设置为`PTE_W | PTE_U`。权限问题无伤大雅，可以到后面再来严格规范。

# 为用户建立虚拟地址映射

这里才是`Lab 3`的内容。和`page`类似，内核通过一个`struct Env`数组`envs`管理用户环境。函数`env_init`初始化了这个数组，具体操作和`page_init`类似，就是拉链表，本文不再赘述。

函数`env_setup_vm`为指定的用户环境`struct Env`初始化虚拟地址映射，得到的是一个`pde_t *`类型的`Page Directory`。需要注意以下几点：

1.  为`Page Directory`分配的新`page`应该增加引用统计次数`pp_ref`。
2.  `UTOP`以下的地址对用户应该为可读可写的。
3.  可以使用`kern_pgdir`作为模板，在其基础上更改。

还是建议你先自己尝试，再来看我的代码。

```c
static int
env_setup_vm(struct Env *e)
{
	int i;
	struct PageInfo *p = NULL;

	// Allocate a page for the page directory
	if (!(p = page_alloc(ALLOC_ZERO)))
		return -E_NO_MEM;
	// LAB 3: Your code here.
    // use kernel page as template
    // can conveniently replace some of the entries, for the pages are marked not referenced
    pde_t *upgdir = page2kva(p);
    memcpy(upgdir, kern_pgdir, PGSIZE);
    // must increment env_pgdir's reference count according to Hint
    p->pp_ref++;
    // setup Env structure
    e->env_pgdir = upgdir;
    // set page directory entries to user accessible
    for (pde_t *pde = upgdir; pde < (pde_t*)((uintptr_t)upgdir + PGSIZE); ++pde) {
        *pde |= PTE_U | PTE_W;
    }
	// UVPT maps the env's own page table read-only.
	// Permissions: kernel R, user R
	e->env_pgdir[PDX(UVPT)] = PADDR(e->env_pgdir) | PTE_P | PTE_U;

	return 0;
}
```

我直接使用`kern_pgdir`作为模板，用`memcpy`复制了过来。原先`kern_pgdir`中没有对`UTOP`以下进行映射，故应添加进来。新添加的映射是用户区，故用户可读可写。其余地址映射有`kern_pgdir`继承而来，如果之前`kern_pgdir`权限位设置宽松，此时的操作令用户区也可以一定地访问内核区空间。

剩余`Lab 3`的内容下一篇再继续。到这里，我们几乎完成了内存地址映射有关的所有内容。