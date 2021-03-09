import camelot
import numpy as np

def angel_pdf_to_csv(pdf_path):
    
    #Reading the PDF file using Camelot and converting to DataFrame
    tables = camelot.read_pdf(pdf_path, flavor='stream', pages='1')
    df = tables[0].df

    #defining standard column names
    columns = ['Segment', 'Scrip Name', 'Buy', 'Buy Market Rate (Avg)', 'Sell Qty', 
           'Sell Market Rate(Avg)','Brokerage', 'STT', 'Other Charges', 'Grand Total']
    
    #Finding the location of client ID and deleting all rows before that row.
    ix_loc = df[df[0].str.startswith('Trading Code')].index[0]
    list1 = [x for x in range(0, ix_loc)]
    df.drop(list1, inplace=True)
    df.reset_index(drop = True, inplace = True)
    
    #storing the client code in a variable
    client_code = df.iat[0,0].split('\n')[0].split(':')[1].strip()
    
    #renaming the columns
    df.columns = columns
    
    #Only filtering for the NSE, BSE and Total trades
    final_df = df[df['Segment'].isin(['NSECM', 'BSECM', 'Total'])]
    final_df.index = np.arange(1, len(final_df) + 1)
    
    #Replacing index name with clientcode
    final_df.index.name = client_code
    
    final_df.reset_index(inplace = True)

    return final_df