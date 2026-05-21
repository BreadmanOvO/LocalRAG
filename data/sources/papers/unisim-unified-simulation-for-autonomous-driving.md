# UniSim Unified Simulation for Autonomous Driving

**Source**: arxiv PDF, 24 pages

**Type**: Academic Paper

---

## Document Content

### Page 1

Capturing Smart Contract Design
with DCR Graphs
Mojtaba Eshghie1[0000−0002−0069−0588], Wolfgang Ahrendt2[0000−0002−5671−2555],
Cyrille Artho1[0000−0002−3656−1614], Thomas Troels
Hildebrandt3[0000−0002−7435−5563], and Gerardo Schneider4[0000−0003−0629−6853]
1 KTH Royal Institute of Technology, Stockholm, Sweden
eshghie@kth.se, artho@kth.se
2 Chalmers University of Technology, Gothenburg, Sweden
ahrendt@chalmers.se
3 University of Copenhagen, Denmark
hilde@di.ku.dk
4 University of Gothenburg, Sweden
gerardo.schneider@gu.se
Abstract. Smart contracts manage blockchain assets and embody busi-
ness processes. However, mainstream smart contract programming lan-
guages such as Solidity lack explicit notions of roles, action dependencies,
and time. Instead, these concepts are implemented in program code. This
makes it very hard to design and analyze smart contracts.
We argue that DCR graphs are a suitable formalization tool for smart
contracts because they explicitly and visually capture the mentioned
features. We utilize this expressiveness to show that many common high-
level design patterns representing the underlying business processes in
smart-contract applications can be naturally modeled this way. Applying
these patterns shows that DCR graphs facilitate the development and
analysis of correct and reliable smart contracts by providing a clear and
easy-to-understand specification.
Keywords: Smart Contract Modelling· DCR Graphs· Design Patterns
1
Introduction
A smart contract is implemented as immutable code executed on a blockchain and
may be seen as a special business process specifying a contractual agreement on
actions to be carried out by different roles. While smart contracts offer advantages
such as uncompromised (automated) execution even without a trusted party,
they can also be complex and difficult to design and understand. This is even
more problematic as they cannot be changed once deployed.
In a normal business process environment, different roles collaborate to achieve
a common business goal. In contrast, different roles in a smart contract typically
have adversarial interests. Therefore, smart contracts introduce new types of
patterns of behavior, which have so far only been informally described [19,30,
50,52]. To provide an unambiguous understanding of the patterns that can also
provide the basis for formal specifications, we set out to extend the study and
formalization of process patterns to include these smart contract patterns.
arXiv:2305.04581v3  [cs.SE]  16 Sep 2023
### Page 2

2
M. Eshghie et al.
Solutions to adversarial-interest problems often use time- or data-related
constraints between actions cutting across the process and the more standard use
of roles and sequential action dependencies. We find that a declarative notation
involving data and time is appropriate for formalizing the new smart contract
process patterns. Moreover, smart contract languages exhibit a transactional
behavior of actions, where an action may be attempted but aborted if the required
constraints for executing it are not fulfilled. This suggests that individual actions
have a life cycle, like sub-processes.
For these reasons, we use DCR graphs [38, 43], which are by now a well-
established declarative business process notation that has been extended with
data [38], time [38], and sub-processes [43]. DCR graphs visually capture impor-
tant properties such as the partial ordering of events, roles of contract users, and
temporal function attributes. Using DCR graphs, it is possible to represent a
smart contract with a clear and concise model that is more expressive and com-
prehensive than other types of models. As the design patterns we model concern
the high-level behavior of a smart contract under analysis, we elide technical
details of the patterns’ implementation and execution. Therefore, we use the
term “high-level” design pattern for the patterns that DCR graphs capture well,
as they represent the underlying business process of the contract. Further, DCR
models are useful for analysis. We show that using DCR graphs facilitates the
development of correct and reliable smart contracts by providing a clear and
easy-to-understand specification. More concretely, our contributions are:
1. We systematically identify and distinguish high-level design patterns from
low-level (implementation-specific) patterns in smart contracts (Table 1), and
demonstrate how we model them with DCR graphs by going through four of
the most complex ones (§3.2, §3.4, §3.8, and §3.9). The DCR models of the
rest of the 19 patterns may be found in the accompanying repository [25].
2. We demonstrate how one can capture the design of a complete contract,
not just a design pattern, with the help of DCR graphs (casino example in
Section 4). The modeled contract has three of the design pattern models
from this paper incorporated, which helps to demonstrate the combinability
of pattern models to shape the final design of the contract.
3. As a result of a thorough analysis of real-world contracts, including pop-
ular contract libraries, we identify (and model) two new design patterns:
time incentivization (§3.2) and escapability (§3.10). Both of these patterns
are extensively used by the Solidity developer community but are not yet
introduced as design patterns in research literature [30,42,50,52].
Our application of these formalized design patterns in Section 4 shows that
using DCR graphs can facilitate the development of correct and reliable smart
contracts by providing a clear and easy-to-understand specification. Moreover,
DCR specifications can provide a basis for automated (dynamic or static) analysis
of smart contracts, which we exemplified by preliminary runtime verification
infrastructure and experiments in our tool paper [27].
Our usage of DCR graphs to model smart contracts and our focus on high-level
rather than low-level properties allows us to capture the key semantics of the
### Page 3

Capturing Smart Contract Design with DCR Graphs
3
contract succinctly. We can verify properties (and likewise lack of vulnerabilities
pertaining to these properties) related to roles and access control [4,5], partial
ordering of actions (function calls and transaction execution) [6], as well as
time-based vulnerabilities [7,9]. Furthermore, not being concerned with low-level
patterns and properties lets our approach remain cross-platform and not tied to
the features and limitations of a certain smart contract execution environment.
We believe that these patterns provide a systematic classification of best practices
for smart contracts in a similar way that software design patterns shaped the
design of traditional software and established a nomenclature for it [31], while
capturing aspects that are unique to smart contracts.
This paper is organized as follows: Section 2 introduces smart contracts and
DCR graphs. Section 3 gives an overview of 19 smart contract design patterns,
which we formalize as DCR graphs. Section 4 shows a case study on a casino
smart contract. Section 5 covers related work, and Section 6 concludes.
2
Background
2.1
Smart Contracts: Ethereum and Solidity
Ethereum [51], with its built-in cryptocurrency Ether, is still the leading
blockchain framework supporting smart contracts. In Ethereum, not only the
users but also the contracts can receive, own, and send Ether. Ethereum miners
look for transaction requests on the network, which contain the contract’s address
to be called, the call data, and the amount of Ether to be sent. Miners are paid for
their efforts in (Ether priced) gas, to be paid by the initiator of the transaction.
A transaction is not always executed successfully. It can be reverted due
to running out of gas, sending of unbacked funds, or failing runtime assertions.
If a miner attempts to execute a transaction, a revert statement within the
transaction’s execution can undo the entire transaction. All the effects so far are
undone (except for the paid gas), as if the original call had never happened.
The most popular programming language for Ethereum smart contracts is
Solidity [17]. Solidity follows largely an object-oriented paradigm, with fields
and methods, called ‘state variables’ and ‘functions’, respectively. Each external
user and each contract instance has a unique address. Each address owns Ether
(possibly 0), can receive Ether, and send Ether to other addresses. For instance,
a.transfer(v) transfers an amount v from the caller to a.
The current caller, and the amount sent with the call, are always available via
msg.sender and msg.value, respectively. Only payable functions accept payments.
Fields marked public are read-public, not write-public. Solidity also offers some
cryptographic primitives, like keccak256 for computing a crypto-hash. require(b)
checks the Boolean expression b, and reverts the transaction if b is false.
Solidity further features programmable modifiers. The contract in Fig. 1
uses the modifiers byOp, inState(s), and noActiveBet, whose implementation
is omitted for brevity. These three modifiers expand to require(b), where b is
msg.sender == operator, state == s, and state != BET_PLACED, respectively.
### Page 4

