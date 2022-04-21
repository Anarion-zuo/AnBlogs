# CSS盒模型box

两种类型：
- block
- inline

两种显示方式display：
- outer
- inner

指定显示方式display为类型block/inline。

## 外部显示outer display

为block时：
- 新开启一行显示block
- 行方向上，盒子尽量充满父级容器，通常会充满整个容器
- 设置属性width/height是有用的
- 盒子边界属性影响盒子的位置padding/margin/border

为inline时：
- 不新开启一行显示盒子
- width/height设置无效
- 垂直方向上的边界属性无效padding/margin/border
- 水平方向上有效，如上

<style>
    .outer-block {
        display: block;
        /* effective size config */
        width: 500px;
        height: 500px;
        background-color: lightblue;
        color: black;
    }
    .inner-block {
        border: black solid 2px;
        display: block;
        /* effective size config */
        height: 100px;
        /* new line in spite of lesser width */
        width: 100px;
    }
    .inner-inline {
        border: black solid 2px;
        display: inline;
        /* nullified size config */
        height: 100px;
        width: 20px;
    }
    .outer-flex {
        display: flex;
        /* effective size config */
        width: 500px;
        height: 500px;
        background-color: lightgreen;
        color: black;
    }
    .inner-flex {
        border: black solid 2px;
        display: flex;
    }
</style>

<div class="outer-block">
    <div class="outer-block">
        <div class="inner-block">new line in spite of lesser width</div>
        <div class="inner-block">new line in spite of lesser width</div>
        <div class="inner-inline">some text to extend this box</div>
    </div>
    <div class="outer-flex">
        <div class="inner-flex">outer behaves as a block </div>
        <div class="inner-flex">outer behaves as a inline</div>
    </div>
</div>

### 内外显示

同样设置display属性，设置为如flex等值时，outer display自动设置，inner display由display设置决定。

## 尺寸

标准模型：
- width/height指定内容宽高
- 盒子真正的宽高=width/height+padding+border
- margin不认为时盒子宽高的一部分

alternative：
- ...

## 边框

### margin

可以给负值，让盒子超出父级容器。

相邻的margin会融合成一个，取最大值。当只有一个为负值，取两个值的和。当两个都为负，取最小值，而不是绝对值最小值。

## inline block

一半的inline盒子，水平方向边框有效，使得周围内容被挤开。垂直方向上无效，内容不会被挤开。

inline-block是两者的中间状态。
- 不想盒子新开一行
- 想让盒子垂直方向不和其他内容重叠，挤开其他内容

## overflow

默认是visible，显示所有内容，超出的部分覆盖其他地方的内容。

设置为hidden，不显示超出的部分。

设置为scroll，显示超出的部分，可以滚动。

可以设置overflow-x/overflow-y，令滚动条出现在不同位置。

设置为auto，控制滚动条在不需要出现的时候隐藏。