#!/usr/bin/python
# coding=utf-8

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
    """
    Hakija ja viranomainen voivat keskustella lupahakemuksesta lisäämällä kommentteja (add-comment).
    Kuinka monta kommenttia on kullakin hakemuksella?
    """
    print(udf.loc[udf['action'] == 'add-comment'].groupby('applicationId').count())


def m1a():
    """
    Kuinka moni kunta käyttää Lupapiste-palvelua käytönaikaisen datan pohjalta laskettuna?
    """
    print(udf.municipalityId.nunique())


def m1c():
    """
    Miten pientalolupiin kirjoitettujen viranomaiskommenttien määrä jakautuu kunnittain?
    """
    municipalities = udf["municipalityId"].unique()
    counts = []
    labels = []
    i = 0
    y = []
    for municipalityId in municipalities:
        size = udf[
            (udf["municipalityId"] == municipalityId) &
            (udf['action'] == 'add-comment') &
            (udf['role'] == 'authority')
        ].size
        counts.append(size)
        labels.append(str(municipalityId))
        y.append(i)
        i += 1
    plt.bar(y, counts, align='center')
    plt.xticks(y, labels)
    plt.xlabel("MunicipalityId")
    plt.ylabel("Comments (pcs)")
    plt.show()


def m2a():
    """
    Kuinka moni kunta käyttää Lupapiste-palvelua operatiivisen datan pohjalta laskettuna?
    """
    print(odf.municipalityId.nunique())


def u1a():
    """
    Kuinka monta käyttäjää Lupapisteessä on?
    """
    udf_a = udf[udf["role"] == "applicant"]
    years = udf_a["datetime"].dt.year.unique()
    years.sort()
    labels = []
    y = []
    counts = []
    max_size = 0
    min_size = sys.maxint
    for year in years:
        months = udf_a[udf_a["datetime"].dt.year == year]["datetime"].dt.month.unique()
        months.sort()
        for month in months:
            total_months = year * 12 + month
            size = udf_a[
                udf_a["datetime"].dt.year * 12 + udf_a["datetime"].dt.month <= total_months
            ]["userId"].unique().size
            counts.append(size)
            labels.append(str(year)+"/"+str(month))
            y.append(total_months)
            if size > max_size:
                max_size = size
            if size < min_size:
                min_size = size
    plt.plot(y, counts)
    plt.xticks(y, labels)
    axes = plt.gca()
    axes.set_ylim([min_size, max_size+5])
    plt.xlabel("Months")
    plt.ylabel("Users (pcs)")
    plt.show()


def u1b():
    """
    Kuinka moni hakija on kertarakentaja?
    (kertarakentajalla on vain yksi lupahakemus, esim. rakentaa pientalon kerran elämässään)
    Kuinka moni käyttäjä on ammattikäyttäjä?
    (10+ lupahakemusta)
    """
    users = udf[udf["role"] == "applicant"]["userId"].unique()
    one_time_users = 0
    pro_users = 0
    for userId in users:
        applications = udf[
            (udf["userId"] == userId) &
            (udf["action"] == "submit-application")
        ].size
        if applications == 1:
            one_time_users += 1
        elif applications > 10:
            pro_users += 1
    print("There where "+str(pro_users)+" pro users.")
    print("There where "+str(one_time_users)+" one time users.")


def a1a():
    """
    Kuinka monta hakemusta Lupapisteessä on haettu?
    """
    print(odf.applicationId.nunique())


def a1b():
    """
    Kausivaihtelu vuositasolla:
    Mihin aikaan vuodesta hakemuksia luodaan?
    Ehkä enemmän keväällä?
    Piirrä kuvaaaja. (Python plot)
    Vinkki: luo operatiivisen datan createdDaten pohjalta uusi muuttuja createdMonth ja piirrä pylväskaavio siten,
    että vaaka-akselilla on kuukaudet 1-12 ja pystyakselilla hakemusten lukumäärä.
    """
    odf["createdMonth"] = odf["createdDate"].dt.month
    counts = []
    months = []
    for month in range(1, 12):
        size = odf[odf["createdMonth"] == month].size
        counts.append(size)
        months.append(month)
    plt.bar(months, counts, 1, color="r")
    plt.xlabel("Months")
    plt.ylabel("Applications (pcs)")
    plt.show()


def time_plot(_odf, _name, _x_label, _y_label, _x_min=0, _x_max=0):
    if _x_min <= _x_max and (_x_min is not _x_max or _x_min is not 0):
        times = range(_x_min, _x_max+1)
    else:
        times = _odf[_name].unique()
    counts = []
    for time in times:
        counts.append(_odf[_odf[_name] == time].size)
    plt.bar(times, counts, 1, color="r")
    x_min = min(times)
    x_max = max(times)
    y_min = min(counts)
    y_max = max(counts)
    plt.axis([x_min, x_max, y_min, y_max])
    plt.xlabel(_x_label)
    plt.ylabel(_y_label)
    plt.show()


def a1c(_only_one_time_builders=False):
    """
    Kausivaihtelu kuukausi-, viikko- ja päivätasolla: milloin
    hakemuksia luodaan eniten? Kuun alussa?
    Viikonloppuna? Klo 3 yöllä? Entä milloin kertarakentaja
    aktivoituu?
    """
    used_odf = odf
    used_odf["month"] = used_odf["createdDate"].dt.day
    used_odf["weekday"] = used_odf["createdDate"].dt.weekday
    used_odf["hour"] = used_odf["createdDate"].dt.hour
    if _only_one_time_builders:
        users = udf[udf["role"] == "applicant"]
        users = users[["applicationId", "userId"]].drop_duplicates()
        multi_users = users["userId"].value_counts()
        multi_users = multi_users[multi_users > 1].index.values
        print(multi_users)
        multi_time_applications = users[users["userId"].isin(multi_users)]["applicationId"].unique()
        print(multi_time_applications)
        used_odf = used_odf[~used_odf["applicationId"].isin(multi_time_applications)]
    print(used_odf)
    time_plot(used_odf, "month", "Month", "Applications (pcs)", 1, 12)
    time_plot(used_odf, "weekday", "Weekday", "Applications (pcs)", 0, 6)
    time_plot(used_odf, "hour", "Hour", "Applications (pcs)", 0, 23)
