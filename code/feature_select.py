import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import OneHotEncoder,LabelEncoder
from scipy import sparse
from sklearn.linear_model import LogisticRegression,SGDClassifier
#from scikitplot.metrics import plot_roc_curve
from sklearn.metrics import roc_auc_score,roc_curve
from sklearn.externals import joblib
import os
from datetime import datetime
import re
from operator import sub,add
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve




def sub_to_other(x):
    x_split=x.split(" ")
    set_tmp=set(map(int,x_split))
    intersec=list(set_tmp & target_set)
    if intersec:
        for target in intersec:
            x_split[x_split.index(str(target))]='other'  
    return ' '.join(x_split)

def plot_cv_train_auc_stdv(x,y):
    plt.figure()
    plt.title("AUC")
    max_value=max(x)
    max_index=x.index(max_value)
    max_value=round(max_value,8)
    print max_value
    show_max=str(max_value)
    mead_sub=map(sub,x,y)
    mead_add=map(add,x,y)
    plt.plot(x,'b--')
    plt.plot(mead_add,'r--')
    plt.plot(mead_sub,'r--')
    plt.plot(max_index,max_value,'gs')
    plt.annotate(show_max,xytext=(max_index,max_value),xy=(max_index,max_value))
    plt.show()
def plot_cv_valid_auc_stdv(x,y):
    plt.figure()
    plt.title("AUC")
    max_value=max(x)
    max_index=x.index(max_value)
    max_value=round(max_value,8)
    print max_value
    show_max=str(max_value)
    mead_sub=map(sub,x,y)
    mead_add=map(add,x,y)
    plt.plot(x,'b--')
    plt.plot(mead_add,'r--')
    plt.plot(mead_sub,'r--')
    plt.plot(max_index,max_value,'gs')
    plt.annotate(show_max,xytext=(max_index,max_value),xy=(max_index,max_value))
    plt.show()
def count_value(x):
    if x=='-1' or x==-1:
        return int(x)
    else:
        split_tmp=x.split(' ')
        return len(split_tmp)

def cv_valid():
    global test_cv_valid
    gbm_valid_data=lgb.Dataset(data_x_valid,y_valid.values.ravel())
    test_cv_valid=lgb.cv(tree_paramas,gbm_valid_data,num_boost_round=1000,metrics='auc',seed=20180512,early_stopping_rounds=100)
    x=test_cv_valid['auc-mean']
    y=test_cv_valid['auc-stdv']
    plot_cv_valid_auc_stdv(x,y)
def cv_train():
    global test_cv_train
    gbm_train_data=lgb.Dataset(data_x_train,y_train.values.ravel())
    test_cv_train=lgb.cv(tree_paramas,gbm_train_data,num_boost_round=1000,metrics='auc',seed=20180512,early_stopping_rounds=100)
    x=test_cv_train['auc-mean']
    y=test_cv_train['auc-stdv']
    plot_cv_train_auc_stdv(x,y)

def corr_2(x):
    return str(x[0])+' '+str(x[1])

run_day=datetime.now().strftime('%m%d%H%M%S')
save_path="/home/heqt/tencent/"+run_day+"/"
if not os.path.exists(save_path):
    os.makedirs(save_path)

#data_fit=pd.read_csv('/home/heqt/tencent/train_all.csv')
#data_test=pd.read_csv('/home/heqt/tencent/test1_all.csv')
#data_fit.loc[data_fit['label']==-1,'label']=0
#data_test.insert(2,'label',-1)
#data_x=pd.concat([data_fit,data_test])
#data_x.to_csv('/home/heqt/tencent/data_all.csv',index=None)
data_x=pd.read_csv('/home/heqt/tencent/data_all.csv')
data_x.fillna('-1',inplace=True)


#fit_model
#one_hot_feature=['lbs','age','carrier','consumptionability','education','gender','house','os','ct','marriagestatus','advertiserid','campaignid', 'creativeid',
#      'adcategoryid', 'creativesize','productid', 'producttype']
one_hot_feature=['producttype','age','creativesize','gender','consumptionability','os','marriagestatus','adcategoryid','carrier','ct','education']
#vector_feature=['appidaction','appidinstall','interest1','interest2','interest3','interest4','interest5','kw1','kw2','kw3','topic1','topic2','topic3']
vector_feature=['interest2']

df_feature_map=pd.DataFrame()
LE=LabelEncoder()
for feature in one_hot_feature:
    try:
        data_x[feature]=LE.fit_transform(data_x[feature].map(np.int))

    except:
        data_x[feature]=LE.fit_transform(data_x[feature])
    #feature important mapping
    finally:
        df_tmp=pd.DataFrame(LE.classes_,columns=['val'])
        df_tmp['feature']='%s' %feature
        df_feature_map=pd.concat([df_feature_map,df_tmp])

print 'LabelEncoder finish'

data_fit=data_x[data_x.label!=-1]
data_y=data_fit.pop('label')
#data_test=data_x[data_x.label==-1]

x_train,x_valid_2,y_train,y_valid= train_test_split(data_fit,data_y,test_size=0.2, random_state=20180505)
x_train,x_valid,y_train,y_valid= train_test_split(x_valid_2,y_valid,test_size=0.3, random_state=20180506)

data_x_train=pd.DataFrame()
data_x_valid=pd.DataFrame()
#data_x_test=pd.DataFrame()
OHE=OneHotEncoder()
for feature in one_hot_feature:
    OHE.fit(x_valid_2[feature].values.reshape(-1,1))
    train_a=OHE.transform(x_train[feature].values.reshape(-1,1))
    valid_a=OHE.transform(x_valid[feature].values.reshape(-1,1))
    #test_a=OHE.transform(data_test[feature].values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #data_x_test=sparse.hstack((data_x_test,test_a))
print 'one_hot finish'
CVec=CountVectorizer(analyzer='word',token_pattern=r'(?u)\b\w+\b',tokenizer =lambda x: x.split(' '))
#CVec=CountVectorizer()
for feature in vector_feature:
    CVec.fit(x_valid_2[feature])
    train_a=CVec.transform(x_train[feature])
    valid_a=CVec.transform(x_valid[feature])
    #test_a=CVec.transform(data_test[feature])
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #data_x_test=sparse.hstack((data_x_test,test_a))
    df_tmp=pd.DataFrame(CVec.get_feature_names(),columns=['val'])
    #feature important mapping
    df_tmp['feature']='%s' %feature
    df_feature_map=pd.concat([df_feature_map,df_tmp])
print ' countvec finish'
df_feature_map.to_csv(save_path+"feature_important_mapping.csv")

#sparse.save_npz(save_path+"data_x_train.npz",data_x_train)
#y_train.to_csv(save_path+"data_y_train.csv",index=None)

#sparse.save_npz(save_path+"data_x_valid.npz",data_x_valid)
#y_valid.to_csv(save_path+"data_y_valid.csv",index=None)

#sparse.save_npz(save_path+"data_x_test.npz",data_x_test)
#result=data_test[['aid','uid']]
#result.to_csv(save_path+"result.csv",index=None)

gbm_clf = lgb.LGBMClassifier(
        boosting_type='gbdt', num_leaves=31, reg_alpha=0.0, reg_lambda=1,
        max_depth=-1, n_estimators=300, objective='binary',
        subsample_freq=1,
        learning_rate=0.02, min_child_weight=50,random_state=20180505,n_jobs=3)

parama={'bin_feature':'appidaction',
        'top_N':100
        }

def aotu_bin(parama):
    global target_set
    file_path='/home/heqt/tencent/countvec/'+str(parama['bin_feature'])+'.csv'
    df_cut=pd.read_csv(file_path,header=None,names=['feature_value','import_value'])
    df_cut_m1=df_cut.loc[df_cut['feature_value']==-1]
    df_cut_nm1=df_cut.loc[df_cut['feature_value']!=-1]
    #prevente top_N less than default
    top_N=min(parama['top_N'],df_cut_nm1.shape[0])
    print top_N
    steps=0
    df_cut_inf=pd.DataFrame(columns=['cut_num','valid_0','valid_1'])
    while top_N>0:
        if steps==0:
            CVec.fit(x_valid_2[parama['bin_feature']])
            train_a=CVec.transform(x_train[parama['bin_feature']])
            valid_a=CVec.transform(x_valid[parama['bin_feature']])
            data_x_train_top=sparse.hstack((data_x_train,train_a))
            data_x_valid_top=sparse.hstack((data_x_valid,valid_a))
        elif steps ==1:
            df_cut_indic=df_cut_nm1.sort_values(by='import_value',ascending=False)[top_N:].feature_value.tolist()
            target_set=set(df_cut_indic)
            x_valid_2[parama['bin_feature']]=x_valid_2[parama['bin_feature']].apply(sub_to_other)
            x_train[parama['bin_feature']]=x_train[parama['bin_feature']].apply(sub_to_other)
            x_valid[parama['bin_feature']]=x_valid[parama['bin_feature']].apply(sub_to_other)
            CVec.fit(x_valid_2[parama['bin_feature']])
            train_a=CVec.transform(x_train[parama['bin_feature']])
            valid_a=CVec.transform(x_valid[parama['bin_feature']])
            data_x_train_top=sparse.hstack((data_x_train,train_a))
            data_x_valid_top=sparse.hstack((data_x_valid,valid_a))
        else:
            df_cut_indic=df_cut_nm1.sort_values(by='import_value',ascending=False).iloc[top_N].feature_value
            parten='\\b'+str(df_cut_indic)+'\\b'
            x_valid_2[parama['bin_feature']]=x_valid_2[parama['bin_feature']].apply(lambda x: re.sub(parten,'other',x))
            x_train[parama['bin_feature']]=x_train[parama['bin_feature']].apply(lambda x: re.sub(parten,'other',x))
            x_valid[parama['bin_feature']]=x_valid[parama['bin_feature']].apply(lambda x: re.sub(parten,'other',x))
            CVec.fit(x_valid_2[parama['bin_feature']])
            train_a=CVec.transform(x_train[parama['bin_feature']])
            valid_a=CVec.transform(x_valid[parama['bin_feature']])
            data_x_train_top=sparse.hstack((data_x_train,train_a))
            data_x_valid_top=sparse.hstack((data_x_valid,valid_a))

        eval_list=[(data_x_train_top,y_train),(data_x_valid_top,y_valid)]
        gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)

        if top_N%10==0:
            print 'gmb_finish','----->',top_N
        #save cut_information
        df_inf_tmp=pd.DataFrame([top_N+1],columns=['cut_num'])
        df_inf_tmp['valid_0']=gbm_clf.best_score_['valid_0']['auc']
        df_inf_tmp['valid_1']=gbm_clf.best_score_['valid_1']['auc']
        df_cut_inf=pd.concat([df_cut_inf,df_inf_tmp])
        steps+=1
        top_N-=1
    df_cut_inf.to_csv(save_path+str(parama['bin_feature'])+"cut_information.csv",index=None)


#after cut,feature ennerging

def sub_to_other(x):
    x_split=x.split(" ")
    set_tmp=set(map(int,x_split))
    intersec=list(set_tmp & target_set)
    if intersec:
        for target in intersec:
            x_split[x_split.index(str(target))]='other'  
    return ' '.join(x_split)


save_path="/home/heqt/tencent/"+"ennerging_feature"+"/"
if not os.path.exists(save_path):
    os.makedirs(save_path)

data_fit=pd.read_csv('/home/heqt/tencent/train_all.csv')
data_fit.loc[data_fit['label']==-1,'label']=0
data_y=data_fit.pop('label')
x_train,x_valid_2,y_train,y_valid= train_test_split(data_fit,data_y,test_size=0.1, random_state=201805)

x_valid_2.insert(2,'label',y_valid)
data_fit=x_valid_2
data_test=pd.read_csv('/home/heqt/tencent/test1_all.csv')
data_test.insert(2,'label',-1)
data_x=pd.concat([data_fit,data_test])
data_x.fillna('-1',inplace=True)
data_x.to_csv(save_path+"data_x_80W.csv",index=None)

one_hot_feature=['lbs','age','carrier','consumptionability','education','gender','house','advertiserid','campaignid', 'creativeid',
       'adcategoryid', 'creativesize','productid', 'producttype']
vector_feature=['appidaction','appidinstall','interest1','interest2','interest3','interest4',
'interest5','kw1','kw2','kw3','topic1','topic2','topic3','os','ct','marriagestatus']
bin_feature=['appidaction','appidinstall','kw1','kw2','kw3','topic1','topic2','topic3']

paramas={
'appidaction':266,
'appidinstall':2875,
'kw1':5690,
'kw2':3698,
'kw3':224,
'topic1':6105,
'topic2':5496,
'topic3':309
}
for feature in bin_feature:
    file_path='/home/heqt/tencent/countvec/'+str(feature)+'.csv'
    df_cut=pd.read_csv(file_path,header=None,names=['feature_value','import_value'])
    df_cut_m1=df_cut.loc[df_cut['feature_value']==-1]
    df_cut_nm1=df_cut.loc[df_cut['feature_value']!=-1]
    top_N=paramas[feature]
    df_cut_indic=df_cut_nm1.sort_values(by='import_value',ascending=False)[top_N:].feature_value.tolist()
    target_set=set(df_cut_indic)
    data_x[feature]=data_x[feature].apply(sub_to_other)
    print feature


data_x.to_csv(save_path+"data_x_cut_80W.csv",index=None)


df_feature_map=pd.DataFrame()
LE=LabelEncoder()
for feature in one_hot_feature:
    try:
        data_x[feature]=LE.fit_transform(data_x[feature].map(np.int))

    except:
        data_x[feature]=LE.fit_transform(data_x[feature])
    #feature important mapping
    finally:
        df_tmp=pd.DataFrame(LE.classes_,columns=['val'])
        df_tmp['feature']='%s' %feature
        df_feature_map=pd.concat([df_feature_map,df_tmp])

print 'LabelEncoder finish'

data_fit=data_x[data_x.label!=-1]
data_y=data_fit.pop('label')
data_test=data_x[data_x.label==-1]

