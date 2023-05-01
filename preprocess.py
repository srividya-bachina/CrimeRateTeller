import pandas as pd
df_crime = pd.read_csv('Data/report.csv')
cities = []
state_codes = []
for i in range(df_crime.shape[0]): 
    t = df_crime.agency_jurisdiction[i].split(',')
    cities.append(t[0].strip())
    try:
        state_codes.append(t[1].strip())
    except IndexError:
        state_codes.append('Unknown')
    i+=1
    
df_crime['city'] = cities
df_crime['state_codes'] = state_codes
df_crime.drop('agency_jurisdiction',axis=1,inplace=True)
df_crime = df_crime.drop(df_crime[df_crime.state_codes == 'Unknown'].index)
df_crime = df_crime.drop('months_reported', axis=1)
df_crime=df_crime.dropna()
df_crime.to_excel("Data/processed_data.xlsx", index= False)