4
M. Eshghie et al.
1
contract
Casino {
2
address
public
operator , player; bytes32
public
hashedNumber ;
3
enum
State { IDLE , GAME_AVAILABLE , BET_PLACED
};
4
State
private
state;
uint
bet;
Coin
guess;
5
function
addToPot () public
payable
byOp
{...}
6
function
removeFromPot (uint
amt) public byOp , noActiveBet
{...}
7
function
createGame(bytes32
hash) public byOp , inState(IDLE) {
8
hashedNumber = hash
9
state = GAME_AVAILABLE ;}
10
function
bet(Coin
_guess) public
payable
inState( GAME_AVAILABLE ) {
11
require (msg.sender
!=
operator);
12
require (msg.value > 0 && msg.value
<= pot);
13
player = msg.sender; bet = msg.value;
14
guess = _guess; state = BET_PLACED;}
15
function
decideBet(uint
secret) public byOp , inState( BET_PLACED ) {
16
require ( hashedNumber
==
keccak256(secret));
17
Coin
secret = (secret% 2 == 0)? HEADS : TAILS;
18
if (secret == wager.guess) { playerWins ();} else { operatorWins ();}
19
state = IDLE;}
20
}
Fig. 1. Solidity-code for casino (some details are omitted)
Commit
Committer...
Reveal
Revealer
Decide
Decider...
=
Pass
Fail
▼
▼▼
▼
▼
▼
+
▼
[ Decide ]
+
▼
[ not Decide ]
%
▼
[ not Decide ]
%
▼
[ Decide ]
%
▼
%
▼
◇
▼
◇
▼
◇
▼
◇
▼
Fig. 2. Commit and reveal design pattern
2.2
Dynamic Condition Response Graphs
A dynamic condition response (DCR) graph defines a dynamic process declar-
atively as a graph, defined formally in Def. 1 below and exemplified in Fig. 2.
DCR graphs offer an alternative to state machines; instead of using transitions
to represent events, DCR graphs represent events as nodes (boxes). Events in a
DCR graph may be restricted to certain roles. Events can be enabled or disabled
by other events, which is represented by different types of arrows.
The nodes of the graph constitute a set E of events labeled with roles and
an action, visualized in Fig. 2 as boxes with the action label in the middle and
the role label in the top bar. Nodes can be either input actions (denoted by a
flipped paper corner in the top right of the box containing the action label; in
this example, actions commit and reveal), computation actions (denoted by an
=-sign in the top right of the box containing the action label; in this example, the
decide action) or simple actions (in this example, the fail and commit actions).
### Page 5

Capturing Smart Contract Design with DCR Graphs
5
Input actions receive a value from the environment when the action is executed,
which is associated with the event. Computation actions execute a computation
expression (that may refer to the current value assigned to itself or other events)
when the action is executed, which is then associated with the event. In this
example, the computation assigned to the decide action is the Boolean expression
commit = hash(reveal) (not shown graphically in Fig. 2), which refers to the
values of the commit and the reveal actions.
The directed edges between nodes define rules for the execution of events. The
rules can be constraints or effects. An example of a constraint is the condition
rule, visualized in Fig. 2 as an orange arrow →• with a bullet at the target. It
states that the event at the source of the edge (in this example, the commit
action) must have been executed at least once (or be excluded) for the event at
the target (in this example, the reveal action) to be executable.
Examples of effects are the exclude, include and response rules, visualized in
Fig. 2 as respectively a red arrow →% with a %-sign at the target, a green arrow
→+ with a +-sign at the target, and a blue arrow •→with a dot at the source.
The exclude (include) rule states that when the event at the source (in this case,
the decide action) is executed, the events at the target (in this case, the fail and
pass actions) are excluded (included). Excluded events cannot be executed and
are also ignored when determining constraints. The possibility for an event to be
excluded makes it easy to express defeasible rules [44]. For instance, in Fig. 4, the
bank can give a fine a month after a loan, except if the client, in the meantime,
pays the loan, in which case the event of the fine action is excluded.
In DCR graphs with data, rules may be guarded by Boolean expressions,
determining whether a rule is to be considered in the current state of the graph.
In this example, the guard decide of the exclude relation →% from decide to
fail means that fail is excluded if and only if the value of decide is true, which
is the case if the committed value provided when commit is executed is equal
to the hash of the value provided when reveal is executed. The response rule
•→denotes that if the event at the source (e. g., the commit action in Fig. 2) is
executed, then the event at the target (e. g., the reveal action in Fig. 2) must be
executed or excluded in the future.
The execution state of a DCR graph is given by a marking, which assigns
state information to each event. In the original version of DCR graphs [37], the
marking of the graph assigned three Booleans to each event, denoting respectively
if the event had been executed, if it is required to be executed (or excluded)
in the future and if it is currently excluded. In this paper, we use an extended
version of DCR graphs, allowing both data, time and nested sub-processes, which
is supported by the online design tool.5 This version of DCR graphs also adds two
new effect rules: A value relation →=, denoted by a grey arrow with an =-sign
at the target, with the effect of updating the value of the target event when
the source event is executed, and a cancel relation •→×, denoted by a brown
arrow with a ×-sign at the target, with the effect of removing a possible pending
5 Available for free for academic use at dcrsolutions.net
### Page 6

6
M. Eshghie et al.
execution requirement (e. g., due to a previous activation of a response rule) of
the target event when the source event is executed.
For a DCR graph with data, the marking assigns the current data value (if
any) associated with each event, as exemplified above. For a DCR graph with
time, the marking additionally assigns time information to events, concretely,
how long ago an event was executed (if it has been executed) and a deadline for
when it is required to be executed (if it is required to be executed in the future).
In Def. 1, we give the formal definition of timed DCR graphs with sub-
processes and data. We combine timed DCR graphs with sub-processes [43] and
timed DCR graphs with data [38] and add a new type of edge denoting a value
effect, making it possible for one event to update the data of another event.
We assume a set of computation expressions ExpE, with BExpE ⊆ExpE being
a subset of Boolean expressions. For every event e ∈E, we assume an expression
e ∈ExpE that denotes the current value of the event (as recorded in the marking).
We also assume a discrete-time model (i. e., time is represented as time steps
given as natural numbers) and let ω denote the natural numbers (including 0)
and ∞= ω ∪{ω}, i. e, the natural numbers and ω (infinity).6 Infinity is used
to represent a non-fixed deadline of a required event, i. e., that an event must
eventually be executed as known from classical liveness properties. This is the
default deadline of a response relation if the deadline is not given, as it is the
case for the two response relations in Fig. 2.
Definition 1. A timed DCR graph with sub-processes, data, and roles G is
given by a tuple (E, sp, D, M, →•, •→, •→×, →⋄, →+, →%, →=, L, l) where
1. E is a finite set of events,
2. sp ∈E ⇁E is an acyclic sub-process function, i. e., for all k > 1 spk(e) ̸=
sp(e), if sp(e) is defined.
3. D : E →ExpE ⊎{?} defines an event as either a computation event with
expression d ∈ExpE or an input event ?,
4. M = (Ex, Re, In, Va) ∈
 (E ⇁ω) × (E ⇁∞) × P(E) × (E ⇁V )