x_train,x_valid,y_train,y_valid= train_test_split(data_fit,data_y,test_size=0.3, random_state=20180506)

data_x_train=pd.DataFrame()
data_x_valid=pd.DataFrame()
data_x_test=pd.DataFrame()
OHE=OneHotEncoder()
for feature in one_hot_feature:
    OHE.fit(data_x[feature].values.reshape(-1,1))
    train_a=OHE.transform(x_train[feature].values.reshape(-1,1))
    valid_a=OHE.transform(x_valid[feature].values.reshape(-1,1))
    test_a=OHE.transform(data_test[feature].values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    data_x_test=sparse.hstack((data_x_test,test_a))
print 'one_hot finish'


CVec=CountVectorizer(analyzer='word',token_pattern=r'(?u)\b\w+\b',tokenizer =lambda x: x.split(' '))
#CVec=CountVectorizer()
for feature in vector_feature:
    CVec.fit(data_x[feature])
    train_a=CVec.transform(x_train[feature])
    valid_a=CVec.transform(x_valid[feature])
    test_a=CVec.transform(data_test[feature])
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    data_x_test=sparse.hstack((data_x_test,test_a))
    df_tmp=pd.DataFrame(CVec.get_feature_names(),columns=['val'])
    #feature important mapping
    df_tmp['feature']='%s' %feature
    df_feature_map=pd.concat([df_feature_map,df_tmp])
print ' countvec finish'
df_feature_map.to_csv(save_path+"feature_important_mapping_cut.csv")

sparse.save_npz(save_path+"data_x_train_cut.npz",data_x_train)
x_train.to_csv(save_path+"x_train_cut.csv",index=None)
y_train.to_csv(save_path+"data_y_train_cut.csv",index=None)

sparse.save_npz(save_path+"data_x_valid_cut.npz",data_x_valid)
x_valid.to_csv(save_path+"x_valid_cut.csv",index=None)
y_valid.to_csv(save_path+"data_y_valid_cut.csv",index=None)

sparse.save_npz(save_path+"data_x_test_cut.npz",data_x_test)
result=data_test[['aid','uid']]
result.to_csv(save_path+"result_cut.csv",index=None)
print 'save_cut_finish'

eval_list=[(data_x_train,y_train),(data_x_valid,y_valid)]

gbm_clf = lgb.LGBMClassifier(
        boosting_type='gbdt', num_leaves=31, reg_alpha=0.0, reg_lambda=1,
        max_depth=-1, n_estimators=1000, objective='binary',
        subsample=0.7, colsample_bytree=0.7, subsample_freq=1,
        learning_rate=0.02, min_child_weight=50,random_state=20180506,n_jobs=7)

gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)
joblib.dump(gbm_clf, '/home/heqt/jupyter_project/model/gbm_clf_cnt_80W.pkl')


#交叉类特征

#house特征的-1取值情况影响不大,"os","ct","marriagestatus"影响不大
#feature_important:580,1920,1165,1305,1715,0,0,0,435
'''
corr_feature=["lbs","age","carrier","education","gender","os","ct","marriagestatus","house"]

for feature in corr_feature:
    corr_feature_path='/home/heqt/tencent/corr_feature/'+str(feature)+'_corr_aid.csv'
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[feature,'aid','label','feacnt','cnt','corr_ctr'])
    df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
    print "df_cor_fea -----> shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=[feature,'aid'])['corr_ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[feature,'aid'])['corr_ctr']
    print "train_a after shape -------->",train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
    print "--------------------"
'''
#统计兴趣的特征,影响不大
intersec_feature=["interest1","interest2","interest3","interest4","interest5"]
for feature in intersec_feature:

    #intersec_feature_path='/home/heqt/tencent/countvec/interest/'+str(feature)+'_count.csv'
    #df_cor_fea=pd.read_csv(intersec_feature_path,header=None,names=['uid',feature,'cnt'])
    #df_cor_fea[feature]=df_cor_fea[feature].map(str)
    #df_cor_fea['cnt']=df_cor_fea['cnt'].map(np.float)
    #print df_cor_fea.shape
    #print df_cor_fea.head(1)
    train_a=x_train[feature].map(count_value)
    valid_a=x_valid[feature].map(count_value)
    print train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
#统计兴趣与广告的交叉特征：1206, 1493,  627,  579, 1324
intersec_feature=["interest1","interest2","interest3","interest4","interest5"]
for feature in intersec_feature:
    intersec_count_path='/home/heqt/tencent/countvec/interest/'+str(feature)+'_count.csv'
    intersec_feature_path='/home/heqt/tencent/corr_feature/interst/'+str(feature)+'_corr_aid.csv'
    df_cnt_fea=pd.read_csv(intersec_count_path,header=None,names=['uid',feature,feature+'cnt'])
    print 'x_train ----> shape',x_train.shape
    x_train=pd.merge(x_train,df_cnt_fea,how='left',on=['uid',feature])
    x_valid=pd.merge(x_valid,df_cnt_fea,how='left',on=['uid',feature])
    print 'x_train after merge ----> shape',x_train.shape
    print 'x_valid after merge ----> shape',x_valid.shape
    df_cor_fea=pd.read_csv(intersec_feature_path,header=None,names=[feature+'cnt','aid','label','feacnt','to_talcnt','corr_ctr'])
    df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','to_talcnt'],axis=1)
    print df_cor_fea.shape
    print df_cor_fea.head(1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=[feature+'cnt','aid'])['corr_ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[feature+'cnt','aid'])['corr_ctr']
    print train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
    print '-----------------------------'
#gender交其他特征, [4,    1,    0,  258,  120,    0] :feature important
var_feature='gender'
corr_feature=["advertiserId","campaignId","creativeSize","adCategoryId","productId","productType"]
for feature in corr_feature:
    corr_feature_path="/home/heqt/tencent/corr_feature/"+var_feature+"/"+var_feature+"_corr_"+str(feature)+".csv"
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[var_feature,feature.lower(),'label','feacnt','cnt','corr_ctr'])
    df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
    print "df_cor_fea ------>shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=[var_feature,feature.lower()])['corr_ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[var_feature,feature.lower()])['corr_ctr']
    print "train_a ---> shape",train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
    print "-----------------------"
#age 交其他广告特征 7,    0,    0,  280,207, 0
var_feature='age'
corr_feature=["advertiserId","campaignId","creativeSize","adCategoryId","productId","productType"]
for feature in corr_feature:
    corr_feature_path="/home/heqt/tencent/corr_feature/"+var_feature+"/"+var_feature+"_corr_"+str(feature)+".csv"
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[var_feature,feature.lower(),'label','feacnt','cnt','corr_ctr'])
    df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
    print "df_cor_fea ------>shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=[var_feature,feature.lower()])['corr_ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[var_feature,feature.lower()])['corr_ctr']
    print "train_a ---> shape",train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
    print "-----------------------"
#其他特征与广告特征交叉,与上面一样，只有"adCategoryId","productId"比较显著,训练模型时不要"lbs","carrier","education","os","ct","marriagestatus","house"
var_features=["gender","age"]
for var_feature in var_features:
    corr_feature=["advertiserId","campaignId","creativeSize","adCategoryId","productId","productType"]
    for feature in corr_feature:
        corr_feature_path="/home/heqt/tencent/corr_feature/"+var_feature+"/"+var_feature+"_corr_"+str(feature)+".csv"
        df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[var_feature,feature.lower(),'label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea ------>shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        train_a=pd.merge(x_train,df_cor_fea,how='left',on=[var_feature,feature.lower()])['corr_ctr']
        valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[var_feature,feature.lower()])['corr_ctr']
        print "train_a ---> shape",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "-----------------------"

#性别*(年龄/学历/消费能力/lbs/兴趣/移动营运商/房子)
source_feature=["gender"]
corr_feature=["lbs","age","carrier","education","consumptionability","house","interest1","interest2","interest3","interest4","interest5"]
for source in source_feature:
    for feature in corr_feature:
        corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(source)+"_"+str(feature)+'_corr_aid.csv'
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature+"cnt",'aid','label','feacnt','cnt','corr_ctr'])
        else:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature,'aid','label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            print "excute interest"
        else:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
        print "train_a after shape -------->",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "--------------------"
#年龄*(学历/消费能力/lbs/兴趣/移动营运商/房子)       
source_feature=["age"]
corr_feature=["lbs","carrier","education","consumptionability","house","interest1","interest2","interest3","interest4","interest5"]
for source in source_feature:
    for feature in corr_feature:
        corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(source)+"_"+str(feature)+'_corr_aid.csv'
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature+"cnt",'aid','label','feacnt','cnt','corr_ctr'])
        else:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature,'aid','label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            print "excute interest"
        else:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
        print "train_a after shape -------->",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "--------------------"
#lbs X(学历/消费能力/兴趣/移动营运商/房子)
source_feature=["lbs"]
corr_feature=["carrier","education","consumptionability","house","interest1","interest2","interest3","interest4","interest5"]
for source in source_feature:
    for feature in corr_feature:
        corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(source)+"_"+str(feature)+'_corr_aid.csv'
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature+"cnt",'aid','label','feacnt','cnt','corr_ctr'])
        else:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature,'aid','label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            print "excute interest"
        else:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
        print "train_a after shape -------->",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "--------------------"
#移动营运商 X(学历/消费能力/兴趣/房子)
source_feature=["carrier"]
corr_feature=["education","consumptionability","house","interest1","interest2","interest3","interest4","interest5"]
for source in source_feature:
    for feature in corr_feature:
        corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(source)+"_"+str(feature)+'_corr_aid.csv'
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature+"cnt",'aid','label','feacnt','cnt','corr_ctr'])
        else:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature,'aid','label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            print "excute interest"
        else:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
        print "train_a after shape -------->",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "--------------------"
#消费能力 X(学历/兴趣/房子)
source_feature=["consumptionability"]
corr_feature=["education","house","interest1","interest2","interest3","interest4","interest5"]
for source in source_feature:
    for feature in corr_feature:
        corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(source)+"_"+str(feature)+'_corr_aid.csv'
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature+"cnt",'aid','label','feacnt','cnt','corr_ctr'])
        else:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature,'aid','label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            print "excute interest"
        else:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
        print "train_a after shape -------->",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "--------------------"

#学历 X(兴趣/房子)
source_feature=["education"]
corr_feature=["house","interest1","interest2","interest3","interest4","interest5"]
for source in source_feature:
    for feature in corr_feature:
        corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(source)+"_"+str(feature)+'_corr_aid.csv'
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature+"cnt",'aid','label','feacnt','cnt','corr_ctr'])
        else:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature,'aid','label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            print "excute interest"
        else:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
        print "train_a after shape -------->",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "--------------------"

#房子 X(兴趣)
source_feature=["house"]
corr_feature=["interest1","interest2","interest3","interest4","interest5"]
for source in source_feature:
    for feature in corr_feature:
        corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(source)+"_"+str(feature)+'_corr_aid.csv'
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature+"cnt",'aid','label','feacnt','cnt','corr_ctr'])
        else:
            df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[source,feature,'aid','label','feacnt','cnt','corr_ctr'])
        df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']*100.0
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        df_cor_fea=df_cor_fea.drop(labels=['label','feacnt','cnt'],axis=1)
        if feature in ["interest1","interest2","interest3","interest4","interest5"]:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature+"cnt",'aid'])['corr_ctr']
            print "excute interest"
        else:
            train_a=pd.merge(x_train,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
            valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[source,feature,'aid'])['corr_ctr']
        print "train_a after shape -------->",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
        #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
        #feature important mapping
        #df_tmp['feature']='%s' %feature
        #df_feature_map=pd.concat([df_feature_map,df_tmp])
        print feature
        print "--------------------"


<<<<<<< Updated upstream
#统计app个数

app_feature=["appidinstall","appidaction"]
for feature in app_feature:
    #intersec_feature_path='/home/heqt/tencent/countvec/interest/'+str(feature)+'_count.csv'
    #df_cor_fea=pd.read_csv(intersec_feature_path,header=None,names=['uid',feature,'cnt'])
    #df_cor_fea[feature]=df_cor_fea[feature].map(str)
    #df_cor_fea['cnt']=df_cor_fea['cnt'].map(np.float)
    #print df_cor_fea.shape
    #print df_cor_fea.head(1)
    train_a=x_train[feature].map(count_value)
    valid_a=x_valid[feature].map(count_value)
    print train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
##2交叉，采用ageXgender的形式
def corr_2(x):
    return str(x[0])+' '+str(x[1])


corr_feature=["lbs","age","carrier","education","gender","os","ct","marriagestatus","house"]
for i in range(len(corr_feature)-1):
    for j in range(i+1,len(corr_feature)):
        var_name=corr_feature[i]+'X'+corr_feature[j]
        print var_name
        x_train[var_name]=x_train[[corr_feature[i],corr_feature[j]]].apply(corr_2,axis=1)
        x_valid[var_name]=x_valid[[corr_feature[i],corr_feature[j]]].apply(corr_2,axis=1)
        print x_train[var_name][0]
        print x_valid[var_name][0]
one_hot_feature=[]
corr_feature=["lbs","age","carrier","education","gender","os","ct","marriagestatus","house"]
for i in range(len(corr_feature)-1):
    for j in range(1,len(corr_feature)):
        var_name=corr_feature[i]+'X'+corr_feature[j]
        one_hot_feature.append(var_name)
x_train['qubie']=1
x_valid['qubie']=0
data_x=pd.concat([x_train,x_valid])
LE=LabelEncoder()
for feature in one_hot_feature:
    try:
        data_x[feature]=LE.fit_transform(data_x[feature].map(np.int))
    except:
        data_x[feature]=LE.fit_transform(data_x[feature])
print "LabelEncoder finish"
x_train=data_x[data_x.qubie==1]
x_valid=data_x[data_x.qubie==0]
data_x.pop('qubie'),x_train.pop('qubie'),x_valid.pop('qubie')


