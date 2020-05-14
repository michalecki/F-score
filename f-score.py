import tabula
import pandas as pd
# import locale
# locale.setlocale(locale.LC_ALL, 'en_US')

def f_score(file,year=2019):
    '''
    Loads data from the pdf research of one of the Finnish banks.
    Retrieves P/B value and calculates F-score.
    https://en.wikipedia.org/wiki/Piotroski_F-score
    :param file: pdf 
    :param year: by default year prior to the investment, can calculate past years  
    :return: 
    '''

    data = tabula.read_pdf(file, stream = True, pages = [1,2,3,4], multiple_tables = True)
    
    y = year
    
    summary = data[0]
    summary.columns = summary.iloc[0]
    
    income_statement = data[1].set_index(data[1].columns[0])
    income_statement.columns = income_statement.iloc[0]
    
    balance_sheet = data[2].set_index(data[2].columns[0])
    balance_sheet.columns = balance_sheet.iloc[0]
    
    cash_flow = data[3].set_index(data[3].columns[0])
    cash_flow.columns = cash_flow.iloc[0]

    #table checks

    if cash_flow.iat[0,7] != str(y): print('Check Cash Flow table and years')
    if balance_sheet.iat[0,7] != str(y): print('Check Balance Sheet table and years')
    if income_statement.iat[0,7] != str(y): print('Check Income Statement table and years')

    P_B = summary[str(y)].iloc[11]
    # summary.iat[]

    F_SCORE = 0
    
    #net income/total assets
    ROA = int(income_statement[str(y)].iloc[18].replace(',',''))/int(balance_sheet[str(y)].iloc[20].replace(',',''))
    if ROA > 0: F_SCORE += 1
    
    #ROA difference of last two years
    d_ROA = ROA - int(income_statement[str(y-1)].iloc[18].replace(',',''))/int(balance_sheet[str(y-1)].iloc[20].replace(',',''))
    if d_ROA > 0: F_SCORE += 1

    #Cash flow from operations scaled by total assets at the beginning of year
    CFO = int(cash_flow[str(y)].iloc[11].replace(',',''))/int(balance_sheet[str(y)].iloc[20].replace(',',''))
    if CFO > 0: F_SCORE += 1
    #(net income - CFO)/total assets
    ACCRUAL = ROA - CFO
    if ACCRUAL < 0: F_SCORE += 1

    #EBITDA/total revenue difference of last two years
    d_MARGIN = int(income_statement[str(y)].iloc[5].replace(',',''))/int(income_statement[str(y)].iloc[1].replace(',','')) \
        - int(income_statement[str(y-1)].iloc[5].replace(',',''))/int(income_statement[str(y-1)].iloc[1].replace(',',''))
    if d_MARGIN > 0: F_SCORE += 1

    #net sales/total assets difference of last two years
    d_TURN = int(income_statement[str(y)].iloc[1].replace(',',''))/int(balance_sheet[str(y)].iloc[20].replace(',','')) \
        - int(income_statement[str(y-1)].iloc[1].replace(',',''))/int(balance_sheet[str(y-1)].iloc[20].replace(',',''))
    if d_TURN > 0: F_SCORE += 1

    #long and short term debt / total assets difference of last two years
    d_LEVER = (
            (int(balance_sheet[str(y)].iloc[27].replace(',','')) + int(balance_sheet[str(y)].iloc[40].replace(',','')))
            / int(balance_sheet[str(y)].iloc[20].replace(',','')) - (int(balance_sheet[str(y-1)].iloc[27].replace(',',''))
            + int(balance_sheet[str(y-1)].iloc[40].replace(',',''))) / int(balance_sheet[str(y-1)].iloc[20].replace(',',''))
            )
    if d_LEVER < 0: F_SCORE += 1

    #total assets/total liabilities difference of last two years
    d_LIQUID = int(balance_sheet[str(y)].iloc[20].replace(',','')) / int(balance_sheet[str(y)].iloc[41].replace(',','')) \
        - int(balance_sheet[str(y-1)].iloc[20].replace(',','')) / int(balance_sheet[str(y-1)].iloc[41].replace(',',''))
    if d_LIQUID > 0: F_SCORE += 1

    #equities issued last year
    EQ = int(cash_flow[str(y)].iloc[19].replace(',',''))
    if EQ <= 0: F_SCORE += 1

    return P_B, F_SCORE




#todo:
# switch using iloc and put to iat (take back indexing (yes) and naming columns(?))
# loop through files to make df
# export (SQL/csv?) and calculate only new