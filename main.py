#!/usr/bin/python

import sys, re, pdb, os
import logging
import argparse

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib, datetime

import utils, data_helper

import analyze


def parse_args():
    """
    Parse command line args.
    
    Example
    -------
    python main.py --input-file-operative ../data/small/some-applications-operative-pub-20161031.csv --input-file-usage ../data/small/some-lupapiste-usage-pub-20161031.csv --output-file-applications ../target/application-summary.csv --output-file-users ../target/user-summary.csv
    """
    parser = argparse.ArgumentParser(description='SOLITADDS analysis')
    parser.add_argument('-io', '--input-file-operative', help='Input CSV file for operative data', required=False,
                        default=os.getcwd() + "/test-data/some-applications-operative-pub-20161031.csv")
    parser.add_argument('-iu', '--input-file-usage', help='Input CSV file for usage data', required=False,
                        default=os.getcwd() + "/test-data/some-lupapiste-usage-pub-20161031.csv")
    parser.add_argument('-oa', '--output-file-applications', help='Output CSV file for applications', required=False,
                        default=os.getcwd() + "summary-applications.csv")
    parser.add_argument('-ou', '--output-file-users', help='Output CSV file for users', required=False,
                        default=os.getcwd() + "summary-users.csv")
    args = vars(parser.parse_args())
    return args


if __name__ == "__main__":
    pd.set_option('display.width', 240)
    args = parse_args()
    input_file_operative = args['input_file_operative']
    input_file_usage = args['input_file_usage']
    output_file_applications = args['output_file_applications']
    output_file_users = args['output_file_users']

    analysis_start_time = datetime.datetime.now()

    odf = data_helper.import_operative_data(input_file_operative)
    udf = data_helper.import_usage_data(input_file_usage)

    print("Total number of apps: {}".format(len(odf)))
    print("Total number of events: {} with time range from {} to {} ".format(len(udf), udf['datetime'].min(),
                                                                             udf['datetime'].max()))

    application_summary = analyze.summarize_applications(odf, udf)
    application_summary.to_csv(output_file_applications, sep=';', encoding='utf-8')

    user_summary = analyze.summarize_users(odf, udf)
    user_summary.to_csv(output_file_users, sep=';', encoding='utf-8')

    print("Analysis took {} seconds".format(datetime.datetime.now() - analysis_start_time))


def h1a():
    print(udf.loc[udf['action'] == 'add-comment'].groupby('applicationId').count())


def a1b():
    odf["month"] = odf["createdDate"].dt.month
    counts = []
    months = []
    for month in range(1, 12):
        size = odf[odf["month"] == month].size
        counts.append(size)
        months.append(month)
    plt.bar(months, counts, 1, color="r")
    plt.show()
