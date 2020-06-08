'''
A script to calculate F-score
https://en.wikipedia.org/wiki/Piotroski_F-score
The source of data are pdf reports from one of the Finnish banks.
The script loops through the pdf files in the folder and
calculates F-score for each company.
'''

import os  # to acces file list in the folder
import tabula  # to read in tables from pdf


def calculate_f_score(file, year=2019):
    '''
    Loads data from the pdf research of one of the Finnish banks.
    Retrieves P/B value and calculates F-score.
    https://en.wikipedia.org/wiki/Piotroski_F-score
    :param file: pdf
    :param year: by default year prior to the investment, can calculate past years
    :return: P/B, F-score
    '''

    if file.split('.')[-1] != 'pdf':
        return print('only pdf please')
    # gets tables from the first 4 pages of the document
    data = tabula.read_pdf(file, stream=True, pages=[1, 2, 3, 4], multiple_tables=True)

    # maps the year to the column in the tables
    if year == 2019:
        y = 8
    else:
        y = 8 - (2019 - year)

    # the file headers are not consistent, using filename in the looping function instead
    # title = PdfFileReader(file).getDocumentInfo().title

    # assigns names to the tables for clarity
    summary = data[0]
    income_statement = data[1]
    balance_sheet = data[2]
    cash_flow = data[3]

    # table checks if retrieving correct data
    if summary.iat[0, 3] != str(year):
        print(file, 'Check Summary table and years')
    if cash_flow.iat[0, 8] != str(year):
        print(file, 'Check Cash Flow table and years')
    if balance_sheet.iat[0, 8] != str(year):
        print(file, 'Check Balance Sheet table and years')
    if income_statement.iat[0, 8] != str(year):
        print(file, 'Check Income Statement table and years')
    if income_statement.iat[18, 0][0:10] != "Net profit":
        print(file, "Check net profit")
    if balance_sheet.iat[20, 0][0:9] != 'Total ass':
        print(file, 'Check total assets')
    if cash_flow.iat[11, 0][0:9] != 'Cash flow':
        print(file, 'Check cfo')
    if income_statement.iat[5, 0][0:6] != 'EBITDA':
        print(file, 'Check EBITDA')
    if income_statement.iat[1, 0][0:13] != 'Total revenue':
        print(file, 'Check Total revenue')
    if balance_sheet.iat[27, 0] != 'Long term interest bearing debt':
        print(file, 'check long-time debt')
    if balance_sheet.iat[40, 0] != 'Short term interest bearing debt':
        print(file, 'Check short-time debt')
    if balance_sheet.iat[41, 0] != 'Total current liabilities':
        print(file, 'Check liabilities')
    if cash_flow.iat[19, 0][0:13] != 'Equity issues':
        print(file, 'Check equity issues')

    try:
        p_b = summary.iat[11, y - 5]
    except:
        p_b = 'Year out of available range (P/B)'

    # calculating the f-score parameter
    f_score = 0

    # net income/total assets
    roa = int(income_statement.iat[18, y].replace(',', '')) / int(
        balance_sheet.iat[20, y].replace(',', ''))
    if roa > 0:
        f_score += 1

    # roa difference of last two years
    d_roa = roa - int(income_statement.iat[18, y - 1].replace(',', '')) / int(
        balance_sheet.iat[20, y - 1].replace(',', ''))
    if d_roa > 0:
        f_score += 1

    # Cash flow from operations scaled by total assets at the beginning of year
    cfo = int(cash_flow.iat[11, y].replace(',', '')) / int(
        balance_sheet.iat[20, y].replace(',', ''))
    if cfo > 0:
        f_score += 1
    # (net income - cfo)/total assets
    accrual = roa - cfo
    if accrual < 0:
        f_score += 1

    # EBITDA/total revenue difference of last two years
    d_margin = int(income_statement.iat[5, y].replace(',', '')) / int(
        income_statement.iat[1, y].replace(',', '')) \
               - int(income_statement.iat[5, y - 1].replace(',', '')) / int(
        income_statement.iat[1, y - 1].replace(',', ''))
    if d_margin > 0:
        f_score += 1

    # net sales/total assets difference of last two years
    d_turn = int(income_statement.iat[1, y].replace(',', '')) / int(
        balance_sheet.iat[20, y].replace(',', '')) \
             - int(income_statement.iat[1, y - 1].replace(',', '')) / int(
        balance_sheet.iat[20, y - 1].replace(',', ''))
    if d_turn > 0:
        f_score += 1

    # long and short term debt / total assets difference of last two years
    d_lever = (
            (int(balance_sheet.iat[27, y].replace(',', '')) + int(
                balance_sheet.iat[40, y].replace(',', '')))
            / int(balance_sheet.iat[20, y].replace(',', '')) - (
                    int(balance_sheet.iat[27, y - 1].replace(',', ''))
                    + int(balance_sheet.iat[40, y - 1].replace(',', ''))) / int(
        balance_sheet.iat[20, y - 1].replace(',', ''))
    )
    if d_lever < 0:
        f_score += 1

    # total assets/total liabilities difference of last two years
    d_liquid = int(balance_sheet.iat[20, y].replace(',', '')) / int(
        balance_sheet.iat[41, y].replace(',', '')) \
               - int(balance_sheet.iat[20, y - 1].replace(',', '')) / int(
        balance_sheet.iat[41, y - 1].replace(',', ''))
    if d_liquid > 0:
        f_score += 1

    # equities issued last year
    try:
        eq = int(cash_flow.iat[19, y].replace(',', ''))
    # sometimes the value is n.a.
    except ValueError:
        eq = 0

    if eq <= 0:
        f_score += 1

    # a parameter for testing
    # test = roa + d_roa + d_turn + d_lever + d_liquid + d_margin + cfo + accrual

    return p_b, f_score


def folder_loop(directory):
    '''
    Helper function to loop through the files in a folder and
    calculate parameters for the files that don't have
    the calculation done yet.
    :param dir: str, directory where the files are
    :return: text file with data: file name, output of f_score
    '''
    # makes a list of the files in the directory
    files = os.listdir(directory)
    titles = list()

    # strips the file name from extension
    for file in files:
        if file.split('.')[-1] == 'pdf':
            titles.append(file.split('.')[0])

    # makes the parameter file or opens it for reading and appending
    try:
        fh = open(f"{directory}/parameters.txt", "r+")
    except FileNotFoundError:
        fh = open(f"{directory}/parameters.txt", "w")
        fh.write("Name, (P/B, F-score)\n")

    calculated = list()
    # reads through file contents to avoid repeating calculation
    try:
        for line in fh:
            if len(line) > 2:
                calculated.append(line.split()[0])
    except:
        pass

    # calculates parameter and adds to the file if the filename in not in the file yet
    for title in titles:
        if title not in calculated:
            fh.write(f"{title} {calculate_f_score(directory + '/' + title + '.pdf')}\n")
    fh.close()


# example use
# will read files in the ./samples folder
# will write the "parameters.txt" file into the ./samples directory
folder_loop('samples')