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
- 盒子边界属性影响盒子的位置 padding/margin/border

为inline时：
- 不新开启一行显示盒子
- width/height设置无效
- 垂直方向上的边界属性无效padding/margin/border
- 水平方向上有效，如上

## 内外显示的区别

同样设置display属性，设置为如flex等值时，outer display自动设置，inner display由display设置决定。