OHE=OneHotEncoder()
data_x_train_1=data_x_train.copy()
data_x_valid_1=data_x_valid.copy()
df_AUC=pd.DataFrame(columns=['var_name','AUC_0','AUC_1'])
for feature in one_hot_feature:
    OHE.fit(data_x[feature].values.reshape(-1,1))
    train_a=OHE.transform(x_train[feature].values.reshape(-1,1))
    valid_a=OHE.transform(x_valid[feature].values.reshape(-1,1))
    print 'train_a ----> one hot--->shape',train_a.shape
    data_x_train=sparse.hstack((data_x_train_1,train_a))
    data_x_valid=sparse.hstack((data_x_valid_1,valid_a))
    eval_list=[(data_x_train,y_train),(data_x_valid,y_valid)]
    gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)

    df_tmp=pd.DataFrame([feature],columns=['var_name'])
    df_tmp['AUC_0']=gbm_clf.best_score_["valid_0"]["auc"]
    df_tmp['AUC_1']=gbm_clf.best_score_["valid_1"]["auc"]
    df_AUC=pd.concat([df_AUC,df_tmp])
    print "data_x_train ---->shape",data_x_train.shape
    print feature
    print "----------------"

#单个appidaction与广告相交：分数没提高，但是重要性有943
sigle_interest=['appidaction']
for feature in sigle_interest:
    intersec_feature_path='/home/heqt/tencent/corr_feature/single_corr/for_smoot/smooted_ctr/'+feature+'_smooted.csv'
    df_cor_fea=pd.read_csv(intersec_feature_path,header=None,skiprows=1,names=['uid','aid',feature+'ctr'])
    print df_cor_fea.shape
    print df_cor_fea.head(1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature+'ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature+'ctr']
    print 'train_a ---> shape',train_a.shape
    print 'train_a --->head(1)',train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
sigle_interest=['interest3','interest4','interest5']
for feature in sigle_interest:
    intersec_feature_path='/home/heqt/tencent/corr_feature/single_corr/'+feature+'_single.csv'
    df_cor_fea=pd.read_csv(intersec_feature_path,header=None,names=['uid','aid',feature+'ctr'])
    print df_cor_fea.shape
    print df_cor_fea.head(1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature+'ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature+'ctr']
    train_a=train_a.map(np.float)
    valid_a=valid_a.map(np.float)
    print 'train_a ---> shape',train_a.shape
    print 'train_a --->head(1)',train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    df_tmp=pd.DataFrame([feature],columns=['var_name'])
    df_tmp['AUC_0']=gbm_clf.best_score_["valid_0"]["auc"]
    df_tmp['AUC_1']=gbm_clf.best_score_["valid_1"]["auc"]
    df_AUC=pd.concat([df_AUC,df_tmp])
    print feature

#appidaction 尝试贝叶斯平滑：效果不是很大，但是其他的效果很大
#这里使用了data_x_train_1，想看每个的效果
df_AUC=pd.DataFrame(columns=['var_name','AUC_0','AUC_1'])
x_train['uid']=x_train['uid'].map(np.int64)
x_valid['aid']=x_valid['aid'].map(np.int64)
sigle_interest=["appidaction","appidinstall","interest1","interest2","interest3","interest4","interest5","kw1",
"kw2","kw3","topic1","topic2","topic3"]
for feature in sigle_interest:
    intersec_feature_path='/home/heqt/tencent/corr_feature/single_corr/for_smoot/smooted_ctr/'+feature+'_uid_aid_ctr.csv'
    df_cor_fea=pd.read_csv(intersec_feature_path,header=None,names=['uid','aid',feature+'ctr'],dtype={0: np.int64,1: np.int64})
    #because smoe label=-1 will cause null,need df_cor_count to fill null
    print "df_cor_fea---->shape",df_cor_fea.shape
    #print df_cor_fea.head(1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature+'ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature+'ctr']
    print 'train_a ---> shape',train_a.shape
    #print 'train_a --->head(1)',train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train_1=sparse.hstack((data_x_train,train_a))
    data_x_valid_1=sparse.hstack((data_x_valid,valid_a))
    eval_list=[(data_x_train_1,y_train),(data_x_valid_1,y_valid)]
    gbm_clf.fit(data_x_train_1,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)

    df_tmp=pd.DataFrame([feature],columns=['var_name'])
    df_tmp['AUC_0']=gbm_clf.best_score_["valid_0"]["auc"]
    df_tmp['AUC_1']=gbm_clf.best_score_["valid_1"]["auc"]
    df_AUC=pd.concat([df_AUC,df_tmp])
    print feature
'''
#尝试改进后的广告交叉特征效果，就是把0值给补上了,这里是在去除缺失率高的变量下跑的全量数据
#array([  11,    0, 1302,  371,  582,  713, 1032,    0,    0,    0,  244])

corr_feature=["lbs","age","carrier","education","consumptionability","gender","os","ct","marriagestatus","house"]

for feature in corr_feature:
    corr_feature_path='/home/heqt/tencent/corr_feature/repair_aid/'+str(feature)+'_corr_aid_ctr_nosmoot.csv'
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[feature,'aid','corr_ctr'])
    df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']
    print "df_cor_fea -----> shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=[feature,'aid'])['corr_ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[feature,'aid'])['corr_ctr']
    print "train_a after shape -------->",train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
    print "--------------------"
#尝试改进后的加上贝叶斯平滑广告交叉特征效果，就是把0值给补上了并且加了贝叶斯平滑,效果比上面好,但是与之前没匹配上直接补0的效果一样
#这里是在去除缺失率高的变量下跑的全量数据
#array([    11, 1280,  377,  563,  750, 1033,    0,    0,    0,  245])
#以前的效果,没补0,直接null.array([  19, 1263,  369,  564,  743, 1055,    0,    0,    0,  242])

#这个是在没有去除缺失率高的数据集上跑全量:
#array([ 720, 1878, 1063, 1264, 1430, 1599,    0,    0,    0,  432])
corr_feature=["lbs","age","carrier","education","consumptionability","gender","os","ct","marriagestatus","house"]

for feature in corr_feature:
    corr_feature_path='/home/heqt/tencent/corr_feature/repair_aid/'+str(feature)+'_ctr_smoot.csv'
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[feature,'aid',feature+'dianji',feature+'baoguang','corr_ctr'])
    df_cor_fea['corr_ctr']=df_cor_fea['corr_ctr']
    print "df_cor_fea -----> shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=[feature,'aid'])['corr_ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[feature,'aid'])['corr_ctr']
    print "train_a after shape -------->",train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
    print "--------------------"
'''
#上面出错了,忽略了labelencode()后数据改变了,重新跑1次
#array([1574, 1345,  594,  847, 1007, 1067,  668, 1143,  924,  547])
corr_feature=["lbs","age","carrier","education","consumptionability","gender","os","ct","marriagestatus","house"]

for feature in corr_feature:
    corr_feature_path='/home/heqt/tencent/corr_feature/repair_aid/'+str(feature)+'_ctr_smoot_onehot.csv'
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=['uid','aid','corr_ctr'])
    print "df_cor_fea -----> shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])['corr_ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])['corr_ctr']
    print "train_a after shape -------->",train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
    print "--------------------"
#aid,lbs,campaignid,producttype的历史点击率,不同广告在不同人群的投放量,left jion有可能会产生null,如果做逻辑回归,需要补0
#array([534, 493,   4,   0,   0])
"""
corr_feature=["aid_toufang","aid","lbs","campaignid","producttype"]
for feature in corr_feature:
    corr_feature_path='/home/heqt/tencent/corr_feature/'+str(feature)+'_uid_count.csv'
    if feature=="aid_toufang":
        feature="aid"
        df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[feature,'corr_ctr'])
    else:
        df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[feature,'label',feature+'dianji',feature+'baoguang','corr_ctr'])
    print "df_cor_fea -----> shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=[feature])['corr_ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[feature])['corr_ctr']
    print "train_a after shape -------->",train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
    print "--------------------"
"""
#aid,lbs,campaignid,producttype的历史点击率,one_hot修改后的
#array([723, 461, 690, 425,  52])

#corr_feature=["aid_toufang","aid","lbs","campaignid","producttype"]
corr_feature=["aid_toufang","aid"]
x_train['uid']=x_train['uid'].map(np.int64)
x_train['aid']=x_train['aid'].map(np.int64)
x_valid['uid']=x_valid['uid'].map(np.int64)
x_valid['aid']=x_valid['aid'].map(np.int64)
for feature in corr_feature:
    corr_feature_path='/home/heqt/tencent/corr_feature/'+str(feature)+'_uid_count_onehot.csv'
    if feature=="aid_toufang":
        feature="aid"
        df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=[feature,'corr_ctr'],dtype={0: np.int64})
        train_a=pd.merge(x_train,df_cor_fea,how='left',on=[feature])['corr_ctr']
        valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=[feature])['corr_ctr']
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
    else:
        df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=['uid','aid','corr_ctr'],dtype={0: np.int64,1: np.int64})
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        train_a=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])['corr_ctr']
        valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])['corr_ctr']
        print "train_a after shape -------->",train_a.shape
        print train_a.head(1)
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
    print "--------------------"



#尝试组合形式
#有效的有,age_aid,education_aid,consumptionability_aid,gender_aid,house_aid

corr_feature=["lbs","age","carrier","education","consumptionability","gender","os","ct","marriagestatus","house"]
x_train['uid']=x_train['uid'].map(np.int64)
x_train['aid']=x_train['aid'].map(np.int64)
x_valid['uid']=x_valid['uid'].map(np.int64)
x_valid['aid']=x_valid['aid'].map(np.int64)
for feature in corr_feature:
    corr_feature_path='/home/heqt/tencent/corr_feature/'+str(feature)+'_aid_zuhe.csv'
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=['uid','aid',feature+'_aid'],dtype={0: np.int64,1: np.int64})
    print "df_cor_fea -----> shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    x_train[feature+'_aid']=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature+'_aid']
    x_valid[feature+'_aid']=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature+'_aid']
x_train['qubie']=1
x_valid['qubie']=0
data_x=pd.concat([x_train,x_valid])
LE=LabelEncoder()
for feature in corr_feature:
    try:
        data_x[feature+'_aid']=LE.fit_transform(data_x[feature+'_aid'].map(np.int))
    except:
        data_x[feature+'_aid']=LE.fit_transform(data_x[feature+'_aid'])
print "LabelEncoder finish"
x_train=data_x[data_x.qubie==1]
x_valid=data_x[data_x.qubie==0]
data_x.pop('qubie'),x_train.pop('qubie'),x_valid.pop('qubie')
OHE=OneHotEncoder()
data_x_train_1=data_x_train.copy()
data_x_valid_1=data_x_valid.copy()
df_AUC=pd.DataFrame(columns=['var_name','AUC_0','AUC_1'])
for feature in corr_feature:
    OHE.fit(data_x[feature+'_aid'].values.reshape(-1,1))
    train_a=OHE.transform(x_train[feature+'_aid'].values.reshape(-1,1))
    valid_a=OHE.transform(x_valid[feature+'_aid'].values.reshape(-1,1))
    print 'train_a ----> one hot--->shape',train_a.shape
    data_x_train=sparse.hstack((data_x_train_1,train_a))
    data_x_valid=sparse.hstack((data_x_valid_1,valid_a))
    eval_list=[(data_x_train,y_train),(data_x_valid,y_valid)]
    gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)

    df_tmp=pd.DataFrame([feature+'_aid'],columns=['var_name'])
    df_tmp['AUC_0']=gbm_clf.best_score_["valid_0"]["auc"]
    df_tmp['AUC_1']=gbm_clf.best_score_["valid_1"]["auc"]
    df_AUC=pd.concat([df_AUC,df_tmp])
    print "data_x_train ---->shape",data_x_train.shape
    print feature
    print "----------------"

#把上面有的逐个合并,然后再看效果
#有效的有,age_aid,education_aid,consumptionability_aid,gender_aid,house_aid
corr_feature=["age","gender","consumptionability","house","education"]
x_train['uid']=x_train['uid'].map(np.int64)
x_valid['aid']=x_valid['aid'].map(np.int64)
for feature in corr_feature:
    corr_feature_path='/home/heqt/tencent/corr_feature/'+str(feature)+'_aid_zuhe.csv'
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=['uid','aid',feature+'_aid'],dtype={0: np.int64,1: np.int64})
    print "df_cor_fea -----> shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    x_train[feature+'_aid']=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature+'_aid']
    x_valid[feature+'_aid']=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature+'_aid']
x_train['qubie']=1
x_valid['qubie']=0
data_x=pd.concat([x_train,x_valid])
LE=LabelEncoder()
for feature in corr_feature:
    try:
        data_x[feature+'_aid']=LE.fit_transform(data_x[feature+'_aid'].map(np.int))
    except:
        data_x[feature+'_aid']=LE.fit_transform(data_x[feature+'_aid'])
print "LabelEncoder finish"
x_train=data_x[data_x.qubie==1]
x_valid=data_x[data_x.qubie==0]
data_x.pop('qubie'),x_train.pop('qubie'),x_valid.pop('qubie')
OHE=OneHotEncoder()
df_AUC=pd.DataFrame(columns=['var_name','AUC_0','AUC_1'])
for feature in corr_feature:
    OHE.fit(data_x[feature+'_aid'].values.reshape(-1,1))
    train_a=OHE.transform(x_train[feature+'_aid'].values.reshape(-1,1))
    valid_a=OHE.transform(x_valid[feature+'_aid'].values.reshape(-1,1))
    print 'train_a ----> one hot--->shape',train_a.shape
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    eval_list=[(data_x_train,y_train),(data_x_valid,y_valid)]
    gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)

    df_tmp=pd.DataFrame([feature+'_aid'],columns=['var_name'])
    df_tmp['AUC_0']=gbm_clf.best_score_["valid_0"]["auc"]
    df_tmp['AUC_1']=gbm_clf.best_score_["valid_1"]["auc"]
    df_AUC=pd.concat([df_AUC,df_tmp])
    print "data_x_train ---->shape",data_x_train.shape
    print feature
    print "----------------"


