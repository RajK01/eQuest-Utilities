import glob as gb
import os
import warnings
import pandas as pd
import streamlit as st
import xlwings as xw # Xlwings is a Python library that makes it easy to call Python from Excel
# used to filter out warning messages generated by modules or functions called in your code.
warnings.filterwarnings("ignore")

def get_PSF_report_Prop(name):
    try:
        with open(name) as f:
            flist = f.readlines()
    
            pse_count = [] 
            for num, line in enumerate(flist, 0):
                if 'PS-F' in line:
                    pse_count.append(num)
                if 'BEPS' in line:
                    numend = num
            numstart = pse_count[0] 
            pse_rpt = flist[numstart:numend]
            
            pse_str = []
            psf_type = []
            # Iterate through each line in lvb_rpt
            for line in pse_rpt:
                # Check conditions and append lines containing relevant data to lvb_str list
                if (('.' in line and 'KW' in line and "=" not in line) or 
                    ('JAN' in line or 'FEB' in line or 'MAR' in line
                      or 'JUN' in line or 'APR' in line or 'MAY' in line or 'JUN' in line or 'JUL' in line or 'AUG' in line or
                      'SEP' in line or 'OCT' in line or 'NOV' in line or 'DEC' in line) or
                    ('.' in line and 'MAX KW' in line)):
                    pse_str.append(line)
                elif ("PS-F" in line and "WEATHER" in line):
                    psf_type.append(line)
            
            # result list to store filtered columns. after 10th column from last remaining values in 1 column.
            result = []  
            for line in pse_str:
                lvb_list = []
                # Split the line by whitespace and store the result in splitter
                splitter = line.split()
                # Join the first part of the splitter except the last 10 elements and store it as space_name
                space_name = " ".join(splitter[:-13])
                # Add space_name as the first element of lvb_list
                lvb_list=splitter[-13:]
                lvb_list.insert(0,space_name)
                # Append lvb_list to result
                result.append(lvb_list)
                
            # strore list to dataframe
            psf_df = pd.DataFrame(result) 
            # # Allot lvb_df columns from sim file
            psf_df.columns = ['UNIT', 'LIGHTS', 'TASK_LIGHTS', 'MISC_EQUIP', 'SPACE_EQUIP', 
                                 'SPACE_COOLING', 'HEAT_REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY',
                                 'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL']
            
            psf_df.index.name = name
            value_before_backslash = ''.join(reversed(name)).split("\\")[0]
            name1 = ''.join(reversed(value_before_backslash))
            name = name1.rsplit(".", 1)[0]
            # psf_df.insert(0, 'RUNNAME', name)
    
            # Find the index of the first occurrence of "JAN" followed by "FEB"
            start_index = None
            for i in range(len(psf_df) - 1):
                if psf_df['LIGHTS'][i] == 'JAN' and psf_df['LIGHTS'][i+1] == 'FEB':
                    start_index = i
                    break
    
            # If "JAN" followed by "FEB" found, delete rows from "JAN" to the end
            if start_index is not None:
                psf_df = psf_df.iloc[0:start_index]
    
            for i in range(len(psf_df)):
                if i < len(psf_df) - 1 and ((psf_df['UNIT'][i] == 'MAX KW' and psf_df['LIGHTS'][i+1] == 'KWH') or (psf_df['UNIT'][i] == 'MAX KW' and psf_df['UNIT'][i+1] == 'KWH')):
                    new_row = {'UNIT': '', 'LIGHTS': 'TOTAL'}  # New row to be inserted
                    psf_df = pd.concat([psf_df.iloc[:i+1], pd.DataFrame([new_row]), psf_df.iloc[i+1:]]).reset_index(drop=True)
    
            # This will tell how many meters we have in KW and KWH case(in CSV)
            countMeters = 0
            for i in range(len(psf_df)):
                if psf_df['LIGHTS'][i] == 'JAN':
                    countMeters += 1
    
            values = []
            for item in psf_type:
                start_index = item.find("for") + len("for")
                end_index = item.find("WEATHER")
                value = item[start_index:end_index].strip()
                values.append(value)
            values1 = list(dict.fromkeys(values))
    
            values2 = []
            for i in range(countMeters):
                values2.append(values1[i])
            
            # Create an empty list to store the indices where rows are to be inserted
            insert_indices = []
    
            # Iterate over the DataFrame to find the indices where 'JAN' occurs
            for index, row in psf_df.iterrows():
                if row['LIGHTS'] == 'JAN':
                    insert_indices.append(index)
    
            # Iterate over the insert indices and insert the corresponding value from values2
            for i, index in enumerate(insert_indices):
                # Calculate the index in values2 to insert
                values2_index = i % len(values2)
                new_row = {'UNIT': values2[values2_index]}
                # Insert the new row before the 'JAN'
                psf_df = pd.concat([psf_df.iloc[:index+i], pd.DataFrame([new_row]), psf_df.iloc[index+i:]]).reset_index(drop=True)
    
            # Reset index after concatenation
            psf_df.reset_index(drop=True, inplace=True)
    
            return psf_df
    except Exception as e:
        print(f"An error occurred: {e}")
        columns = ['AZIMUTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)', 'AVERAGE U-VALUE(WALLS+WINDOWS)(BTU/HR-SQFT-F)', 
                              'WINDOW(AREA)(SQFT)', 'WALL(AREA)(SQFT)', 'WINDOW+WALL(AREA)(SQFT)']
        return pd.DataFrame()

