import numpy as np

# import keras
import keras
from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, CuDNNLSTM,LSTM
from rl.core import Processor
from tensorflow.python.keras.optimizer_v2 import adam
import tensorflow as tf
# keras-rl agent
from rl.agents.dqn import DQNAgent
from rl.policy import BoltzmannQPolicy, EpsGreedyQPolicy
from rl.memory import SequentialMemory
from rl.util import WhiteningNormalizer
from sklearn.preprocessing import MinMaxScaler, StandardScaler
# trader environment
from environment import OhlcvEnv
# custom normalize
print(tf.__version__)
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
            temp = np.concatenate((observe, agent_state),axis=1)
            temp = temp.reshape((1,) + temp.shape)
            k.append(temp)
        batch = np.concatenate(tuple(k))
        return batch

class trader():
    def __init__(self):
        ENV_NAME = 'OHLCV-v0'
        TIME_STEP = 64

        # Get the environment and extract the number of actions.
        #PATH_TRAIN = "./data/train/"
        #PATH_TEST = "./data/test/"
        #self.env = OhlcvEnv(TIME_STEP, path=PATH_TRAIN)
        #self.env_test = OhlcvEnv(TIME_STEP, path=PATH_TEST)

        # random seed
        np.random.seed(456)
        #self.env.seed(562)

        #self.nb_actions = self.env.action_space.n
        self.model = self.create_model(shape=(64,9), nb_actions=3)
        print(self.model.summary())

        # Finally, we configure and compile our agent. You can use every built-in Keras optimizer and even the metrics!
        self.memory = SequentialMemory(limit=50000, window_length=TIME_STEP)
        # policy = BoltzmannQPolicy()
        self.policy = EpsGreedyQPolicy()
        # enable the dueling network
        # you can specify the dueling_type to one of {'avg','max','naive'}-+
        self.dqn = DQNAgent(model=self.model, nb_actions=3, memory=self.memory, nb_steps_warmup=2000,
                            enable_dueling_network=True, dueling_type='avg', target_model_update=1e-2,
                            policy=self.policy,
                            processor=NormalizerProcessor())
        self.opt = tf.keras.optimizers.Adam(learning_rate=1e-3)

        self.dqn.compile(optimizer=self.opt, metrics=['mae'])


    def create_model(self,shape, nb_actions):
        model = Sequential()
        model.add(LSTM(64, input_shape=shape, return_sequences=True))
        model.add(LSTM(64))
        model.add(Dense(32))
        model.add(Activation('relu'))
        model.add(Dense(nb_actions, activation='linear'))
        return model
    
    def main(self):
        # train
        self.dqn.fit(self.env, nb_steps=300000, nb_max_episode_steps=100000, visualize=True, verbose=2)
        self.dqn.save_weights('./model/duel_dqn.h5f', overwrite=True)
        """try:
            # validate
            info = dqn.test(env_test, nb_episodes=1, visualize=False)
            n_long, n_short, total_reward, portfolio = info['n_trades']['long'], info['n_trades']['short'], info[
                'total_reward'], int(info['portfolio'])
            np.array([info]).dump(
                './info/duel_dqn_{0}_weights_{1}LS_{2}_{3}_{4}.info'.format(ENV_NAME, portfolio, n_long, n_short,
                                                                            round(total_reward,3)))
            dqn.save_weights(
                './model/duel_dqn_{0}_weights_{1}LS_{2}_{3}_{4}.h5f'.format(ENV_NAME, portfolio, n_long, n_short,
                                                                            round(total_reward,2)),overwrite=True)
        except KeyboardInterrupt:
            continue"""
if __name__ == '__main__':
    x=trader()
    x.main()