#组合统计量
corr_feature=["age","gender","campaignid"]
x_train['uid']=x_train['uid'].map(np.int64)
x_train['aid']=x_train['aid'].map(np.int64)
x_valid['uid']=x_valid['uid'].map(np.int64)
x_valid['aid']=x_valid['aid'].map(np.int64)
for feature in corr_feature:
    corr_feature_path='/home/heqt/tencent/corr_feature/'+str(feature)+'_aid_count.csv'
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=['uid','aid','corr_ctr'],dtype={0: np.int64,1: np.int64})
    print "df_cor_fea -----> shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])['corr_ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])['corr_ctr']
    print "train_a after shape -------->",train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
    print "--------------------"
#尝试用用户特征组合广告的其他特征

corr_feature=["age","gender","house","lbs","carrier","education","consumptionability","os","ct","marriagestatus"]
aid_feature=["advertiserid","campaignid","creativesize","adcategoryid","productid","producttype"]
#为了labelencoder用的list
Encoder_list=[]
x_train['uid']=x_train['uid'].map(np.int64)
x_train['aid']=x_train['aid'].map(np.int64)
x_valid['uid']=x_valid['uid'].map(np.int64)
x_valid['aid']=x_valid['aid'].map(np.int64)
for feature in corr_feature:
    for adfeature in aid_feature:
        if feature not in ["os","ct","marriagestatus"]:
            corr_feature_path='/home/heqt/tencent/corr_feature/'+str(feature)+'/'+str(feature)+'_'+str(adfeature)+'_zuhe.csv'
        else :
            corr_feature_path='/home/heqt/tencent/corr_feature/'+str(feature)+'/'+str(feature)+'_'+str(adfeature)+'_aid_zuhe.csv'
        df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=['uid','aid',feature+'_'+adfeature],dtype={0: np.int64,1: np.int64})
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        x_train[feature+'_'+adfeature]=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature+'_'+adfeature]
        x_valid[feature+'_'+adfeature]=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature+'_'+adfeature]
        Encoder_list.append(feature+'_'+adfeature)
x_train['qubie']=1
x_valid['qubie']=0
data_x=pd.concat([x_train,x_valid])
LE=LabelEncoder()
for feature in Encoder_list:
    try:
        data_x[feature]=LE.fit_transform(data_x[feature].map(np.int))
    except:
        data_x[feature]=LE.fit_transform(data_x[feature])
print "LabelEncoder finish"
x_train=data_x[data_x.qubie==1]
x_valid=data_x[data_x.qubie==0]
data_x.pop('qubie'),x_train.pop('qubie'),x_valid.pop('qubie')
OHE=OneHotEncoder()
data_x_train_1=data_x_train.copy()
data_x_valid_1=data_x_valid.copy()
df_AUC=pd.DataFrame(columns=['var_name','AUC_0','AUC_1'])
for feature in Encoder_list:
    OHE.fit(data_x[feature].values.reshape(-1,1))
    train_a=OHE.transform(x_train[feature].values.reshape(-1,1))
    valid_a=OHE.transform(x_valid[feature].values.reshape(-1,1))
    print 'train_a ----> one hot--->shape',train_a.shape
    data_x_train=sparse.hstack((data_x_train_1,train_a))
    data_x_valid=sparse.hstack((data_x_valid_1,valid_a))
    eval_list=[(data_x_train,y_train),(data_x_valid,y_valid)]
    gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)

    df_tmp=pd.DataFrame([feature],columns=['var_name'])
    df_tmp['AUC_0']=gbm_clf.best_score_["valid_0"]["auc"]
    df_tmp['AUC_1']=gbm_clf.best_score_["valid_1"]["auc"]
    df_AUC=pd.concat([df_AUC,df_tmp])
    print "data_x_train ---->shape",data_x_train.shape
    print feature
    print "----------------"

#看上面挑选出来的特征的组合效果

corr_feature=["marriagestatus","age","consumptionability"]
aid_feature=["creativesize"]
#为了labelencoder用的list
Encoder_list=[]
x_train['uid']=x_train['uid'].map(np.int64)
x_train['aid']=x_train['aid'].map(np.int64)
x_valid['uid']=x_valid['uid'].map(np.int64)
x_valid['aid']=x_valid['aid'].map(np.int64)
for feature in corr_feature:
    for adfeature in aid_feature:
        if feature not in ["os","ct","marriagestatus"]:
            corr_feature_path='/home/heqt/tencent/corr_feature/'+str(feature)+'/'+str(feature)+'_'+str(adfeature)+'_zuhe.csv'
        else :
            corr_feature_path='/home/heqt/tencent/corr_feature/'+str(feature)+'/'+str(feature)+'_'+str(adfeature)+'_aid_zuhe.csv'
        df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=['uid','aid',feature+'_'+adfeature],dtype={0: np.int64,1: np.int64})
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        x_train[feature+'_'+adfeature]=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature+'_'+adfeature]
        x_valid[feature+'_'+adfeature]=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature+'_'+adfeature]
        Encoder_list.append(feature+'_'+adfeature)
x_train['qubie']=1
x_valid['qubie']=0
data_x=pd.concat([x_train,x_valid])
LE=LabelEncoder()
for feature in Encoder_list:
    try:
        data_x[feature]=LE.fit_transform(data_x[feature].map(np.int))
    except:
        data_x[feature]=LE.fit_transform(data_x[feature])
print "LabelEncoder finish"
x_train=data_x[data_x.qubie==1]
x_valid=data_x[data_x.qubie==0]
data_x.pop('qubie'),x_train.pop('qubie'),x_valid.pop('qubie')
OHE=OneHotEncoder()
#data_x_train_1=data_x_train.copy()
#data_x_valid_1=data_x_valid.copy()
df_AUC=pd.DataFrame(columns=['var_name','AUC_0','AUC_1'])
for feature in Encoder_list:
    OHE.fit(data_x[feature].values.reshape(-1,1))
    train_a=OHE.transform(x_train[feature].values.reshape(-1,1))
    valid_a=OHE.transform(x_valid[feature].values.reshape(-1,1))
    print 'train_a ----> one hot--->shape',train_a.shape
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    eval_list=[(data_x_train,y_train),(data_x_valid,y_valid)]
    gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)

    df_tmp=pd.DataFrame([feature],columns=['var_name'])
    df_tmp['AUC_0']=gbm_clf.best_score_["valid_0"]["auc"]
    df_tmp['AUC_1']=gbm_clf.best_score_["valid_1"]["auc"]
    df_AUC=pd.concat([df_AUC,df_tmp])
    print "data_x_train ---->shape",data_x_train.shape
    print feature
    print "----------------"
#单独跑age与adcategoryid
corr_feature=["age"]
aid_feature=["adcategoryid"]
#为了labelencoder用的list
Encoder_list=[]
x_train['uid']=x_train['uid'].map(np.int64)
x_train['aid']=x_train['aid'].map(np.int64)
x_valid['uid']=x_valid['uid'].map(np.int64)
x_valid['aid']=x_valid['aid'].map(np.int64)
for feature in corr_feature:
    for adfeature in aid_feature:
        if feature not in ["os","ct","marriagestatus"]:
            corr_feature_path='/home/heqt/tencent/corr_feature/'+str(feature)+'/'+str(feature)+'_'+str(adfeature)+'_zuhe.csv'
        else :
            corr_feature_path='/home/heqt/tencent/corr_feature/'+str(feature)+'/'+str(feature)+'_'+str(adfeature)+'_aid_zuhe.csv'
        df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=['uid','aid',feature+'_'+adfeature],dtype={0: np.int64,1: np.int64})
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        x_train[feature+'_'+adfeature]=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature+'_'+adfeature]
        x_valid[feature+'_'+adfeature]=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature+'_'+adfeature]
        Encoder_list.append(feature+'_'+adfeature)
x_train['qubie']=1
x_valid['qubie']=0
data_x=pd.concat([x_train,x_valid])
LE=LabelEncoder()
for feature in Encoder_list:
    try:
        data_x[feature]=LE.fit_transform(data_x[feature].map(np.int))
    except:
        data_x[feature]=LE.fit_transform(data_x[feature])
print "LabelEncoder finish"
x_train=data_x[data_x.qubie==1]
x_valid=data_x[data_x.qubie==0]
data_x.pop('qubie'),x_train.pop('qubie'),x_valid.pop('qubie')
OHE=OneHotEncoder()
#data_x_train_1=data_x_train.copy()
#data_x_valid_1=data_x_valid.copy()
df_AUC=pd.DataFrame(columns=['var_name','AUC_0','AUC_1'])
for feature in Encoder_list:
    OHE.fit(data_x[feature].values.reshape(-1,1))
    train_a=OHE.transform(x_train[feature].values.reshape(-1,1))
    valid_a=OHE.transform(x_valid[feature].values.reshape(-1,1))
    print 'train_a ----> one hot--->shape',train_a.shape
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    eval_list=[(data_x_train,y_train),(data_x_valid,y_valid)]
    gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)

    df_tmp=pd.DataFrame([feature],columns=['var_name'])
    df_tmp['AUC_0']=gbm_clf.best_score_["valid_0"]["auc"]
    df_tmp['AUC_1']=gbm_clf.best_score_["valid_1"]["auc"]
    df_AUC=pd.concat([df_AUC,df_tmp])
    print "data_x_train ---->shape",data_x_train.shape
    print feature
    print "----------------"





#尝试之前做的2组合交叉
#挑选了下面这些
"""
lbs_age
os_gender
carrier_education
carrier_gender
carrier_house
carrier_age
ct_education
ct_house
marriagestatus_house
consumptionability_age
consumptionability_gender
consumptionability_house
consumptionability_education


"""
corr_feature=['lbs_age','os_gender','carrier_education','carrier_gender','carrier_house','carrier_age','ct_education','ct_house',
'marriagestatus_house','marriagestatus_house','consumptionability_age','consumptionability_house','consumptionability_education']
#为了labelencoder用的list
x_train['uid']=x_train['uid'].map(np.int64)
x_train['aid']=x_train['aid'].map(np.int64)
x_valid['uid']=x_valid['uid'].map(np.int64)
x_valid['aid']=x_valid['aid'].map(np.int64)
for feature in corr_feature:
    corr_feature_path='/home/heqt/tencent/corr_feature/'+str(feature)+'_zuhe.csv'
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=['uid','aid',feature],dtype={0: np.int64,1: np.int64})
    print "df_cor_fea -----> shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    x_train[feature]=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature]
    x_valid[feature]=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature]
x_train['qubie']=1
x_valid['qubie']=0
data_x=pd.concat([x_train,x_valid])
LE=LabelEncoder()
for feature in corr_feature:
    try:
        data_x[feature]=LE.fit_transform(data_x[feature].map(np.int))
    except:
        data_x[feature]=LE.fit_transform(data_x[feature])
print "LabelEncoder finish"
x_train=data_x[data_x.qubie==1]
x_valid=data_x[data_x.qubie==0]
data_x.pop('qubie'),x_train.pop('qubie'),x_valid.pop('qubie')
OHE=OneHotEncoder()
#data_x_train_1=data_x_train.copy()
#data_x_valid_1=data_x_valid.copy()
df_AUC=pd.DataFrame(columns=['var_name','AUC_0','AUC_1'])
for feature in corr_feature:
    OHE.fit(data_x[feature].values.reshape(-1,1))
    train_a=OHE.transform(x_train[feature].values.reshape(-1,1))
    valid_a=OHE.transform(x_valid[feature].values.reshape(-1,1))
    print 'train_a ----> one hot--->shape',train_a.shape
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    eval_list=[(data_x_train,y_train),(data_x_valid,y_valid)]
    gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)

    df_tmp=pd.DataFrame([feature],columns=['var_name'])
    df_tmp['AUC_0']=gbm_clf.best_score_["valid_0"]["auc"]
    df_tmp['AUC_1']=gbm_clf.best_score_["valid_1"]["auc"]
    df_AUC=pd.concat([df_AUC,df_tmp])
    print "data_x_train ---->shape",data_x_train.shape
    print feature
    print "----------------"

#3交叉组合



corr_feature=["age_gender_aid","age_consumptionability_aid","age_education_aid","gender_house_aid","gender_consumptionability_aid",
             "gender_marriagestatus_aid","gender_education_aid","house_consumptionability_aid",
             "house_marriagestatus_aid","consumptionability_marriagestatus_aid",
             "consumptionability_education_aid","education_marriagestatus_aid"]
#为了labelencoder用的list
x_train['uid']=x_train['uid'].map(np.int64)
x_train['aid']=x_train['aid'].map(np.int64)
x_valid['uid']=x_valid['uid'].map(np.int64)
x_valid['aid']=x_valid['aid'].map(np.int64)
for feature in corr_feature:
    corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(feature)+'_zuhe.csv'
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=['uid','aid',feature],dtype={0: np.int64,1: np.int64})
    print "df_cor_fea -----> shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    x_train[feature]=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature]
    x_valid[feature]=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature]
x_train['qubie']=1
x_valid['qubie']=0
data_x=pd.concat([x_train,x_valid])
LE=LabelEncoder()
for feature in corr_feature:
    try:
        data_x[feature]=LE.fit_transform(data_x[feature].map(np.int))
    except:
        data_x[feature]=LE.fit_transform(data_x[feature])
print "LabelEncoder finish"
x_train=data_x[data_x.qubie==1]
x_valid=data_x[data_x.qubie==0]
data_x.pop('qubie'),x_train.pop('qubie'),x_valid.pop('qubie')
OHE=OneHotEncoder()
#data_x_train_1=data_x_train.copy()
#data_x_valid_1=data_x_valid.copy()
df_AUC=pd.DataFrame(columns=['var_name','AUC_0','AUC_1'])
for feature in corr_feature:
    OHE.fit(data_x[feature].values.reshape(-1,1))
    train_a=OHE.transform(x_train[feature].values.reshape(-1,1))
    valid_a=OHE.transform(x_valid[feature].values.reshape(-1,1))
    print 'train_a ----> one hot--->shape',train_a.shape
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    eval_list=[(data_x_train,y_train),(data_x_valid,y_valid)]
    gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)

    df_tmp=pd.DataFrame([feature],columns=['var_name'])
    df_tmp['AUC_0']=gbm_clf.best_score_["valid_0"]["auc"]
    df_tmp['AUC_1']=gbm_clf.best_score_["valid_1"]["auc"]
    df_AUC=pd.concat([df_AUC,df_tmp])
    print "data_x_train ---->shape",data_x_train.shape
    print feature
    print "----------------"