is the
timed marking with data,
5. →• ⊆E × ω × BExpE × E, is the guarded timed condition relation,
6. •→⊆E × ∞× BExpE × E, is the guarded timed response relation,
7. •→×, →⋄, →+, →%, →= ⊆E × BExpE × E are the guarded cancel, milestone,
include, exclude and value relations, respectively,
8. L = P(R) × A is the set of labels, with R and A sets of roles and actions,
9. l: E →L is a labelling function between events and labels.
The sub-process function sp(e) defines a partial containment relation of
events, which allows an event to be refined by a sub-process defined by the events
contained in it. We call such a refined event a sub-process event. A sub-process
event gets executed when an event contained in it is executed, and no events
of the sub-process in the resulting marking are required to be executed in the
future.
6 The ISO 8601 standard (www.iso.org/iso-8601-date-and-time-format.html) is
used in the design tool, allowing the use of years, months, days, and seconds.
### Page 7

Capturing Smart Contract Design with DCR Graphs
7
As already informally described above, the marking M = (Ex, Re, In, Va)
defines the state of the process. Formally, the marking consists of three partial
functions (Ex, Re, and Va) and a set In of events. Ex(e), if defined, yields the time
since event e was last Executed. Re(e), if defined, yields the deadline for when
the event is Required to happen (if it is included). The set In is the currently
Included events. Finally, Va(e), if defined, is the current value of an event.
Enabledness. The condition →• and milestone →⋄relations constrain the enabling
of events and determine when events can be executed. As exemplified above, a
condition e′→•e means that e′ must have been executed at least once or currently
be excluded for e to be enabled. A milestone e′→⋄e means that e′ must either be
currently excluded or not be pending for e to be enabled. In the example in Fig. 2,
the milestone relations ensure that the commit action cannot be repeated as long
as required executions of reveal, decide, fail, or pass are pending. Formally, an
event e is enabled in marking M = (Ex, Re, In, Va) and can be executed by role
r ∈R, if l(e) = (R′, a) for r ∈R′ and (1) e is included: e ∈In, (2) all conditions
for the event are met: ∀e′ ∈E.(e′, k, d, e) ∈→•.(e′ ∈In ∧[[d]]M) =⇒Ex(e′) ≥k
and (3) all milestones for the event are met: ∀e′ ∈E.(e′, k, d, e) ∈→⋄.(e′ ∈
In ∧[[d]]M) =⇒Re(e′) is undefined and (4) e is not contained in a sub-process
event, or sp(e) is enabled and can be executed by role r.
In the DCR graph in Fig. 2, the only enabled event is the event commit. It is
enabled because it is included and the source events of the two milestone rules are
not initially required to be executed. The reveal and decide events are blocked
by condition rules, and the fail and pass events are disabled because they are
initially excluded (marked by a dashed border).
We refer the reader to [38,43] for a more detailed definition and explanation
of the execution semantics of timed DCR graphs with data and sub-processes.
3
Smart Contract Design Patterns as DCR Graphs
Due to the high stakes involved in applications, ensuring the safety and security
of smart contracts is crucial. To address this, both the Solidity documentation
and the developer and smart contract security community have put forth a range
of recommendations. A considerable number of these recommendations are now
known as design patterns [31], because they are widely adopted as a solution
to recurring design problems. These patterns promote the creation of contracts
that are designed with safety and security in mind, mitigating potential risks
and safeguarding users’ assets in the design phase.
We collected these design patterns from academic design pattern surveys
[19,30,40,50,52], documentation of Solidity [17] and the Ethereum Foundation [15],
and recommendations by a popular contract auditing company [22]. These design
patterns are also confirmed by their occurrence in popular libraries and contracts
such as OpenZeppelin, SolidState Solidity, and Aragon OSx [10,14,16,45,48].
First, we identify the design patterns representing high-level behavior rather
than implementation- and platform-specific patterns (Table 1). The latter con-
cerns features inside a function (the execution of which we model as an event
### Page 8

8
M. Eshghie et al.
Safe self-
destruction
Automatic 
deprecation
Time
constraint
Time
incentivization
Access
control
Oracle
Tokens
Pull over
push
Governance
Upgradablility
Action dependencies
and contract staging
Time-based
constraints
Roles and access
control
Structural 
Legend
Rate
limitation
Speed
bump
Commit
and reveal
Circuit
breaker
Escapability
Secure
Ether
transfer
Checks,
effects,
interactions
Guard
check
Abstract
contract
states
Fig. 3. Classification of smart contract high-level design patterns (upper part of Table 1)
in DCR graphs). The analysis of low-level patterns is orthogonal to our work
and can be handled, e. g., by runtime analysis of code [32]. We then classify the
high-level patterns into the following four categories (see Fig. 3):
1. Time-based constraints: Time-based patterns impose constraints on when
activities can be performed, which typically include deadlines and delays.
2. Roles and access control: Role-based access control [46] restricts access
to given functions to predefined roles.
3. Action dependencies and contract staging: High-level design of a smart
contract may impose an ordering on any pair of activities.
4. Structural patterns: These patterns impose a certain structure on the
contract business process (and the implementation as a result) and are created
by combining other design patterns.
Many patterns combine aspects of several categories; Fig. 3 depicts a classification
of 19 design patterns we have identified. We elucidate these patterns further
below. Also, we describe DCR graphs for selected design patterns here; the others
are available on GitHub.7 Table 1 gives an overview of references of the design
patterns, libraries that implement them, and their respective DCR models.
In the following subsections, we delve into each design pattern, highlighting its
utility, and, for a chosen subset, offer the visual representation of their model and
a succinct description of the associated DCR graph models. This study provides
supplementary details and examples for each pattern, along with the DCR model
semantics used, in our corresponding GitHub repository. We plan to focus on
comprehensive guidelines for smart contract modeling in future research.
3.1. Time constraint. In multi-stage business processes, code execution must
adhere to specific stages. This can be achieved through time-based or action-
based dependencies. The former denotes stages solely based on elapsed time [19].
7 https://github.com/mojtaba-eshghie/SmartContractDesignPatternsInDCRGraphs
### Page 9

Capturing Smart Contract Design with DCR Graphs
9
Table 1. Smart contract design patterns and their respective DCR graph models.
High-level patterns (upper part of the table) are further categorized in Fig. 3.
Design Pattern
Libraries
DCR Model
High-level Patterns
Time constraint [19]
[45]
GitHub, §3.1
Time incentivization1
[3,8,11,12,14] GitHub, §3.2, §4
Automatic deprecation [52]
—
GitHub, §3.3
Rate limitation [50]
[22]
GitHub, §3.4
Speed bump [50]
[22]
GitHub, §3.5
Safe self-destruction [19,52]
[45]
GitHub, §3.6
Ownership / Authorization / Access Control [19,30,52]
[10,45,48]
GitHub, §3.7, §4
Commit and reveal [52]
—
GitHub, §3.8, §4
Circuit breaker / Emergency stop [50]
—
GitHub, §3.9
Escapability1
[1,2,33,36]
GitHub, §3.10
Checks, effects, interactions [30,50]
—
GitHub, §3.11
Guard check [30]
[29]
GitHub, §3.12
Abstract contract states [52]
[45]
GitHub, §3.13, §4
Secure Ether transfer [30]
—
GitHub, §3.14
Oracle [19,52]
—
GitHub, §3.15
Token [19]
[45]
GitHub, §3.16
Pull over push [52]
[45]
GitHub, §3.17
Upgradability [42,52]
[45]
GitHub, §3.18
Governance [19,40]
[13,21,45]
GitHub, §3.19
Low-level Patterns
Randomness [19,30]
—
✗
Safe math operations [19]
[45]
✗
Variable Packing [30,42]
[45]
✗
Avoiding on-chain data storage [42]
[45]
✗
Mutex [50]
[45]
✗
Freeing storage [42]
—
✗
1 We identify these as design patterns since they have been used as a recurring solution in
several real-world smart contracts but have not yet been considered a design pattern in
the literature.
This pattern prohibits calling a function until a specific time is reached on the
blockchain, represented by a delayed condition relation in DCR graphs. The
simplest form of this pattern is modeled directly using a delayed condition DCR
relation. Modeling more complex time constraints where only part of a function
should be executed or blocked based on time is challenging and may require
multiple guard conditions in DCR graphs. One approach is to interpret Solidity’s
require statements as guard conditions in DCR graphs, connecting multiple
activities to shape the business logic.
3.2. Time Incentivization. In Ethereum, smart contracts work as a reactive
system where specific function calls execute transactions. There are scenarios
where certain actions should be performed at a specific time or when a specific
condition is fulfilled. A lack of action may prevent progress, opening up adver-
sarial behavior (e. g., the eternal locking of assets). The purpose of the time
incentivization pattern is to motivate parties to cooperate even in the existence
of conflicting interests. The incentivization is typically done by stipulating a
deadline before which an actor shall make a move. The actor that misses the
deadline can afterward be punished by other actors, e. g., by forfeiting the bets,
as modeled in the casino contract (see §4).
### Page 10

