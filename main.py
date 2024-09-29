import torch
from torch.utils.data import DataLoader
from torchvision.datasets import MNIST
from torchvision.transforms import ToTensor

import argparse
import cProfile
import pstats

from judge import Judge
from agent import Agent
from debate import Debate
from utilities import AverageMeter, track_stats_

import numpy as np

def flip_honesty(helper, liar):
    liar.honest = True
    helper.honest = False
    return (helper, liar)
    
def main(args):
    """main man"""
    # reproducibility
    if args.seed is not None:
        torch.manual_seed(args.seed) # unsure if this works with SparseMNIST right now
        np.random.seed(args.seed)

    # cuda
    args.use_cuda = not args.no_cuda and torch.cuda.is_available()
    args.device = torch.device("cuda" if args.use_cuda else "cpu")

    # data
    dataset = MNIST('./data/', train=False, transform=ToTensor(), download=True)
    kwargs = {'num_workers': 1}
    if args.use_cuda:
        kwargs['pin_memory'] = True
    data_loader = DataLoader(dataset, args.batch_size, shuffle=True, **kwargs)
    if args.rounds is None:
        args.rounds = len(dataset) // args.batch_size

    # load judge
    judge_state = torch.load(args.checkpoint)['state_dict']

    # debate game
    judge = Judge().to(args.device)
    judge.load_state_dict(judge_state)
    judge.eval()
    helper = Agent(honest=True, args=args)
    liar = Agent(honest=False, args=args)
    debate = Debate((helper, liar), data_loader, args)

    # flip the honesty:
    
    if args.flip:
        flipped_debate = Debate((liar, helper), data_loader, args)

    total_meter = AverageMeter()
    class_meters = [AverageMeter() for i in range(10)]
    
    # TODO precommit logic
    for _ in range(args.rounds):
        print("starting round {}".format(_))
        helper.precommit_(None, None)
        liar.precommit_(None, None)
        result = debate.play(judge, args.device)
        track_stats_(total_meter,
                        class_meters,
                        result['helper']['preds'],
                        result['helper']['wins'],
                        result['labels'],
                        args.precommit)
        
        if args.flip:
            print("============= Flipped Debate =============")
            flip_honesty(helper, liar)
            flipped_result = flipped_debate.play(judge, args.device)
            track_stats_(total_meter,
                            class_meters,
                            flipped_result['helper']['preds'],
                            flipped_result['helper']['wins'],
                            flipped_result['labels'],
                            args.precommit)
            
            flip_honesty(helper, liar)
            final_result = debate.play(judge, args.device)
            track_stats_(total_meter,
                            class_meters,
                            final_result['helper']['preds'],
                            final_result['helper']['wins'],
                            final_result['labels'],
                            args.precommit)

    print('Total accuracy: {}'.format(total_meter.avg))
    print('Accuracy per class\n==============================================')
    for i in range(10):
        print('Digit {}: {}'.format(i, class_meters[i].avg))


if __name__=='__main__':
    parser = argparse.ArgumentParser(description='MNIST Debate Game')
    parser.add_argument('--pixels', type=int, required=True, metavar='C',
                        help='number of nonzero pixels to uncover in sparse image (required)')
    parser.add_argument('--flip', type=bool, required=False, default=True,
                        help='Should we flip the honesty of the players midway?')
    parser.add_argument('--checkpoint', type=str, required=True, metavar='CHAR',
                        help='model checkpoint to use as judge (required)')
    parser.add_argument('--rounds', type=int, default=None, metavar='N',
                        help='number of vectorized rounds (default: floor(10000 / batch_size))')
    parser.add_argument('--rollouts', type=int, default=10000, metavar='N',
                        help='number of rollouts to do before move selection (default: 10,000)')
    parser.add_argument('--no-precommit', action='store_true', default=False,
                        help='playout games without precommit')
    parser.add_argument('--honest-first', action='store_true', default=False,
                        help='honest player plays first')
    parser.add_argument('--batch-size', type=int, default=128, metavar='N',
                        help='simlutaneous games to play (default: 1000)')
    parser.add_argument('--no-cuda', action='store_true', default=False,
                        help='disables CUDA training')
    parser.add_argument('--seed', type=int, default=None, metavar='S',
                        help='random seed (default: None)')
    parser.add_argument('--data-folder', type=str, default='./data/', metavar='PATH',
                        help='root path for folder containing MNIST data download \
                        (default: ./data/)')
    args = parser.parse_args()

    args.precommit = not args.no_precommit
    args.liar_first = not args.honest_first
    fname = './profiles/profile.{}px.{}rnds.{}roll.{}bs.{}.txt'.format(
        args.pixels, args.rounds, args.rollouts, args.batch_size,
        'cuda' if not args.no_cuda else 'nocuda')
    pr = cProfile.Profile()
    pr.enable()
    main(args)
    pr.disable()
    with open(fname, 'w') as f:
        stats = pstats.Stats(pr, stream=f).sort_stats('cumulative')
        stats.print_stats()