#尝试age与广告其他特征的3交叉效果:

corr_feature=["age_gender_creativesize","age_consumptionability_creativesize","age_education_creativesize",
              "age_gender_adcategoryid","age_consumptionability_adcategoryid","age_education_adcategoryid",
              "age_gender_productid","age_consumptionability_productid","age_education_productid","age_gender_producttype",
              "age_consumptionability_producttype","age_education_producttype"]
#为了labelencoder用的list
x_train['uid']=x_train['uid'].map(np.int64)
x_train['aid']=x_train['aid'].map(np.int64)
x_valid['uid']=x_valid['uid'].map(np.int64)
x_valid['aid']=x_valid['aid'].map(np.int64)
for feature in corr_feature:
    corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(feature)+'_zuhe.csv'
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=['uid','aid',feature],dtype={0: np.int64,1: np.int64})
    print "df_cor_fea -----> shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    x_train[feature]=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature]
    x_valid[feature]=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature]
x_train['qubie']=1
x_valid['qubie']=0
data_x=pd.concat([x_train,x_valid])
LE=LabelEncoder()
for feature in corr_feature:
    try:
        data_x[feature]=LE.fit_transform(data_x[feature].map(np.int))
    except:
        data_x[feature]=LE.fit_transform(data_x[feature])
print "LabelEncoder finish"
x_train=data_x[data_x.qubie==1]
x_valid=data_x[data_x.qubie==0]
data_x.pop('qubie'),x_train.pop('qubie'),x_valid.pop('qubie')
OHE=OneHotEncoder()
#data_x_train_1=data_x_train.copy()
#data_x_valid_1=data_x_valid.copy()
df_AUC_age=pd.DataFrame(columns=['var_name','AUC_0','AUC_1'])
for feature in corr_feature:
    OHE.fit(data_x[feature].values.reshape(-1,1))
    train_a=OHE.transform(x_train[feature].values.reshape(-1,1))
    valid_a=OHE.transform(x_valid[feature].values.reshape(-1,1))
    print 'train_a ----> one hot--->shape',train_a.shape
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    eval_list=[(data_x_train,y_train),(data_x_valid,y_valid)]
    gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)

    df_tmp=pd.DataFrame([feature],columns=['var_name'])
    df_tmp['AUC_0']=gbm_clf.best_score_["valid_0"]["auc"]
    df_tmp['AUC_1']=gbm_clf.best_score_["valid_1"]["auc"]
    df_AUC_age=pd.concat([df_AUC_age,df_tmp])
    print "data_x_train ---->shape",data_x_train.shape
    print feature
    print "----------------"

#尝试gender与广告其他特征的3交叉效果:

corr_feature=["gender_house_creativesize","gender_consumptionability_creativesize","gender_marriagestatus_creativesize",
              "gender_education_creativesize","gender_house_adcategoryid","gender_consumptionability_adcategoryid",
              "gender_marriagestatus_adcategoryid","gender_education_adcategoryid","gender_house_productid",
              "gender_consumptionability_productid","gender_marriagestatus_productid","gender_education_productid",
              "gender_house_producttype","gender_consumptionability_producttype","gender_marriagestatus_producttype",
              "gender_education_producttype"]

x_train['uid']=x_train['uid'].map(np.int64)
x_train['aid']=x_train['aid'].map(np.int64)
x_valid['uid']=x_valid['uid'].map(np.int64)
x_valid['aid']=x_valid['aid'].map(np.int64)
for feature in corr_feature:
    corr_feature_path='/home/heqt/tencent/3corr_feature/'+str(feature)+'_zuhe.csv'
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=['uid','aid',feature],dtype={0: np.int64,1: np.int64})
    print "df_cor_fea -----> shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    x_train[feature]=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature]
    x_valid[feature]=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature]
x_train['qubie']=1
x_valid['qubie']=0
data_x=pd.concat([x_train,x_valid])
LE=LabelEncoder()
for feature in corr_feature:
    try:
        data_x[feature]=LE.fit_transform(data_x[feature].map(np.int))
    except:
        data_x[feature]=LE.fit_transform(data_x[feature])
print "LabelEncoder finish"
x_train=data_x[data_x.qubie==1]
x_valid=data_x[data_x.qubie==0]
data_x.pop('qubie'),x_train.pop('qubie'),x_valid.pop('qubie')
OHE=OneHotEncoder()
#data_x_train_1=data_x_train.copy()
#data_x_valid_1=data_x_valid.copy()
df_AUC=pd.DataFrame(columns=['var_name','AUC_0','AUC_1'])
for feature in corr_feature:
    OHE.fit(data_x[feature].values.reshape(-1,1))
    train_a=OHE.transform(x_train[feature].values.reshape(-1,1))
    valid_a=OHE.transform(x_valid[feature].values.reshape(-1,1))
    print 'train_a ----> one hot--->shape',train_a.shape
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    eval_list=[(data_x_train,y_train),(data_x_valid,y_valid)]
    gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)

    df_tmp=pd.DataFrame([feature],columns=['var_name'])
    df_tmp['AUC_0']=gbm_clf.best_score_["valid_0"]["auc"]
    df_tmp['AUC_1']=gbm_clf.best_score_["valid_1"]["auc"]
    df_AUC=pd.concat([df_AUC,df_tmp])
    print "data_x_train ---->shape",data_x_train.shape
    print feature
    print "----------------"


#尝试逻辑回归拟合数值型变量,把得分输进去
x_train['uid']=x_train['uid'].map(np.int64)
x_train['aid']=x_train['aid'].map(np.int64)
x_valid['uid']=x_valid['uid'].map(np.int64)
x_valid['aid']=x_valid['aid'].map(np.int64)
df_LR_train=pd.DataFrame()
df_LR_valid=pd.DataFrame()
#sigle_interest=["appidaction","kw1","kw2","kw3","topic1","topic2","topic3"]
sigle_interest=["appidaction","appidinstall","interest1","interest2","interest3","interest4","interest5","topic1","topic2","topic3","kw1","kw2","kw3"]
for feature in sigle_interest:
    intersec_feature_path='/home/heqt/tencent/corr_feature/single_corr/for_smoot/smooted_ctr/'+feature+'_uid_aid_ctr_rv_0.csv'
    df_cor_fea=pd.read_csv(intersec_feature_path,header=None,names=['uid','aid',feature+'ctr'],dtype={0: np.int64,1: np.int64})
    #because smoe label=-1 will cause null,need df_cor_count to fill null
    print "df_cor_fea---->shape",df_cor_fea.shape
    #print df_cor_fea.head(1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature+'ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature+'ctr']
    #test_a=pd.merge(data_test,df_cor_fea,how='left',on=['uid','aid'])[feature+'ctr']
    df_LR_train=pd.concat([df_LR_train,train_a],axis=1)
    df_LR_valid=pd.concat([df_LR_valid,valid_a],axis=1)
    #train_a[np.where(x_train[feature]=='-1')[0]]=-1
    #valid_a[np.where(x_valid[feature]=='-1')[0]]=-1
    #test_a[np.where(data_test[feature]=='-1')[0]]=-1
    print 'train_a ---> shape',train_a.shape
    #print 'train_a --->head(1)',train_a.head(1)
    #train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    #valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    #test_a=sparse.csr_matrix(test_a.values.reshape(-1,1))
    #data_x_train=sparse.hstack((data_x_train,train_a))
    #data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #data_x_test=sparse.hstack((data_x_test,test_a))
    print feature
LR_clf=LogisticRegression(penalty='l2', tol=0.0001, C=500,random_state=20180521, solver='lbfgs', max_iter=200,n_jobs=10)
LR_pre_train=LR_clf.predict_proba(df_LR_train)
LR_pre_valid=LR_clf.predict_proba(df_LR_valid)
train_a=LR_pre_train[:,1]
valid_a=LR_pre_valid[:,1]
train_a=sparse.csr_matrix(train_a.reshape(-1,1))
valid_a=sparse.csr_matrix(valid_a.reshape(-1,1))
data_x_train=sparse.hstack((data_x_train,train_a))
data_x_valid=sparse.hstack((data_x_valid,valid_a))


#最后一波统计特征,是用用户特征交广告其他特征:

corr_feature=["advertiserid","campaignid","creativesize","adcategoryid","productid","producttype"]
aid_feature=["age","gender","house","lbs","carrier","education","consumptionability","os","ct","marriagestatus"]
#array([329, 123,  28,   9,   7,   0,   1,   0,   0,   0, 
#       636, 183,  50,   15,   2,   2,   0,   0,   0,   0, 
#       186,  65,  20,  10,   2,   0,0,   0,   0,   0, 
#       298,  81,  13,   9,   6,   0,   0,   0,   0,0, 
#       161,  33,   5,   4,   0,   0,   1,   0,   0,   0, 
#       107,  32, 9,   4,   4,   0,   0,   0,   0,   0])

#为了labelencoder用的list
x_train['uid']=x_train['uid'].map(np.int64)
x_train['aid']=x_train['aid'].map(np.int64)
x_valid['uid']=x_valid['uid'].map(np.int64)
x_valid['aid']=x_valid['aid'].map(np.int64)
for feature in corr_feature:
    for adfeature in aid_feature:
        corr_feature_path='/home/heqt/tencent/tongjitezheng/'+str(feature)+'_'+str(adfeature)+'_tongji.csv'
        df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=['uid','aid',feature+'_'+adfeature],dtype={0: np.int64,1: np.int64})
        print "df_cor_fea -----> shape",df_cor_fea.shape
        print df_cor_fea.head(1)
        train_a=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])[feature+'_'+adfeature]
        valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])[feature+'_'+adfeature]
        train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
        valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
        data_x_train=sparse.hstack((data_x_train,train_a))
        data_x_valid=sparse.hstack((data_x_valid,valid_a))

#尝试之前没入模的的组合特征,与aid组合
corr_feature=["lbs","carrier","consumptionability","education","gender","os","ct","marriagestatus"]
x_train['uid']=x_train['uid'].map(np.int64)
x_train['aid']=x_train['aid'].map(np.int64)
x_valid['uid']=x_valid['uid'].map(np.int64)
x_valid['aid']=x_valid['aid'].map(np.int64)
for feature in corr_feature:
    corr_feature_path='/home/heqt/tencent/corr_feature/'+str(feature)+'_aid_count.csv'
    df_cor_fea=pd.read_csv(corr_feature_path,header=None,names=['uid','aid','corr_ctr'],dtype={0: np.int64,1: np.int64})
    print "df_cor_fea -----> shape",df_cor_fea.shape
    print df_cor_fea.head(1)
    train_a=pd.merge(x_train,df_cor_fea,how='left',on=['uid','aid'])['corr_ctr']
    valid_a=pd.merge(x_valid,df_cor_fea,how='left',on=['uid','aid'])['corr_ctr']
    print "train_a after shape -------->",train_a.shape
    print train_a.head(1)
    train_a=sparse.csr_matrix(train_a.values.reshape(-1,1))
    valid_a=sparse.csr_matrix(valid_a.values.reshape(-1,1))
    data_x_train=sparse.hstack((data_x_train,train_a))
    data_x_valid=sparse.hstack((data_x_valid,valid_a))
    #df_tmp=pd.DataFrame(['ctr'],columns=['val'])
    #feature important mapping
    #df_tmp['feature']='%s' %feature
    #df_feature_map=pd.concat([df_feature_map,df_tmp])
    print feature
    print "--------------------"

#产生树的索引
train_tree_index=gbm_clf_3.apply(data_x_train)
valid_tree_index=gbm_clf_3.apply(data_x_valid)
tree_index=np.concatenate([train_tree_index,valid_tree_index])
OHE=OneHotEncoder()
for index in range(tree_index.shape[1]):
    OHE.fit(tree_index[:,index].reshape(-1,1))
    train_a=OHE.transform(train_tree_index[:,index].reshape(-1,1))
    valid_a=OHE.transform(valid_tree_index[:,index].reshape(-1,1))
    if index==0:
        data_x_train_2=train_a
        data_x_valid_2=valid_a
    else:
        data_x_train_2=sparse.hstack((data_x_train_2,train_a))
        data_x_valid_2=sparse.hstack((data_x_valid_2,valid_a))
    if index %50==0:
        print index
        print 'train_a ----> one hot--->shape',train_a.shape

#尝试逻辑回归:




=======
>>>>>>> Stashed changes


df_feature_map.to_csv(save_path+"feature_important_mapping_cut_corr.csv")
sparse.save_npz(save_path+"data_x_train_cut_corr.npz",data_x_train)
sparse.save_npz(save_path+"data_x_valid_cut_corr.npz",data_x_valid)

eval_list=[(data_x_train,y_train),(data_x_valid,y_valid)]

gbm_clf = lgb.LGBMClassifier(
        boosting_type='gbdt', num_leaves=31, reg_alpha=0.0, reg_lambda=1,
        max_depth=-1, n_estimators=1000, objective='binary',
        subsample=0.7, colsample_bytree=0.7, subsample_freq=1,
        learning_rate=0.02, min_child_weight=50,random_state=20180506,n_jobs=7)

gbm_clf.fit(data_x_train,y_train,eval_set=eval_list,eval_metric ='auc',early_stopping_rounds =100)
joblib.dump(gbm_clf, '/home/heqt/jupyter_project/model/gbm_clf_cnt_80W_corr.pkl')



SGDLR_clf=SGDClassifier(loss='log', penalty='l2', alpha=0.04, l1_ratio=0.15, average=True,max_iter=50,
     random_state=20150511,learning_rate='optimal',n_jobs=15,n_iter=2)

SGDLR_clf.fit(data_x_train_LR,y_train)
joblib.dump(gbm_clf, '/home/heqt/jupyter_project/model/feature_SGDLR_clf.pkl')



