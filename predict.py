#-------------------------------------------------
# Try and predict score on play n 
#-------------------------------------------------

#import modules
import json
import scipy.stats.mstats as ssm
import scipy
import numpy as np
from pylab import * 
from scipy.stats.stats import pearsonr

import ols #download ols.0.2.py from http://www.scipy.org/Cookbook/OLS and rename ols.py


# ------------------------------------------------
# import data from json
print "loading data"
fh=open('data_by_cookie.json')
data=json.load(fh)

# --------------------------------------------
# look at subsample of people who played more than x times   
print "organising data"
big = {k: data[k] for k in data if len(data[k]) > 9} #pythonic

# --------------------------------------------
#calc dict of maximum score for each player(=each key)
maxscore={}
    
for key in big:
    maxscore[key]= max([big[key][attempt][0] for attempt in big[key]])

# sort maximum scores, smallest to biggest
ranked_maxscore=sorted(maxscore[key] for key in maxscore)

#calc percentile ranking for each player (=each key)
prcentiles=[]
for p in range(100):
    prcentiles.append(ssm.scoreatpercentile(ranked_maxscore,p))


#now let's calc variance

av1={}
var1={}
av2={}
var2={}

score1={}
score10={}

first_plays = ['%.5d'%(i+1) for i in range(5)]
second_plays = ['%.5d'%(i+6) for i in range(5)]

#construct vaiables dicts

print "calculating summary stats"
#for each player make two lists, of plays 1-5 (first) and 6-10 (second)
#and calculate summary stats av1,var1 and av2, var2
for key in big:
    attempt=first_plays[0]
    try:
        score1[key]=big[key][attempt][0]
    except KeyError:
        score1[key]=NaN    
    attempt=second_plays[4]
    try:
        score10[key]=big[key][attempt][0]
    except KeyError:
        score10[key]=NaN    
    
    first=[]
    for attempt in first_plays:
        try:
            first.append(big[key][attempt][0])
        except KeyError:
            continue
    av1[key]=scipy.stats.nanmean(first)
    var1[key]=var(first)
    second=[]
    for attempt in second_plays:
        try:
            second.append(big[key][attempt][0])
        except KeyError:
            continue       
    av2[key]=scipy.stats.nanmean(second) 
    var2[key]=var(second)


#make list of summary stats
avs1=[]
vars1=[]
avs2=[]
vars2=[]
scores1=[]
scores10=[]

for key in big:
    avs1.append(av1[key])
    vars1.append(var1[key])
    avs2.append(av2[key])
    vars2.append(var2[key])
    scores1.append(score1[key])
    scores10.append(score10[key])
    
    
#make array
arravs1=np.array(avs1)
arravs2=np.array(avs2)
arrvars1=np.array(vars1)
arrvars2=np.array(vars2)
arrscores1=np.array(scores1)
arrscores10=np.array(scores10)

#mask according to nans in eitherof the paired variable arrays
#print "score 1 predicts average of 5-10"
#pearsonr((arrscores1[~isnan(arrscores1)&~isnan(arravs2)]),(arravs2[~isnan(arrscores1)&~isnan(arravs2)]))
#print "average of 1-5 predicts average of 5-10"
#pearsonr((arravs1[~isnan(arravs1)&~isnan(arravs2)]),(arravs2[~isnan(arravs1)&~isnan(arravs2)]))
#print "variance of 1-5 predicts average of 5-10"
#pearsonr((arrvars1[~isnan(arrvars1)&~isnan(arravs2)]),(arravs2[~isnan(arrvars1)&~isnan(arravs2)]))
#
#print "score 1 predicts score 10"
#pearsonr((arrscores1[~isnan(arrscores1)&~isnan(arrscores10)]),(arrscores10[~isnan(arrscores1)&~isnan(arrscores10)]))
#print "av 1-5 predicts score 10"
#pearsonr((arravs1[~isnan(arravs1)&~isnan(arrscores10)]),(arrscores10[~isnan(arravs1)&~isnan(arrscores10)]))
#print "var 1-5 predicts score 10"
#pearsonr((arrvars1[~isnan(arrvars1)&~isnan(arrscores10)]),(arrscores10[~isnan(arrvars1)&~isnan(arrscores10)]))

#define mask to remove NaNs
mask=~isnan(arrscores10)&~isnan(arravs1)&~isnan(arrvars1)

y=arrscores10[mask]
x=column_stack((arravs1[mask],arrvars1[mask]))
mymodel = ols.ols(y,x,'score10',['av1to5','var1to5'])

mymodel.summary()

#beta weight for x1
numerator=pearsonr(y,x[:,0])[0]-pearsonr(y,x[:,1])[0]*pearsonr(x[:,0],x[:,1])[0]
denominator=1-pearsonr(x[:,0],x[:,1])[0]**2

beta1=numerator/denominator
 
#beta weight for x2 
numerator=pearsonr(y,x[:,1])[0]-pearsonr(y,x[:,0])[0]*pearsonr(x[:,0],x[:,1])[0]
denominator=1-pearsonr(x[:,0],x[:,1])[0]**2

beta2=numerator/denominator

print "Model with av1-5 and var1-5"
print "Beta 1 = %.2f, Beta 2 = %.2f" %(beta1, beta2)

#define mask to remove NaNs
mask=~isnan(arrscores10)&~isnan(arrscores1)&~isnan(arrvars1)

y=arrscores10[mask]
x=column_stack((arrscores1[mask],arrvars1[mask]))
mymodel = ols.ols(y,x,'score10',['score1','var1to5'])

mymodel.summary()

#beta weight for x1
numerator=pearsonr(y,x[:,0])[0]-pearsonr(y,x[:,1])[0]*pearsonr(x[:,0],x[:,1])[0]
denominator=1-pearsonr(x[:,0],x[:,1])[0]**2

beta1=numerator/denominator
 
#beta weight for x2 
numerator=pearsonr(y,x[:,1])[0]-pearsonr(y,x[:,0])[0]*pearsonr(x[:,0],x[:,1])[0]
denominator=1-pearsonr(x[:,0],x[:,1])[0]**2

beta2=numerator/denominator

print "Model with score1 and var1-5"
print "Beta 1 = %.2f, Beta 2 = %.2f" %(beta1, beta2)