def get_PSF_report_Base(name):
    try:
        with open(name) as f:
            flist = f.readlines()
    
            pse_count = [] 
            for num, line in enumerate(flist, 0):
                if 'PS-F' in line:
                    pse_count.append(num)
                if 'BEPS' in line:
                    numend = num
            numstart = pse_count[0] 
            pse_rpt = flist[numstart:numend]
            
            pse_str = []
            psf_type = []
            # Iterate through each line in lvb_rpt
            for line in pse_rpt:
                # Check conditions and append lines containing relevant data to lvb_str list
                if (('.' in line and 'KW' in line and "=" not in line) or 
                    ('JAN' in line or 'FEB' in line or 'MAR' in line
                      or 'JUN' in line or 'APR' in line or 'MAY' in line or 'JUN' in line or 'JUL' in line or 'AUG' in line or
                      'SEP' in line or 'OCT' in line or 'NOV' in line or 'DEC' in line) or
                    ('.' in line and 'MAX KW' in line)):
                    pse_str.append(line)
                elif ("PS-F" in line and "WEATHER" in line):
                    psf_type.append(line)
            
            # result list to store filtered columns. after 10th column from last remaining values in 1 column.
            result = []  
            for line in pse_str:
                lvb_list = []
                # Split the line by whitespace and store the result in splitter
                splitter = line.split()
                # Join the first part of the splitter except the last 10 elements and store it as space_name
                space_name = " ".join(splitter[:-13])
                # Add space_name as the first element of lvb_list
                lvb_list=splitter[-13:]
                lvb_list.insert(0,space_name)
                # Append lvb_list to result
                result.append(lvb_list)
                
            # strore list to dataframe
            psf_df = pd.DataFrame(result) 
            # # Allot lvb_df columns from sim file
            psf_df.columns = ['UNIT', 'LIGHTS', 'TASK_LIGHTS', 'MISC_EQUIP', 'SPACE_EQUIP', 
                                 'SPACE_COOLING', 'HEAT_REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY',
                                 'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL']
            
            psf_df.index.name = name
            value_before_backslash = ''.join(reversed(name)).split("\\")[0]
            name1 = ''.join(reversed(value_before_backslash))
            name = name1.rsplit(".", 1)[0]
            # psf_df.insert(0, 'RUNNAME', name)
    
            # Find the index of the first occurrence of "JAN" followed by "FEB"
            start_index = None
            for i in range(len(psf_df) - 1):
                if psf_df['LIGHTS'][i] == 'JAN' and psf_df['LIGHTS'][i+1] == 'FEB':
                    start_index = i
                    break
    
            # If "JAN" followed by "FEB" found, delete rows from "JAN" to the end
            if start_index is not None:
                psf_df = psf_df.iloc[0:start_index]
    
            for i in range(len(psf_df)):
                if i < len(psf_df) - 1 and ((psf_df['UNIT'][i] == 'MAX KW' and psf_df['LIGHTS'][i+1] == 'KWH') or (psf_df['UNIT'][i] == 'MAX KW' and psf_df['UNIT'][i+1] == 'KWH')):
                    new_row = {'UNIT': '', 'LIGHTS': 'TOTAL'}  # New row to be inserted
                    psf_df = pd.concat([psf_df.iloc[:i+1], pd.DataFrame([new_row]), psf_df.iloc[i+1:]]).reset_index(drop=True)
    
            # This will tell how many meters we have in KW and KWH case(in CSV)
            countMeters = 0
            for i in range(len(psf_df)):
                if psf_df['LIGHTS'][i] == 'JAN':
                    countMeters += 1
    
            values = []
            for item in psf_type:
                start_index = item.find("for") + len("for")
                end_index = item.find("WEATHER")
                value = item[start_index:end_index].strip()
                values.append(value)
            values1 = list(dict.fromkeys(values))
    
            values2 = []
            for i in range(countMeters):
                values2.append(values1[i])
            
            # Create an empty list to store the indices where rows are to be inserted
            insert_indices = []
    
            # Iterate over the DataFrame to find the indices where 'JAN' occurs
            for index, row in psf_df.iterrows():
                if row['LIGHTS'] == 'JAN':
                    insert_indices.append(index)
    
            # Iterate over the insert indices and insert the corresponding value from values2
            for i, index in enumerate(insert_indices):
                # Calculate the index in values2 to insert
                values2_index = i % len(values2)
                new_row = {'UNIT': values2[values2_index]}
                # Insert the new row before the 'JAN'
                psf_df = pd.concat([psf_df.iloc[:index+i], pd.DataFrame([new_row]), psf_df.iloc[index+i:]]).reset_index(drop=True)
    
            # Reset index after concatenation
            psf_df.reset_index(drop=True, inplace=True)
    
            return psf_df
    except Exception as e:
        print(f"An error occurred: {e}")
        columns = ['AZIMUTH', 'AVERAGE(U-VALUE/WINDOWS)(BTU/HR-SQFT-F)', 'AVERAGE(U-VALUE/WALLS)(BTU/HR-SQFT-F)', 'AVERAGE U-VALUE(WALLS+WINDOWS)(BTU/HR-SQFT-F)', 
                              'WINDOW(AREA)(SQFT)', 'WALL(AREA)(SQFT)', 'WINDOW+WALL(AREA)(SQFT)']
        return pd.DataFrame()