SGDLR_clf=SGDClassifier(loss='log', penalty='l2', alpha=0.04, l1_ratio=0.15, average=True,max_iter=50,
     random_state=20150511,learning_rate='optimal',n_jobs=15,n_iter=2)

#value在0.01到0.001之间，n_inter越大（这里取10），AUC越好.0.001训练集的AUC比较大
df_SGD=pd.DataFrame(columns=["value","iter","train_auc","valid_auc"])
serch_list=list(10.0**-np.arange(1,7))
n_inters=[2,5,10]
for value in serch_list:
    for n_inter in n_inters:
        SGDLR_clf=SGDClassifier(loss='log', penalty='l2', alpha=value, l1_ratio=0.15, average=True,max_iter=50,
         random_state=20150511,learning_rate='optimal',n_jobs=15,n_iter=n_inter)
        SGDLR_clf.fit(data_x_train_2,y_train)
        SGD_pre_train=SGDLR_clf.predict_proba(data_x_train_2)
        SGD_pre_valid=SGDLR_clf.predict_proba(data_x_valid_2)
        df_tmp=pd.DataFrame([value],columns=["value"])
        df_tmp["iter"]=n_inter
        df_tmp['train_auc']=roc_auc_score(y_train,SGD_pre_train[:,1])
        df_tmp["valid_auc"]=roc_auc_score(y_valid,SGD_pre_valid[:,1])
        df_SGD=pd.concat([df_SGD,df_tmp])
        print value,n_inter
        print "train_auc---->",roc_auc_score(y_train,SGD_pre_train[:,1])
        print "valid_auc---->",roc_auc_score(y_valid,SGD_pre_valid[:,1])


df_SGD=pd.DataFrame(columns=["penalty","l1_ratio","train_auc","valid_auc"])
serch_list=['elasticnet']
n_inters=[0.001,0.01,0.05,0.07]
for value in serch_list:
    for n_inter in n_inters:
        SGDLR_clf=SGDClassifier(loss='log', penalty=value, alpha=0.004, l1_ratio=n_inter,max_iter=1000,tol=0.000001,
         random_state=20150511,learning_rate='optimal',n_jobs=15,n_iter=100)
        SGDLR_clf.fit(data_x_train_2,y_train)
        SGD_pre_train=SGDLR_clf.predict_proba(data_x_train_2)
        SGD_pre_valid=SGDLR_clf.predict_proba(data_x_valid_2)
        df_tmp=pd.DataFrame([value],columns=["penalty"])
        df_tmp["l1_ratio"]=n_inter
        df_tmp['train_auc']=roc_auc_score(y_train,SGD_pre_train[:,1])
        df_tmp["valid_auc"]=roc_auc_score(y_valid,SGD_pre_valid[:,1])
        df_SGD=pd.concat([df_SGD,df_tmp])
        print value,n_inter
        print "train_auc---->",roc_auc_score(y_train,SGD_pre_train[:,1])
        print "valid_auc---->",roc_auc_score(y_valid,SGD_pre_valid[:,1])

df_LR=pd.DataFrame(columns=["value","iter","train_auc","valid_auc"])
CS=[0.0002,0.0004,0.0006,0.0008]
n_inters=[100,150]
for value in CS:
    for n_inter in n_inters:
        LR_clf=LogisticRegression(penalty='l2', tol=0.0001, C=value,random_state=20180517, solver='lbfgs', max_iter=n_inter,n_jobs=10)
        LR_clf.fit(data_x_train_2,y_train)
        LR_pre_train=LR_clf.predict_proba(data_x_train_2)
        LR_pre_valid=LR_clf.predict_proba(data_x_valid_2)
        df_tmp=pd.DataFrame([value],columns=["value"])
        df_tmp["iter"]=n_inter
        df_tmp['train_auc']=roc_auc_score(y_train,LR_pre_train[:,1])
        df_tmp["valid_auc"]=roc_auc_score(y_valid,LR_pre_valid[:,1])
        df_LR=pd.concat([df_LR,df_tmp])
        print value,n_inter
        print "train_auc---->",roc_auc_score(y_train,LR_pre_train[:,1])
        print "valid_auc---->",roc_auc_score(y_valid,LR_pre_valid[:,1])


#调试模型LR:
df_LR=pd.DataFrame(columns=["value","iter","train_auc","valid_auc"])
CS=[1,0.1,0.01,0.001,0.0001]
n_inters=[100,150]
for value in CS:
    for n_inter in n_inters:
        LR_clf=LogisticRegression(penalty='l2', tol=0.0001, C=value,random_state=20180517, solver='lbfgs', max_iter=n_inter,n_jobs=10)
        LR_clf.fit(df_LR_train,y_train)
        LR_pre_train=LR_clf.predict_proba(df_LR_train)
        LR_pre_valid=LR_clf.predict_proba(df_LR_valid)
        LR_pre_test=LR_clf.predict_proba(df_LR_test)
        df_tmp=pd.DataFrame([value],columns=["value"])
        df_tmp["iter"]=n_inter
        df_tmp['train_auc']=roc_auc_score(y_train,LR_pre_train[:,1])
        df_tmp["valid_auc"]=roc_auc_score(y_valid,LR_pre_valid[:,1])
        df_LR=pd.concat([df_LR,df_tmp])
        print value,n_inter
        print "train_auc---->",roc_auc_score(y_train,LR_pre_train[:,1])
        print "valid_auc---->",roc_auc_score(y_valid,LR_pre_valid[:,1])








#------------------------------以下是kuaishou的代码

app_launch=pd.read_csv()_log.txt
user_activity_log.txt
user_register_log.txt
video_create_log.txt

app_launch_path='/home/heqt/kuaishou/app_launch_log.txt'
user_activity_path='/home/heqt/kuaishou/user_activity_log.txt'
user_register_path='/home/heqt/kuaishou/user_register_log.txt'
video_create_path='/home/heqt/kuaishou/video_create_log.txt'
app_launch=pd.read_csv(app_launch_path,sep='\t',dtype=np.int)
user_activity=pd.read_csv(user_activity_path,sep='\t',dtype=np.int)
user_register=pd.read_csv(user_register_path,sep='\t',dtype=np.int)
video_create=pd.read_csv(video_create_path,sep='\t',dtype=np.int)

#0个人
set(video_create.user_id.tolist())-set(user_register.user_id.tolist())

#0个人
set(user_activity.user_id.tolist())-set(user_register.user_id.tolist())

#0个人
set(app_launch.user_id.tolist())-set(user_register.user_id.tolist())

#8001个人
set(user_register.user_id.tolist())-set(user_activity.user_id.tolist())

#44103
len(set(user_register.user_id.tolist())-set(video_create.user_id.tolist()))

#0个人
len(set(user_register.user_id.tolist())-set(app_launch.user_id.tolist()))

#把app_launch整理成bag of word的形式
app_launch['cnt']=1
app_launch_bagofword=app_launch.set_index(['user_id','day'])['cnt'].unstack(1).fillna(0)
app_launch_bagofword.columns.name=None
app_launch_bagofword=app_launch_bagofword.rename(lambda x:'app_launch_day'+str(x),axis=1)
app_launch_bagofword=app_launch_bagofword.reset_index()
#app_launch_bagofword=app_launch_bagofword.astype(np.int)

#video_create整理成 bag of word的形式

video_create['cnt']=1
video_create_bagofword=video_create.groupby(by=['user_id','day'])['cnt'].sum().unstack(1).fillna(0)
video_create_bagofword.columns.name=None
video_create_bagofword=video_create_bagofword.rename(lambda x:'video_create_day'+str(x),axis=1)
video_create_bagofword=video_create_bagofword.reset_index()
#video_create_bagofword=video_create_bagofword.astype(np.int)

#看video_create,app_launch,user_activity是否有交集
#0
len(set(video_create.user_id.tolist())-set(app_launch.user_id.tolist()))
#239
len(set(video_create.user_id.tolist())-set(user_activity.user_id.tolist()))
#8001
len(set(app_launch.user_id.tolist())-set(user_activity.user_id.tolist()))
#44103
len(set(app_launch.user_id.tolist())-set(video_create.user_id.tolist()))
#36341
len(set(user_activity.user_id.tolist())-set(video_create.user_id.tolist()))
#0
len(set(user_activity.user_id.tolist())-set(app_launch.user_id.tolist()))

#user_register变量衍生:
day=23

user_register=user_register[user_register.register_day<=day]

user_register.columns

#register_day_user_id
t1=user_register.groupby(by='register_day')['user_id'].nunique().to_frame('register_day_user_id').reset_index()

#register_type_user_id
t2=user_register.groupby(by='register_type')['user_id'].nunique().to_frame('register_type_user_id').reset_index()

#device_type_user_id
t3=user_register.groupby(by='device_type')['user_id'].nunique().to_frame('device_type_user_id').reset_index()

#merget
data_x_all=pd.merge(user_register,t1,how='left',on='register_day')
data_x_all=pd.merge(data_x_all,t2,how='left',on='register_type')
data_x_all=pd.merge(data_x_all,t3,how='left',on='device_type')

#app_launch衍生:
app_launch_23day=app_launch[app_launch.day<=day]

app_launch_23day=app_launch_23day.sort_values(by=['user_id','day'])

#首次登陆时间与注册时间相同
first_launch=app_launch_23day.drop_duplicates(subset='user_id',keep='first').rename(columns={'day':'first_launch_day'})

last_launch=app_launch_23day.drop_duplicates(subset='user_id',keep='last').rename(columns={'day':'last_launch_day'})

launch_days=app_launch_23day.groupby(by='user_id')['day'].size().to_frame('launch_days').reset_index()

launch_day_user=app_launch_23day.groupby('day')['user_id'].nunique().to_frame('launch_day_user').reset_index()

launch_day_user.rename(columns={'day':'register_day'},inplace=True)

data_x_all=pd.merge(data_x_all,last_launch,how='left',on='user_id').eval('last_launch_day_sub_register=last_launch_day-register_day')

data_x_all.eval('register_cnt=%s-register_day' %day,inplace=True)

data_x_all['register_cnt']=data_x_all['register_cnt']+1

data_x_all=pd.merge(data_x_all,launch_days,how='left',on='user_id')

data_x_all=pd.merge(data_x_all,launch_day_user,how='left',on='register_day')

data_x_all.eval('avg_launch_day=launch_days/register_cnt',inplace=True)

data_x_all.eval('register_sub_launch=register_cnt-launch_days',inplace=True)


#拍摄日志变量衍生
video_create_23day=video_create[video_create.day<=23]

video_create_23day=video_create_23day.sort_values(by=['user_id','day'])

first_video=video_create_23day.drop_duplicates(subset='user_id',keep='first').rename(columns={'day':'first_video_day'})

last_video=video_create_23day.drop_duplicates(subset='user_id',keep='last').rename(columns={'day':'last_video_day'})

video_days=video_create_23day.groupby(by=['user_id'])['day'].nunique().to_frame('video_days').reset_index()

video_frequency=video_create_23day.groupby(by=['user_id','day']).size().to_frame('video_frequency').reset_index()

video_frequency_total=video_frequency.groupby(by=['user_id'])['video_frequency'].sum(axis=1).to_frame('video_frequency_total').reset_index()

video_frequency_max=video_frequency.groupby(by=['user_id'])['video_frequency'].max(axis=1).to_frame('video_frequency_max').reset_index()

video_frequency_min=video_frequency.groupby(by=['user_id'])['video_frequency'].min(axis=1).to_frame('video_frequency_min').reset_index()

video_frequency_avg=video_frequency.groupby(by=['user_id'])['video_frequency'].mean().to_frame('video_frequency_avg').reset_index()

video_frequency_std=video_frequency.groupby(by=['user_id'])['video_frequency'].std(ddof=1).to_frame('video_frequency_std').reset_index()

video_day_user=video_create_23day.groupby(by='day')['user_id'].nunique().to_frame('video_day_user').reset_index().rename(columns={'day':'register_day'})

video_day_frequency=video_create_23day.groupby(by='day')['user_id'].count().to_frame('video_day_frequency').reset_index().rename(columns={'day':'register_day'})

data_x_all=pd.merge(data_x_all,first_video,how='left',on='user_id')

data_x_all=pd.merge(data_x_all,last_video,how='left',on='user_id')

data_x_all.eval('first_video_day_sub_register=first_video_day-register_day',inplace=True)

data_x_all.eval('last_video_day_sub_register=last_video_day-register_day',inplace=True)

data_x_all=pd.merge(data_x_all,video_days,how='left',on='user_id')

data_x_all=pd.merge(data_x_all,video_frequency_avg,how='left',on='user_id')

data_x_all=pd.merge(data_x_all,video_frequency_max,how='left',on='user_id')

data_x_all=pd.merge(data_x_all,video_frequency_min,how='left',on='user_id')

data_x_all=pd.merge(data_x_all,video_frequency_std,how='left',on='user_id')

data_x_all=pd.merge(data_x_all,video_frequency_total,how='left',on='user_id')

data_x_all.eval('avg_video_day=video_days/register_cnt',inplace=True)

data_x_all.eval('register_sub_video=register_cnt-video_days',inplace=True)

data_x_all.eval('register_sub_video=launch_days-video_days',inplace=True)

data_x_all=pd.merge(data_x_all,video_day_user,how='left',on='register_day')

data_x_all=pd.merge(data_x_all,video_day_frequency,how='left',on='register_day')

data_x_all.eval('last_video_sub_frist_video=last_video_day-video_days',inplace=True)

#活跃用户衍生:

