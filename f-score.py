import tabula
#import pandas as pd
from PyPDF4 import PdfFileReader
import os


def f_score(file, year=2019):
    '''
    Loads data from the pdf research of one of the Finnish banks.
    Retrieves P/B value and calculates F-score.
    https://en.wikipedia.org/wiki/Piotroski_F-score
    :param file: pdf
    :param year: by default year prior to the investment, can calculate past years
    :return: name of the company, P/B, F-score
    '''

    data = tabula.read_pdf(file, stream=True, pages=[1, 2, 3, 4], multiple_tables=True)

    if year == 2019: y = 8
    else: y = 8 - (2019 - year)

    # the file headers are not consistent, using filename instead
    # title = PdfFileReader(file).getDocumentInfo().title
    title = file.split('.')[0]

    summary = data[0]

    income_statement = data[1]

    balance_sheet = data[2]

    cash_flow = data[3]

    # table checks
    if summary.iat[0,3] != str(year): print('Check Summary table and years')
    if cash_flow.iat[0, 8] != str(year): print('Check Cash Flow table and years')
    if balance_sheet.iat[0, 8] != str(year): print('Check Balance Sheet table and years')
    if income_statement.iat[0, 8] != str(year): print('Check Income Statement table and years')
    if income_statement.iat[18,0][0:10] != "Net profit" : print("Check net profit")
    if balance_sheet.iat[20,0][0:9] != 'Total ass': print('Check total assets')
    if cash_flow.iat[11,0][0:9] != 'Cash flow': print('Check CFO')
    if income_statement.iat[5,0][0:6] != 'EBITDA': print('Check EBITDA')
    if income_statement.iat[1,0][0:13] != 'Total revenue': print('Check Total revenue')
    if balance_sheet.iat[27,0] != 'Long term interest bearing debt': print('check long-time debt')
    if balance_sheet.iat[40,0] != 'Short term interest bearing debt': print('Check short-time debt')
    if balance_sheet.iat[41,0] != 'Total current liabilities': print('Check liabilities')
    if cash_flow.iat[19,0][0:13] != 'Equity issues': print('Check Equity issues')

    try:
        P_B = summary.iat[11,y-5]
    except: P_B = 'Year out of available range (P/B)'

    F_SCORE = 0

    # net income/total assets
    ROA = int(income_statement.iat[18,y].replace(',', '')) / int(balance_sheet.iat[20,y].replace(',', ''))
    if ROA > 0: F_SCORE += 1

    # ROA difference of last two years
    d_ROA = ROA - int(income_statement.iat[18,y-1].replace(',', '')) / int(
        balance_sheet.iat[20,y-1].replace(',', ''))
    if d_ROA > 0: F_SCORE += 1

    # Cash flow from operations scaled by total assets at the beginning of year
    CFO = int(cash_flow.iat[11,y].replace(',', '')) / int(balance_sheet.iat[20,y].replace(',', ''))
    if CFO > 0: F_SCORE += 1
    # (net income - CFO)/total assets
    ACCRUAL = ROA - CFO
    if ACCRUAL < 0: F_SCORE += 1

    # EBITDA/total revenue difference of last two years
    d_MARGIN = int(income_statement.iat[5,y].replace(',', '')) / int(
        income_statement.iat[1,y].replace(',', '')) \
               - int(income_statement.iat[5,y-1].replace(',', '')) / int(
        income_statement.iat[1,y-1].replace(',', ''))
    if d_MARGIN > 0: F_SCORE += 1

    # net sales/total assets difference of last two years
    d_TURN = int(income_statement.iat[1,y].replace(',', '')) / int(
        balance_sheet.iat[20,y].replace(',', '')) \
             - int(income_statement.iat[1,y-1].replace(',', '')) / int(
        balance_sheet.iat[20,y-1].replace(',', ''))
    if d_TURN > 0: F_SCORE += 1

    # long and short term debt / total assets difference of last two years
    d_LEVER = (
            (int(balance_sheet.iat[27,y].replace(',', '')) + int(
                balance_sheet.iat[40,y].replace(',', '')))
            / int(balance_sheet.iat[20,y].replace(',', '')) - (
                        int(balance_sheet.iat[27,y-1].replace(',', ''))
                        + int(balance_sheet.iat[40,y-1].replace(',', ''))) / int(
        balance_sheet.iat[20,y-1].replace(',', ''))
    )
    if d_LEVER < 0: F_SCORE += 1

    # total assets/total liabilities difference of last two years
    d_LIQUID = int(balance_sheet.iat[20,y].replace(',', '')) / int(
        balance_sheet.iat[41,y].replace(',', '')) \
               - int(balance_sheet.iat[20,y-1].replace(',', '')) / int(
        balance_sheet.iat[41,y-1].replace(',', ''))
    if d_LIQUID > 0: F_SCORE += 1

    # equities issued last year
    EQ = int(cash_flow.iat[19,y].replace(',', ''))
    if EQ <= 0: F_SCORE += 1

    # test = ROA + d_ROA + d_TURN + d_LEVER + d_LIQUID + d_MARGIN + CFO + ACCRUAL

    return title, P_B, F_SCORE


def folder_loop(dir):
    '''

    :param dir:
    :return:
    '''
    files = os.listdir(dir)
    titles = list()

    for file in files:
        titles.append(file.split('.')[0])
    try:
        fh = open("parameters.txt", "r+")
    except FileNotFoundError:
        fh = open("parameters.txt", "w")
        fh.write("Name, P/B, F-score\n")
    calculated = list()

    try:
        for line in fh:
            calculated.append(line.rstrip())
    except:
        pass

    for title in titles:
        # if file.startswith('.'): continue
        if title not in calculated:
            fh.write(f"{title}{f_score(dir+'/'+title+'.pdf')} \n")

    fh.close()

folder_loop('samples')


#todo:
# remove double name printing
# add documentation