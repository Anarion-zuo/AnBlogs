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
is the expected value of some trajectory starting from state $s$, given policy $\pi$. There exists an optimal $\pi$ s.t. $V^*=\argmax_\pi V^{\pi}$.

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
- Rollout: Start exploring from a given state. We get a trajectory after a rollout, a sequence of states, actions, and reward values.

## Bellman Operators

Given any function $V:S\rightarrow \R$, some policy $\pi$, where $S$ is the state set. Define the *Value Function of the policy* as:
$$
V^\pi(s)=E[\sum_{t=0}^{\infty} \gamma^t r(s_t, a_t)|s_0=s, \pi]
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
T^* V(s) = \max_{a\in A} \left\{ r(s, a) + \gamma\sum_{s'}p(s'|s,a)V(s') \right\} = \max_{a\in A} \left\{ r(s, a) + \gamma E_{s'\sim p(\cdot|s,a)} V(s') \right\}
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
T^\pi W_1 - T^\pi W_2 = \gamma E_{s'\sim (\cdot|s, a)}\left[W_1(s') - W_2(s')\right]
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

The truncated sum has a recursive form. Denote $R_t^\pi V^\pi(s_t)=r_{t,i}+\gamma V^\pi (s_{t+1})$. The truncated sum can be written as $\hat{R}_i(s_0)=R^\pi_0R^\pi_1...R_{T-1}^\pi V^\pi(s_0)$, applying the operator $T$ times.

During the RL training process, when the $V^\pi$ is not yet optimal, i.e. we only have a biased $\hat V^\pi$, this estimate is in turn biased.

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
and cat use the one-step *truncated* form since we want $\hat{V}^\pi$ to be the unbiased approximation to $V^\pi$.
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

### From $V$ to $Q$

The *state value function* and the *action-state value function* are equivalent, and can be used interchangably with some small fix. Suppose $V^\pi$ is the state value function of policy $\pi$, and $Q^\pi$ also is fit for $\pi$, i.e. they are the fixed point of the Bellman operator $T^\pi$.

The state value function is the expected return considering all actions taken at some given state.
$$
V^\pi(s)=E_{a\sim \pi(\cdot|s)} Q^\pi (s,a)
$$

The action state value function is the expected return when taking a specific action at the state, considering all future possible states and actions.
$$
Q^\pi(s,a)=r(s,a)+\gamma E_{s'\sim p(\cdot|s,a)} V^\pi(s')
$$

This definition fits into the fixed point property of the Bellman operator. So we have a Bellman operator for $Q$, and it has a fixed point, equivalent with the Bellman operator for $V$. One step further for the Bellman operator for $Q^\pi$:
$$
Q^\pi(s,a)=r(s,a)+\gamma E_{s'\sim p(\cdot|s,a)}E_{a\sim\pi(\cdot|s)}Q^\pi(s,a)
$$

Plugin the condition for the optimal Bellman operator, i.e. $\pi(a|s)=\delta(a-a^*)$. We have the equations for the optimal policy.
$$
V^*(s) = \max_a Q^*(s,a), Q^*(s,a) = r(s,a) + \gamma E_{s'\sim p(\cdot|s,a)} V^*(s)
$$

One step further for the optimal policy to get the optimal Bellman operator for $Q$.
$$
Q^*(s,a) = r(s,a) + \gamma E_{s'\sim p(\cdot|s,a)} \max_a Q^*(s,a)
$$

### Return \& Multi-step Return

On observing a new transition, the updated Q value should be:

$$
Q_{k+1}=TQ_k=r_{t+1} + \gamma\max_{a'} Q_k(s_{t+1}, a')
$$

This is a biased TD(0) estimate. The $\argmax_a$ process of $Q$ introduces the bias, which we do not have for estimating $V$. To estimate $\max_a Q(s',a)$ for any $s$, we plugin $a^*=\argmax_a Q(s',a)$ to compute an estimate. This choice of $a$ introduces a bias. See more in *Double DQN*.

By steering the model's prediction towards this value, we perform one step in an approximated Value Iteration process.

We can also work with a truncated TD(1) estimate, on observing a trajectory with length larger than 1.

$$
Q_{k+1}=T^nQ_k=r_{t+1}+\gamma r_{t+2}+...+\gamma^{n-1}r_{t+n}+\gamma^n \max_{a'} Q_k(s_{t+n}, a')
$$
where the $Q$ is often computed in the Double DQN fashion. This is a unbiased estimate of $Q$ if the $Q$ in the formular is unbiased. If it is computed in the Double DQN fashion, it is an underestimate. Otherwise it is an overestimate.

We are talking about *estimate*s in the preceding discussion, in the sense that $r_i$'s are estimates of $r(s_i,a_i)$ and $Q_k$'s are estimates of the $Q$'s value in the $k$th term of a *generalized policy iteration* process. The $r_i$'s are observations in experiments, making it an unbiased estimate by definition. The $Q_k$'s are *almost* unbiased at best, due to the approximation ingredient of the process. Following this line of thoughts, the $T$ operator in this case is only for *computation*, since it is w/o an expectation operator and takes estimate values as input. We would hope that the output of this computation described by the formula would yield *almost* unbiased estimate values.

### Double DQN

This is SOP for computing TD estimate in DQN ever since it is published.

We first consider Double Q learning's theory.

Consider $\hat Q(s',a)$ as a series of estimators for each different $a$ to a set of random variables. Denote the estimators as $\hat Q_i=\hat Q(s',a_i)$. Denote the real expected value of $Q$ as $Q_i=E[Q(s',a_i)]$. We want a good estimate of $\max_i Q_i$. An intuitive choice is $\max_i \hat Q_i$, but this is an overestimation. We want an underestimation for this. It is not clear why an underestimation is better in some cases.

Consider 2 sets of independent estimators, predicting the same things. Denote this as $\hat Q_i^A, \hat Q_i^B$. Pick estimators that maximizes $\hat Q^A$, i.e. $a^*=\argmax_i \hat Q^A_i$. These estimators' corresponds to $Q_{a^*}$ for the target values. Consider the estimators in set $B$ predicting the same targets $\hat Q^B_{a^*}$. It is proved that $\hat Q_{a^*}^B\le \max_i Q_i$, which is the ultimate target of this whole thing.

Double DQN trains 2 sets of params for 2 predictors, $\theta,\theta'$. The $a$ in the Bellman target is given by $\theta$, while the $Q$ is computed with params $\theta'$. The 2 sets of params switches role constantly. This implements the idea in Double Q learning, and gets an at-most underestimate result.
$$
TQ_{\theta'}=r_{t+1} + \gamma Q_{\theta'}(s_{t+1}, a^*), a^*=\argmax_a Q_{\theta}(s_{t+1},a)
$$

Why is an underestimate result better is not proved in general.

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

## Monte-Carlo Tree-based Search

In general, tree search estimates $Q$ or $V$ with Monte-Carlo much like other methods. The process maintains the estimate $Q(s,a)$ and number of visitation $N(s,a)$, and updates the estimate each time a new sample $G$ is observed.
$$
Q(s,a) = (1-\frac{1}{N(s,a)})Q(s,a) + \frac{1}{N(s,a)}G
$$

### UCB

UCB is a simple tree based method. We try to go over the essential parts of MC TB search. The algorithm iteratively constructs a tree, and starts explorations from the leaf nodes. Once an rollout/exploration is done, the nodes' $V$ estimates are updated, representing state updates.

We must first choose a leaf node to start the rollout. We start traversing down the tree from the root node. At each nonterminal node, calculate the UCB score of its child, and go to the child with the largest score. The child can also be chosen stochastically according to the score.

The UCB score:
$$
\argmax_a Q(s,a) + 2C_p\sqrt{\frac{2\log N(s)}{N(s,a)}}
$$

In general, the traversing represents part of the exploration policy, in the multi-armed bandit to be specific.

Now that we are at a leaf node, we try to expand it. Pick an action at random and sample a state from the transition kernel $p(s'|s,a)$. Consider the sampled state as a child of the current leaf node. If the node is never sampled before, we must somehow initialize it in memory. UCB requires that the first time a leaf node is encountered in the traversal, do not expand it yet before the next time it is encountered.

Now that we are truly at a leaf node, we start a simulation/rollout starting from the state it represents. At each step of the simulation, pick an action at random and sample the next state from $p(s'|s,a)$. We get an estimation of the value function of the leaf node's state directly. We can update the estimate of the value function with this new value.

We also update the value function estimate of the ancestor nodes of the leaf node. Simply prepend the nodes to the simulation's trajectory and consider more rewards in the prepended trajectory.

## Pretraining

Before the actor really starts exploring, we collected some trajectories and can use them to boost training a little, or can at least make use of them. The pre-existing experience can be from a human expert's demonstration or data collected from previous runs, or from simulation. The idea is to sample from the experiences/demonstrations and perform a pseudo-VI/PI.

### DQN from Demonstration

Before exploring, load the existing trajectories into the replay buffer, then sample with priority. See priority DQN for details. Except for the standard 1-step TD loss, add an $n$-step TD loss, an L2 regularization loss, and a supervised loss. The supervised loss is
$$
J_E(Q) = \max_a \left[ Q(s,a) + l(a_E,a) \right] - Q(s, a_E)
$$
where $\cdot_E$ means the $\cdot$ is the value for the (expert's) demonstration. This loss push the params towards $\max_a \left[ Q(s,a) + l(a_E,a) \right] = Q(s, a_E)$, i.e. $\forall a, Q(s,a_E)-Q(s,a)=l(a_E,a)$. There is always a positive margin between any action and the current action from demonstration in the $Q$ value. Suppose we are sampling exploration trajectories according to this $Q$, the actions from demonstration always have a larger probability. This loss makes the pretraining phase look like a part of normal training, sampling trajectories in the pseudo-$\epsilon$-greedy fashion.

After the pretraining phase, demonstration data is not discarded entirely. They co-exists with trajectories from real exploration in the replay buffer. Demonstration data and exploration data holds different priorities, according to the proportional prioritized sampling, with a different constant added to their priority values.

In general, the loss for a given trajectory is
$$
J(Q) = J_{DQ}(Q) + \lambda_1 J_n(Q) + \lambda_2 J_E(Q) + \lambda_3 J_{L_2}(Q)
$$
where:

- $J_{DQ}$ is the classical DQN loss.
- $J_n$ is the n-step TD loss.
- $J_E$ is the loss from demonstration data, or supervised loss. $\lambda_2$ is 0 for real exploration data.
- $J_{L_2}$ is the regularization loss.

## Off-policy Exploration

Evaluating a policy often involes an on-policy process, i.e. to follow the currently estimated target process to collect trajectories. This is not often acheivable or better. We always want some more *liberty* when training, to cover as many parts of the distribution as possible. Sometimes only an off-policy scheme is all we have, or an off-policy scheme introduces less variance, etc. We try to find a better exploration policy, other than the greedy one, while ensuring the trained model is unbiased to a certain degree.

### Importance Sampling

Denote the exploring and target policy respectively as $\mu, \pi$. The correction we must introduce into the TD(1) state value function estimate as we sample from $\mu\ne\pi$ is
$$
RQ(x,a)=Q(x,a)+E_\mu\left[ \gamma_t \left( \prod_{s=1}^t c_s \right) (r_t + \gamma E_\pi Q(x_{t+1},\cdot) - Q(x_t,a_t)) \right]
$$
where the IS weight is $c_s=\frac{\pi(a_s|x_s)}{\mu(a_s|x|s)}$. The formula can be rewritten into the form of taking the expectation over the target policy $\pi$ by expanding $E_\mu[\cdot]$ to be $\sum_{a_t,x_t,x_{t+1}}p(a_t,x_t,x_{t+1}) [\cdot]$, cancelling out the $c_s$ products. The current form enable us to replace the $E_\mu$ with sampled $x_t,a_t,x_{t+1}$ values plugged into it. The computed result would be an unbiased estimate of the Bellman target $RQ(x,a)$ of the target policy, where sample data are collected under the exploration policy $\mu$.

### V-trace

Vtrace is an improvement over Retrace, which we do not talk about here. The training process is splitted into the learner part and the actor part, which runs entirely independently from each other. An actor collects trajectories according to the local model in a greedy fashion, as computed by the local policy model. Once some trajectories are collected, the actor send them to the learner via a shared queue, and recieves params update from the learner in its own pace, without any waiting to sync with the learner. The learner waits for the actors to send their trajectories by polling on the shared queue and makes no attempt to coordinate the actors.

Vtrace implements an async actor-critic training fashion, which introduces a correction from the difference between the learners' newest param version and the not-yet-updated version held by individual actors. The actors may push trajectories into the shared queue several times, before they pull params from the learners. By the time new trajectories are collected and respective values are computed by the actor, the learners' params would have been updated for several runs unknown to the actor. So the actor computes not only the rewards in the trajectories, but also the policy likelihood, to let the learner compute a correction for this param lag. In general, Vtrace is a *close* on-policy learning scheme with clever correction computations.

Bellman target with correction in the general form:
$$
v_s=V(x_s) + \sum_{t=s}^{s+n-1} \gamma^{t-s} \left(\prod_{i=s}^{t-1} c_i \right)\delta_t, \delta_t=\rho_t (r_t + \gamma V(x_{t+1}) - V(x_t))
$$

The importance sampling weights are composed of $\rho_t,c_i$, with $\rho_t$ being weight at time $t$ and $c_i$ being weights at time from $s$ to $t$.

For a real IS scheme, the weights are $c_i=\frac{\pi(a_i|x_i)}{\mu(a_i|x_i)}$.

For the Vtrace scheme, the weights are truncated IS weights.
$$
\rho_t=\min(\bar\rho,\frac{\pi(a_t|x_t)}{\mu(a_t|x_t)}),c_i=\min(\bar c,\frac{\pi(a_i|x_i)}{\mu(a_i|x_i)})
$$

$\rho_t$ effects the fixed point that the generalized policy iteration converges to, given by the following. $c_i$ exists as an IS correction, with variance reduction technique, as in Retrace, and does not effect the convergence target.
$$
\pi_{\bar\rho}(a|x)=\frac{\min(\bar\rho\mu(a|x),\pi(a|x))}{\sum_b \min(\bar\rho\mu(b|x),\pi(b|x))}
$$

We will talk more about Vtrace in the Async training section.

### Curiosity Exploration \& NGU \& Agent57

## Async/Distributed Training

Rate of experience collection is often the bottleneck of DRL training. Thus, we like to have multiple actors and multiple learner, provided that the training scheme can be seperated as such, as is true for most of the cases. The actor collects experience trajectories from some CPU-bound simulation, while the learner runs the deep learning model training, which is GPU-bound. The learners are often organized in the fashion of classic deep learning distributed training, with multiple GPU worker and a centrialized parameter server. The actors are replicas of the same simulation process.

An actor pulls from the learner the latest version of model params to facilitates the exploration policy. When the actor is done exploring for a while and collects a trajectory ready to be sent to the learner for model training, the learner most likely has many other trajectories at hand. The action taken at this point divides the methods into sync and async schemes. Async schemes have the model update its params as long as a batch of predetermined size of trajectories are ready, while the sync schemes wait for all the actors to send their trajectories for this period. The async schemes introduce a lag in params between the learner and the actor, while runs more efficiently on both sides.

### Ape-X: Basic Distributed Async Prioritized Experience Replay

Each transition trajectory in the replay buffer has a priority attached to it. Some possible ways to define the priority:

- TD error: $\delta_t = r_t + \gamma_t \max_a Q(S_t,a)-Q(S_{t-1},A_{t-1})$, absolute value $|\delta_t|$ or squared $\delta_t^2$.

At training time, priorities are computed or updated when one is encountered. The priorities are never updated as the model updates. Trajectories are sampled from the replay buffer according to the priority. It can be done entirely greedy, i.e. $\arg\max_i P(i)$ or stochastically, the latter being more effective, as it is more flexible. In general, the sampling distribution of the replay buffer is:
$$
P(i) = \frac{p_i^\alpha}{\sum_k p_k^\alpha}
$$
As $\alpha$ goes to infinity, the sampling of replay buffer becomes greedy according to the priority values, and converges to an one-hot vector in the end.

By applying modified sampling from the replay buffer, an importance sampling weight must be also introduced. Denote prioritized sampling distribution as $\mu(i)=P(i)$ as defined above, and the original sampling distribution as $\pi(i)=\frac{1}{N}$, where $N$ is the replay buffer size. The expectation of the sampled TD error is corrected by multiplying an importance sampling weight:

$$
w_i=\frac{1}{N\cdot P(i)}
$$

The priority is computed when:

- The trajectory is encountered and added to the replay buffer.
- The trajectory is sampled from the replay buffer.

To increase the rate of exploration, we have a more general weight $w_i=(\frac{1}{N\cdot P(i)})^\beta$. By setting $\beta$ other than 1, a bias is introduced to the estimated $Q$ function. We design an annealed weight, starting from some $\beta_0 \lt 1$ and reaches 1 after sufficient rounds of training. This effectively increases exploration, while removes the bias in the end.

With a centuralized replay buffer at hand, the param lag introduced by async training does not bother us, as is mediated by the replay buffer.

### R2D2: LSTM Ape-X

### A3C: Async Actor Critic

### IMPALA/V-trace

See V-trace under *Off-policy Exploration*.

Vtrace is designed specifically to improve Retrace, the latter being for "updating the model with trajectories both on and off policy". That is to say, Vtrace or Retrace runs on an on-policy scheme in general, but have the param lag problem with the distributed training method. This in turn makes some trajectories off-policy, since they may be collected by exploring on out-dated model params. The trajectories are on-policy *at first rough glance*, only with a minor correction needed for the Bellman target's computation.

Vtrace can be used with or without a replay buffer, the latter method making the param lag worse in general, but shows better results.

## Experience Distribution


### GDI

## Doesn't Really belong Anywhere

### Go-Explore

Go-Explore argues that the key in learning good policies lies in the proper handling of detachment and derailment in training. Detachment means the agent does not often have trajectories leading to a *good* state, that may yield good information for trajectories that pass through it. Derailment means the agent does not often return to a *good* state. In general, Go-Explore believes that there exists *good* states in the state space, that trajectories may do well to pass through them, either originating from them, or revisiting them for multiple times.

Throughout training, an archive of states are maintained. States are aggregated into *Cell*s and stored in the archive. Each cell stores one state that is most *valuable* among all the states that may be categorized into this cell. In the beginning, the archive holds only the global start state. As the agent(s) start exploring, according to a policy or entirely randomly, new states are added to the archive. For each state, there is a score associated with it. If a state is mapped to a cell, the cell is only updated when the state holds a higher score than the existing state in the cell.

Training is composed of the exploration phase and the robustification phase. The exploration phase collects trajectories, while the robustification phase update the model according to the collected trajectories.

In the exploration phase, the agent selects a cell in the archive with probability proportional to $W=(C_{seen}+1)^{-1/2}$. The more a cell is selected in the past, the less it is selected in the future. The state stored in the cell is restored to the simulation environment, and the agent starts exploring from that state. When a trajectory is collected, the archive would have been updated, and the agent starts all over. This is similar to the tree-based search methods.

In the robustification phase, the learner uses a *backward algorithm* that is a LFD (Learn from Demonstartion) algorithm.

## Useful Sites

[OpenAI Paper Summary](https://spinningup.openai.com/en/latest/spinningup/keypapers.html#bonus-classic-papers-in-rl-theory-or-review)
[Recent Paper Summary](https://github.com/yingchengyang/Reinforcement-Learning-Papers?tab=readme-ov-file#ICLR22)