user_activity_23day=user_activity[user_activity.day<=day]
#先排序
user_activity_23day=user_activity_23day.sort_values(by=['user_id','day'])
#首次活跃时间
first_activity=user_activity_23day.drop_duplicates(subset='user_id',keep='first')[['user_id','day']].rename(columns={'day':'first_activity_day'})
#最后活跃时间(last_activity_day)
last_activity=user_activity_23day.drop_duplicates(subset='user_id',keep='last')[['user_id','day']].rename(columns={'day':'last_activity_day'})
#活跃天数(activity_days)
activity_days=user_activity_23day.groupby(by=['user_id'])['day'].nunique().to_frame('activity_days').reset_index()
#活跃次数：（max,min,sum,avg,std）
activity_frequency=user_activity_23day.groupby(by=['user_id','day']).size().to_frame('activity_frequency').reset_index()
#total
activity_frequency_total=activity_frequency.groupby(by=['user_id'])['activity_frequency'].sum(axis=1).to_frame('activity_frequency_total').reset_index()
#max
activity_frequency_max=activity_frequency.groupby(by=['user_id'])['activity_frequency'].max(axis=1).to_frame('activity_frequency_max').reset_index()
#min
activity_frequency_min=activity_frequency.groupby(by=['user_id'])['activity_frequency'].min(axis=1).to_frame('activity_frequency_min').reset_index()
#mean
activity_frequency_avg=activity_frequency.groupby(by=['user_id'])['activity_frequency'].mean().to_frame('activity_frequency_avg').reset_index()
#std
activity_frequency_std=activity_frequency.groupby(by=['user_id'])['activity_frequency'].std(ddof=1).to_frame('activity_frequency_std').reset_index()
#每天活跃人数(activity_day_user)
activity_day_user=user_activity_23day.groupby(by='day')['user_id'].nunique().to_frame('activity_day_user').reset_index().rename(columns={'day':'register_day'})
#每天活跃次数(activity_day_frequency)
activity_day_frequency=user_activity_23day.groupby(by='day')['user_id'].count().to_frame('activity_day_frequency').reset_index().rename(columns={'day':'register_day'})

data_x_all=pd.merge(data_x_all,first_activity,how='left',on='user_id')

data_x_all=pd.merge(data_x_all,last_activity,how='left',on='user_id')
#首次活跃时间与注册时间差(first_activity_day_sub_register)
data_x_all.eval('first_activity_day_sub_register=first_activity_day-register_day',inplace=True)
#最后活跃时间与注册时间差(last_activity_day_sub_register)
data_x_all.eval('last_activity_day_sub_register=last_activity_day-register_day',inplace=True)

data_x_all=pd.merge(data_x_all,activity_days,how='left',on='user_id')

data_x_all=pd.merge(data_x_all,activity_frequency_avg,how='left',on='user_id')

data_x_all=pd.merge(data_x_all,activity_frequency_max,how='left',on='user_id')

data_x_all=pd.merge(data_x_all,activity_frequency_min,how='left',on='user_id')

data_x_all=pd.merge(data_x_all,activity_frequency_std,how='left',on='user_id')

data_x_all=pd.merge(data_x_all,activity_frequency_total,how='left',on='user_id')
#平均活跃天数（活跃天数与注册天数占比）(avg_activity_day)
data_x_all.eval('avg_activity_day=activity_days/register_cnt',inplace=True)
#注册天数与活跃天数差(register_sub_activity)
data_x_all.eval('register_sub_activity=register_cnt-activity_days',inplace=True)
#登录天数与活跃天数差(launch_sub_activity)
data_x_all.eval('register_sub_activity=launch_days-activity_days',inplace=True)
#活跃天数与拍摄天数差
data_x_all.eval('activity_sub_video=activity_days-video_days',inplace=True)

data_x_all=pd.merge(data_x_all,activity_day_user,how='left',on='register_day')

data_x_all=pd.merge(data_x_all,activity_day_frequency,how='left',on='register_day')
#最后活跃时间与首次活跃时间差(last_ activity _sub_frist_ activity)
data_x_all.eval('last_activity_sub_frist_activity=last_activity_day-activity_days',inplace=True)


#用户点击的不同页面数,用户播放不同video数,用户关注不同作者数,用户不同行为类型数
activity_user_cnt=user_activity_23day.groupby(by=['user_id'])[['page','video_id','author_id','action_type']].nunique().reset_index().\
rename(columns={'page':'user_page_cnt','video_id':'user_video_cnt','author_id':'user_author_cnt','action_type':'user_action_cnt'})

#用户在每个页面点击的次数
user_page_frequency=user_activity_23day.groupby(by=['user_id','page']).size().unstack(1).rename(columns=lambda x:'page'+str(x)+'_frequency')
user_page_frequency.columns.name=None
user_page_frequency=user_page_frequency.reset_index()
#用户在每个页面活跃的天数
user_page_day=user_activity_23day.groupby(by=['user_id','page'])['day'].nunique().unstack(1).rename(columns=lambda x:'page'+str(x)+'_day')
user_page_day.columns.name=None
user_page_day=user_page_day.reset_index()
#用户在每个页面播放不同的视频数
user_page_video=user_activity_23day.groupby(by=['user_id','page'])['video_id'].nunique().unstack(1).rename(columns=lambda x:'page'+str(x)+'_video')
user_page_video.columns.name=None
user_page_video=user_page_video.reset_index()
#用户在每个页面关注不同的作者数
user_page_author=user_activity_23day.groupby(by=['user_id','page'])['author_id'].nunique().unstack(1).rename(columns=lambda x:'page'+str(x)+'_author')
user_page_author.columns.name=None
user_page_author=user_page_author.reset_index()
#用户在每个页面不同的行为类型数
user_page_action=user_activity_23day.groupby(by=['user_id','page'])['action_type'].nunique().unstack(1).rename(columns=lambda x:'page'+str(x)+'_action')
user_page_action.columns.name=None
user_page_action=user_page_action.reset_index()

#用户每个行为类型发生次数
user_action_frequency=user_activity_23day.groupby(by=['user_id','action_type']).size().unstack(1).rename(columns=lambda x:'action'+str(x)+'_frequency')
user_action_frequency.columns.name=None
user_action_frequency=user_action_frequency.reset_index()
#用户在每个行为类型活跃的天数
user_action_day=user_activity_23day.groupby(by=['user_id','action_type'])['day'].nunique().unstack(1).rename(columns=lambda x:'action'+str(x)+'_day')
user_action_day.columns.name=None
user_action_day=user_action_day.reset_index()
#用户在每个行为类型播放不同的视频数
user_action_video=user_activity_23day.groupby(by=['user_id','action_type'])['video_id'].nunique().unstack(1).rename(columns=lambda x:'action'+str(x)+'_video')
user_action_video.columns.name=None
user_action_video=user_action_video.reset_index()
#用户在每个行为类型关注不同的作者数
user_action_author=user_activity_23day.groupby(by=['user_id','action_type'])['author_id'].nunique().unstack(1).rename(columns=lambda x:'action'+str(x)+'_author')
user_action_author.columns.name=None
user_action_author=user_action_author.reset_index()
#用户在每个行为类型发生的不同页面数
user_action_page=user_activity_23day.groupby(by=['user_id','action_type'])['page'].nunique().unstack(1).rename(columns=lambda x:'action'+str(x)+'_page')
user_action_page.columns.name=None
user_action_page=user_action_page.reset_index()
for merge in [activity_user_cnt,user_page_frequency,user_page_day,user_page_video,user_page_author,user_page_action,\
user_action_frequency,user_action_day,user_action_video,user_action_author,user_action_page]:
    data_x_all=pd.merge(data_x_all,merge,how='left',on='user_id')

'''下面的实现不了,维度太大
#每个视频被播放的人数
acti_video_user=user_activity_23day.groupby(by='video_id')['user_id'].nunique().to_frame('acti_video_user').reset_index()
#每个视频被播放的次数
acti_video_frequency=user_activity_23day.groupby(by='video_id')['user_id'].size().to_frame('acti_video_frequency').reset_index()
#每个作者被关注的人数
acti_author_user=user_activity_23day.groupby(by='author_id')['user_id'].nunique().to_frame('acti_author_user').reset_index()
#每个作者被关注的次数
acti_author_frequency=user_activity_23day.groupby(by='author_id')['user_id'].size().to_frame('acti_author_frequency').reset_index()

#  5个行为页面分别点击的人数
page_user=user_activity_23day.groupby(by='page')['user_id'].nunique().to_frame('page_user').reset_index()
#  5个行为页面分别点击的次数
page_frequency=user_activity_23day.groupby(by='page')['user_id'].size().to_frame('page_frequency').reset_index()
#  6个行为类型分别点击的人数
action_user=user_activity_23day.groupby(by='action_type')['user_id'].nunique().to_frame('action_user').reset_index()
#  6个行为类型分别点击的次数
action_frequency=user_activity_23day.groupby(by='action_type')['user_id'].size().to_frame('action_frequency').reset_index()
'''
#合并数据:

#define f1_score
def f1_score(y_true,y_pred):
    eval_name='f1_score'
    precision,recall,threshold =precision_recall_curve(y_true,y_pred)
    f1_list=(2*precision*recall)/(precision+recall)
    max_index=np.argmax(f1_list)
    print 'threshold--->',threshold[max_index]
    f1=np.max(f1_list)
    return eval_name,f1,True

#提取label
def get_label_data(app_launch_,video_create_,user_activity_):
    app_launch_lable=app_launch_.drop_duplicates(subset=['user_id','day'])
    video_create_label=video_create_.drop_duplicates(subset=['user_id','day'])
    user_activity_label=user_activity_.drop_duplicates(subset=['user_id','day'])[['user_id','day']]
    data_label=pd.concat([app_launch_lable,video_create_label])
    data_label=pd.concat([data_label,user_activity_label])
    data_label=data_label.drop_duplicates(subset=['user_id','day'])
    return data_label

class Get_data_launched_record(object):
    #register_data:data_frame
    #label_data:data_frame
    def __init__(self,data_register,data_label,split_day=23,merge_day=7,label_count_day=7):
        self._data_register=data_register
        self._data_label=data_label.set_index('user_id')
        self._split_day=split_day
        self._merge_day=merge_day
        self._label_count_day=label_count_day
        self._register_people_af_split=data_register[data_register.register_day>split_day].user_id.unique()
        self._register_people_cnt_af_split=data_register[data_register.register_day>split_day].user_id.nunique()
    #plot graph
    def _plot_people_cnt(self,x):
        plot_x=np.arange(len(x.index))
        plot_y=x['cnt'].values
        plt.figure(figsize=(20,1))
        plt.bar(plot_x,plot_y)
        plt.xticks(plot_x,x.index)
        plt.xlabel('day')
        plt.ylabel('people_cnt')
        for i,j in zip(plot_x,plot_y):
            plt.text(i,j,'%.0f'%j,ha='center', va= 'bottom',fontsize=10)
        plt.show()
    #merget register information
    def _merge_data_register(self):
        register_bins=list(range(1,self._split_day+1))[::-self._merge_day][::-1]
        register_bins.insert(0,0)
        register_cut=pd.cut(self._data_register['register_day'],register_bins)
        register_people=self._data_register.groupby(by=register_cut)['user_id'].unique().to_frame('register_people').reset_index()
        self._register_people=register_people
        self._register_bins=register_bins
        self._register_cut=register_cut
    #calculate the number of people of forecast
    def _count_data_label(self):
        for ind in range(self._register_people.shape[0]):
            register_people_index=self._register_people.register_people.iloc[ind]
            data_label_index=self._data_label.loc[register_people_index].reset_index()
            label_count_bins=range(self._register_bins[ind+1],30)
            label_count_bins=label_count_bins[::self._label_count_day]
            label_count_bins.insert(len(label_count_bins),30)
            self._label_count_bins=label_count_bins
            data_label_index_cut=pd.cut(data_label_index.day,label_count_bins)
            data_label_index_cnt=data_label_index.groupby(by=data_label_index_cut)['user_id'].nunique()\
            .to_frame('cnt').reset_index()
            data_label_index_cnt.loc[-1]=[str(self._register_people['register_day'][ind]),self._register_people['register_people'][ind].shape[0]]
            data_label_index_cnt.index=data_label_index_cnt.index+1
            data_label_index_cnt.sort_index(inplace=True)
            data_label_index_cnt.set_index('day',inplace=True)
            #self._data_label_index_cnt=data_label_index_cnt
            self._plot_people_cnt(data_label_index_cnt)
    # to get labeled people
    def get_label_people(self,start_day,end_day,count_day=7):
        source_people=self._data_register[(self._data_register.register_day>=start_day) & \
        (self._data_register.register_day<=end_day)]['user_id'].values
        target_people=self._data_label.loc[source_people].reset_index()
        target_bins=range(end_day,30)
        target_bins=target_bins[::count_day]
        target_bins.insert(len(target_bins),30)
        self._label_people_bins=target_bins
        target_cuts=pd.cut(target_people.day,target_bins)
        label_people=target_people.groupby(by=target_cuts)['user_id'].unique().to_frame('label_people').reset_index()
        self.label_people=label_people
    #plot launch trend
    def plot_trend(self):
        self._merge_data_register()
        self._count_data_label()


