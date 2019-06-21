import random
import numpy as np
from policies.cnn_policies import StackedFrameCNNPolicy
from utils.buffers import SimpleReplayBuffer
import warnings
warnings.filterwarnings("ignore")

MAX_EPSILON = 1.0
REPLAY_BUFFER_CAPACITY = 100000
STEPS_BEFORE_EPSILON_DECAY = 500000
BATCH_SIZE = 32
TERMINAL_STATE = None
DISCOUNT_FACTOR = 0.99


class Agent:
    steps = 0
    epsilon = MAX_EPSILON

    def __init__(self, num_actions, observation_space_shape, replace_target=10, *args, **kwargs):
        self.evaluation_network = StackedFrameCNNPolicy(name='Evaluation Network', num_frames_to_stack=4, observation_space_shape=observation_space_shape, num_actions=num_actions)
        #self.target_network = SimpleCNNPolicy(name='Target Network', observation_space_shape=observation_space_shape, num_actions=num_actions)
        self.num_actions = num_actions
        self.observation_space_shape = observation_space_shape
        self.memory = SimpleReplayBuffer(REPLAY_BUFFER_CAPACITY)
        self.replace_target = replace_target

    def act(self, current_state):
        """
        Decide action to take based on current state and exploration strategy. Initailly we explore (i.e. choose uniformly random action) 100% of the times
        But epsilon decays as we gain experience and we start taking policy determined actions, i.e. the action with highest Q value at current state, as determined by evaluation network
        """
        if random.random() < self.epsilon:
            # Exploration: Return index of chosen action within action space. Actual action is self.action_space[<returned_value>]
            return random.randint(0, self.num_actions-1)

        # Exploitation: Return index of action with highest Q value at current state, as determined by evaluation network
        return np.argmax(self.evaluation_network.predict(current_state))

    def observe(self, sample):
        self.steps += 1
        self.memory.add(sample)
        if self.steps >= STEPS_BEFORE_EPSILON_DECAY:
            self.epsilon *= 0.99999

    def learn(self):
        batch = self.memory.sample(BATCH_SIZE)
        
        current_states = [ e[0] for e in batch ]
        next_states = [ e[3] for e in batch ]
        
        predicted_q_values = self.evaluation_network.predict(current_states)
        q_values_at_next_state = self.evaluation_network.predict(next_states)

        target_q_values = predicted_q_values

        for i in range(BATCH_SIZE):
            current_state, current_action, reward, next_state, is_done = batch[i]

            if is_done:
                target_q_values[i][current_action] = reward 
            else:
                target_q_values[i][current_action] = reward  + DISCOUNT_FACTOR * np.max(q_values_at_next_state[i])

        self.evaluation_network.optimise(current_states, target_q_values)

        if self.steps % self.replace_target == 0:
            self.update_graph()

    def update_graph(self):
        pass
        #print("Updating...")
        #self.target_network.q = self.evaluation_network.q.clone('clone')
        