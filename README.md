This is a novel attempt to improve debate quality by flipping the honesty of agents midway of the debate.
This is to improve an honest agent's ability to argue by making it capable of anticipating the counter-arguments. This research chooses flipping honesty as the key

### Debate Architecture:

- A question q ∈ Q is shown to agents
- Agent a₁ and a₂ take turns in making their arguments about their statements s₀, s₁,...sₗ ∈ S
- A judge decides the winner (for comparing improvements)
- The honesty of the agents is flipped.
- Agents continue to take turn and present sₗ₊₁, sₗ₊₂,...sₘ
- A judge decides the winner (for comparing improvements)
- Honesty is flipped again (to original state)
- Agents continue to take turn and present sₘ₊₁, sₘ₊₂,...sₙ
- A judge decides the final winner

### Claims:

Claim 1: You can argue better when you know to counter-argue.

Given agent A and B, if A can argue better if it can anticipate the counter argument. This drives up quality of arguments by A. Making it harder and harder for agent B to lie. As quality of lies improves, A's ability to argue improves too.  On repeating this whole cycle for few rounds, we can train the agent A to be unequivocally honest.

Claim 2: You can catch a lie only when you know how to lie

If an agent is trained to be dishonest, when its role is reversed, it can identify the dishonesty of the opposite agent.
An agent that can identify a lie is better prepared to catch one.

Claim 3: Training a judge for cleverer responses from evolved* agents makes it well positioned for everyday.<br>

Improving the quality of arguments ultimately increases the challenge for the judge. This improves judge-model's ability to handle real world scenarios.

\*evolved: an agent that can argue both sides and can anticipate dishonesty.

### Experimental Results
**Sparse classifier on random data**

Density | Accuracy | Average Cross-Entropy | Mode
--- | --- | ---
4px | 45% | 1.465 | Training
4px | 47.17% | 1.4949 | Validation
4px | 46.65% | 1.4785 | Test

**Commands to reproduce**<br>
`python train_judge.py --pixels 4 --batches 50000 --seed 4224 --checkpoint-filename 4px`

### References
- [arxiv](https://arxiv.org/abs/1805.00899)
- [blog post](https://openai.com/index/debate/)
- Starter code from: [safe debate](https://github.com/jvmncs/safe-debates)
