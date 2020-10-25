#! https://zhuanlan.zhihu.com/p/268637430
# 翻译｜学CMake

本文是[How to Build a CMake-Based Project](https://preshing.com/20170511/how-to-build-a-cmake-based-project/)和[Learn CMake's Scripting Language in 15 Minutes](https://preshing.com/20170522/learn-cmakes-scripting-language-in-15-minutes/)两篇博客的简单翻译，带上了我自己对`CMake`的理解，也是为了帮助自己加深理解。

前一篇讲解`CMake`的工作流程，以及如何在命令行中使用`cmake`。后一篇讲解`cmake`脚步语法。这是我找到的为数不多系统讲解`CMake`工具的材料，非常可贵，值得写本文，值得好好阅读理解。

本文md文档链接：

下面正式开始。

----

# How to Build a CMake-Based Project

## 源文件目录和二进制输出目录

`CMake`定义了**构建流水线**`build pipelines`，其它形式的构建流水线如`Visual Studio`的`.sln`文件、`Xcode`的`.xcodeproj`、`Unix`系统的`Makefile`。

**构建流水线**的建立需要指定**源文件目录**和**输出目录**。对于`CMake`，原文件目录是**包含**`CMakeLists.txt`的目录，输出目录是**建立**构建流水线时的**工作目录**。常用的结构时，在原文件目录下创建一个`build`子目录，以`build`目录为工作目录创建**构建流水线**。把**输出目录**和**源文件目录**分开，可以随时删掉**输出目录**，甚至可以同时使用多个**构建流水线**，放在多个不同的`build`目录下。

我们通常不把**输出目录**下的文件提交给`VCS`。

## 配置和生成两步

有很多中办法运行`CMake`，无论如何，一定包含两步，配置`configure`和生成`generate`。

![两步](CMake-15min.assets/cmake-simple-flowchart.png)

**生成**`configure`步就是运行`CMakeLists.txt`，定义了一些目标`target`。执行过程中做了哪些事情，由`CMakeLists.txt`内容决定。

## 从命令行运行CMake

选好`CMakeLists.txt`文件所在目录和`cmake`指令的工作目录，决定了源文件目录和二进制输出目录。通常在源文件目录下创建子目录`build`，在`build`目录下执行`cmake`。

```bash
mkdir build
cd build
cmake ..
```

给`-G`值，指定想要输出哪种`build pipeline`。

```bash
cmake -G "Visual Studio 15 2017" ..
```

如果没有指定，`cmake`会根据当前系统自动指定一个。如在`Unix`系下可能自动生成`Makefile`，相当于`-G "Unix Makefiles"`。

给`-D`值，创建一个`CMake`脚本变量。

```bash
cmake -G "Visual Studio 15 2017" -DDEMO_ENABLE_MULTISAMPLE=1 ..
```

以上创建了变量`DEMO_ENABLE_MULTISAMPLE`，值为`1`。注意，`-D`后没有空格。

写`C/C++`项目时，你可能想要指定`CMAKE_BUILD_TYPE=Debug/Release`。`CMake`默认选项为未优化、无符号，即没有效率提升，也不能用于`debug`，没啥用。`CMAKE_BUILD_TYPE`最好一定手动指定。

产生了一个`build pipeline`之后，就和`CMake`没什么关系了。如以`make`为目标，在`CMakeLists.txt`中定义的所有`target`都可以通过`make`构建。

构建其它类型的`build pipeline`，请参考[原文](https://preshing.com/20170511/how-to-build-a-cmake-based-project/)。

# Learn CMake's Scripting Language in 15 Minutes

每次你添加一个新库，或为一个新平台提供支持时，你都要修改`CMake`脚本。我花了很多时间，机械地修改`CMake`脚本，而没有真正理解我作的这些编辑，只是简单地参考了各式各样的文档、博客和教程。最终，我对`CMake`好像有了新的理解，可以不借助外力、自由使用了。

从**到处看教程抄代码**到**学会CMake**，本文的目的就是帮助你缩短这一过程，为你提供稍微系统一些的解释。本文当然不会完全讲解所有的`CMake`指令，更多是讲解`CMake`的语法和语言模型，帮助你获得更系统的认识。

本文讲解对应的官方文档是[command reference](https://cmake.org/cmake/help/latest/manual/cmake-commands.7.html)，没有包含[generator expressions](https://cmake.org/cmake/help/latest/manual/cmake-generator-expressions.7.html#manual:cmake-generator-expressions(7))有关内容。

## Hello World

创建文件`hello.txt`：

```cmake
message("Hello World")
```

可以在命令行下执行：

```bash
cmake -P hello.txt
```

得到`Hello World`输出。

可以看到，`cmake`指令在命令行下启动`CMake`，`-P`指定了要执行的`CMake`脚本文件。

## 所有变量都是字符串

`CMake`中，所有变量都是字符串。你可以在字符串中包含另一个字符串，也就是将另一个变量的值嵌入字符串中，如下：

```cmake
message("Hello ${NAME}")
```

变量，也就是字符串的内容，取代`${}`位置。

变量可以在`CMake`脚本内部定义，也可以在调用`CMake`的时候定义：

```bash
cmake -DNAME=Newman -P hello.txt
```

则变量`NAME`具有了值`Newman`。

若变量未定义，则当作空串处理：

```bash
$ cmake -P hello.txt
Hello !   # empty after Hello
```

在`CMake`脚本中定义变量，使用`set`指令。

```cmake
set(THING "funk")
message("we want the ${THING}!")
```

`set`指令中，不一定要在**值**位置上写双引号，如下代码和上面等价：

```cmake
set(THING funk)
message("we want the ${THING}!")
```

也可以在**变量名**位置上写双引号，如下代码和上面等价：

```cmake
set("THING" funk)
message("we want the ${THING}!")
```

故是否写双引号，更多是个人习惯。我推荐你不给变量名写双引号，而给变量值，也就是字符串，写双引号，以求和写其它代码的时候习惯一致，也就是上面第一次出现`set`指令的代码块那样。

## 使用前缀模拟数据结构

`CMake`没有类`class`或结构体`struct`机制，但你还是可以自己模拟类似机制。

你可以认定，具有相同前缀的变量是统一对象的属性，如`JOHN_NAME, JOHN_ADDRESS`都是`JOHN`的属性，可以通过`JOHN`对象调用这些属性，如下：

```cmake
set(PERSON "JOHN")
set(JOHN_NAME "John Smith")
set(JOHN_ADDRESS "123 Fake St")
message("${${PERSON}_NAME} lives at ${${PERSON}_ADDRESS}.")
```

可以看出，这里利用了`${}`操作符的特性，即可以嵌套使用。

更进一步，可以直接通过`${}`设置属性。

```cmake
set(${PERSON}_NAME "John Goodman")
```

这样一来，改变`PERSON`变量的值，即改变所有其它属性的归属，十分方便。`PERSON`为`JOHN`的抽象。

## 每个表达式都是指令

每个表达式`statement`都是指令，每个指令接受一系列参数，没有返回值。这些参数由空格隔开，每个参数都是一个字符串，若参数中需要包含空格，则必须使用双引号定义参数，否则认定空格为分隔符。

上面的`set`指令就是**指令**的一个好例子，这里看看另一个例子`math`，用来做一些简单的数字计算。

`math`指令接受三个参数。

- 第一个参数一定是`EXPR`。
- 第二个参数用来接受计算结果。
- 第三个参数是计算表达式。

```cmake
math(EXPR MY_SUM "1 + 1")                   # Evaluate 1 + 1; store result in MY_SUM
message("The sum is ${MY_SUM}.")
math(EXPR DOUBLE_SUM "${MY_SUM} * 2")       # Multiply by 2; store result in DOUBLE_SUM
message("Double that is ${DOUBLE_SUM}.")
```

更多指令请看[CMake command](https://cmake.org/cmake/help/latest/manual/cmake-commands.7.html)。`string`指令用于字符串处理，`file`指令用于文件读写，以及文件路径字符串操作。

## if

一对关键字`if/else/endif`，判断变量是否被声明过。

```cmake
if(WIN32)
    message("You're running CMake on Windows 32.")
else()
	message("You're not running CMake on Windows 32.")
endif()
```

判断一个可能的内置变量`WIN32`，`Win 32`平台下的`CMake`才会执行里面的`message`指令。

也可以在`()`中写产生布尔值的语句：

```cmake
if (${address} STREQUAL "ON")
    ...
else()
    ...
endif()
```

## while

一对关键字`while/endwhile`，表达循环。原文的例子是计算`Fibonacci`数列。

```cmake
set(A "1")
set(B "1")
while(A LESS "1000000")
    message("${A}")                 # Print A
    math(EXPR T "${A} + ${B}")      # Add the numeric values of A and B; store result in T
    set(A "${B}")                   # Assign the value of B to A
    set(B "${T}")                   # Assign the value of T to B
endwhile()
```

更多产生布尔值的语句，请看[documentation](https://cmake.org/cmake/help/latest/command/if.html)。

## 数组是含有分号的字符串

把几个变量用空格隔开，等价于把他们的值用`;`隔开放入同一字符串。

```cmake
set(MY_LIST These are separate arguments)
message("${MY_LIST}")    # Prints: These;are;separate;arguments
```

一个字符串中包含`;`，等价于多个变量用空格隔开。

```cmake
set(ARGS "EXPR;T;1 + 1")
math(${ARGS})            # Equivalent to calling math(EXPR T "1 + 1")
```

## 操作数组

`list`指令操作数组，增删改查中，增已经很容易实现，再实现删就可以顺便实现改。通过`list`进行**删**如下：

```cmake
set(MY_LIST These are separate arguments)
list(REMOVE_ITEM MY_LIST "separate")  # Removes "separate" from the list
message("${MY_LIST}")                 # Prints: These;are;arguments
```

`foreach`操作遍历数组，非常简单。

```cmake
foreach(ARG These are separate arguments)
    message("${ARG}")                # Prints each word on a separate line
endforeach()
```

## 函数有命名空间，宏没有

`CMake`可以定义函数。

```cmake
function(doubleIt VALUE)
    math(EXPR RESULT "${VALUE} * 2")
    message("${RESULT}")
endfunction()

doubleIt("4")        # Prints: 8
```

调用函数`doubleIt`，输出了信息，没有直接的**返回值**机制。

函数内不可以修改函数外定义的变量，也就不用担心**污染**。若想向函数外的变量传值，需给`set`指令多传指令`PARENT_SCOPE`。

```cmake
function(doubleIt VARNAME VALUE)
    math(EXPR RESULT "${VALUE} * 2")
    set(${VARNAME} "${RESULT}" PARENT_SCOPE)    # Set the named variable in caller's scope
endfunction()

doubleIt(RESULT "4")                    # Tell the function to set the variable named RESULT
message("${RESULT}")                    # Prints: 8
```

`VARNAME`的值在调用函数时指定，这里指定为`RESULT`。

函数可以接受任意个数参数，通过关键字`ARGN`，获得参数列表。

```cmake
function(doubleEach)
    foreach(ARG ${ARGN})           # Iterate over each argument
        math(EXPR N "${ARG} * 2")  # Double ARG's numeric value; store result in N
        message("${N}")            # Print N
    endforeach()
endfunction()

doubleEach(5 6 7 8)                # Prints 10, 12, 14, 16 on separate lines
```

相比之下，**宏**可以访问定义在自己之外的变量。

```cmake
macro(doubleIt VARNAME VALUE)
    math(EXPR ${VARNAME} "${VALUE} * 2")        # Set the named variable in caller's scope
endmacro()

doubleIt(RESULT "4")     # Tell the macro to set the variable named RESULT
message("${RESULT}")     # Prints: 8
```

`RESULT`的值在宏中被修改了。

## include

`include`包含另一个文件中的`CMake`脚本指令，被包含的指令和本文件的指令在同一命名空间，相当于`C/C++`的`include`，只是机械地从另一个文件搬运代码。

另一个指令`find_package`，查找命名形如`Find*.cmake`的文件，专门用于添加新库。如`find_package(SDL2)`等价于`include(FindSDL2.cmake)`。

指令`add_subdirectory`创建了一个新的命名空间，被包含的子目录和原文件相互独立，用于包含另一个完整的`CMake`项目，是为子项目。子项目中定义的各种变量不会污染本项目，除非想上面那样给`set`指令写`PARENT_SCOPE`。

以[Turf](https://github.com/preshing/turf)为例：

![Turf例子](CMake-15min.assets/cmake-variable-scopes.png)

## 读写属性

`CMake`项目有一些**目标**`target`，这些`target`在`CMake`项目被编译之后，可以通过`make`构建。指令`add_executable, add_library, add_custom_target`可以创建`target`，创建之后，`target`就具有了一些**属性**`properties`。通过`get_property, set_property`指令可以修改这些属性。

```cmake
add_executable(MyApp "main.cpp")        # Create a target named MyApp

# Get the target's SOURCES property and assign it to MYAPP_SOURCES
get_property(MYAPP_SOURCES TARGET MyApp PROPERTY SOURCES)

message("${MYAPP_SOURCES}")             # Prints: main.cpp
```

`get_property`中，指定了`target`为`MyApp`，`property`名为`SOURCES`，最终结果存储在`MYAPP_SOURCES`。

一些指令可以**间接**修改一些`property`，即`LINK_LIBRARIES, INCLUDE_DIRECTORIES, COMPILE_DEFINITIONS`。修改的指令有`target_link_libraries, target_include_directories, target_compile_definitions`。更多`property`请看[directory properties](https://cmake.org/cmake/help/latest/manual/cmake-properties.7.html#properties-on-directories), [global properties](https://cmake.org/cmake/help/latest/manual/cmake-properties.7.html#properties-of-global-scope), [source file properties](https://cmake.org/cmake/help/latest/manual/cmake-properties.7.html#properties-on-source-files)。