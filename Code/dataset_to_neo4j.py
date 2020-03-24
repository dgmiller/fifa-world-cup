import pandas as pd
import utils

df = pd.read_csv('worldcup2019.csv')

with open('to_neo4j.txt','w') as f:

    f.write("CREATE ")

    for t in utils.teams:
        tt = t.lower().replace(" ","")
        group = df[df['team']==t]['group'].iloc[0]
        node = "({0}:Team {{name:'{1}', group:'{2}'}}),\n".format(tt,t,group)
        f.write(node)

    for row in range(len(df)):
        team = df.iloc[row]['team'].lower().replace(" ","")
        game = df.iloc[row]['game']
        opponent = df.iloc[row]['opponent'].lower().replace(" ","")
        versus = "({0}) -[:VERSUS {{game:{1}}}]-> ({2}),\n".format(team,game,opponent)
        f.write(versus)