######################################### BASED ON UNITS #########################################

def get_PSF_report_Prop_all(name):
    try:
        with open(name) as f:
            flist = f.readlines()

            pse_count = [] 
            for num, line in enumerate(flist, 0):
                if 'PS-F' in line:
                    pse_count.append(num)
                if 'BEPS' in line:
                    numend = num
            numstart = pse_count[0] 
            pse_rpt = flist[numstart:numend]
            
            pse_str = []
            psf_type = []
            # Iterate through each line in lvb_rpt
            for line in pse_rpt:
                # Check conditions and append lines containing relevant data to lvb_str list
                if (('.' in line and 'KW' in line and "=" not in line) or 
                    ('JAN' in line or 'FEB' in line or 'MAR' in line
                    or 'JUN' in line or 'APR' in line or 'MAY' in line or 'JUN' in line or 'JUL' in line or 'AUG' in line or
                    'SEP' in line or 'OCT' in line or 'NOV' in line or 'DEC' in line) or
                    ('.' in line and 'MAX KW' in line) or ('.' in line and 'THERM' in line) or ('.' in line and 'MAX THERM/HR' in line) or 
                    ('.' in line and 'MBTU' in line) or ('.' in line and 'MAX MBTU/HR' in line)):
                    pse_str.append(line)
                elif ("PS-F" in line and "WEATHER" in line):
                    psf_type.append(line)
            
            # result list to store filtered columns. after 10th column from last remaining values in 1 column.
            result = []  
            for line in pse_str:
                lvb_list = []
                # Split the line by whitespace and store the result in splitter
                splitter = line.split()
                # Join the first part of the splitter except the last 10 elements and store it as space_name
                space_name = " ".join(splitter[:-13])
                # Add space_name as the first element of lvb_list
                lvb_list=splitter[-13:]
                lvb_list.insert(0,space_name)
                # Append lvb_list to result
                result.append(lvb_list)
                
            # strore list to dataframe
            psf_df = pd.DataFrame(result) 
            # # Allot lvb_df columns from sim file
            psf_df.columns = ['UNIT', 'LIGHTS', 'TASK_LIGHTS', 'MISC_EQUIP', 'SPACE_EQUIP', 
                                'SPACE_COOLING', 'HEAT_REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY',
                                'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL']

            # Find the index of the first occurrence of "JAN" followed by "FEB"
            start_index = None
            for i in range(len(psf_df) - 1):
                if psf_df['LIGHTS'][i] == 'JAN' and psf_df['LIGHTS'][i+1] == 'FEB':
                    start_index = i
                    break

            # If "JAN" followed by "FEB" found, delete rows from "JAN" to the end
            if start_index is not None:
                psf_df = psf_df.iloc[0:start_index]

            for i in range(len(psf_df)):
                if i < len(psf_df) - 1 and ((psf_df['UNIT'][i] == 'MAX KW' and psf_df['LIGHTS'][i+1] == 'KWH') or (psf_df['UNIT'][i] == 'MAX KW' and psf_df['UNIT'][i+1] == 'KWH') or
                                            (psf_df['UNIT'][i] == 'MAX THERM/HR' and psf_df['LIGHTS'][i+1] == 'THERM') or (psf_df['UNIT'][i] == 'MAX THERM/HR' and psf_df['UNIT'][i+1] == 'THERM') or
                                            (psf_df['UNIT'][i] == 'MAX MBTU/HR' and psf_df['LIGHTS'][i+1] == 'MBTU') or (psf_df['UNIT'][i] == 'MAX MBTU/HR' and psf_df['UNIT'][i+1] == 'MBTU')):
                  
                    new_row = {'UNIT': 'TOTAL', 'LIGHTS': ''}  # New row to be inserted
                    psf_df = pd.concat([psf_df.iloc[:i+1], pd.DataFrame([new_row]), psf_df.iloc[i+1:]]).reset_index(drop=True)

            # This will tell how many meters we have in KW and KWH case(in CSV)
            countMeters = 0
            for i in range(len(psf_df)):
                if psf_df['LIGHTS'][i] == 'JAN':
                    countMeters += 1

            values = []
            for item in psf_type:
                start_index = item.find("for") + len("for")
                end_index = item.find("WEATHER")
                value = item[start_index:end_index].strip()
                values.append(value)
            values1 = list(dict.fromkeys(values))

            values2 = []
            for i in range(countMeters):
                values2.append(values1[i])
            
            # Create an empty list to store the indices where rows are to be inserted
            insert_indices = []

            # Iterate over the DataFrame to find the indices where 'JAN' occurs
            for index, row in psf_df.iterrows():
                if row['LIGHTS'] == 'JAN':
                    insert_indices.append(index)

            # Iterate over the insert indices and insert the corresponding value from values2
            for i, index in enumerate(insert_indices):
                # Calculate the index in values2 to insert
                values2_index = i % len(values2)
                new_row = {'UNIT': values2[values2_index]}
                # Insert the new row before the 'JAN'
                psf_df = pd.concat([psf_df.iloc[:index+i], pd.DataFrame([new_row]), psf_df.iloc[index+i:]]).reset_index(drop=True)
            
    
            months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
            # Remove rows where 'LIGHTS' column contains month names
            psf_df = psf_df[~psf_df['LIGHTS'].isin(months)]

            # # Reset index after concatenation
            psf_df.reset_index(drop=True, inplace=True)
            if psf_df.loc[len(psf_df) - 3, 'UNIT'] != 'TOTAL':
                # Create a new row with 'TOTAL' in the 'LIGHTS' column
                new_row = pd.DataFrame({'UNIT': ['TOTAL']})
                # Insert the new row at the third last position
                psf_df = pd.concat([psf_df.iloc[:len(psf_df) - 2], new_row, psf_df.iloc[len(psf_df) - 2:]]).reset_index(drop=True)

            # Storing meterings in a list
            keywords_to_filter = ['KW', 'KWH', 'MAX KW', 'TOTAL', 'THERM', 'MAX THERM/HR', 'MBTU', 'MAX MBTU/HR', '']
            filtered_df = psf_df[~psf_df['UNIT'].isin(keywords_to_filter)]
            filtered_df = filtered_df['UNIT']
            filtered_df = filtered_df.loc[filtered_df.index.repeat(3)].reset_index(drop=True)
            # # psf_df['Meterings'] = filtered_df

            total_mask = psf_df['UNIT'] == 'TOTAL'
            if any(total_mask):
                total_indices = psf_df.index[total_mask]
                indices_to_keep = []
                for index in total_indices:
                    indices_to_keep.extend([index, index + 1, index + 2])
                psf_df = psf_df.loc[indices_to_keep].reset_index(drop=True)
            else:
                psf_df = pd.DataFrame()
            psf_df['Meterings'] = filtered_df
            cols = list(psf_df.columns)
            psf_df = psf_df[[cols[-1]] + cols[:-1]]

            total_mask1 = psf_df['UNIT'] == 'TOTAL'
            if any(total_mask1):
                total_indices1 = psf_df.index[total_mask1]
                indices_to_keep1 = []
                for index in total_indices1:
                    indices_to_keep1.extend([index + 1, index + 2])
                psf_df = psf_df.loc[indices_to_keep1].reset_index(drop=True)
            else:
                psf_df = pd.DataFrame()
            
            return psf_df

    except Exception as e:
        print(f"An error occurred: {e}")
        columns = ['UNIT', 'LIGHTS', 'TASK_LIGHTS', 'MISC_EQUIP', 'SPACE_EQUIP', 
                    'SPACE_COOLING', 'HEAT_REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY',
                    'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL']
        return pd.DataFrame(columns=columns)

