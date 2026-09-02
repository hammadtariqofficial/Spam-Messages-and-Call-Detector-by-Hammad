from __future__ import annotations
import csv, json, random, argparse
from pathlib import Path
from collections import Counter

from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, classification_report
import joblib

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'spam_dataset.csv'
MODEL_DIR = ROOT / 'models'
REPORT_DIR = ROOT / 'reports'
MODEL_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)


def load_rows():
    rows=[]
    with DATA.open(encoding='utf-8', newline='') as f:
        for i,r in enumerate(csv.DictReader(f)):
            label = 1 if r['label'].strip().lower() in ('spam','1') else 0
            rows.append((r['text'].strip(), label, r.get('group', f'legacy_{i}')))
    return rows


def metric_block(y_true, y_pred):
    p,r,f,_=precision_recall_fscore_support(y_true,y_pred,average='binary',zero_division=0)
    return {'accuracy':round(float(accuracy_score(y_true,y_pred)),4),'precision_spam':round(float(p),4),'recall_spam':round(float(r),4),'f1_spam':round(float(f),4)}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--seed',type=int,default=42)
    args=ap.parse_args()
    random.seed(args.seed)
    rows=load_rows()
    texts=[x[0] for x in rows]; y=[x[1] for x in rows]; groups=[x[2] for x in rows]

    # Grouped split prevents near-identical generated variants from leaking
    # between train/validation/test sets.
    gss=GroupShuffleSplit(n_splits=1,test_size=0.20,random_state=args.seed)
    trainval_idx,test_idx=next(gss.split(texts,y,groups))
    trainval_groups=[groups[i] for i in trainval_idx]
    gss2=GroupShuffleSplit(n_splits=1,test_size=0.20,random_state=args.seed+1)
    tr_rel,val_rel=next(gss2.split(trainval_idx,[y[i] for i in trainval_idx],trainval_groups))
    train_idx=[trainval_idx[i] for i in tr_rel]; val_idx=[trainval_idx[i] for i in val_rel]

    features=FeatureUnion([
        ('word',TfidfVectorizer(lowercase=True,ngram_range=(1,2),min_df=1,max_df=0.98,sublinear_tf=True,max_features=20000)),
        ('char',TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),min_df=1,max_features=25000,sublinear_tf=True)),
    ])
    model=Pipeline([
        ('features',features),
        ('classifier',LogisticRegression(max_iter=2500,class_weight='balanced',C=3.0,solver='liblinear',random_state=args.seed)),
    ])
    model.fit([texts[i] for i in train_idx],[y[i] for i in train_idx])
    val_pred=model.predict([texts[i] for i in val_idx]); test_pred=model.predict([texts[i] for i in test_idx])
    val_metrics=metric_block([y[i] for i in val_idx],val_pred)
    test_metrics=metric_block([y[i] for i in test_idx],test_pred)
    cm=confusion_matrix([y[i] for i in test_idx],test_pred).tolist()

    # Final fit on train+validation, preserving the untouched grouped test set.
    fit_idx=train_idx+val_idx
    model.fit([texts[i] for i in fit_idx],[y[i] for i in fit_idx])
    joblib.dump(model,MODEL_DIR/'spam_model.pkl',compress=3)
    # Compatibility artifact: detector now accepts a pipeline model, but retain
    # a vectorizer artifact for existing tooling/documentation.
    joblib.dump(model.named_steps['features'],MODEL_DIR/'tfidf_vectorizer.pkl',compress=3)

    report={
        'dataset_rows':len(rows),
        'class_counts':dict(Counter(y)),
        'split_rows':{'train':len(train_idx),'validation':len(val_idx),'test':len(test_idx)},
        'grouped_split':True,
        'seed':args.seed,
        'model':'word+character TF-IDF + Logistic Regression',
        'validation':val_metrics,
        'test':test_metrics,
        'test_confusion_matrix_labels_0_normal_1_spam':cm,
        'classification_report':classification_report([y[i] for i in test_idx],test_pred,target_names=['normal','spam'],output_dict=True,zero_division=0),
        'note':'Dataset contains curated baseline examples plus synthetic/template-generated examples. Treat these metrics as engineering validation, not a benchmark of real-world production performance.'
    }
    (REPORT_DIR/'ml_evaluation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    (REPORT_DIR/'ml_evaluation.txt').write_text(
        f"Industrial ML Evaluation\nDataset: {len(rows)} rows\nTrain: {len(train_idx)} | Validation: {len(val_idx)} | Test: {len(test_idx)}\n"
        f"Validation: {val_metrics}\nTest: {test_metrics}\nConfusion matrix [normal,spam]: {cm}\n\nIMPORTANT: synthetic/template-generated data is included; metrics are not proof of production accuracy.\n",encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