class Get_data_feature(object):
    '''
    ps:forcast_week:提前预测的周,比如我要预测这周的客户在接下来一周还会不会登录,则为1
    如果要预测这周的客户在接下来2周还会不会登录,则取值为2
    如果 forcast_week=0,证明提取正常的特征,也就是预测特征
    '''
    def __init__(self,register_data,app_launch_data,video_create_data,user_activity_data,start_day=1,end_day=23,forcast_week=1):
        self._register_data=register_data
        self._app_launch_data=app_launch_data
        self._video_create_data=video_create_data
        self._user_activity_data=user_activity_data
        self._start_day=start_day
        self._end_day=end_day
        self._forcast_week=forcast_week
        self.shiff_day=(37-forcast_week*7-end_day) if forcast_week !=0 else 0
        self.add_fea_day=(forcast_week-1)*7 if forcast_week !=0 else  30-end_day

    def _get_register_feature(self):
        user_register_nday=self._register_data[(self._register_data.register_day>=self._start_day)&(self._register_data.register_day<=self._end_day)]
        user_register_nday.register_day=user_register_nday.register_day+self.shiff_day
        #register_day_user_id

        t1=user_register_nday.groupby(by='register_day')['user_id'].nunique().to_frame('register_day_user_id').reset_index()
        #register_type_user_id
        t2=user_register_nday.groupby(by='register_type')['user_id'].nunique().to_frame('register_type_user_id').reset_index()
        #device_type_user_id
        t3=user_register_nday.groupby(by='device_type')['user_id'].nunique().to_frame('device_type_user_id').reset_index()
        #merget
        self.data_x_all=user_register_nday[['user_id','register_day','register_type','device_type']]
        self.data_x_all=pd.merge(self.data_x_all,t1,how='left',on='register_day')
        self.data_x_all=pd.merge(self.data_x_all,t2,how='left',on='register_type')
        self.data_x_all=pd.merge(self.data_x_all,t3,how='left',on='device_type')

    def _get_app_launch_feature(self):
        app_launch_nday=self._app_launch_data[(self._app_launch_data.day>=self._start_day)&(self._app_launch_data.day<=(self._end_day+self.add_fea_day))]
        app_launch_nday.day=app_launch_nday.day+self.shiff_day
        app_launch_nday=app_launch_nday.sort_values(by=['user_id','day'])
        #首次登陆时间与注册时间相同
        #first_launch=app_launch_nday.drop_duplicates(subset='user_id',keep='first').rename(columns={'day':'first_launch_day'})
        last_launch=app_launch_nday.drop_duplicates(subset='user_id',keep='last').rename(columns={'day':'last_launch_day'})
        launch_days=app_launch_nday.groupby(by='user_id')['day'].size().to_frame('launch_days').reset_index()
        launch_day_user=app_launch_nday.groupby('day')['user_id'].nunique().to_frame('launch_day_user').reset_index()
        launch_day_user.rename(columns={'day':'register_day'},inplace=True)
        self.data_x_all=pd.merge(self.data_x_all,last_launch,how='left',on='user_id').eval('last_launch_day_sub_register=last_launch_day-register_day')
        self.data_x_all.eval('register_cnt=%s -register_day' % 31,inplace=True)
        self.data_x_all=pd.merge(self.data_x_all,launch_days,how='left',on='user_id')
        self.data_x_all=pd.merge(self.data_x_all,launch_day_user,how='left',on='register_day')
        self.data_x_all.eval('avg_launch_day=launch_days/register_cnt',inplace=True)
        self.data_x_all.eval('register_sub_launch=register_cnt-launch_days',inplace=True)

    def _get_video_feature(self):
        video_create_nday=self._video_create_data[(self._video_create_data.day>=self._start_day)&(self._video_create_data.day<=(self._end_day+self.add_fea_day))]
        video_create_nday.day=video_create_nday.day+self.shiff_day
        video_create_nday=video_create_nday.sort_values(by=['user_id','day'])
        #拍摄日志变量衍生
        first_video=video_create_nday.drop_duplicates(subset='user_id',keep='first').rename(columns={'day':'first_video_day'})
        last_video=video_create_nday.drop_duplicates(subset='user_id',keep='last').rename(columns={'day':'last_video_day'})
        video_days=video_create_nday.groupby(by=['user_id'])['day'].nunique().to_frame('video_days').reset_index()
        video_frequency=video_create_nday.groupby(by=['user_id','day']).size().to_frame('video_frequency').reset_index()
        video_frequency_total=video_frequency.groupby(by=['user_id'])['video_frequency'].sum(axis=1).to_frame('video_frequency_total').reset_index()
        video_frequency_max=video_frequency.groupby(by=['user_id'])['video_frequency'].max(axis=1).to_frame('video_frequency_max').reset_index()
        video_frequency_min=video_frequency.groupby(by=['user_id'])['video_frequency'].min(axis=1).to_frame('video_frequency_min').reset_index()
        video_frequency_avg=video_frequency.groupby(by=['user_id'])['video_frequency'].mean().to_frame('video_frequency_avg').reset_index()
        video_frequency_std=video_frequency.groupby(by=['user_id'])['video_frequency'].std(ddof=1).to_frame('video_frequency_std').reset_index()
        video_day_user=video_create_nday.groupby(by='day')['user_id'].nunique().to_frame('video_day_user').reset_index().rename(columns={'day':'register_day'})
        video_day_frequency=video_create_nday.groupby(by='day')['user_id'].count().to_frame('video_day_frequency').reset_index().rename(columns={'day':'register_day'})
        self.data_x_all=pd.merge(self.data_x_all,first_video,how='left',on='user_id')
        self.data_x_all=pd.merge(self.data_x_all,last_video,how='left',on='user_id')
        self.data_x_all.eval('first_video_day_sub_register=first_video_day-register_day',inplace=True)
        self.data_x_all.eval('last_video_day_sub_register=last_video_day-register_day',inplace=True)
        self.data_x_all=pd.merge(self.data_x_all,video_days,how='left',on='user_id')
        self.data_x_all=pd.merge(self.data_x_all,video_frequency_avg,how='left',on='user_id')
        self.data_x_all=pd.merge(self.data_x_all,video_frequency_max,how='left',on='user_id')
        self.data_x_all=pd.merge(self.data_x_all,video_frequency_min,how='left',on='user_id')
        self.data_x_all=pd.merge(self.data_x_all,video_frequency_std,how='left',on='user_id')
        self.data_x_all=pd.merge(self.data_x_all,video_frequency_total,how='left',on='user_id')
        self.data_x_all.eval('avg_video_day=video_days/register_cnt',inplace=True)
        self.data_x_all.eval('register_sub_video=register_cnt-video_days',inplace=True)
        self.data_x_all.eval('register_sub_video=launch_days-video_days',inplace=True)
        self.data_x_all=pd.merge(self.data_x_all,video_day_user,how='left',on='register_day')
        self.data_x_all=pd.merge(self.data_x_all,video_day_frequency,how='left',on='register_day')
        self.data_x_all.eval('last_video_sub_frist_video=last_video_day-video_days',inplace=True)

    def _get_activity_feature(self):
        activity_create_nday=self._user_activity_data[(self._user_activity_data.day>=self._start_day)&(self._user_activity_data.day<=(self._end_day+self.add_fea_day))]
        activity_create_nday.day=activity_create_nday.day+self.shiff_day
        activity_create_nday=activity_create_nday.sort_values(by=['user_id','day'])
        #活跃用户衍生:
        #首次活跃时间
        first_activity=activity_create_nday.drop_duplicates(subset='user_id',keep='first')[['user_id','day']].rename(columns={'day':'first_activity_day'})
        #最后活跃时间(last_activity_day)
        last_activity=activity_create_nday.drop_duplicates(subset='user_id',keep='last')[['user_id','day']].rename(columns={'day':'last_activity_day'})
        #活跃天数(activity_days)
        activity_days=activity_create_nday.groupby(by=['user_id'])['day'].nunique().to_frame('activity_days').reset_index()
        #活跃次数：（max,min,sum,avg,std）
        activity_frequency=activity_create_nday.groupby(by=['user_id','day']).size().to_frame('activity_frequency').reset_index()
        #total
        activity_frequency_total=activity_frequency.groupby(by=['user_id'])['activity_frequency'].sum(axis=1).to_frame('activity_frequency_total').reset_index()
        #max
        activity_frequency_max=activity_frequency.groupby(by=['user_id'])['activity_frequency'].max(axis=1).to_frame('activity_frequency_max').reset_index()
        #min
        activity_frequency_min=activity_frequency.groupby(by=['user_id'])['activity_frequency'].min(axis=1).to_frame('activity_frequency_min').reset_index()
        #mean
        activity_frequency_avg=activity_frequency.groupby(by=['user_id'])['activity_frequency'].mean().to_frame('activity_frequency_avg').reset_index()
        #std
        activity_frequency_std=activity_frequency.groupby(by=['user_id'])['activity_frequency'].std(ddof=1).to_frame('activity_frequency_std').reset_index()
        #每天活跃人数(activity_day_user)
        activity_day_user=activity_create_nday.groupby(by='day')['user_id'].nunique().to_frame('activity_day_user').reset_index().rename(columns={'day':'register_day'})
        #每天活跃次数(activity_day_frequency)
        activity_day_frequency=activity_create_nday.groupby(by='day')['user_id'].count().to_frame('activity_day_frequency').reset_index().rename(columns={'day':'register_day'})

        self.data_x_all=pd.merge(self.data_x_all,first_activity,how='left',on='user_id')

        self.data_x_all=pd.merge(self.data_x_all,last_activity,how='left',on='user_id')
        #首次活跃时间与注册时间差(first_activity_day_sub_register)
        self.data_x_all.eval('first_activity_day_sub_register=first_activity_day-register_day',inplace=True)
        #最后活跃时间与注册时间差(last_activity_day_sub_register)
        self.data_x_all.eval('last_activity_day_sub_register=last_activity_day-register_day',inplace=True)

        self.data_x_all=pd.merge(self.data_x_all,activity_days,how='left',on='user_id')

        self.data_x_all=pd.merge(self.data_x_all,activity_frequency_avg,how='left',on='user_id')

        self.data_x_all=pd.merge(self.data_x_all,activity_frequency_max,how='left',on='user_id')

        self.data_x_all=pd.merge(self.data_x_all,activity_frequency_min,how='left',on='user_id')

        self.data_x_all=pd.merge(self.data_x_all,activity_frequency_std,how='left',on='user_id')

        self.data_x_all=pd.merge(self.data_x_all,activity_frequency_total,how='left',on='user_id')
        #平均活跃天数（活跃天数与注册天数占比）(avg_activity_day)
        self.data_x_all.eval('avg_activity_day=activity_days/register_cnt',inplace=True)
        #注册天数与活跃天数差(register_sub_activity)
        self.data_x_all.eval('register_sub_activity=register_cnt-activity_days',inplace=True)
        #登录天数与活跃天数差(launch_sub_activity)
        self.data_x_all.eval('register_sub_activity=launch_days-activity_days',inplace=True)
        #活跃天数与拍摄天数差
        self.data_x_all.eval('activity_sub_video=activity_days-video_days',inplace=True)

        self.data_x_all=pd.merge(self.data_x_all,activity_day_user,how='left',on='register_day')

        self.data_x_all=pd.merge(self.data_x_all,activity_day_frequency,how='left',on='register_day')
        #最后活跃时间与首次活跃时间差(last_ activity _sub_frist_ activity)
        self.data_x_all.eval('last_activity_sub_frist_activity=last_activity_day-activity_days',inplace=True)

        #用户点击的不同页面数,用户播放不同video数,用户关注不同作者数,用户不同行为类型数
        activity_user_cnt=activity_create_nday.groupby(by=['user_id'])[['page','video_id','author_id','action_type']].nunique().reset_index().\
        rename(columns={'page':'user_page_cnt','video_id':'user_video_cnt','author_id':'user_author_cnt','action_type':'user_action_cnt'})
        #用户在每个页面点击的次数
        user_page_frequency=activity_create_nday.groupby(by=['user_id','page']).size().unstack(1).rename(columns=lambda x:'page'+str(x)+'_frequency')
        user_page_frequency.columns.name=None
        user_page_frequency=user_page_frequency.reset_index()
        #用户在每个页面活跃的天数
        user_page_day=activity_create_nday.groupby(by=['user_id','page'])['day'].nunique().unstack(1).rename(columns=lambda x:'page'+str(x)+'_day')
        user_page_day.columns.name=None
        user_page_day=user_page_day.reset_index()
        #用户在每个页面播放不同的视频数
        user_page_video=activity_create_nday.groupby(by=['user_id','page'])['video_id'].nunique().unstack(1).rename(columns=lambda x:'page'+str(x)+'_video')
        user_page_video.columns.name=None
        user_page_video=user_page_video.reset_index()
        #用户在每个页面关注不同的作者数
        user_page_author=activity_create_nday.groupby(by=['user_id','page'])['author_id'].nunique().unstack(1).rename(columns=lambda x:'page'+str(x)+'_author')
        user_page_author.columns.name=None
        user_page_author=user_page_author.reset_index()
        #用户在每个页面不同的行为类型数
        user_page_action=activity_create_nday.groupby(by=['user_id','page'])['action_type'].nunique().unstack(1).rename(columns=lambda x:'page'+str(x)+'_action')
        user_page_action.columns.name=None
        user_page_action=user_page_action.reset_index()
        #用户每个行为类型发生次数
        user_action_frequency=activity_create_nday.groupby(by=['user_id','action_type']).size().unstack(1).rename(columns=lambda x:'action'+str(x)+'_frequency')
        user_action_frequency.columns.name=None
        user_action_frequency=user_action_frequency.reset_index()
        #用户在每个行为类型活跃的天数
        user_action_day=activity_create_nday.groupby(by=['user_id','action_type'])['day'].nunique().unstack(1).rename(columns=lambda x:'action'+str(x)+'_day')
        user_action_day.columns.name=None
        user_action_day=user_action_day.reset_index()
        #用户在每个行为类型播放不同的视频数
        user_action_video=activity_create_nday.groupby(by=['user_id','action_type'])['video_id'].nunique().unstack(1).rename(columns=lambda x:'action'+str(x)+'_video')
        user_action_video.columns.name=None
        user_action_video=user_action_video.reset_index()
        #用户在每个行为类型关注不同的作者数
        user_action_author=activity_create_nday.groupby(by=['user_id','action_type'])['author_id'].nunique().unstack(1).rename(columns=lambda x:'action'+str(x)+'_author')
        user_action_author.columns.name=None
        user_action_author=user_action_author.reset_index()
        #用户在每个行为类型发生的不同页面数
        user_action_page=activity_create_nday.groupby(by=['user_id','action_type'])['page'].nunique().unstack(1).rename(columns=lambda x:'action'+str(x)+'_page')
        user_action_page.columns.name=None
        user_action_page=user_action_page.reset_index()
        for merge in [activity_user_cnt,user_page_frequency,user_page_day,user_page_video,user_page_author,user_page_action,\
        user_action_frequency,user_action_day,user_action_video,user_action_author,user_action_page]:
            self.data_x_all=pd.merge(self.data_x_all,merge,how='left',on='user_id')

    def get_feature(self):
        self._get_register_feature()
        self._get_app_launch_feature()
        self._get_video_feature()
        self._get_activity_feature()


