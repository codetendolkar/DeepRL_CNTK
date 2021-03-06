import gym
from agents.a2c.a2c import A2CAgent
from utils.preprocessing import downscale
import numpy as np
from agents.a2c.hyperparams import CKPT_PATH

# Create environment
ENV_NAME = 'Pong-v0'
env = gym.make(ENV_NAME, frameskip=2)

NUM_STATES = (84, 84)  # env.observation_space.shape

NUM_ACTION_VALUES = 3  # env.action_space.n

MAX_NUM_EPISODES = 100000

agent = A2CAgent(num_actions=NUM_ACTION_VALUES, observation_space_shape=(84, 84),
                 actor_pretrained_policy=None, critic_pretrained_policy=None)

# Create a function that runs ONE episode and returns cumulative reward at the end
def run(render=False):
    # Reset the environment to get the initial state. current_state is a single RGB [210 x 160 x 3] image
    current_state = env.reset()
    current_state = downscale(current_state)
    current_state = agent.frame_preprocessor.add_frame(current_state)

    # Set cumulative episode reward to 0
    cumulative_reward = 0

    while True:

        # Based of agent's exploration/exploitation policy, either choose a random action or do a
        # forward pass through agent's policy to obtain action
        current_action = agent.act(current_state)
        action_to_take = current_action + 1

        # Take a step in environment
        next_state, reward, is_done, info = env.step(action_to_take)
        next_state = downscale(next_state)
        next_state = agent.frame_preprocessor.add_frame(next_state)

        agent.observe((current_state, current_action, reward, next_state, is_done))

        current_state = next_state

        # Add reward to cumulative episode reward
        cumulative_reward += reward

        # OPTIONAL (slows down training): render method displays the current state of the environment
        if render:
            env.render()

        # Save policy after every episode and return cumulative earned reward.
        # Note that the saving part is the only CNTK specific code in this entire file
        # Ensuring such modularities are key to building complex libraries
        if is_done:
            agent.learn()

            if ep % 200 == 0:
                agent.actor_policy.probabilities.save(CKPT_PATH+ENV_NAME+".actor.ep_{}.model".format(ep))
                agent.critic_policy.value.save(CKPT_PATH+ENV_NAME+".critic.ep_{}.model".format(ep))

            agent.frame_preprocessor.reset()
            agent.memory.reset()
            return cumulative_reward


print("Training Starts..")

# Training code
ep = 0
episode_rewards = []
while ep < MAX_NUM_EPISODES:
    episode_reward = run(render=False)
    episode_rewards.append(episode_reward)
    with open(CKPT_PATH+"episode_rewards.txt", "w") as f:
        f.write(str(episode_rewards))
    avg_reward = np.mean(episode_rewards[-100:]) if len(episode_rewards)>=100 else np.mean(episode_rewards)
    print(("Episode {}: Reward: {}, Average Reward in past " + str(min(100, len(episode_rewards))) +
           " episodes {}, Steps: {}").format(ep, episode_reward, avg_reward, agent.steps))
    ep += 1

    if avg_reward > 20:
        break
