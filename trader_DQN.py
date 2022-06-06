import numpy as np

# import keras
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


def create_model(shape, nb_actions):
    print(shape)
    model = Sequential()
    model.add(LSTM(64, input_shape=shape, return_sequences=True))
    model.add(LSTM(64))
    model.add(Dense(32))
    model.add(Activation('relu'))
    model.add(Dense(nb_actions, activation='linear'))
    return model

def main():
    # OPTIONS
    ENV_NAME = 'OHLCV-v0'
    TIME_STEP = 10

    # Get the environment and extract the number of actions.
    PATH_TRAIN = "./data/train/"
    PATH_TEST = "./data/test/"
    env = OhlcvEnv(TIME_STEP, path=PATH_TRAIN)
    env_test = OhlcvEnv(TIME_STEP, path=PATH_TEST)

    # random seed
    np.random.seed(456)
    env.seed(562)

    nb_actions = env.action_space.n
    model = create_model(shape=env.shape, nb_actions=nb_actions)
    print(model.summary())

    # Finally, we configure and compile our agent. You can use every built-in Keras optimizer and even the metrics!
    memory = SequentialMemory(limit=50000, window_length=TIME_STEP)
    # policy = BoltzmannQPolicy()
    policy = EpsGreedyQPolicy()
    # enable the dueling network
    # you can specify the dueling_type to one of {'avg','max','naive'}-+
    dqn = DQNAgent(model=model, nb_actions=nb_actions, memory=memory, nb_steps_warmup=200,
                   enable_dueling_network=True, dueling_type='avg', target_model_update=1e-2, policy=policy,
                   processor=NormalizerProcessor())
    opt = tf.keras.optimizers.Adam(learning_rate=1e-3)

    dqn.compile(optimizer=opt, metrics=['mae'])

    while True:
        # train
        dqn.fit(env, nb_steps=100000, nb_max_episode_steps=10000, visualize=True, verbose=2)
        try:
            # validate
            info = dqn.test(env_test, nb_episodes=1, visualize=False)
            n_long, n_short, total_reward, portfolio = info['n_trades'][0], info['long']['short'], info[
                'total_reward'], int(info['portfolio'])
            np.array([info]).dump(
                './info/duel_dqn_{0}_weights_{1}LS_{2}_{3}_{4}.info'.format(ENV_NAME, portfolio, n_long, n_short,
                                                                            total_reward))
            dqn.save_weights(
                './model/duel_dqn_{0}_weights_{1}LS_{2}_{3}_{4}.h5f'.format(ENV_NAME, portfolio, n_long, n_short,
                                                                            total_reward),
                overwrite=True)
        except KeyboardInterrupt:
            continue
if __name__ == '__main__':
    main()