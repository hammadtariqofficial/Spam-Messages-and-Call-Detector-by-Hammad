from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from detector import SpamDetector

NORMAL=[
 'Please send me the project report tomorrow.', 'Can you call me when you are free?', 'The class starts at nine tomorrow morning.',
 'Thanks for sending the files I will review them tonight.', 'Please bring your laptop to class.', 'I will be late by ten minutes.',
 'Can you share the notes from today lecture?', 'Lets meet at the library after class.', 'Dinner is ready when you get home.',
 'Please remind me about the assignment.', 'I finished the coding task we discussed.', 'What time is the football match?',
 'Thank you for helping me with the project.', 'I will send the document this evening.', 'See you tomorrow at college.',
 'Can you review my presentation?', 'The meeting is confirmed for Monday at 10 AM.', 'Please confirm the delivery time for our office order.',
 'The tracking number is in the project spreadsheet.', 'Our teacher asked us to update the report before Friday.',
 'The bank statement is attached to the accounting report for class.', 'We should discuss the payment schedule at the meeting.',
 'Please call me after the lecture.', 'I received the parcel from the courier today.', 'The security lecture covers password hygiene.',
 'I am testing the login page in our local development project.', 'Please verify the figures in the presentation before submission.',
 'The event registration link is on the college website.', 'I will bring the receipt to the office tomorrow.',
 'Can you send the invoice to the team email?', 'Our project team won the college competition.',
 'Congratulations on finishing the assignment.', 'Please claim your certificate from the office.', 'The prize ceremony starts after lunch.',
 'We need to confirm the booking with the organizer.', 'The account team will review the request tomorrow.',
 'Please check the package tracking status in the official app.', 'The teacher asked everyone to update their password.',
 'Please schedule the study session for Thursday.', 'Can you print the final report for the meeting?'
]
SPAM=[
 'URGENT click this link to verify your bank account immediately.', 'Final notice your account is suspended verify now.',
 'Congratulations you won a free cash prize claim now.', 'Winner selected claim your reward before midnight.',
 'Your OTP is needed to confirm your prize.', 'Click this link to update your card details immediately.',
 'Security alert reset your password immediately or access will be blocked.', 'Free voucher waiting click here to collect.',
 'Your payment failed update your card at this link.', 'Exclusive loan approved pay a small fee to release funds.',
 'You have won a lottery jackpot call now to claim.', 'Act now to receive your cash reward.',
 'Unusual login detected confirm your password through this link.', 'Your bank security requires immediate verification.',
 'You are eligible for a free gift click here.', 'Final warning send the OTP to unlock your account.',
 'Congratulations your reward is waiting click the link to receive it.', 'Urgent payment verification required enter your passcode.',
 'Claim your cash prize now before the offer expires.', 'Your card is blocked verify your credentials immediately.',
 'Lottery winner selected call now and pay the processing fee.', 'Free bonus available click to claim today.',
 'Account suspension notice verify identity through the attached link.', 'Investment profit guaranteed send the fee now.',
 'Your password expired click the secure portal to reset immediately.', 'Winner winner free voucher claim now.',
 'Immediate action required to release your reward send the verification code.', 'Your bank account needs urgent confirmation click this link.',
 'Prize notification you were selected call now to receive cash.', 'Loan approved with zero paperwork pay the release fee.',
 'Security alert your login is blocked confirm OTP immediately.', 'Limited time reward click here before midnight.',
 'Your payment is pending update your card details now.', 'Congratulations claim your lottery winnings through this link.',
 'Final notice verify your identity or your account will be suspended.', 'Free cash bonus waiting claim it now.',
 'Urgent account alert enter your password and OTP to continue.', 'Exclusive prize offer click to collect your voucher.',
 'Your card requires verification provide your banking details immediately.', 'Act immediately to avoid account suspension and confirm your credentials.',
 'Cash reward available call now to claim your prize.', 'You won a free gift claim now through this link.'
]
SUSPICIOUS=[
 'Please verify your account using the new company portal.', 'Your delivery needs confirmation, please check the tracking portal.',
 'Please confirm the payment schedule with the vendor.', 'Your package tracking needs an update before delivery.',
 'Please verify the invoice details before payment.', 'The account team asked me to confirm the request.',
 'Please check the delivery link in the official app.', 'Can you confirm the booking and call the office?',
 'Please verify the registration link before opening it.', 'The courier sent a tracking message that needs confirmation.',
 'Please confirm your delivery address with the carrier.', 'Can you verify the payment reference before we proceed?',
 'Please check this login notification with the IT team.', 'The security team asked us to confirm the account status.',
 'Please verify the receipt before submitting the expense.', 'The bank statement needs confirmation for our accounting report.',
 'Please check the official tracking portal for the shipment.', 'Can you confirm the invoice and payment details?',
 'Please verify the event link before registration.', 'The package is waiting for delivery confirmation.',
 'Please confirm the account information with the office.', 'Can you verify the document link before opening it?',
 'The payment record needs a quick confirmation.', 'Please check the sender and verify the delivery request.',
 'The tracking portal asks for confirmation of the shipment.', 'Please verify the account request with support before responding.',
 'Can you confirm the payment request through the official contact?', 'Please check the package status and confirm the delivery.',
 'The login notification should be verified with our IT administrator.', 'Please confirm the invoice before the scheduled payment.',
 'Please verify the registration request with the organizer.', 'The courier delivery requires address confirmation.',
 'Please check the account status before making the payment.', 'Confirm the tracking number with the official carrier.',
 'Please verify the attached document before submitting it.', 'The office asked for payment confirmation.',
 'Please check the sender before following the registration link.', 'Can you verify this delivery request with the carrier?',
 'The vendor needs confirmation of the invoice details.', 'Please verify the booking request with the organizer.',
 'The account request should be confirmed with support.', 'Please check the payment reference before approving it.'
]
CASES=[('NORMAL',x,'') for x in NORMAL]+[('SPAM',x,'') for x in SPAM]+[('SUSPICIOUS',x,'Unknown') for x in SUSPICIOUS]

