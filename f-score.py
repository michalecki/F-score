import tabula
import pandas as pd
# import locale
# locale.setlocale(locale.LC_ALL, 'en_US')
data = tabula.read_pdf('samples/metsa.pdf',stream = True, pages = [1,2,3,4], multiple_tables = True)


summary = data[0]
summary.columns = summary.iloc[0]

income_statement = data[1].set_index(data[1].columns[0])
income_statement.columns = income_statement.iloc[0]

balance_sheet = data[2].set_index(data[2].columns[0])
balance_sheet.columns = balance_sheet.iloc[0]

cash_flow = data[3].set_index(data[3].columns[0])
cash_flow.columns = cash_flow.iloc[0]

P_B = summary['2019'].iloc[11]

#net income/total assets
ROA = int(income_statement['2019'].iloc[18].replace(',',''))/int(balance_sheet['2019'].iloc[20].replace(',',''))


#todo:
# continue with other markers
# turn into a function returning a dictionary
# loop through files to make df
# export (SQL/csv?) and calculate only new