10
M. Eshghie et al.
     
pay loan   
     
client   
     
fine   
     
bank   
     
give loan   
     
bank   
   
◆   
   
▼   
     
P1M   
     
+   
   
▼   
     
+   
     
%   
    
%   
     
▼   
     
▼   
     
▼   
Fig. 4. DCR model of time incentivization design pattern.
To demonstrate this pattern, we use the simple example of giving a loan and
then motivating the client to pay for the loan. Giving a loan is performed only
by bank role. In Fig. 4, immediately after giving the loan, the bank includes →+
both the pay loan and fine activities. Without any more relationships, this would
mean that the bank might increase the interest on the loan without giving the
client enough time to pay for it. This issue is resolved by using the pre-condition
arrow →• from give loan to activity fine. As this pre-condition arrow has a
deadline attribute of P1M (one month), it will suspend the availability of fine to
one month later. Without this pattern, the client could refuse to pay the loan by
not participating in any further transaction.
Despite the widespread usage of this pattern in popular smart contracts such
as Augur, MakerDAO, Compound, Aragon Court, and Synthetix [3,8,11,12,14]
to incentivize taking the next step by the actor(s), the current work is the first
one classifying it as a design pattern and formalizing it using DCR graphs.
3.3. Automatic Deprecation. Automatic deprecation is the opposite of
a time constraint, stipulating a deprecation time (block number) after which
a function is not executable anymore [52]. In Solidity code, such functions are
typically enabled by a require statement checking at the function entry point
against the expiration. This means that a smart contract function can be called
and reverted, which is different from DCR model semantics, where an activity is
enabled only if it will successfully execute. We model this in DCR by checking
the deprecation condition on an exclusion arrow from another activity to the
target activity subject to deprecation.
3.4. Rate Limitation. Rate limitation imposes a limit on the number of
successful function calls by a participating user during a specific time period [22].
The more common type of this pattern that we analyze here explicitly limits the
total amount of transfers allowed during the defined period.
To model this pattern, we assume the sensitive activity is the withdraw
operation. We present the model in Fig. 5. When the model is simulated, the
only included available activity to execute is set limit. The new period activity
is initially executed (tick the on activity box). The gray arrow valuerel from
new period to rate limiter copies value 0 to rate limiter every time new period is
executed. Each execution of new period sets a deadline and delay of one day (P1D)
for the given activity. Having such relationships (response and precondition) on
### Page 11

Capturing Smart Contract Design with DCR Graphs
11
rate limiter
s
=
new period
!✓
system
Set limit
user
withdraw
user
▼
P1D
▼
▼
P1D
◇
▼
[ currentamount >= limit ]
=
▼
( 0 )
Fig. 5. Rate limitation pattern modeled in DCR graphs
new period and assigning an automatic agent to the system (when simulating the
model) ensures that new period is indeed executed at exactly one-day intervals.
In Fig. 5, labels P1D on the reflexive pre-condition →• and reflexive response
•→arrows of new period impose this periodic execution. Based on the purple
milestone relation →⋄, if the current period amount does not exceed the limit,
role user can withdraw. Furthermore, having the milestone relation from new
period to rate limiter occur periodically with currentamount ≥limit ensures
that if the current withdrawal of the period exceeds the limit, withdraw will not
be executable until the next execution of new period. The new execution of new
period resets the currentamount to 0 again.
3.5. Timed Temporal Constraint (Speed Bump). A speed bump is used
to slow down critical operations such as the withdrawal of assets, authorization
of significant actions, etc. [22]. It imposes a temporal barrier that gives enough
time to a monitoring system to detect a problematic activity and mitigate it.
This pattern is a specialized form of the time constraint pattern where the
participating user can only execute an action after a predefined time period has
passed (from the point the action request has been registered). The wait time
is modeled using a delay on a condition arrow from the activity requesting the
specified action to the actual action.
3.6. Safe Self-Destruction. It is possible to define a function in Solidity
that uses selfdestruct(address target) to destroy the contract intentionally
and send all Ether in the contract account to the target. Safe self-destruction
is about limiting the execution of the function to specific roles such as the
administrator. [19,52]. The simplest way to achieve this is to refine the access
control pattern (§3.7). However, guard check and time constraint patterns (§3.12
and §3.1) can also be used to ensure safety.
3.7. Access Control. Access control restricts access to desired functions to
only a subset of accounts calling them [19,30,52]. A common instance of this
pattern is to initialize a variable owner to the contract deployer and only allow
this account to successfully call certain functions. Here, we can nicely exploit that
access control is built into DCR graphs as a first-class citizen, in the form of roles
assigned to activities. Each activity in a DCR model can be limited to one or
more specific roles. In simpler scenarios, roles are assigned statically to accounts
when a contract is deployed on the blockchain. In general, however, access rights
can be assigned dynamically. DCR graphs support this using activity effects from
### Page 12

12
M. Eshghie et al.
sell
client
transfer
client
circuit-breaker
s
panic
monitor
buy
client
contingency
admin
revive
admin
▼
+
▼
%
▼
%
▼
%
▼
%
▼
◇
▼
◇
▼
◇
▼
◇
▼
Fig. 6. Circuit breaker design pattern DCR model
an external database source. This feature allows changing the roles of activities
as a result of an activity being executed.
3.8. Commit and Reveal. In a public permissionless blockchain platform
such as Ethereum, transaction data is public [52]. Therefore, if a secret is sent
along with a transaction request, participants in the blockchain consensus protocol
can see the secret value even before the transaction is finalized. On the other hand,
the party holding the secret should commit to it before other parties act, so the
secret cannot be changed after the fact. The commit and reveal pattern addresses
this problem and works in two phases. In Phase 1, a piece of data is submitted
that depends on the secret (which itself is not yet submitted). Often, that data
is the crypto-hash of the secret, such that the secret cannot be reconstructed.
Phase 2 is the submission (and reveal) of the secret itself. We use a combination
of condition, milestone, and response relations to enforce the ordering of actions
in the commit and reveal pattern in Fig. 2. Here, the activity reveal is blocked
initially by the condition relation from commit to reveal, and is enabled once
a user commits. The commit makes reveal pending (by the response relation
arrow). Finally, the milestone relation from the pending reveal to commit means
that unless a reveal happens, no other commit is possible. The decision is then
made using the decide activity based on committed and revealed values.
3.9. Circuit Breaker (Emergency Stop). This pattern enables the contract
owner to temporarily halt the contract’s normal operations until a manual or
automatic investigation is performed [50]. Other contract functions, such as those
based on timed temporal constraints (§3.5), can also trigger the circuit breaker.
To model this design pattern, we categorize activities into two subsets: activities
that are available in the normal execution of the contract and those that are only
available when the circuit breaker is triggered. There is a milestone relationship
→⋄between circuit breaker grouping and all other DCR nodes. The existence of
this milestone helps to disable the execution of all of these activities by making
the circuit breaker pending. In Fig. 6, the activity panic executed by the monitor
role makes the circuit breaker pending (panic •→circuit breaker). This means
unless revive activity in the circuit breaker group is executed, none of the buy,
sell, transfer, and panic activities are executable. Executing contingency instead
will enable a contingency plan (related to §3.10).
### Page 13