# Additional regression coverage: multilingual-style Roman Urdu/Hinglish and
# realistic hard negatives. These are intentionally deterministic and do not
# claim to represent a production benchmark.
NORMAL_EXTRA=[
 'Kal class 9 baje hai, report le ana.', 'Bhai meeting 5 baje confirm hai.',
 'Please send the assignment file to our group.', 'Aaj library mein study karte hain.',
 'Teacher ne kaha report Friday se pehle submit karni hai.', 'I will call you after the lecture.',
 'Office ka invoice accounting team ko bhej diya hai.', 'Courier ka official tracking number spreadsheet mein hai.',
 'Our bank statement is needed for the accounting report.', 'Please update the presentation figures before submission.',
 'Congratulations on completing your college project.', 'Prize ceremony will start after lunch at college.'
]
SPAM_EXTRA=[
 'URGENT verify your bank account and enter OTP using this link now.',
 'You won a free cash reward, click to claim immediately.',
 'Final warning your card is blocked, confirm your password now.',
 'Exclusive voucher winner, call now and pay the processing fee.',
 'Your account will be suspended, click the link and send your passcode.',
 'Guaranteed investment profit, transfer the release fee immediately.',
 'Free gift waiting, open this link and claim your reward today.',
 'Lottery jackpot winner selected, call now to receive cash.',
 'Payment failed, update card details through this link immediately.',
 'Urgent security alert, verify credentials and OTP to unlock account.',
 'Congratulations you won a prize, claim the cash reward before midnight.',
 'Loan approved, pay the fee now to release your funds.'
]
SUSPICIOUS_EXTRA=[
 'Please verify the invoice with the vendor before payment.',
 'Can you confirm the delivery address with the carrier?',
 'Please check the official account portal before responding.',
 'The registration request needs confirmation from the organizer.',
 'Please verify the payment reference with the finance team.',
 'Can you confirm the shipment status with the official carrier?',
 'Please check the login notification with your IT administrator.',
 'The vendor asked for confirmation of the invoice details.',
 'Please verify the booking request through the official office number.',
 'Can you check the account request with support before proceeding?',
 'Please confirm the package tracking information with the courier.',
 'The office needs verification of the expense receipt.'
]
CASES += [('NORMAL',x,'') for x in NORMAL_EXTRA]
CASES += [('SPAM',x,'') for x in SPAM_EXTRA]
CASES += [('SUSPICIOUS',x,'Unknown') for x in SUSPICIOUS_EXTRA]

assert len(CASES)>=160
D=SpamDetector(); failures=[]
for i,(expected,text,sender) in enumerate(CASES,1):
    r=D.analyze(text,sender)
    if r['classification']!=expected:
        failures.append({'id':i,'expected':expected,'actual':r['classification'],'risk':r['risk_score'],'text':text})
result={'total_cases':len(CASES),'passed':len(CASES)-len(failures),'failed':len(failures),'pass_rate':round((len(CASES)-len(failures))/len(CASES),4),'failures':failures}
Path(ROOT/'reports'/'automated_test_report.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
if failures: raise SystemExit(1)
