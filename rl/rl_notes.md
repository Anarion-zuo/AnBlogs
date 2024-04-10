# RL notes

## Problem Formulation

An *actor* interacts with the *environment*, transitioning from *state* to *state* in the process. Each *state transition* is triggered by an *action*, and receives a *reward* from the *environment*.

Denote states $s_t$, action $a$, and their sets $S, A$. Each action is drawn from some policy $\pi$, defined as the conditional probability $p(a|s)$ or $\pi(a|s)$ or $\pi(s, a)$. Reward is a function of state and action, denoted $r(s, a)$. Can characterize state transition as:
$$
p(s_{t+1}|s_t)=\sum_a p(s_{t+1}|s_t, a_t)p(a_t|s_t)=E_{a\sim (\cdot |s_t)} [p(s_{t+1}|s_t, a_t)]
$$
where $p(a_t|s_t)$ is defined by the policy, and $p(s_{t+1}|s_t, a_t)$ is the transition kernel. The problem is assumed to satisfy the *Markov* property, or is a *Markov Decision Process*, i.e. $p(s_{t+1}|s_t, a_t)=p(s_{t+1}|s_{1...t}, a_{1...t})$.

Can have 2 different objectives. Only care about the discounted value function, or the *State Value Function*:
$$
V^\pi(s)=E[\sum_{t=0}^{\infty} \gamma^t r(s_t, a_t)|s_0=s, \pi]
$$
is the expected value of some trajectory starting from state $s$, given policy $\pi$. There exists an optimal $\pi$ s.t. $V^*=\argmin_\pi V^{\pi}$.

## Markov Decision Process (MDP)

A Markov Chain or, Markov process, has the property $p(x_t|x_{1...(t-1)})=p(x_t|x_{t-1})$. To define a Markov Chain, we only need the initial distribution $p(x_0)$ and the transition kernel $p(x_t|x_{t-1})$. Then the whole chain's distribution can be represented.
$$
p(x_t,x_{t-1},...,x_0)=p(x_0)p(x_1|x_0)...p(x_{t}|x_{t-1})=p(x_0)\prod_{t=1}^T p(x_t|x_{t-1})
$$
Any one entry's distribution:
$$
p(x_i)=\int_{x_{-i}} dx_{-i} p(\{x_i\})
$$
Given the first state:
$$
p(x_i|x_0)=\int_{x_{-i,-0}} dx_{-i,-0} \frac{p(\{x_i\})}{p(x_0)}
$$

The Markov Decision Process (MDP) is Markov Chain with *action*s added. The transition kernel becomes $p(s_{t+1}|s_t,a_t)$. And a policy distribution $\pi(s,a)=p(a|s)$. So the whole trajectory can be represented.
$$
p((s_t,a_t)_t|\pi_\theta)=p(s_0,a_0,s_1,a_1,...|\pi_\theta)=p(s_0)\prod_{t} p(s_{t+1},a_t|s_{t}), p(s_{t+1},a_t|s_t)=p(s_{t+1}|a_t,s_t)\pi_\theta(a_t|s_t)
$$
Denote the initial state distribution as $p(s_0)=\mu(s_0)$. Denote the trajectory visitation distribution for any state $s$, $p(s|\pi)=d_{\mu}^\pi(s)$, given start state distribution $\mu$ and policy $\pi$. Expand the visitation distribution:
$$
d^\pi_\mu(s)=\sum_{s_0}\mu(s_0)p(s|s_0),p(s|s_0)=\sum_t p(t)p(s_t=s|s_0,t)
$$
where $t$ is the length of a trajectory reaching state $s$ at the last state. Suppose trajectory length attains the geometric distribution $Geom(\gamma)$, then
$$
p(t)=(1-\gamma)\gamma^t
$$

Expand state distribution at step $t$ on a given trajectory with start state $s$ and policy $\pi$
$$
p(s_t|s_0)=\sum_{(s_k,a_k)_{k=1}^{t-1}} p(s_t,(s_k,a_k)_{k=1}^{t-1}|s_0)=\sum_{(s_k,a_k)_{k=1}^{t-1}} p(s_t|s_{t-1},a_{t-1})p((s_k,a_k)_{k=0}^{t-1}|s_0)
$$
to compute which we need the defined policy and transition probability kernel.


## The Process in general

