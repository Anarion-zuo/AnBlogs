# Java | 用条件变量和锁实现读写锁

我在写[simpledb](https://github.com/MIT-DB-Class/simple-db-hw-2021/blob/master/lab4.md)的时候，需要实现比Java本身有的`ReentrantReadWriteLock`更多功能的读写锁，也不能简单封装`ReentrantReadWriteLock`，只能用基础设施从头开始写。算是练习了Java并发编程。

完整[代码](https://github.com/Anarion-zuo/simpledb/blob/lab3/src/java/simpledb/transaction/LockManager.java)和[测试](https://github.com/Anarion-zuo/simpledb/blob/lab3/test/simpledb/LockManagerTest.java)在这里。本文只放了部分代码。

代码都是数据库项目场景下的，但是可以拓展到一般场景。每个线程带着一个`TransactionId`，锁管理的资源是`PageId`类，代表一个数据库**事务**申请或释放一个存储页。加锁和解锁的接口大概形状为：

```java
public void sharedLock(TransactionId transactionId);
public void releaseShared(TransactionId transactionId);
public void exclusiveLock(TransactionId transactionId);
public void releaseExclusive(TransactionId transactionId);
```

按照正常开发流程，应先确定接口形状、写好功能说明和测试，再写具体实现。本文展开顺序与此相反。提醒一下你，最后的测试部分最好在写具体实现之前写好，这样更容易找出bug。测试部分贴了很多代码，如果你只想看原理，就没必要看了。

# 类结构

锁管理的对象是`PageId`类，这里不考虑其它类。管理锁的类用哈希表建立`PageId`对象到具体锁的映射，再用额外的锁管理对这个哈希表的访问。

```java
public class LockManager {
    private final HashMap<PageId, LockItem> lockMap = new HashMap<>();
    private final Lock mapLock = new ReentrantLock();
    // ...
}
```

要对锁进行操作，通过`PageId`获得锁。

```java
mapLock.lock();
LockItem lockItem = lockMap.get(pageId);
if (lockItem == null) {
    lockItem = new LockItem();
    lockMap.put(pageId, lockItem);
}
mapLock.unlock();
// lockItem.aquireXxx();
```

锁对象的核心是互斥锁和条件变量，另外记录申请到读锁和写锁和线程，之后项目中可能用到。用集合`sharedTransactions`记录申请到读锁的线程，因为可以有多个。申请到写锁的线程只能有一个，所以用一个对象`exclusiveTransaction`指着。

```java
private static class LockItem {
    private final Condition cond;
    private final Lock lock;
    private final HashSet<TransactionId> sharedTransactions = new HashSet<>();
    private TransactionId exclusiveTransaction = null;

    // ...
}
```

读写锁具有以下性质：

- 未加写锁时，取读锁不阻塞。
- 加写锁后，取读锁、写锁都阻塞。
- 加读锁后，取写锁阻塞。
- 有写锁在等待读锁时，再取读锁阻塞。

根据这些性质，依次实现。

# 读锁

申请读锁需要等待写线程释放写锁，故写进程释放写锁时应创造条件。

```java
public void releaseExclusive(TransactionId transactionId) throws DbException {
    lock.lock();
    exclusiveTransaction = null;
    cond.signalAll();
    lock.unlock();
}
```

申请读锁时等待条件满足，把申请到锁的线程记录在集合里面。

```java
public void sharedLock(TransactionId transactionId) {
    lock.lock();
    try {
        while (exclusiveTransaction != null) {
            cond.await();
        }
        sharedTransactions.add(transactionId);
    } catch (InterruptedException e) {
        e.printStackTrace();
    } finally {
        lock.unlock();
    }
}
```

# 写锁

申请写锁应该等待所有读线程释放，故读进程释放时创造条件。

```java
public void releaseShared(TransactionId transactionId) throws DbException {
    lock.lock();
    sharedTransactions.remove(transactionId);
    if (sharedTransactions.isEmpty()) {
        cond.signalAll();
    }
    lock.unlock();
}
```

申请写锁时等待条件，要同时满足所有读线程释放和上一个写线程释放。`exclusiveTransaction`为空时，代表没有线程加了写锁，需要等待这个条件满足，再令`exclusiveTransaction`指向自己。然后等待所有读线程释放锁。

```java
public void exclusiveLock(TransactionId transactionId) {
    lock.lock();
    try {
        /**
            * First, must ensure exclusive Transaction be given to this transactionId.
            * Must wait for the preceding one to release.
            */
        while (!transactionId.equals(exclusiveTransaction)) {
            while (exclusiveTransaction != null) {
                cond.await();
            }
            exclusiveTransaction = transactionId;
        }
        /**
            * Then, must wait for all shared locks to be released.
            */
        while (!sharedTransactions.isEmpty()) {
            cond.await();
        }
    } catch (InterruptedException e) {
        e.printStackTrace();
    } finally {
        lock.unlock();
    }
}
```

# 重复加锁

一般系统提供的互斥锁不能同一线程重复加锁，重复加锁会直接导致死锁。本项目中存在很多重复申请资源的操作，故把检查是否上锁的任务交给`LockItem`，让程序员（也就是我）轻松一点。

实现起来不难，只需要检查一下之前加过锁没有。读锁只需要检查一下集合`sharedTransactions`，写锁检查当前`exclusiveTransaction`是否相等。

读锁：

```java
if (sharedTransactions.contains(transactionId)) {

} else {
    while (exclusiveTransaction != null) {
        cond.await();
    }
    sharedTransactions.add(transactionId);
}
```

写锁不需要特别处理，上面的代码刚好满足了重复加锁的要求。

# 写当作读

线程获得写锁后，应该自动获得读锁，即申请读锁不阻塞。只需要检查当前读线程是否是当前正在申请锁的线程。

```java
if (transactionId.equals(exclusiveTransaction)) {

} else {
    if (sharedTransactions.contains(transactionId)) {

    } else {
        while (exclusiveTransaction != null) {
            cond.await();
        }
        sharedTransactions.add(transactionId);
    }
}
```

# 读等待在等待的写

为了防止写线程饥饿，当有写线程在等待时，新的读锁申请应该阻塞。上面的实现刚好满足了这个要求，把`exclusiveTransaction`设置为自己后，申请读锁就需要等待`exclusiveTransaction`为空才能继续。

```java
while (exclusiveTransaction != null) {
    cond.await();
}
```

# 测试

依次写好对读写锁特性的测试。

不同线程可以同时持有读锁，不应该阻塞，能正常释放一次，未加锁不能释放。

```java
@Test public void sharedLockTest() {
    TransactionId tid1 = new TransactionId();
    TransactionId tid2 = new TransactionId();
    PageId pageId = new HeapPageId(0, 0);
    lockManager.aquireSharedLock(tid1, pageId);
    // should not block
    lockManager.aquireSharedLock(tid2, pageId);
    try {
        lockManager.releaseSharedLock(tid1, pageId);
        lockManager.releaseSharedLock(tid2, pageId);
    } catch (DbException e) {
        Assert.fail();
    }
    try {
        lockManager.releaseSharedLock(tid1, pageId);
        Assert.fail("releasing not aquired lock not throwing");
    } catch (DbException e) {

    }
    try {
        lockManager.releaseSharedLock(tid2, pageId);
        Assert.fail("releasing not aquired lock not throwing");
    } catch (DbException e) {

    }
}
```

能够正常申请和释放写锁，未加锁不能释放。同一线程加锁后再申请同一锁不阻塞。同一线程已经加写锁后，再申请读锁不阻塞。

```java
@Test public void exclusiveLockTest() {
    TransactionId tid1 = new TransactionId();
    PageId pageId = new HeapPageId(0, 0);
    lockManager.aquireExclusiveLock(tid1, pageId);
    // same lock can be aquired twice by the same transaction
    // but not by any other transaction
    lockManager.aquireExclusiveLock(tid1, pageId);
    // can use an exclusive lock as a shared lock
    lockManager.aquireSharedLock(tid1, pageId);
    try {
            lockManager.releaseSharedLock(tid1, pageId);
            Assert.fail("release exclusive lock as shared lock");
        } catch (DbException e) {
        }
        try {
            lockManager.releaseExclusiveLock(tid1, pageId);
        } catch (DbException e) {
            Assert.fail("cannot release aquired lock");
        }
        try {
            lockManager.releaseExclusiveLock(tid1, pageId);
            Assert.fail("releasing not aquired lock not throwing");
        } catch (DbException e) {

        }
}
```

已申请到的读锁可以转化为写锁，且等待其他读锁完成。

```java
@Test public void upgradeWaitsForSharedTest() throws InterruptedException {
    TransactionId tid1 = new TransactionId();
    PageId pageId = new HeapPageId(0, 0);
    lockManager.aquireSharedLock(tid1, pageId);
    var ref = new Object() {
        boolean flag = false;
    };
    // start a thread to aquire exclusive lock
    Thread thread = new Thread(() -> {
        TransactionId tid2 = new TransactionId();
        // should block
        lockManager.aquireSharedLock(tid2, pageId);
        lockManager.aquireExclusiveLock(tid2, pageId);
        if (!ref.flag) {
            Assert.fail("exclusive lock did not wait for shared lock");
        }
    });
    thread.start();
    Thread.sleep(500);  // 500ms
    try {
        ref.flag = true;
        lockManager.releaseSharedLock(tid1, pageId);
    } catch (DbException e) {
        Assert.fail("failed to release aquired shared lock");
    }
    thread.join();
}
```

和以上相同的模式可以写申请读锁等待写锁完成、申请写锁等待读锁完成、申请写锁等待写锁完成，就不一一列举。

最重要的，当有线程阻塞在申请写锁时，申请新的读锁应该阻塞。

```java
@Test public void sharedWaitsForPendingExclusiveTest() throws InterruptedException, DbException {
    int sharedCount = 1001;
    PageId pageId = new HeapPageId(0, 0);
    // aquire some shared locks
    TransactionId shared1 = new TransactionId();
    TransactionId shared2 = new TransactionId();
    lockManager.aquireSharedLock(shared1, pageId);
    lockManager.aquireSharedLock(shared2, pageId);

    var prevReleasedWrapper = new Object() {
        boolean prevSharedReleased = false;
        boolean prevExReleased = false;
    };

    // start a thread to aquire exlusive lock
    Thread pendingExclusive = new Thread(() -> {
        TransactionId ex1 = new TransactionId();
        // should block
        lockManager.aquireExclusiveLock(ex1, pageId);
        System.out.println("supposed pending exclusive locks aquired");
        Assert.assertTrue(prevReleasedWrapper.prevSharedReleased);
        // start a thread to aquire shared lock
        Thread tryLockShare = new Thread(() -> {
            TransactionId tryShare = new TransactionId();
            // should block
            lockManager.aquireSharedLock(tryShare, pageId);
            System.out.println("supposed pending shared locks aquired");
            Assert.assertTrue(prevReleasedWrapper.prevSharedReleased);
            try {
                System.out.println("release supposed pending shared locks");
                lockManager.releaseSharedLock(tryShare, pageId);
            } catch (DbException e) {
                Assert.fail("failed to released previously aquired shared lock");
            }
        });
        System.out.println("start pending shared lock");
        tryLockShare.start();
        try {
            Thread.sleep(500);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        try {
            prevReleasedWrapper.prevExReleased = true;
            System.out.println("release exclusive lock");
            lockManager.releaseExclusiveLock(ex1, pageId);
        } catch (DbException e) {
            Assert.fail("failed to released previously aquired exclusive lock");
        }
        try {
            tryLockShare.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    });
    System.out.println("start pending exclusive lock");
    pendingExclusive.start();
    Thread.sleep(500);
    prevReleasedWrapper.prevSharedReleased = true;
    System.out.println("release first shared locks");
    lockManager.releaseSharedLock(shared1, pageId);
    lockManager.releaseSharedLock(shared2, pageId);
    pendingExclusive.join();
}
```
