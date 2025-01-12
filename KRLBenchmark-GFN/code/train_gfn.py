######################################
#  Code base: train_actor_critic.py  #
######################################


from tqdm import tqdm
from time import time
import torch
from torch.utils.data import DataLoader
import argparse
import numpy as np
import os

from model.agent import *
from model.policy import *
from model.critic import *
from model.buffer import *
#from env import *
from env import *

import utils


if __name__ == '__main__':
    
    # initial args
    init_parser = argparse.ArgumentParser()
    init_parser.add_argument('--env_class', type=str, required=True, help='Environment class.')
    init_parser.add_argument('--policy_class', type=str, required=True, help='Policy class')
    init_parser.add_argument('--critic1_class', type=str, required=True, help='Critic class')
    init_parser.add_argument('--critic2_class', type=str, required=True, help='Critic class')
    init_parser.add_argument('--agent_class', type=str, required=True, help='Learning agent class')
    init_parser.add_argument('--buffer_class', type=str, required=True, help='Buffer class.')
    
    initial_args, _ = init_parser.parse_known_args()
    print(initial_args)
    
    envClass = eval('{0}.{0}'.format(initial_args.env_class))
    policyClass = eval('{0}.{0}'.format(initial_args.policy_class))
    critic1Class = eval('{0}.{0}'.format(initial_args.critic1_class))
    critic2Class = eval('{0}.{0}'.format(initial_args.critic2_class))
    agentClass = eval('{0}.{0}'.format(initial_args.agent_class))
    bufferClass = eval('{0}.{0}'.format(initial_args.buffer_class))
    
    # control args
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=11, help='random seed')
    parser.add_argument('--cuda', type=int, default=-1, help='cuda device number; set to -1 (default) if using cpu')
    
    # customized args
    parser = envClass.parse_model_args(parser)
    parser = policyClass.parse_model_args(parser)
    parser = critic1Class.parse_model_args(parser)
    parser = critic2Class.parse_model_args(parser)
    parser = agentClass.parse_model_args(parser)
    parser = bufferClass.parse_model_args(parser)
    args, _ = parser.parse_known_args()
    
    if args.cuda >= 0 and torch.cuda.is_available():
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.cuda)
        torch.cuda.set_device(args.cuda)
        device = f"cuda:{args.cuda}"
    else:
        device = "cpu"
    args.device = device
    print('device:', device)
    utils.set_random_seed(args.seed)
    
    # Environment
    print("Loading environment")
    env = envClass(args)
    
    # Agent
    print("Setup policy:")
    policy = policyClass(args, env)
    policy.to(device)
    print(policy)
    print("Setup critic:")
    critic1 = critic1Class(args, env, policy)
    critic2 = critic2Class(args, env, policy)
    critic1 = critic1.to(device)
    critic2 = critic2.to(device)
    print(critic1)
    print("Setup buffer:")
    buffer = bufferClass(args, env, policy, [critic1,critic2])
    print(buffer)
    print("Setup agent:")
    agent = agentClass(args, env, policy, [critic1,critic2], buffer)
    print(agent)
    
    try:
        print(args)
        agent.train()
    except KeyboardInterrupt:
        print("Early stop manually")
        exit_here = input("Exit completely without evaluation? (y/n) (default n):")
        if exit_here.lower().startswith('y'):
            print(os.linesep + '-' * 20 + ' END: ' + utils.get_local_time() + ' ' + '-' * 20)
            exit(1)