Set up the problem with what we know. Decide on an exploring policy. Think lightly on the possible differences between exploring and target policy. Let the actor start exploring and collect trajectories. Compute a Bellman target $V(s)$ given the collected trajectories and/or estimate $\nabla_\theta V(s)$. Verify the biasness of the estimates. Collect more trajectories and so on.

## Jargons

- Target/Control policy: Control policy is the policy setting how the agent acts and collect state transition informantion $(s, a, s', r)$. Target policy is the policy we want to learn through RL.
- On/Off-policy: On policy learning is when the Control policy is the same as the currently learned target policy. Note that the currently learned target policy may not be acceptably optimal.
- Model-based/free: Whether the learning process extracts state transition information $p(s'|s,a)$ or $p(s'|s)$ from the environment directly, or through a (deep) model modeling the environment.
- Offline/Online: Offline training is when you use data collected from pre-computed simulations or pre-run interactions. The data can be stored and reused. Online training is when you collect data from an actually running actor.
- Exploration/Exploitation: Exploitation means keep doing the action that improves the objective the most. Exploration means try to do actions other than the currently improving ones, so that some other improving actions may show up in the future.

## Bellman Operators

Given any function $V:S\rightarrow \R$, some policy $\pi$, where $S$ is the state set. Define the *Value Function of the policy* as:
$$
V^\pi=E[\sum_{t=0}^{\infty} \gamma^t r(s_t, a_t)|s_0=s, \pi]
$$

Define the policy's *Bellman Operator* for any function $V$ as:
$$
T^\pi V(s) = r(s, \pi(s)) + \gamma\sum_{s'}p(s'|s, \pi(s))V(s') = r(s, \pi(s)) + \gamma E_{s'\sim(\cdot|s, a)}[V(s')]
$$
where $\pi(s)$ denotes an action selected according to the policy $\pi$, or sampled from $p^\pi(\cdot|s)$.

Write out the $\pi(s)$ defined as $p(a|s)$:
$$
T^\pi V(s) = E_{a\sim p(\cdot|s)}\left\{ r(s, a) + \gamma E_{s'\sim (\cdot|s, a)}[V(s')] \right\} = E_{a\sim p(\cdot|s)}[r(s, a)] + \gamma E_{s'\sim (\cdot|s)}[V(s')]
$$

Define the *Optimal* Bellman Operator as:
$$
T^* V(s) = \max_{a\in A} \left\{ r(s, a) + \gamma\sum_{s'}p(s'|s,a)V(s') \right\}
$$
is a special case of the *policy's* Bellman Operator, with $p(a|s)=\delta(a-a^*_s)$, where $a^*_s=\argmax_a p(a|s)$, abusing the letter $a$.

### Fixed Point property

Thm: In general, $V_n=(T^\pi)^n W$ has a limit as $n\rightarrow\infty$, $\forall W: S\rightarrow\R$, as measured by the $\infty$-norm. The limit is $V^\pi$, the state value function of the policy $\pi$. Specifically, the Optimal Bellman Operator shares this property.

STS the contraction property:
$$
\|T^\pi W_1-T^\pi W_2\| \le \gamma \|W_1-W_2\|
$$

Then:
$$
\|(T^\pi)^n W-V^\pi\|\le \|(T^\pi)^n W-(T^\pi)^n V^\pi\|\le \gamma^n \|W-V^\pi\|
$$

The contraction property:
$$
\|T^\pi W_1(s)-T^\pi W_2(s)\| = \gamma \|\sum_{s'} p(s'|s,\pi(s)) \left\{ W_1-W_2 \right\}\| \le \gamma \sum_{s'} p(s'|s,\pi(s)) \| W_1-W_2 \| = \gamma \| W_1-W_2 \|
$$

## Value Iteration & Policy Iteration

Value iteration works since the optimal Bellman Operator converges to a fixed point. Must evaluate $r(s,a)$ for all possible $s, a$ and $V(s)$ for all possible $s$.

Policy iteration works since the policy's Bellman Operator converges to a fixed point, the state value function of the policy. Since the policy is not optimal, the greedy policy derived from the state value function is not the original function, i.e. $T^*V^\pi\ne V^\pi$. Since the new policy is greedy, it is better than the original policy, i.e. $T^*V^\pi \ge V^\pi$. The Bellman Operator of the next policy has the property $T^{\pi_{k+1}}V^{\pi_k}=T^*V^{\pi_k}$, so:
$$
V^{\pi_k}\le T^* V^{\pi_k}\le T^{\pi_{k+1}}V^{\pi_k}\le (T^{\pi_{k+1}})^n V^{\pi_k}\le V^{\pi_{k+1}}
$$
This is true once the monotonocity property of the Bellman Operator is proved. This is trivial:
$$
T^\pi W_1 - T^\pi W_2 = \gamma E_{s'\sim (\cdot|s, a)}[W_1(s') - W_2(s')]
$$
which preserves the sign from $W_1-W_2$. So $W_1\le W_2 \Rightarrow T^\pi W_1\le T^\pi W_2$.

## Model-free Monte Carlo Policy Evaluation

Recall: Model-free means evaluate a policy without a model. A policy is defined as $p(a|s)$ for all possible $a, s$. *Evaluation* is the process of computing the state value function $V^\pi(s)$ for all $s$.

An unbiased approximation of $V^\pi(s)$ is
$$
\hat{R}_i(s) = \sum_{t=0}^\infty \gamma^t r_{t,i}
$$
given a trajectory $\{s_i\}$ sampled from an actor acting according to the policy $\pi$ and observed rewards $\{r_{t,i}\}$. By the *Big Number Theorem*, $\frac{1}{n}\sum_{i=1}^n \hat{R}_i(s)$ converges to $V^\pi(s)$ *almost surely*. Thus we have an unbiased approximation given some starting state $s$ and a policy $\pi$ to be evaluated, once there is an actor to act according to the policy.

If some RL training process relies on this method to evaluate the target policy, it is *on-policy*, since the actor must act according to the target policy, thus making the target and control policy identical.

Plug in the Bellman Equation's recursive form of $V^\pi$, we have the *truncated* form:
$$
\hat{R}_i (s_0) = \sum_{t=0}^T \gamma^t r_{t,i} + \gamma^{T+1}V^\pi(s_{T+1})
$$
which still is an unbiased approximation of $V^\pi$.

Monte Carlo computes the empirical mean in a sequential manner.
$$
\hat{V}_n^\pi(s)=\frac{1}{n}\sum_{i=1}^n \hat{R}_i(s)=\frac{n-1}{n}\hat{V}_{n-1}^\pi(s)+\frac{1}{n}\hat{R}_n(s)
$$
More generally, assign a weight $\eta(i)$ to each sample $\hat{R}_i$ at each step,
$$
\hat{V}_n^\pi(s)=(1-\eta(n))\hat{V}_{n-1}^\pi(s)+\eta(n)\hat{R}_n(s)
$$

### TD(0)

Consider only trajectories with one state transition, i.e. $(s_t,a_t,s_{t+1})$, and $r_t=r(s_t,a_t)$. Plugin:
$$
\hat{R}(s)=r_t
$$
and cat use the *truncated* form since we want $\hat{V}^\pi$ to be the unbiased approximation to $V^\pi$.
$$
\hat{V}^\pi(s_t)=(1-\eta)\hat{V}^\pi(s_t) + \eta(r_t+\gamma\hat{V}^\pi(s_{t+1}))=\hat{V}^\pi(s_t) + \eta(r_t + \gamma\hat{V}^\pi(s_{t+1})-\hat{V}^\pi(s_t))
$$

Define the *temporal difference* as
$$
\delta_t=r_t+\gamma\hat{V}^\pi(s_{t+1})-\hat{V}^\pi(s_t)
$$
is an unbiased estimate of
$$
B(\hat{V},s)=T^\pi\hat{V}-\hat{V}
$$
given starting state $s_t$
$$
B^\pi=E_{r_t,s_{t+1}\sim(\cdot|s_t)}[\delta_t]
$$

### TD(1) or Incremental Monte Carlo

Consider multi-step $\hat{R}_n(s_0)=\sum_t\gamma^tr_{t,n}$. Notice that $r_{t,n}+\gamma\hat{V}_n^\pi(s_{t+1,n})-\hat{V}_n^\pi(s_{t,n})=\delta_{t,n}$. Expand $\hat{R}_{n+1}(s_0)-\hat{V}_n^\pi(s_0)$ and
$$
\hat{V}_{n+1}^\pi(s_0)=\hat{V}_n^\pi(s_0) + \eta_{n+1}(\hat{R}_{n+1}(s_0)-\hat{V}_n^\pi(s_0))=\hat{V}_n^\pi(s_0) + \eta_{n+1}\sum_t \gamma^t \delta_{t,n}
$$

TD(1) has a long sum of observed $r_t$, although it is often formulated as the sum of $\delta_{t_n}$. This ensures its *unbiasness* w.r.t. $V^\pi$. But having many terms makes its variance large. TD(0) has only one observation $r_{t,n}$ and under-opt $\hat{V}^pi$, which makes it *biased*. But having less terms makes its variance small.

## Value-based Model-free Policy Learning

### Go straight from TD evaluation

The following statements describe the same purpose:

- evaluate $V^*$
- apply infinitely many Optimal Bellman Operator on some random function $V:S\rightarrow\R$
- apply value iteration starting with some random function $V:S\rightarrow\R$
- apply policy iteration starting with some random policy

Some algo examples:

- Q-Learning: Plugin to TD(0) $\delta_t$ definition for the *Optimal* Bellman Operator.
- SARSA: define policy as $p(a|s)=\text{softmax}_a(Q(s,a))$ and define $\delta_t$ with that Bellman Operator.

### Value Iteration DL fix

Consider Q-Learning. The update step in TD(0) is derived from taking the empirical mean of $\hat{R}_n$. For DL, this must be changed to some gradient method for function approximation. So at each step:
$$
Q_{k+1}=\arg\min_{Q}\| Q - TQ_k \|
$$
and do some gradient descent here.

TD(0) is triggered once a state transition is observed, i.e. $TQ_k = r_t + \gamma\max_{a'} Q_k(s_{t+1}, a')$ once $s\rightarrow s'$ is observed. TD(1) is triggered when a trajectory sampled on a policy is deemed long enough.

### DQN and $\epsilon$-greedy Policy

Tricks in DQN (w/o any justifications in particular...):

- Replay buffer to make transition samples i.i.d.
- Two DNNs to "stablize" the training.
- $\epsilon$-greedy exploration policy.
- Reward normalization to eliminate reward scale differences among games.

Note that this can be and often is done off-policy. The target value of $TQ_k$ is an expectation over all possible actions and next states conditioned on the current state. The actions are sampled from the greedy policy, while the exploring policy is often $\epsilon$-greedy, i.e. the exploring policy takes a random action with probability $\epsilon$, which decreases as the training goes on. This addresses the so-called exploration-exploitation problem.

The joint distribution is $p(s',a|s)=p(a|s)p(s'|a,s)$, where $p(a|s)$ is somewhat given. We care about exploring wide enough so that we gets more information on $p(s'|a,s)$. Since the under-optimal trained policy is biased, we may not get reasonable $p(s'|a,s)$ if we use the purely greedy policy. In general, there is no strict math explaination on the matter, so it's best to take this as a "if you do this, it is better" thing.

In the end, the model converges to the state value function of the $\epsilon$-greedy policy, which is biased w.r.t. the optimal value function. This is acceptable, so long as the greedy policy derived by the biased value function does not deviate too much from the optimal policy. 2 close enough but different value function can derive to the same policy, so long as the $\arg\max$ choices are not effected by the small error for a given state $s$ and different action $a$. This is ok for the case where states are finite, but gets stretchy under the inifinite or uncountable cases.

Note the replay buffer's role in trajectory sampling. As the actor explores according to the $\epsilon$-greedy policy, the data distribution of the replay buffer sampling gradually shifts to the exploring distribution, i.e. the trajector distribution of the $\epsilon$-greedy policy.

### DQN Family

## Policy-based Model-free Policy Learning

### Policy Gradient \& Actor Critic

Policy $\pi$ parameterized by $\theta$, i.e. $\pi_\theta$. Evaluate $V^{\pi_\theta}$ and do some gradient ascend directly, as is described by the policy iteration process.

Denote the defined policy $\pi$ parameterized by $\theta$ as $\pi_\theta(a|s)=p(a|s)$. $d_\mu^{\pi_\theta}$ is the trajectory distribution given the policy. The state value function is the expected return $\sum_t \gamma^t r(s_t,a_t)$ over the trajectory distribution, i.e. the distribution of $(s_0,a_0,s_1,a_1,...)$.
$$
\hat{V}^{\pi_\theta}=E_{(s_t,a_t)_t\sim p(\cdot|\pi_\theta)}[\sum_t \gamma^t r(s_t, a_t)]
$$

Can reformulate the expectation notation for the sake of argument.
$$
E_{(s_t,a_t)_t\sim p(\cdot|\pi_\theta)}=E_{s\sim d_\mu^{\pi_\theta}}E_{a\sim\pi^\theta(\cdot|s)}
$$

The gradient of the state value function w.r.t. $\theta$ is
$$
\nabla_\theta V^{\pi_\theta} = E_{(s_t,a_t)_t\sim p(\cdot|\pi_\theta)}[\nabla_\theta \log\pi_\theta(a|s)\hat{Q}^{\pi_\theta}]
$$

Make it more "empirical":
$$
\nabla_\theta V^{\pi_\theta} = E \left(\sum_t \nabla_\theta\log\pi_\theta(a_t|s_t)\right)\left(\sum_t r_t\right)
$$

Can throw away some reward data since the expectation on $p((s_t,a_t)_t|\pi_\theta)$ is 0.
$$
\nabla_\theta V^{\pi_\theta} = E \left(\sum_t \nabla_\theta\log\pi_\theta(a_t|s_t)\sum_{t'\ge t} r_{t'}\right)
$$

Use a value iteration estimate to make it simpler, $Q^{\pi_\theta}(s_t,a_t)=\sum_{t'\ge t r_{t'}}$. Then we have *Actor Critic* when we do value iteration (or Q-Learning) on $Q^{\pi_\theta}$ along side policy improvement on the policy gradient. It turns out that this scheme requires other conditions to hold.

Suppose $Q_\omega(s,a)$, parameterized by $\omega$, minimizes $E_{s\sim d^{\pi_\theta}}[\sum_a \pi_\theta(a|s)(Q^{\pi_\theta}(s,a)-Q_\omega(s,a))^2]$, and satisfies the *Compatibility* property $\nabla_\omega Q_\omega(s,a)=\nabla_\theta\log\pi_\theta(s,a)$. Then the policy gradient has the old form.
$$
\nabla_\theta V^{\pi_\theta} = E_{s\sim d^{\pi_\theta}} E_{a\sim\pi_\theta}[\nabla_\theta\log\pi_\theta(a|s)Q_\omega(s,a)]
$$

Obviously, a form of $Q$ holding compatibility property is $Q_\omega=\sum_i\alpha_i (\nabla_\theta\log\pi_\theta(s,a))_i + b(s)$, where $\omega=\{\alpha\}$ and $b(s)$ is some function unrelated to $\omega$ depending on only the state, by which property $b$ disappears after taking $\nabla_\omega$.

Pick $b(s)=-V(s)$ to minimize sample variance. Then this $Q$ has the form and property of the *advantage function* $A^\pi(s,a)=Q^\pi(s,a)-V(s)$.

### Conservative Policy Iteration


## Off-policy Exploration

Evaluating a policy often involes an on-policy process, i.e. to follow the currently estimated target process to collect trajectories. This is not often acheivable or better. We always want some more *liberty* when training, to cover as many parts of the distribution as possible. Sometimes only an off-policy scheme is all we have, or an off-policy scheme introduces less variance, etc. We try to find a better exploration policy, other than the greedy one, while ensuring the trained model is unbiased to a certain degree.

### Importance Sampling

Denote the exploring and target policy respectively as $\mu, \pi$. The correction we must introduce into the TD(1) state value function estimate as we sample from $\mu\ne\pi$ is
$$
V^\pi(s_t)=V(s_t) + \sum_{k=0}^{K-1}\gamma^k E_{\{a_t\}\sim \mu(\cdot|\{s_t\})}\left\{ \delta(s_{t+k}, a_{t+k}) \prod_{i=0}^k \frac{\pi(a_{t+i}|s_{t+i})}{\mu(a_{t+i}|s_{t+i})} \right\}
$$
where $\delta(s_i,a_i)$ is the temporal difference in the TD series of policy evaluation schemes. A simple divide and multiply trick in the expectated value computation does the job. This is the naive *Importance Sampling*, and is an unbiased approximation to the on-policy TD(1) policy evaluation scheme.

### Retrace \& V-trace \& LASER

### Curiosity Exploration \& NGU \& Agent57


## Async/Distributed Training

### Distributed Prioritized Replay

### Async Actor-Critic

## Experience Distribution

### Prioritized Replay

### GDI
