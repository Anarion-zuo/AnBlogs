# 链式复制机制

- 另一种主从复制机制
- 读操作只涉及一个节点
- 更简单的故障恢复机制
- 更简单的linearizability

## 系统状态

系统状态抽象为两个集合$Hist_{objID}$和$Pending_{ibjID}$，代表对于特定对象$obj$的已经执行的的修改请求和已收到待执行的修改请求。

对应这两个集合，有以下几种改变状态的方式：

- 接受到新请求$Pending:=Pending\cup \{r\}$
- 忽略接受到的请求$Pending:=Pending-\{r\}$
- 处理一个处在$Pending$中的请求
  - 读请求根据$Hist$返回
  - 写请求放入$Hist$

## 链式结构

服务器组织成一个线性序列，每个服务器都有一个前驱和后继，除了头和尾之外。所有节点都能接受请求，并把请求往头或尾的方向转发。转发是指直接发送给节点，而不是沿着链结构依次传播过去。

读请求全部转发到尾节点，尾节点产生所有对读请求的响应。

写请求全部转发到头节点，在头节点原子地执行写操作。头结点执行完成后，利用链结构向其他节点依次传播，其余节点依次改变自己的状态。

新状态的更新过程中，离头结点远的节点状态当然不如更近的节点状态新，即$Hist^j\inf Hist^i,i\le j$。基于这个事实，可以得到节点故障导致链断裂、进而导致头尾节点改变时，对整个集群状态的影响。

写操作在完成同步之后返回，即在整个链完整传播之后，头结点给客户端返回ok。所以，对于同一个客户端，这样的设计保证了强一致性。

## 节点的添加和删除

一个处在链结构之外的master集群应该用来维护集群的结构信息，每个服务器的前驱、后继信息，当前链的头尾节点信息等。文章中原型系统用Paxos实现了这件事。

### 头节点挂掉

头结点保存了最新的$Hist$，但对于客户端来说，$Hist$实际上的版本是尾节点具有的，故头结点的版本丢失后，等效于删除了$Pending$集合中的部分内容。

无论头结点是否已经成功执行写操作，在写操作还未传播到尾节点时，就相当于还未执行完成。如果头节点挂掉前，新状态已经传播至另一个节点，则中间节点是否挂掉直接影响尾节点最终状态的变化。

### 尾节点挂掉

尾节点的$Hist$状态最旧，故尾节点挂掉可导致集群整体状态变新，即$Hist$变大、$Pending$变小。

### 中间节点挂掉

中间节点挂掉之后，其前驱和后继连接在一起，弥合丢失的节点。

每个节点记录已经传递但尾节点还未处理的集合$Sent$，当尾节点处理了一个更新后，向头结点方向传播一个ack信号。每个节点收到这个ack信号之后，将对应的id从$Sent$集合删除。

当发生中间节点丢失时，原前驱节点向原后继节点传播所有在$Sent$集合里面的更新请求。

### 添加一个节点

理论上，在链的任意位置添加节点都是可以的。实际上，在尾部添加最简单。

原尾节点应将自己的整个$Hist$传输给新节点。如果想实现传输和读操作回复的并发，则可以将新来的更新请求放入$Sent$集合，然后正常地向新节点传输。

新节点开始插入时，旧尾节点开始向新节点传输自己的$Hist$集合，并把新来的更新请求放入自己的$Sent$集合。传输$Hist$完成后，改变master集群的状态，令新节点成为尾节点，原尾节点中的$Sent$集合开始向新节点传输，所有读请求被转发到新节点。

新节点成为尾节点后，要等到旧节点完成$Sent$的发送，才能开始处理读请求。这段时间，客户端等待服务端响应，当作是正常执行的一部分。

## 主从复制视角

一般的主从复制采用星型结构，写指令时间平均需要两倍的写操作时间，即在主节点写和在从节点写的时间。

链式结构下，写操作时间和节点个数成正比，效率明显更差。这是用效率换可靠性，因为每次写操作结束的时刻，为所有节点都同步完成的时刻。一般主从复制机制可能认为超过半数的节点完成同步就是写操作完成。

当有节点挂掉时，两种机制的反应不同。链结构表现为响应时间延长，因为内部结构需要调整。星结构主节点挂掉时，会有一段时间的不接受服务阶段。虽然可以令客户端把这段时间当作延迟来处理。

## 优化

### 多个链

类似sharding，特定对象都能映射到多个链上的一个。每个链相互独立地运行。