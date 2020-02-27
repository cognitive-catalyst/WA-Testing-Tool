#! /usr/bin/python
""" Generate confusion matrix from intent training/testing results
"""
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from argparse import ArgumentParser

# For treemap
import matplotlib
import matplotlib.pyplot as plt
from  matplotlib.colors import LinearSegmentedColormap
import squarify

def func(args):
    in_df = pd.read_csv(args.in_file, delimiter='\t',
                        encoding='utf-8', keep_default_na=False)

    generateTreemap(in_df, args.size_column, args.sort_column, args.label_column, args.title, args.out_file)

def generateTreemap(df, size_column, sort_column, label_column, title, out_file=None):
    plt.figure(figsize=(15,10))

    # Organize the values for a more readable map.
    plotDF = df.sort_values(by=[sort_column], ascending=False)

    # Color should never be the only differentiating factor.
    # If you prefer sorting by 'number of samples' you should use the one-color scale as you otherwise have no visual color-less dimension
    #    to see 'f-score'
    #One-color alternative
    #cmap = matplotlib.cm.Greens
    #Two-color from red-to-green requires sorting by f-score for accessibility. Else you would sort by 'number of samples'
    cmap=LinearSegmentedColormap.from_list('rg',["r", "w", "g"], N=256)

    colors = [cmap(value) for value in plotDF[sort_column]]
    treemap = squarify.plot(sizes=plotDF[size_column],
                            label=plotDF[label_column],
                            color=colors, alpha=.8,
                            text_kwargs={'fontsize':12},
                            bar_kwargs={'linewidth':0.5, 'edgecolor':'#000000'} )
    plt.axis('off')
    plt.title(title)

    patches_array = [
        matplotlib.patches.Patch(edgecolor='black',facecolor=cmap(0.0), linewidth=0.25, label='0%'),
        matplotlib.patches.Patch(edgecolor='black',facecolor=cmap(.25), linewidth=0.25, label='25%'),
        matplotlib.patches.Patch(edgecolor='black',facecolor=cmap(.50), linewidth=0.25, label='50%'),
        matplotlib.patches.Patch(edgecolor='black',facecolor=cmap(.75), linewidth=0.25, label='75%'),
        matplotlib.patches.Patch(edgecolor='black',facecolor=cmap(1.0), linewidth=0.25, label='100%')
    ]

    plt.legend(title=sort_column,
               handles=patches_array,
               bbox_to_anchor=(1.05, 1),
               loc='upper left',
               borderaxespad=0.)

    if out_file:
        plt.savefig(out_file,bbox_inches='tight',dpi=400)
        print ("Wrote tree map image to {}.".format(out_file))
    else:
        plt.show()

def create_parser():
    parser = ArgumentParser(
        description='Generate confusion matrix')
    parser.add_argument('-i', '--in_file', type=str, required=True,
                        help='File that contains intent data')
    parser.add_argument('-o', '--out_file', type=str,
                        help='Output file path', required=True)
    parser.add_argument('-s', '--size_column', type=str, required=True,
                        help='Name of column defining size of rectangles')
    parser.add_argument('-r', '--sort_column', type=str,
                        help='Name of column defining sorting of rectangles')
    parser.add_argument('-l', '--label_column', type=str, required=True,
                        help='Name of column defining label of rectangles')
    parser.add_argument('-t', '--title', type=str,
                        help='Chart title')
    return parser


if __name__ == '__main__':
    ARGS = create_parser().parse_args()
    func(ARGS)
