import gym
import os
from agents.dqn.dqn import RAMAgent
from utils.preprocessing import downscale
import numpy as np

# Create environment
ENV_NAME = 'LunarLander-v2'
env = gym.make(ENV_NAME)

NUM_STATES = env.observation_space.shape

NUM_ACTION_VALUES = env.action_space.n  # env.action_space.n

base_path = os.path.dirname(os.path.abspath(__file__))

agent = RAMAgent(num_actions=NUM_ACTION_VALUES, observation_space_shape=NUM_STATES, pretrained_policy=base_path+'/pretrained/LunarLander.model', explore=False)


# Create a function that runs ONE episode and returns cumulative reward at the end
def run(render=False):
    # Reset the environment to get the initial state. current_state is a single RGB [210 x 160 x 3] image
    current_state = env.reset()
    current_state = np.array(current_state, dtype=np.float32)
    # Set cumulative episode reward to 0
    cumulative_reward = 0

    while True:
        vr.capture_frame()
        # Based of agent's exploration/exploitation policy, either choose a random action or do a
        # forward pass through agent's policy to obtain action
        current_action = agent.act(current_state)
        action_to_take = current_action

        # Take a step in environment
        next_state, reward, is_done, info = env.step(action_to_take)
        next_state = np.array(next_state, dtype=np.float32)

        current_state = next_state

        # Add reward to cumulative episode reward
        cumulative_reward += reward

        # OPTIONAL (slows down training): render method displays the current state of the environment
        #env.render()


        # Save policy after every episode and return cumulative earned reward.
        # Note that the saving part is the only CNTK specific code in this entire file
        # Ensuring such modularities are key to building complex libraries
        if is_done:
            return cumulative_reward


print("Training Starts..")

# Training code
from pyvirtualdisplay import Display
virtual_display = Display(visible=0, size=(1400, 900))
virtual_display.start()

vr = gym.wrappers.monitoring.video_recorder.VideoRecorder(env, base_path+'/pretrained/demo.mp4')
episode_reward = run(render=False)
vr.close()