Capturing Smart Contract Design with DCR Graphs
13
3.10. Escapability. There have been cases where a vulnerability in the
contract triggered by a certain transaction led to funds being locked in the
contract [36]. To prevent this, a smart contract can have a function whose logic
is independent of the main contract logic; when triggered, it can withdraw all
assets in the contract to a certain address. This new address can be the upgraded
version of the contract that contains a patch for the vulnerability. Escapability
is arguably the complementary pattern for the circuit breaker pattern (§3.9),
as it concerns the functionality behind the contingency activity in Fig. 6 for
the circuit breaker. This functionality often consists of transferring assets to an
escape hatch. Despite being used by the community [1,2,36], the current work is
the first one promoting it as a design pattern.
3.11. Checks, Effects, Interactions. This pattern is concerned with the
order of certain activities, especially when interactions with other contracts
(external calls) happen [30,50]. External calls can be risky, as call targets cannot
necessarily be trusted. One risk is that the called contract calls back into the calling
contract before returning, purposefully abusing the calling contract’s logic [28].
To prevent such exploits, the caller first performs checks on its bookkeeping
variables (variables keeping the balance of tokens, assets, etc.). Then, it modifies
these bookkeeping variables based on the business logic (effects). Last, there are
interactions with (i. e., calls to) other contracts. In DCR graphs, we specify this
strict ordering via inclusion/exclusion relations among the respective activities.
3.12. Guard Check. A guard check validates user inputs and checks book-
keeping variables and invariants before the execution of the function body (mainly
as a require statement) [29]. This pattern is often applied using function modifiers
in Solidity and represented using guard conditions on DCR relations.
3.13. Abstract Contract States. In most processes, action dependencies
impose a partial order on action executions that a smart contract has to follow, as
shown in the casino contract (§4). In Solidity, a state variable of type enumeration
can mimic a finite state automaton [52], whose state transitions enforce the set
of executable functions, encoding a partial order among action executions.
In DCR graphs, such dependencies (partial orderings of actions) can be
represented explicitly. If the ordering between activities does not matter, no
arrows are required. Therefore, DCR graphs can make contract states obsolete at
the modeling level. If there is a strong reason for modeling the abstract contract
states instead of the action dependencies they imply, it is still possible to model
them using DCR graphs. This is done by grouping activities of the same state
into the same group in DCR graphs and using arrows between state groupings to
reflect state transitions of the system.
3.14. Secure Ether Transfer. This structural design pattern imposes a
design choice between various ways of sending Ether from one contract to the
other (via send, transfer, or call) [30]. Using each of them requires a distinct
way of ensuring the target contract cannot harm the contract sending Ether.
As a structural design pattern, Secure Ether Transfer imposes certain guard
checks, mutual exclusions, and ordering of actions to ensure that an external call
(especially to transfer Ether) is not exploitable by a malicious party. Therefore,
### Page 14

14
M. Eshghie et al.
this pattern can be represented in DCR graphs as action dependency relation in
combination with the guard check (§3.12) and mutex (Table 1) design patterns.
3.15. Oracle. Oracles enable smart contracts to incorporate off-chain data in
their execution and push information from a blockchain to external systems [19,52].
The oracle pattern employs an external call to another service smart contract
(data source) to register the request for off-chain data. This registration call
information should also be kept in bookkeeping variables inside the contract
itself. When the data is ready in the service contract, it will inform the main
contract about the result by calling a specific callback function. To model this,
the callback function of the smart contract is excluded by default and is included
when the smart contract calls an oracle.
3.16. Token Design Patterns. Tokens represent assets, their behavior, and
manageability [19]. Ethereum smart contracts and token standards (such as
ERC-20, ERC-721, and ERC-777) enable developers to use tokens according to
specific requirements. DCR graphs can model both tokens and their interacting
contracts. The ERC-20 token standard model included in the accompanying
repository to this work involves inclusion/exclusion relations to model the partial
ordering of activities. Tokens and contracts that use this model typically involve
several other design patterns (most notably §3.17 and §3.14).
3.17. Pull Over Push. A contract might need to send a token or Ether to
other accounts. The “pull over push” pattern discourages pushing tokens or Ether
to the destination as a side-effect of calling a function. Rather, it encourages
exposing a withdraw function that users of the contract can call [52] for this
reason. This inclination towards pull is based on the fact that when sending Ether
or tokens via any external call (even when adhering to patterns such as §3.14), the
receiver may act unexpectedly before returning control. We model this pattern
in a DCR graph by having an extra activity for the withdraw functionality.
3.18. Upgradability. This design pattern consists of up to five parts: (1) The
proxy keeps addresses of referred contracts. (2) The data segregation part sep-
arates the logic and data layers by storing data in a separate smart contract.
(3) The satellite part outsources functional units to separate satellite contracts
and stores their addresses in a base contract, allowing the replacement of their
functionality. (4) The register contract tracks different versions of a contract
and points to the latest one. (5) While keeping the old contract address, the
relay pattern uses a proxy contract to forward calls and data to the newest con-
tract version [52]. Data segregation, satellite, and relay are platform-dependent
low-level patterns, which we do not capture with our DCR graph model. Our
upgradability pattern model (Table 1) instead explicitly includes activities for
the register and proxy parts.
3.19. Governance. On-chain governance is a crucial component of decen-
tralized protocols, allowing for decision-making on parameter changes, upgrades,
and management [19,40]. The governance pattern is typically used to allow token
holders or a group of privileged users to vote on proposals and make decisions
that affect the contract’s behavior. This pattern works in conjunction with other
patterns, such as guard check (§3.12) and role-based access control (§3.7).
### Page 15

Capturing Smart Contract Design with DCR Graphs
15
4
Modeling and Analysis of A Casino Smart Contract
As an example of how patterns modeled in DCR graphs come into play when
modeling a concrete smart contract scenario, we present a simple casino con-
tract [26].8 It uses four design patterns identified in Table 1: time incentivization,
role-based access control, commit and reveal, and abstract contract states. This
endeavor demonstrates how utilizing and combining the DCR model of several
design patterns into one model captures the intended smart contract design.
The casino has two explicitly declared roles, operator and player. It also
contains three abstract states (see §3.13): IDLE, GAME AVAILABLE, and
BET PLACED. Three modifiers check the pre-conditions →• of each function
based on the roles and the state the contract is in.
Fig. 7 shows the DCR model of this contract. The activities all reflect functions
of the same name, except subprocess casino, which everything is grouped under.
This subprocess reflects the behavior of the deployed contract, which includes a
suicidal closeCasino function that selfdestructs, shown by an exclusion arrow from
closeCasino to the subprocess in Fig. 7. Without a subprocess, an exclusion arrow
would go from closeCasino to all other activities, which is visually unappealing.
Furthermore, we do not model the actual states of the contract, instead choosing
to order the activities by inclusion →+ and exclusion →% arrows.
When the casino contract is deployed, it is in the IDLE abstract state. It
is possible to create a game, add to the pot, remove from it, or self-destruct.
Creating a game will change the abstract state to GAME AVAILABLE, which
enables anyone in the Ethereum network to place a bet and take the role of the
player (as a result). The function decideBet checks if the player is the winner
by comparing the guess with the secret number. This gives both the player
and the operator a 50 % chance of winning the game. In the model, a response
arrow •→from placeBet to decideBet emphasizes that decideBet has to execute
at some point and should not block the game from continuing. However, since
continuing the game at this point depends on the operator making a transaction,
it is possible for a malicious operator or buggy reverted decideBet function to
lock the funds the player puts in the game. Furthermore, after a player places the
bet, the operator should not be able to change the actual secret stored. Therefore,
three patterns are used in the model to provide the following functionality:
– A time incentivization pattern (§3.2) ensures that continuing the game is the
favorable option for the casino operator. Fig. 7 shows the required mechanism,
where timeoutBet becomes available with a desirable delay (here P1D, one
day) to provide the player with an option when the operator is unable or
unwilling to make a transaction to decideBet. Calling this function after the
timeout guarantees the player wins the game and motivates the operator to
decide the game in time.
– A commit and reveal pattern (§3.8) is used to ensure when operator cre-
ateGame is called, the operator commits to a secret without sending it. The
8 The scenario was originally provided by Gordon Pace.
### Page 16

