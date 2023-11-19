import pandas as pd
import re
import json

df_ip=pd.read_csv('data.csv')

for i in range(len(df_ip)):
    try:
        matches = re.search(r'@[\w.]+', df_ip.loc[i,'post']).group(0)
        df_ip.loc[i,'firtstmatch']=matches
    except:
        pass

df_ip.to_csv('data.csv',index=None)

profiles=[i for i in df_ip.firtstmatch.tolist() if isinstance(i, str) and '@' in i]
profiles=list(set(profiles))
with open("profiletocrawl.json", "w") as fp:
    json.dump(profiles, fp)