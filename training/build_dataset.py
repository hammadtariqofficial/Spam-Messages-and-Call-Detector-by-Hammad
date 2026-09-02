from pathlib import Path
import csv, random
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'spam_dataset.csv'
random.seed(42)

spam_starts=['URGENT','FINAL NOTICE','SECURITY ALERT','IMPORTANT NOTICE','ACTION REQUIRED','IMMEDIATE ACTION REQUIRED','LAST WARNING','ACCOUNT ALERT','Congratulations','You have won','Winner selected','Exclusive reward','Limited time offer','Special promotion','Claim notice','Prize notification','Your payment failed','Your account is suspended','Your card requires verification','Your bank security check is pending','Your delivery is on hold','Loan approved','Investment opportunity','Cash reward available','Free voucher available','Bonus waiting for you','Lottery result available']
spam_actions=['verify your account immediately','confirm your identity now','click the link to continue','open the secure portal now','update your card details','enter your OTP to continue','reset your password immediately','send the verification code','call the number to claim','claim your prize today','pay the small processing fee','provide your banking details','confirm your payment information','unlock your account using this link','complete verification before midnight','transfer the fee to release the reward','share the one-time password','sign in through the attached link','respond immediately to avoid suspension']
spam_objects=['before access is blocked','or your account will be suspended','to receive the reward','before the offer expires','to release the funds','to avoid a service interruption','and confirm your credentials','to receive your cash prize','before the deadline','to complete the security check','to collect the voucher','to unlock the bonus']

subjects=['project report','college assignment','presentation','lecture notes','team meeting','library visit','football match','lunch plan','dinner plan','office document','invoice','receipt','parcel','delivery schedule','event registration','class timetable','coding task','database report','security lecture','lab exercise','travel plan','family dinner','birthday plan','group project','budget sheet','attendance record','course registration','certificate collection','appointment','study session']
actions=['send','review','share','check','update','print','bring','confirm','discuss','prepare','finish','submit','read','forward','compare','organize','download','attach','present','schedule']
contexts=['tomorrow','this evening','after class','before the meeting','when you have time','for our college project','for the team','after lunch','before Friday','during the lab','for the presentation','at the office','for the next session','when you get home','for our study group']
people=['me','the team','our teacher','the office','the group','my classmate','the project lead','our coordinator']
details=['as discussed yesterday','using the latest file','from our shared folder','with the updated figures','for the next review','with the final draft','for the lab record','for our weekly plan','with the correct date','after checking the notes','for the scheduled session']

rows=[]
legacy=ROOT/'data'/'spam_dataset_original.csv'
with legacy.open(encoding='utf-8',newline='') as f:
    for i,r in enumerate(csv.DictReader(f)):
        rows.append((r['text'].strip(),r['label'].strip(),f'legacy_{i}'))

for i in range(300):
    start=spam_starts[i%len(spam_starts)]; action=spam_actions[(i*7)%len(spam_actions)]; obj=spam_objects[(i*11)%len(spam_objects)]
    variants=[f'{start}: {action} {obj}.',f'{start}! Please {action} {obj}.',f'{start} — {action}; {obj}.']
    for j,t in enumerate(variants): rows.append((t,'spam',f'spam_group_{i}'))

# Additional hard-negative normal groups: benign messages deliberately use words
# such as bank, account, password, payment, link, prize, delivery and verify
# without asking for secrets or unsafe actions.
hard_subjects=['bank statement','account report','password policy','payment schedule','delivery notice','tracking record','security lecture','invoice review','event link','certificate prize list','reward program report','card statement','login test','verification checklist','package record']
hard_actions=['review','discuss','archive','print','compare','attach','update','present','check','record']
hard_contexts=['for the office meeting','for our college project','with the finance team','for the weekly report','during the lab','with the coordinator','before the scheduled meeting','for the class presentation','in the official system','for the accounting exercise']

# 300 unique normal groups, each with 3 natural variants. The construction
# intentionally includes benign security/finance/delivery vocabulary.
for i in range(300):
    subj=subjects[i%len(subjects)]; act=actions[(i*3)%len(actions)]; ctx=contexts[(i*5)%len(contexts)]; person=people[(i*7)%len(people)]; detail=details[(i*13)%len(details)]
    variants=[
        f'Please {act} the {subj} {ctx}, {detail}.' ,
        f'Can you {act} my {subj} {ctx} and let {person} know, {detail}?' ,
        f'We need to {act} the {subj} {ctx}; this is for a normal task, {detail}.' ,
    ]
    for j,t in enumerate(variants): rows.append((t,'ham',f'normal_group_{i}'))

for i in range(150):
    subj=hard_subjects[i%len(hard_subjects)]; act=hard_actions[(i*3)%len(hard_actions)]; ctx=hard_contexts[(i*7)%len(hard_contexts)]
    variants=[
        f'Please {act} the {subj} {ctx}.',
        f'The {subj} is ready to {act} {ctx}; no urgent action is required.',
        f'Our team will {act} the {subj} {ctx} using the normal office process.'
    ]
    for j,t in enumerate(variants): rows.append((t,'ham',f'hard_normal_group_{i}'))

seen=set(); out=[]
for t,l,g in rows:
    k=(t.lower(),l)
    if k not in seen: seen.add(k); out.append((t,l,g))
with OUT.open('w',encoding='utf-8',newline='') as f:
    w=csv.writer(f); w.writerow(['text','label','group']); w.writerows(out)
print(f'Wrote {len(out)} rows to {OUT}')