16
M. Eshghie et al.
Casino
s
decideBet
Operator
addToPot
Operator
closeCasino
Operator
removeFromPot
Operator
createGame
✓
Operator
timeoutBet
✓
Player
✓
s
placeBet
✓
Player
◆
▼
P1D
▼
+
▼
+
▼
+
▼
+
▼
+
▼
+
▼
+
▼
+
▼
%
▼
%
▼
%
▼
%
▼
%
▼
%
▼
[ guess != hashedNumber ]
%
▼
%
▼
+
▼
%
▼
placeBetWrapper
Fig. 7. Casino contract model.
revealing phase of this pattern is performed in decideBet, where the secret is
submitted, checked, and compared to the player’s guess.
– A role-based access control pattern (§3.7) to confine player and operator roles
to their respective activities.
The abstract contract states pattern (§3.13) used in the implementation (Fig. 1)
is not needed in the model (Fig. 7): The model’s partial ordering provides the
same semantics without the complications of abstract contract states.
As mentioned in §1, DCR specifications provide a basis for automated analysis,
to verify that the implementation of the contracts adheres to their models.
We have implemented a runtime monitoring tool “Clawk” [27]. Clawk captures
transactions from the Ethereum client and executes an instance of the DCR
graph model in tandem. For each Ethereum transaction, Clawk checks if the
DCR graph model permits a corresponding action in the model. If this is not the
case, the tool reports a violation.
By leveraging runtime information, our framework enables automated runtime
verification. While runtime verification in the blockchain domain is typically
associated with the performance overhead of contract or platform instrumentation
[32, 34, 41], we address this concern by placing the monitor off-chain. If any
deviations from the specification are detected, Clawk generates alerts, which can
be used to enhance the contract’s implementation or enable a circuit breaker
pattern in the contract implementation (cf. §3.9).
5
Related Work
Smart contracts often involve multiple dependent transactions, a challenge that
has been addressed through various approaches. Sergey and Hobor discuss the
non-deterministic nature of transaction ordering decided by miners [47], while
### Page 17

Capturing Smart Contract Design with DCR Graphs
17
other works focus on commutativity conditions to exploit interleavings [18] or
identify serializable transactions in Ethereum [23]. These issues have also been
modeled using finite state automata, which can lead to “bad states” in certain
scenarios (e. g., when most of the actions are not accessible) [24]. DCR graphs
offer a more elegant solution in such cases. Transactions and their dependencies
can be graphically represented, as demonstrated by Chen et al., who use this
to identify potential security issues [20]. Our work uniquely combines these
general properties [49] with specific features like access control [39] to provide a
comprehensive framework for smart contracts.
Chen et al. use graphs to analyze transactional dependencies and security in
smart contracts, but their approach is statistical and less precise than ours [20].
While general properties of smart contracts focus on transactional integrity (not
creating or destroying funds in the contract) [49], specific features can be modeled
through access control [39] or finite-state machines [35]. To our knowledge, our
work is the first to systematically apply a combination of these two aspects to
smart contracts in terms of general and reusable patterns.
6
Conclusion and Future Work
Smart contracts are critical yet complex pieces of software that encode business
processes in an executable form on a blockchain. We collected 19 smart contract
design patterns that dissect complex smart contracts into smaller reusable com-
ponents, making it easier to reason about them. DCR graphs are an ideal way to
formally model the semantics of these patterns, supporting the concepts of time,
data, and sub-processes. We demonstrate their usefulness on the casino smart
contract that combines multiple patterns.
The contract DCR models serve as a repository of reusable templates for de-
veloping more secure and efficient smart contracts across various applications and
smart contract execution platforms. This not only aids in the initial design phase
but also has uses in monitoring the contract behavior, allowing for automated
verification [27], which reduces the risk of vulnerabilities. Future directions of our
research include an extensive evaluation of the Clawk tool, combinations of static
or dynamic analysis of low-level patterns [32] with runtime monitoring against
our high-level design patterns, as well as automated discovery of the models from
the contract transaction history.
### Page 18

18
M. Eshghie et al.
Appendix
A
Casino Contract Source
1
pragma
solidity
^0.4.11;
2
3
contract
Casino {
4
address
public
operator;
5
uint256
public
timeout;
6
uint256
constant
DEFAULT_TIMEOUT = 30
minutes;
7
uint256
public
pot;
8
bytes32
public
hashedNumber ;
9
address
public
player;
10
11
enum
Coin {
12
HEADS ,
13
TAILS
14
}
15
struct
Wager {
16
uint256
bet;
17
Coin
guess;
18
uint256
timestamp;
19
}
20
Wager
private
wager;
21
enum
State {
22
IDLE ,
23
GAME_AVAILABLE ,
24
BET_PLACED
25
}
26
State
private
state;
27
28
//
Modifiers
29
modifier
inState(State
_state) {
30
require(_state == state);
31
_;
32
}
33
modifier
byOperator () {
34
require(msg.sender ==
operator);
35
_;
36
}
37
modifier
noActiveBet () {
38
require(state == State.IDLE
state == State. GAME_AVAILABLE );
39
_;
40
}
41
//
-----------------------------------------
42
// Create a new
casino
43
constructor () public {
44
operator = msg.sender;
45
state = State.IDLE;
46
timeout = DEFAULT_TIMEOUT ;
47
pot = 0;
48
wager.bet = 0;
49
}
### Page 19

Capturing Smart Contract Design with DCR Graphs
19
50
//
Changing
the
timeout
value
51
function
updateTimeout (uint256
_timeout) public
byOperator
noActiveBet {
52
timeout = _timeout;
53
}
54
// Add
money to pot
55
function
addToPot () public
payable
byOperator {
56
// The
operator
can
choose a positive
value to pay and
raise
the pot by
57
require(msg.value > 0);
58
59
pot = pot + msg.value;
60
}
61
// Remove
money
from
pot
62
function
removeFromPot (uint256
amount) public
byOperator
noActiveBet {
63
require(amount > 0 && amount
<= pot);
64
pot = pot - amount;
65
msg.sender.transfer(amount);
66
}
67
//
Operator
opens a bet
68
function
createGame(bytes32
_hashedNumber )
69
public
70
byOperator
71
inState(State.IDLE)
72
{
73
hashedNumber = _hashedNumber ;
74
state = State. GAME_AVAILABLE ;
75
}
76
// Player
places a bet
77
function
placeBet(Coin
_guess)
78
public
79
payable
80
inState(State. GAME_AVAILABLE )
81
{
82
require(msg.sender !=
operator);
83
require(msg.value > 0 && msg.value
<= pot);
84
state = State.BET_PLACED;
85
player = msg.sender;
86
wager = Wager ({ bet: msg.value , guess: _guess , timestamp: now
});
87
}
88
//
Operator
resolves a bet
89
function
decideBet(uint256
secretNumber )
90
public
91
byOperator
92
inState(State.BET_PLACED)
93
{
94
require( hashedNumber
==
keccak256( secretNumber ));
95
Coin
secret = ( secretNumber % 2 == 0) ? Coin.HEADS : Coin.
TAILS;
96
if (secret == wager.guess) {
97
playerWins ();
98
} else {
### Page 20

20
M. Eshghie et al.
99
operatorWins ();
100
}
101
state = State.IDLE;
102
}
103
// Player
resolves a bet
because
of
operator
not
acting on time
104
function
timeoutBet () public
inState(State.BET_PLACED ) {
105
require(msg.sender == player);
106
require(now - wager.timestamp
> timeout);
107
playerWins ();
108
state = State.IDLE;
109
}
110
// Player
wins
and
gets
back
twice
his
original
wager
111
function
playerWins ()
private {
112
pot = pot - wager.bet;
113
player.transfer(wager.bet * 2);
114
wager.bet = 0;
115
}
116
//
Operator
wins , transferring
the
wager to the pot
117
function
operatorWins ()
private {
118
pot = pot + wager.bet;
119
wager.bet = 0;
120
}
121
//
Operator
closes
casino
122
function
closeCasino () public
inState(State.IDLE) byOperator {
123
selfdestruct (operator);
124
}
125
function () {}
126
}
Appendix Fig. A-1. The complete source code for Casino contract
B
Casino Contract Description
The Casino contract simulates a simple coin-tossing game where an operator and
a player interact. The contract starts in an IDLE state, allowing the operator to
create a game, add or remove funds from the pot, or even close the casino. Once a
game is created, it transitions to the GAME AVAILABLE state, enabling players
to place bets. After a bet is placed, the contract moves to the BET PLACED
state, where the operator must decide the outcome of the bet. The contract then
returns to the IDLE state, ready for the next game.
B.1
Design Patterns
Time Incentivization The contract employs a time incentivization pattern to
ensure that the operator acts within a reasonable time frame. This is implemented
through the timeout variable and the timeoutBet() function. If the operator fails
to decide the bet within the specified timeout, the player can call timeoutBet()
to automatically win the game. This mechanism encourages the operator to act
promptly, mitigating the risk of funds being locked in the contract.
### Page 21