def get_PSF_report_Base_all(name):
    try:
        with open(name) as f:
            flist = f.readlines()

            pse_count = [] 
            for num, line in enumerate(flist, 0):
                if 'PS-F' in line:
                    pse_count.append(num)
                if 'BEPS' in line:
                    numend = num
            numstart = pse_count[0] 
            pse_rpt = flist[numstart:numend]
            
            pse_str = []
            psf_type = []
            # Iterate through each line in lvb_rpt
            for line in pse_rpt:
                # Check conditions and append lines containing relevant data to lvb_str list
                if (('.' in line and 'KW' in line and "=" not in line) or 
                    ('JAN' in line or 'FEB' in line or 'MAR' in line
                    or 'JUN' in line or 'APR' in line or 'MAY' in line or 'JUN' in line or 'JUL' in line or 'AUG' in line or
                    'SEP' in line or 'OCT' in line or 'NOV' in line or 'DEC' in line) or
                    ('.' in line and 'MAX KW' in line) or ('.' in line and 'THERM' in line) or ('.' in line and 'MAX THERM/HR' in line) or 
                    ('.' in line and 'MBTU' in line) or ('.' in line and 'MAX MBTU/HR' in line)):
                    pse_str.append(line)
                elif ("PS-F" in line and "WEATHER" in line):
                    psf_type.append(line)
            
            # result list to store filtered columns. after 10th column from last remaining values in 1 column.
            result = []  
            for line in pse_str:
                lvb_list = []
                # Split the line by whitespace and store the result in splitter
                splitter = line.split()
                # Join the first part of the splitter except the last 10 elements and store it as space_name
                space_name = " ".join(splitter[:-13])
                # Add space_name as the first element of lvb_list
                lvb_list=splitter[-13:]
                lvb_list.insert(0,space_name)
                # Append lvb_list to result
                result.append(lvb_list)
                
            # strore list to dataframe
            psf_df = pd.DataFrame(result) 
            # # Allot lvb_df columns from sim file
            psf_df.columns = ['UNIT', 'LIGHTS', 'TASK_LIGHTS', 'MISC_EQUIP', 'SPACE_EQUIP', 
                                'SPACE_COOLING', 'HEAT_REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY',
                                'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL']

            # Find the index of the first occurrence of "JAN" followed by "FEB"
            start_index = None
            for i in range(len(psf_df) - 1):
                if psf_df['LIGHTS'][i] == 'JAN' and psf_df['LIGHTS'][i+1] == 'FEB':
                    start_index = i
                    break

            # If "JAN" followed by "FEB" found, delete rows from "JAN" to the end
            if start_index is not None:
                psf_df = psf_df.iloc[0:start_index]

            for i in range(len(psf_df)):
                if i < len(psf_df) - 1 and ((psf_df['UNIT'][i] == 'MAX KW' and psf_df['LIGHTS'][i+1] == 'KWH') or (psf_df['UNIT'][i] == 'MAX KW' and psf_df['UNIT'][i+1] == 'KWH') or
                                            (psf_df['UNIT'][i] == 'MAX THERM/HR' and psf_df['LIGHTS'][i+1] == 'THERM') or (psf_df['UNIT'][i] == 'MAX THERM/HR' and psf_df['UNIT'][i+1] == 'THERM') or
                                            (psf_df['UNIT'][i] == 'MAX MBTU/HR' and psf_df['LIGHTS'][i+1] == 'MBTU') or (psf_df['UNIT'][i] == 'MAX MBTU/HR' and psf_df['UNIT'][i+1] == 'MBTU')):
                  
                    new_row = {'UNIT': 'TOTAL', 'LIGHTS': ''}  # New row to be inserted
                    psf_df = pd.concat([psf_df.iloc[:i+1], pd.DataFrame([new_row]), psf_df.iloc[i+1:]]).reset_index(drop=True)

            # This will tell how many meters we have in KW and KWH case(in CSV)
            countMeters = 0
            for i in range(len(psf_df)):
                if psf_df['LIGHTS'][i] == 'JAN':
                    countMeters += 1

            values = []
            for item in psf_type:
                start_index = item.find("for") + len("for")
                end_index = item.find("WEATHER")
                value = item[start_index:end_index].strip()
                values.append(value)
            values1 = list(dict.fromkeys(values))

            values2 = []
            for i in range(countMeters):
                values2.append(values1[i])
            
            # Create an empty list to store the indices where rows are to be inserted
            insert_indices = []

            # Iterate over the DataFrame to find the indices where 'JAN' occurs
            for index, row in psf_df.iterrows():
                if row['LIGHTS'] == 'JAN':
                    insert_indices.append(index)

            # Iterate over the insert indices and insert the corresponding value from values2
            for i, index in enumerate(insert_indices):
                # Calculate the index in values2 to insert
                values2_index = i % len(values2)
                new_row = {'UNIT': values2[values2_index]}
                # Insert the new row before the 'JAN'
                psf_df = pd.concat([psf_df.iloc[:index+i], pd.DataFrame([new_row]), psf_df.iloc[index+i:]]).reset_index(drop=True)
            
            months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
            # Remove rows where 'LIGHTS' column contains month names
            psf_df = psf_df[~psf_df['LIGHTS'].isin(months)]

            # # Reset index after concatenation
            psf_df.reset_index(drop=True, inplace=True)
            if psf_df.loc[len(psf_df) - 3, 'UNIT'] != 'TOTAL':
                # Create a new row with 'TOTAL' in the 'LIGHTS' column
                new_row = pd.DataFrame({'UNIT': ['TOTAL']})
                # Insert the new row at the third last position
                psf_df = pd.concat([psf_df.iloc[:len(psf_df) - 2], new_row, psf_df.iloc[len(psf_df) - 2:]]).reset_index(drop=True)

            # Storing meterings in a list
            keywords_to_filter = ['KW', 'KWH', 'MAX KW', 'TOTAL', 'THERM', 'MAX THERM/HR', 'MBTU', 'MAX MBTU/HR', '']
            filtered_df = psf_df[~psf_df['UNIT'].isin(keywords_to_filter)]
            filtered_df = filtered_df['UNIT']
            filtered_df = filtered_df.loc[filtered_df.index.repeat(3)].reset_index(drop=True)
            # # psf_df['Meterings'] = filtered_df

            total_mask = psf_df['UNIT'] == 'TOTAL'
            if any(total_mask):
                total_indices = psf_df.index[total_mask]
                indices_to_keep = []
                for index in total_indices:
                    indices_to_keep.extend([index, index + 1, index + 2])
                psf_df = psf_df.loc[indices_to_keep].reset_index(drop=True)
            else:
                psf_df = pd.DataFrame()
            psf_df['Meterings'] = filtered_df
            cols = list(psf_df.columns)
            psf_df = psf_df[[cols[-1]] + cols[:-1]]

            total_mask1 = psf_df['UNIT'] == 'TOTAL'
            if any(total_mask1):
                total_indices1 = psf_df.index[total_mask1]
                indices_to_keep1 = []
                for index in total_indices1:
                    indices_to_keep1.extend([index + 1, index + 2])
                psf_df = psf_df.loc[indices_to_keep1].reset_index(drop=True)
            else:
                psf_df = pd.DataFrame()
            
            return psf_df

    except Exception as e:
        print(f"An error occurred: {e}")
        columns = ['UNIT', 'LIGHTS', 'TASK_LIGHTS', 'MISC_EQUIP', 'SPACE_EQUIP', 
                    'SPACE_COOLING', 'HEAT_REJECT', 'PUMPS & AUX', 'VENT FANS', 'REFRIG DISPLAY',
                    'HT PUMP SUPPLEM', 'DOMEST HOT WTR', 'EXT USAGE', 'TOTAL']
        return pd.DataFrame(columns=columns)
