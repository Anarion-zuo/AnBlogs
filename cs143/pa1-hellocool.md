#! https://zhuanlan.zhihu.com/p/250667235
# CS143：编译原理｜PA1：熟悉Cool语言

这是本人实现斯坦福`CS143`编程作业的笔记，对应第一次作业`PA1`。环境搭建和一些说明请看：[CS143：编译原理 | 环境搭建HelloWorld](https://zhuanlan.zhihu.com/p/226190284)

从第一篇搬运一段话。

>   你可能发现了，[课程官网](http://web.stanford.edu/class/cs143/)上的`PA1`和我们下载的`PA1`不相符，课程官网上的`PA1`已经开始写编译器了。这是MOOC版本和正式课程的区别。正式课程如课程官网所示，有4个主要编程作业，最后一个是**加分项**`Extra Credit`，第一个作业就开始写编译器。MOOC版本的第一个编程作业是**熟悉Cool语言**，之后的4个编程作业和正式课程相同。在文章[环境搭建](https://zhuanlan.zhihu.com/p/226190284)中，我们下载到的是MOOC版本的材料，也就接着使用这个版本的，反正和正式课程没有特别大的区别。
>

你可以像正式课那样，跳过这个**熟悉Cool语言**部分，直接开始写编译器，那么你就没必要阅读本文。如果你想在写Cool语言的编译器之前，先熟悉它的语法，可以参考本文。

`PA1`的主要难度在于`coolc`编译器的报错信息很不友好，导致不熟悉`Cool`语法的我们经常对着报错信息不知所措，而说明文档说得不太明白，需要我们自己探索，十分伤脑筋。换一种角度来看，这也是一种锻炼，所以还是加油试试吧。

本文md文档源码链接：[AnBlogs](https://github.com/Anarion-zuo/AnBlogs/blob/master/cs143/pa1-hellocool.md)

# 简单的编程要求

这个`PA`的要求在`handouts/PA1.pdf`中。我们需要实现一个**栈机器**`Stack Machine`，这个机器以栈为存储和执行的基础。这里简单翻译一下PDF里面的描述。

启动栈机器后，机器创造一个命令行空间，在终端显示一个`>`，可以接受以下指令，这些指令都被压入到栈中。

-   整数
-   字符`+, s, e`

输入字符`e`，会针对当前栈顶指令进行一些操作。

若栈顶为`+`，则将`+`和`+`之后的两个整数弹出，将两个整数相加后的结果压栈。我们不考虑`+`之后的两个元素不是整数、是其它指令的情况。

若栈顶为`s`，则将`s`弹出，再将之后的两个元素互换在栈中的位置。

若栈顶为一个整数，或栈为空，不进行任何操作。

输入字符`x`，退出这个栈机器。

# Cool语言语法提醒

`handout`中建议我们采用面向对象的方法处理不同指令，不管怎样，你都要先阅读`Cool Manual`和`Cool Tour`，了解`Cool`语言的基本语法。这两个文件都在`handouts`目录下。建议你通读这两个PDF文件，之后的`PA`也需要大量的阅读和自己的研究，这是进入状态的好机会！你可以练习**在长文本中筛选重要信息**、**在短时间内理解帮助文档**这些非常重要的技能，

这里提一些需要注意的点，是我经常犯错误的地方，而`coolc`几乎没有错误提示，要修改语法错误很伤脑筋。

1.  每个**类方法**由一个表达式定义，这个表达式可能是一个**变量**、一个**代码块**`{}`，表达式的值就是方法的返回值，故经常出现**大括号内包含大括号**的情况。方法的结束大括号`}`后需要添加`;`。
2.  `if, while`等结构后需要跟`then, loop`等关键字，不能直接跟表达式。
3.  `if, while`等结构也是一种**表达式**，也有值。当需要包含多个表达式时，要使用`{}`代码块，类似**类方法**。
4.  `Local Variable`需要用`let`关键字定义，不能**直接在代码段中定义**。

# 我的实现

这里贴上我在文件`stack.cl`中的代码，仅供参考。

首先定义`Command`系列类，共有`execute, getChar`接口，分别进行指令的执行和获得指令名称的操作。

```java
class StackCommand {

   getChar(): String {
      "Called from base class"
   };

   execute(node: StackNode): StackNode {
      let ret: StackNode in {
         (new IO).out_string("Undefined execution!\n");
         ret;
      }
   };

   getNumber(): Int {
      0
   };
};

class IntCommand inherits StackCommand {
   number: Int;

   init(num: Int): SELF_TYPE {
      {
         number <- num;
         self;
      }
   };

   execute(node: StackNode): StackNode {
      node
   };

   getNumber(): Int {
      number
   };

   getChar(): String {
      (new A2I).i2a(number)
   };
};

class PlusCommand inherits StackCommand {
   init(): SELF_TYPE {
      self
   };

   execute(node: StackNode): StackNode {
      let n1: StackNode <- node.getNext(),
         n2: StackNode <- n1.getNext(),
         sum: Int,
         ret: StackNode in {
            if (not (isvoid n1)) then
               if (not (isvoid n2)) then {
                  sum <- n1.getCommand().getNumber() + n2.getCommand().getNumber();
                  ret <- (new StackNode).init((new IntCommand).init(sum), n2.getNext());
               } 
               else 
                  0
               fi
            else
               0
            fi;
            ret;
         }
   };

   getChar(): String {
      "+"
   };
};

class SwapCommand inherits StackCommand {
   init(): SELF_TYPE {
      self
   };

   execute(node: StackNode): StackNode {
      let next: StackNode <- node.getNext().getNext() in {
         node <- node.getNext();
         node.setNext(next.getNext());
         next.setNext(node);
         next;
      }
   };

   getChar(): String {
      "s"
   };
};
```

指令类的执行接口`execute`接受栈顶作为参数，返回新的栈顶。栈的结构定义如下：

```java
class StackNode {
   command : StackCommand;
   next : StackNode;

   init(co: StackCommand, ne: StackNode): StackNode {
      {
         command <- co;
         next <- ne;
         self;
      }
   };

   putOnTop(co: StackCommand): StackNode {
      let newNode: StackNode in {
         newNode <- (new StackNode).init(co, self);
         newNode;
      }
   };

   getCommand(): StackCommand {
      {
         command;
      }
   };

   getNext(): StackNode {
      {
         next;
      }
   };

   setNext(node: StackNode): StackNode {
      next <- node
   };
};
```

有了这些基础之后，在`Main`类中实现主流程。`main`函数不断等待命令行输入，对得到的字符指令进行处理。

```java
class Main inherits A2I {
   stackTop: StackNode;

   printStack(): Object {
      let node: StackNode <- stackTop in {
         while (not (isvoid node)) loop
         {
            (new IO).out_string(node.getCommand().getChar());
            (new IO).out_string("\n");
            node <- node.getNext();
         }
         pool;
      }
   };

   pushCommand(command: StackCommand): StackCommand {
      {
         if (isvoid stackTop) then {
            let nil: StackNode in {
               stackTop <- (new StackNode).init(command, nil);
            };
         } else {
            stackTop <- stackTop.putOnTop(command);
         } fi;
         command;
      }
   };

   executeStackMachine(inString: String): Object {
      {
         if (inString = "+") then
         {
            pushCommand((new PlusCommand).init());
         }
         else
            if (inString = "s") then
               pushCommand((new SwapCommand).init())
            else
               if (inString = "d") then
                  printStack()
               else
                  if (inString = "x") then
                     -- stop
                     {
                        (new IO).out_string("stop!\n");
                        abort();
                     }
                  else
                     if (inString = "e") then
                        let node: StackNode <- stackTop in {
                           if (not (isvoid node)) then
                              stackTop <- node.getCommand().execute(node)
                           else
                              0
                           fi;
                        }
                     else
                        pushCommand((new IntCommand).init((new A2I).a2i(inString)))
                     fi
                  fi
               fi
            fi
         fi;
      }
   };

   main() : Object {
      let inString: String in {
         while (true) loop
         {
            (new IO).out_string(">");
            inString <- (new IO).in_string();
            executeStackMachine(inString);
         }
         pool;
      }
   };

};
```

# 让Cool程序跑起来

不建议使用提供好的`make test`测试，因为这个指令将`stack.test`中的字符一股脑往我们的程序里塞，可能造成格式错乱。

我给这个`Makefile`新增了一项：

```makefile
run: compile
	${CLASSDIR}/bin/spim -file stack.s
```

这是为了方便地运行我们的程序。运行之后，你可以玩玩自己写的这个**栈机器**。我将`stack.test`中的指令依次打给栈机器，得到结果如下，你也可以玩玩别的，挺有趣。

```shell
../../bin/spim -file stack.s
SPIM Version 6.5 of January 4, 2003
Copyright 1990-2003 by James R. Larus (larus@cs.wisc.edu).
All Rights Reserved.
See the file README for a full copyright notice.
Loaded: ../lib/trap.handler
>e
>e
>1
>+
>2
>s
>d
s
2
+
1
>e
>d
+
2
1
>e
>+
>1
>s
>s
>s
>d
s
s
s
1
+
3
>e
>e
>s
>e
>e
>e
>d
4
>x
stop!
Abort called from class Main
```

这样就结束了简单而简短的`PA1`。