Capturing Smart Contract Design with DCR Graphs
21
Role-Based Access Control The contract uses a role-based access control
pattern to restrict access to certain functions based on the caller’s role. This
is implemented using the byOperator and inState modifiers. The byOperator
modifier ensures that only the operator can call certain functions like createGame,
addToPot, and removeFromPot. The inState modifier checks that the contract
is in the appropriate state for the function to be called, effectively acting as a
role-based control for the contract’s states.
Commit and Reveal The commit and reveal pattern is used to maintain the
secrecy of the operator’s choice until the bet is decided. The operator initially
submits a hashed number using createGame, which commits them to a secret
number without revealing it. Later, in decideBet, the operator reveals the secret
number, which is then hashed and checked against the initially submitted hash.
This ensures fairness and prevents the operator from changing their choice midway
through the game.
Abstract Contract States The contract uses an enumerated type, State, to
represent its abstract states: IDLE, GAME AVAILABLE, and BET PLACED.
These states are managed by the private variable state and checked by the inState
modifier before executing certain functions. This pattern simplifies the contract’s
logic and makes it easier to understand the allowed transitions between states.
B.2
Functions and Modifiers
Modifiers
– inState(State state): Checks if the contract is in the specified state.
– byOperator(): Checks if the message sender is the operator.
– noActiveBet(): Checks if there is no active bet.
Core Functions
– constructor(): Initializes the contract, setting the operator and default values.
– updateTimeout(uint256 timeout): Allows the operator to update the timeout
value.
– addToPot(): Allows the operator to add funds to the pot.
– removeFromPot(uint256 amount): Allows the operator to remove funds from
the pot.
– createGame(bytes32 hashedNumber): Allows the operator to start a new
game.
– placeBet(Coin guess): Allows a player to place a bet.
– decideBet(uint256 secretNumber): Allows the operator to decide the outcome
of a bet.
– timeoutBet(): Allows the player to win by default if the operator fails to act
within the timeout.
### Page 22

22
M. Eshghie et al.
– playerWins(): Private function to handle the logic when the player wins.
– operatorWins(): Private function to handle the logic when the operator wins.
– closeCasino(): Allows the operator to close the casino and retrieve the re-
maining funds.
References
1. A Decentralized Escape Hatch for DAOs, https://hackingdistributed.com/
2016/07/11/decentralized-escape-hatches-for-smart-contracts/, accessed:
2023-08-29
2. Implement
escape
hatch
mechanism
contracts
·
Issue
#1
·
OpenZeppelin/openzeppelin-contracts,
https://github.com/OpenZeppelin/
openzeppelin-contracts/issues/1, accessed: 2023-08-29
3. The Maker Protocol White Paper — Feb 2020, https://makerdao.com/en, accessed:
2023-08-29
4. SWC-105 - Smart Contract Weakness Classification (SWC), https://swcregistry.
io/docs/SWC-105/, accessed: 2023-09-01
5. SWC-106 - Smart Contract Weakness Classification (SWC), https://swcregistry.
io/docs/SWC-106/, accessed: 2023-09-01
6. SWC-114 - Smart Contract Weakness Classification (SWC), https://swcregistry.
io/docs/SWC-114/, accessed: 2023-09-01
7. SWC-116 - Smart Contract Weakness Classification (SWC), https://swcregistry.
io/docs/SWC-116/#time_locksol, accessed: 2023-09-01
8. Synthetixio/synthetix: Synthetix Solidity smart contracts, https://github.com/
Synthetixio/synthetix, accessed: 2023-08-29
9. Timestamp
Dependence
-
Ethereum
Smart
Contract
Best
Prac-
tices,
https://consensys.github.io/smart-contract-best-practices/
development-recommendations/solidity-specific/timestamp-dependence/
#avoid-using-blocknumber-as-a-timestamp, accessed: 2023-09-01
10. Aragon OSx Protocol (Jun 2023), https://github.com/aragon/osx, accessed:
2023-08-29
11. Aragon/aragon-court (Jul 2023), Aragon, accessed: 2023-08-29
12. Augur (Aug 2023), https://github.com/AugurProject/augur, accessed: 2023-08-
29
13. Chainbridge-solidity
(Aug
2023),
https://github.com/ChainSafe/
chainbridge-solidity, accessed: 2023-08-29
14. Compound Protocol (Jun 2023), Compound, accessed: 2023-08-29
15. Ethereum development documentation (Aug 2023), https://ethereum.org/en/
developers/docs/, accessed: 2023-08-29
16. Smartcontractkit/chainlink (Jun 2023), https://github.com/smartcontractkit/
chainlink, accessed: 2023-08-29
17. Solidity
documentation
(Aug
2023),
https://docs.soliditylang.org/en/
latest/, accessed: 2023-08-29
18. Bansal, K., Koskinen, E., Tripp, O.: Automatic Generation of Precise and Use-
ful Commutativity Conditions. In: Beyer, D., Huisman, M. (eds.) Tools and Al-
gorithms for the Construction and Analysis of Systems. pp. 115–132. Lecture
Notes in Computer Science, Springer International Publishing, Cham (2018).
https://doi.org/10.1007/978-3-319-89960-2 7
### Page 23

