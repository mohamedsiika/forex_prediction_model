import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Activation, LSTM
from rl.core import Processor
import tensorflow as tf
from rl.agents.dqn import DQNAgent
from rl.policy import EpsGreedyQPolicy
from rl.memory import SequentialMemory
from sklearn.preprocessing import StandardScaler

tf.compat.v1.experimental.output_all_intermediates(True)
tf.compat.v1.disable_eager_execution()

ADDITIONAL_STATE = 4


class NormalizerProcessor(Processor):
    def __init__(self):
        self.scaler = StandardScaler()
        self.normalizer = None

    def process_state_batch(self, batch):
        batch_len = batch.shape[0]
        k = []
        for i in range(batch_len):
            observe = batch[i][..., :-ADDITIONAL_STATE]
            observe = self.scaler.fit_transform(observe)
            agent_state = batch[i][..., -ADDITIONAL_STATE:]
            temp = np.concatenate((observe, agent_state), axis=1)
            temp = temp.reshape((1,) + temp.shape)
            k.append(temp)
        batch = np.concatenate(tuple(k))
        return batch


class trader():
    def __init__(self):
        TIME_STEP = 64
        # random seed
        np.random.seed(456)

        self.model = self.create_model(shape=(64, 9), nb_actions=3)

        # Finally, we configure and compile our agent. You can use every built-in Keras optimizer and even the metrics!
        self.memory = SequentialMemory(limit=50000, window_length=TIME_STEP)
        self.policy = EpsGreedyQPolicy()
        # enable the dueling network
        # you can specify the dueling_type to one of {'avg','max','naive'}-+
        self.dqn = DQNAgent(model=self.model, nb_actions=3, memory=self.memory, nb_steps_warmup=2000,
                            enable_dueling_network=True, dueling_type='avg', target_model_update=1e-2,
                            policy=self.policy,
                            processor=NormalizerProcessor())
        self.opt = tf.keras.optimizers.Adam(learning_rate=1e-3)

        self.dqn.compile(optimizer=self.opt, metrics=['mae'])

    def create_model(self, shape, nb_actions):
        model = Sequential()
        model.add(LSTM(64, input_shape=shape, return_sequences=True))
        model.add(LSTM(64))
        model.add(Dense(32))
        model.add(Activation('relu'))
        model.add(Dense(nb_actions, activation='linear'))
        return model