Capturing Smart Contract Design with DCR Graphs
23
19. Bartoletti, M., Pompianu, L.: An Empirical Analysis of Smart Contracts: Platforms,
Applications, and Design Patterns. In: Financial Cryptography and Data Security.
pp. 494–509. LNCS, Springer, Cham (2017)
20. Chen, T., Li, Z., Zhu, Y., Chen, J., Luo, X., Lui, J.C.S., Lin, X., Zhang, X.:
Understanding Ethereum via graph analysis. ACM TOIT 20(2), 1–32 (2020)
21. Compound: Compound v2 Governance, https://docs.compound.finance/v2/
governance/, accessed: 2023-08-29
22. Consensys:
Ethereum
Smart
Contract
Best
Practices
(Aug
2023),
https://consensys.github.io/smart-contract-best-practices/
development-recommendations/precautions/, accessed: 2023-08-29
23. Dickerson, T., Gazzillo, P., Herlihy, M., Koskinen, E.: Adding Concurrency to Smart
Contracts. In: PODC. pp. 303–312. ACM (2017)
24. Ellul, J., Pace, G.J.: Runtime Verification of Ethereum Smart Contracts. In:
2018 14th European Dependable Computing Conference (EDCC). IEEE (2018).
https://doi.org/10.1109/EDCC.2018.00036
25. Eshghie, M.: A comprehensive collection of dcr graph model of business process-
level (contract-level) design patterns in smart contracts (Aug 2023), https://
github.com/mojtaba-eshghie/SmartContractDesignPatternsInDCRGraphs,
ac-
cessed: 2023-08-29
26. Eshghie,
M.:
mojtaba-eshghie/CLawK
(Aug
2023),
https://github.com/
mojtaba-eshghie/CLawK/blob/925bf9c9afe344c763963e0e40098c66420d1d6a/
server/monitor/contracts/source/Casino.sol, accessed: 2023-08-29
27. Eshghie, M., Ahrendt, W., Artho, C., Hildebrandt, T.T., Schneider, G.:
CLawK:
Monitoring
Business
Processes
in
Smart
Contracts
(Aug
2023).
https://doi.org/10.48550/arXiv.2305.08254, accessed: 2023-08-29
28. Eshghie, M., Artho, C., Gurov, D.: Dynamic Vulnerability Detection on Smart
Contracts Using Machine Learning. In: EASE 2021. pp. 305–312. ACM (2021)
29. etherscan.io:
HOLDIT
|
Etherscan,
http://etherscan.io/address/
0x24021d38DB53A938446eCB0a31B1267764d9d63D, accessed: 2023-08-29
30. Fravoll:
Solidity
Patterns
(Aug
2023),
https://fravoll.github.io/
solidity-patterns/, accessed: 2023-08-29
31. Gamma, E., Helm, R., Johnson, R., Johnson, R.E., Vlissides, J.: Design patterns:
elements of reusable object-oriented software. Pearson Deutschland GmbH (1995)
32. Gao, J., Liu, H., Liu, C., Li, Q., Guan, Z., Chen, Z.: EASYFLOW: Keep Ethereum
Away from Overflow. In: 2019 IEEE/ACM 41st International Conference on Software
Engineering: Companion Proceedings (ICSE-Companion). pp. 23–26 (May 2019).
https://doi.org/10.1109/ICSE-Companion.2019.00029, iSSN: 2574-1934
33. giveth.io:
common-contract-deps
(May
2021),
https://github.com/Giveth/
common-contract-deps/blob/094d36028eab30444314395016817735e57e9d77/
contracts/Escapable.sol, accessed: 2023-08-29
34. Grossman, S., Abraham, I., Golan-Gueta, G., Michalevsky, Y., Rinetzky, N., Sagiv,
M., Zohar, Y.: Online Detection of Effectively Callback Free Objects with Applica-
tions to Smart Contracts (Jan 2018). https://doi.org/10.48550/arXiv.1801.04032,
http://arxiv.org/abs/1801.04032, arXiv:1801.04032 [cs]
35. Guth, F., W¨ustholz, V., Christakis, M., M¨uller, P.: Specification mining for smart
contracts with automatic abstraction tuning. arXiv:1807.07822 (2018)
36. Explained: The Akutars NFT Incident (April 2022) - Halborn Blockchain Security
Firm: Ethical Hackers, Infosec & Pen Tests}, https://halborn.com/blog/post/
explained-the-akutars-nft-incident-april-2022, accessed: 2023-08-29
### Page 24

24
M. Eshghie et al.
37. Hildebrandt, T.T., Mukkamala, R.R.: Declarative event-based workflow as dis-
tributed dynamic condition response graphs. In: Honda, K., Mycroft, A. (eds.) Pro-
ceedings Third Workshop on Programming Language Approaches to Concurrency
and communication-cEntric Software, PLACES 2010, Paphos, Cyprus, 21st March
2010. EPTCS, vol. 69, pp. 59–73 (2010). https://doi.org/10.4204/EPTCS.69.5,
https://doi.org/10.4204/EPTCS.69.5
38. Hildebrandt, T.T., Normann, H., Marquard, M., Debois, S., Slaats, T.: Decision
modelling in timed dynamic condition response graphs with data. In: Business
Process Management Workshops. pp. 362–374. Springer, Cham (2022)
39. Liu, Y., Li, Y., Lin, S.W., Artho, C.: Finding permission bugs in smart contracts
with role mining. In: SIGSOFT ISSTA 2022. p. 716–727. ACM (2022)
40. Liu, Y., Lu, Q., Zhu, L., Paik, H.Y., Staples, M.: A systematic literature review on
blockchain governance. Journal of Systems and Software 197 (2023)
41. Ma, F., Fu, Y., Ren, M., Wang, M., Jiang, Y., Zhang, K., Li, H., Shi,
X.: EVM: From Offline Detection to Online Reinforcement for Ethereum
Virtual Machine. In: 2019 IEEE 26th International Conference on Software
Analysis, Evolution and Reengineering (SANER). pp. 554–558 (Feb 2019).
https://doi.org/10.1109/SANER.2019.8668038, iSSN: 1534-5351
42. Marchesi, L., Marchesi, M., Destefanis, G., Barabino, G., Tigano, D.: Design
Patterns for Gas Optimization in Ethereum. In: IEEE IWBOSE. pp. 9–15 (2020)
43. Normann, H., Debois, S., Slaats, T., Hildebrandt, T.T.: Zoom and enhance: Action
refinement via subprocesses in timed declarative processes. In: BPM 2021. pp.
161–178. Springer, Cham (2021)
44. Nute, D.: Handbook of logic in artificial intelligence and logic programming, vol. 3,
chap. Defeasible Logic. Clarendon Press, Oxford University Press (1994)
45. OpenZeppelin: OpenZeppelin Contracts, https://github.com/OpenZeppelin/
openzeppelin-contracts, accessed: 2023-08-29
46. Sandhu, R.S.: Role-based access control. In: Advances in Computers, vol. 46, pp.
237–286. Elsevier (1998)
47. Sergey, I., Hobor, A.: A Concurrent Perspective on Smart Contracts (2017), http:
//arxiv.org/abs/1702.05511
48. Solidstate:
SolidState
Solidity
(Feb
2023),
https://
github.com/solidstate-network/solidstate-solidity/blob/
de7c9545ac015f42a03aa3a678000ec1ec4c14a4/contracts/access/access_
control/AccessControl.sol, accessed: 2023-08-29
49. Wang, H., Liu, Y., Li, Y., Lin, S., Artho, C., Ma, L., Liu, Y.: Oracle-supported
dynamic exploit generation for smart contracts. IEEE Transactions on Dependable
and Secure Computing 19(03), 1795–1809 (2022)
50. Wohrer, M., Zdun, U.: Smart contracts: security patterns in the Ethereum ecosystem
and Solidity. In: IEEE IWBOSE. pp. 2–8 (2018)
51. Wood, G.: Ethereum: A secure decentralised generalised transaction ledger.
Ethereum Project Yellow Paper 151, 1–32 (2014)
52. W¨ohrer, M., Zdun, U.: Design Patterns for Smart Contracts in the Ethereum
Ecosystem. In: iThings/GreenCom/CPSCom/SmartData. pp. 1513–1520 (2018)