import csv, sys, threading, webbrowser, traceback, os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from detector import SpamDetector, save_scan, history, init_db
try:
    from live_call import LiveCallEngine
    LIVE_CALL_AVAILABLE = True
except Exception:
    LiveCallEngine = None
    LIVE_CALL_AVAILABLE = False

NAVY="#172033"; BLUE="#3B82F6"; PURPLE="#8B5CF6"; ORANGE="#F59E0B"; RED="#EF4444"
WHITE="#FFFFFF"; BG="#0F172A"; PANEL="#172033"; MUTED="#94A3B8"; GREEN="#22C55E"

def _show_friendly_error(exc_type, exc_value, exc_tb):
    # Keep unexpected errors visible but never dump a console traceback at the
    # user. A small log is also written to the per-user data directory.
    try:
        log_dir = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "SpamMessageCallDetector"
        log_dir.mkdir(parents=True, exist_ok=True)
        (log_dir / "error.log").write_text("".join(traceback.format_exception(exc_type, exc_value, exc_tb)), encoding="utf-8")
    except Exception:
        pass
    try:
        messagebox.showerror("Spam Message & Call Detector", f"The application handled an unexpected error.\n\n{exc_value}\n\nA diagnostic log was saved in your LocalAppData folder.")
    except Exception:
        pass

sys.excepthook = _show_friendly_error

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Spam Message & Call Detector")
        self.geometry("1180x760")
        self.minsize(1000,680)
        self.configure(bg=BG)
        init_db()
        self.detector=SpamDetector()
        self.last_result=None
        self.live_engine=None
        self._style()
        self._build()
        self._refresh_dashboard()

    def _style(self):
        s=ttk.Style(self); s.theme_use("clam")
        s.configure("TNotebook",background=BG,borderwidth=0)
        s.configure("TNotebook.Tab",background=PANEL,foreground=MUTED,padding=(18,10))
        s.map("TNotebook.Tab",background=[("selected",BLUE)],foreground=[("selected",WHITE)])
        s.configure("Treeview",background=PANEL,fieldbackground=PANEL,foreground=WHITE,rowheight=32,borderwidth=0)
        s.configure("Treeview.Heading",background=NAVY,foreground=WHITE,font=("Segoe UI",10,"bold"))
        s.configure("TProgressbar",troughcolor="#263248",background=BLUE,borderwidth=0)

    def _label(self,parent,text,size=11,color=WHITE,bold=False):
        return tk.Label(parent,text=text,bg=parent.cget("bg"),fg=color,font=("Segoe UI",size,"bold" if bold else "normal"))

    def _build(self):
        top=tk.Frame(self,bg=NAVY,height=76); top.pack(fill="x")
        tk.Label(top,text="◉  SPAM MESSAGE & CALL DETECTOR",bg=NAVY,fg=WHITE,font=("Segoe UI",20,"bold")).pack(side="left",padx=28,pady=18)
        status="ML ENGINE ONLINE" if self.detector.model_loaded else "RULE ENGINE ONLY"
        tk.Label(top,text="●  "+status,bg=NAVY,fg=GREEN if self.detector.model_loaded else ORANGE,font=("Segoe UI",10,"bold")).pack(side="right",padx=28)

        nb=ttk.Notebook(self); nb.pack(fill="both",expand=True,padx=18,pady=18)
        self.analyze_tab=tk.Frame(nb,bg=BG); self.dashboard_tab=tk.Frame(nb,bg=BG)
        self.history_tab=tk.Frame(nb,bg=BG); self.live_tab=tk.Frame(nb,bg=BG); self.guide_tab=tk.Frame(nb,bg=BG)
        nb.add(self.analyze_tab,text="  Analyze  "); nb.add(self.dashboard_tab,text="  Dashboard  ")
        nb.add(self.history_tab,text="  History  "); nb.add(self.live_tab,text="  Live Call  "); nb.add(self.guide_tab,text="  Safety Guide  ")
        self._analyze_ui(); self._dashboard_ui(); self._history_ui(); self._live_ui(); self._guide_ui()
        if LIVE_CALL_AVAILABLE:
            self.live_engine=LiveCallEngine(self.detector, self._live_transcript, self._live_result, self._live_status)
        else:
            self.live_start.config(state="disabled")
            self._live_status("Live Call module unavailable; message analysis remains fully available.")
        self.protocol("WM_DELETE_WINDOW", self._close_app)

    def _analyze_ui(self):
        left=tk.Frame(self.analyze_tab,bg=PANEL); left.pack(side="left",fill="both",expand=True,padx=(0,10))
        right=tk.Frame(self.analyze_tab,bg=PANEL,width=400); right.pack(side="right",fill="y",padx=(10,0)); right.pack_propagate(False)
        tk.Label(left,text="MESSAGE ANALYSIS",bg=PANEL,fg=WHITE,font=("Segoe UI",14,"bold")).pack(anchor="w",padx=22,pady=(22,4))
        tk.Label(left,text="Classify SMS, call-related text and suspicious requests.",bg=PANEL,fg=MUTED,font=("Segoe UI",10)).pack(anchor="w",padx=22)
        tk.Label(left,text="Sender / Caller (optional)",bg=PANEL,fg=WHITE,font=("Segoe UI",10,"bold")).pack(anchor="w",padx=22,pady=(24,6))
        self.sender=tk.Entry(left,bg="#243047",fg=WHITE,insertbackground=WHITE,relief="flat",font=("Segoe UI",11))
        self.sender.pack(fill="x",padx=22,ipady=10)
        tk.Label(left,text="Message / Call Text",bg=PANEL,fg=WHITE,font=("Segoe UI",10,"bold")).pack(anchor="w",padx=22,pady=(18,6))
        self.text=tk.Text(left,height=10,bg="#0B1220",fg=WHITE,insertbackground=WHITE,relief="flat",font=("Segoe UI",11),wrap="word")
        self.text.pack(fill="both",expand=True,padx=22)
        btn=tk.Frame(left,bg=PANEL); btn.pack(fill="x",padx=22,pady=18)
        tk.Button(btn,text="ANALYZE MESSAGE",command=self.analyze,bg=BLUE,fg=WHITE,relief="flat",font=("Segoe UI",11,"bold"),padx=22,pady=11,cursor="hand2").pack(side="left")
        tk.Button(btn,text="CLEAR",command=self.clear,bg="#334155",fg=WHITE,relief="flat",font=("Segoe UI",10,"bold"),padx=18,pady=11).pack(side="left",padx=10)
        tk.Button(btn,text="EXPORT RESULT",command=self.export_result,bg="#334155",fg=WHITE,relief="flat",font=("Segoe UI",10,"bold"),padx=18,pady=11).pack(side="right")

        tk.Label(right,text="DETECTION RESULT",bg=PANEL,fg=WHITE,font=("Segoe UI",14,"bold")).pack(anchor="w",padx=22,pady=(22,8))
        self.result_badge=tk.Label(right,text="WAITING",bg="#334155",fg=WHITE,font=("Segoe UI",18,"bold"),padx=15,pady=12)
        self.result_badge.pack(fill="x",padx=22)
        self.risk_title=tk.Label(right,text="Risk Score",bg=PANEL,fg=MUTED,font=("Segoe UI",10)); self.risk_title.pack(anchor="w",padx=22,pady=(22,4))
        self.risk=tk.Label(right,text="—",bg=PANEL,fg=WHITE,font=("Segoe UI",32,"bold")); self.risk.pack(anchor="w",padx=22)
        self.bar=ttk.Progressbar(right,maximum=100,length=320); self.bar.pack(fill="x",padx=22,pady=(0,15))
        self.meta=tk.Label(right,text="ML probability: —\nRule indicators: —",bg=PANEL,fg=MUTED,justify="left",font=("Segoe UI",10)); self.meta.pack(anchor="w",padx=22)
        tk.Label(right,text="WHY THIS RESULT",bg=PANEL,fg=WHITE,font=("Segoe UI",10,"bold")).pack(anchor="w",padx=22,pady=(22,6))
        self.reasons=tk.Text(right,height=6,bg="#0B1220",fg=WHITE,relief="flat",font=("Segoe UI",10),wrap="word"); self.reasons.pack(fill="x",padx=22)
        tk.Label(right,text="SAFETY RECOMMENDATION",bg=PANEL,fg=WHITE,font=("Segoe UI",10,"bold")).pack(anchor="w",padx=22,pady=(10,3))
        rec_frame=tk.Frame(right,bg="#0B1220"); rec_frame.pack(fill="x",padx=22,pady=(0,12))
        self.rec=tk.Text(rec_frame,height=3,bg="#0B1220",fg=MUTED,relief="flat",font=("Segoe UI",10),wrap="word",
                         padx=8,pady=6,highlightthickness=0,borderwidth=0)
        self.rec.pack(side="left",fill="both",expand=True)
        rec_scroll=ttk.Scrollbar(rec_frame,orient="vertical",command=self.rec.yview)
        rec_scroll.pack(side="right",fill="y")
        self.rec.configure(yscrollcommand=rec_scroll.set)
        self.rec.insert("1.0","Analyze a message to receive guidance.")
        self.rec.configure(state="disabled")

    def analyze(self):
        try:
            r=self.detector.analyze(self.text.get("1.0","end"),self.sender.get())
        except ValueError as e:
            messagebox.showwarning("Input required",str(e)); return
        self.last_result=r; save_scan(r)
        c=RED if r["classification"]=="SPAM" else ORANGE if r["classification"]=="SUSPICIOUS" else GREEN
        self.result_badge.config(text=f'{r["classification"]}  •  {r["severity"]}',bg=c)
        self.risk.config(text=f'{r["risk_score"]:.0f}%')
        self.bar["value"]=r["risk_score"]
        self.meta.config(text=f'ML probability: {r["ml_probability"]:.2f}%\nRule indicators: {r["rule_score"]:.0f}/100')
        self.reasons.delete("1.0","end")
        for x in r["reasons"]: self.reasons.insert("end","• "+x+"\n")
        self.rec.config(state="normal",fg=WHITE)
        self.rec.delete("1.0","end")
        self.rec.insert("1.0",r["recommendation"])
        self.rec.config(state="disabled")
        self._refresh_dashboard(); self._refresh_history()

    def clear(self):
        self.sender.delete(0,"end"); self.text.delete("1.0","end")
        self.result_badge.config(text="WAITING",bg="#334155"); self.risk.config(text="—"); self.bar["value"]=0
        self.meta.config(text="ML probability: —\nRule indicators: —"); self.reasons.delete("1.0","end")
        self.rec.config(state="normal",fg=MUTED)
        self.rec.delete("1.0","end")
        self.rec.insert("1.0","Analyze a message to receive guidance.")
        self.rec.config(state="disabled")
        self.last_result=None

    def export_result(self):
        if not self.last_result: messagebox.showinfo("Nothing to export","Analyze a message first."); return
        path=filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Text file","*.txt"),("JSON","*.json")])
        if not path:return
        if path.lower().endswith(".json"):
            import json; Path(path).write_text(json.dumps(self.last_result,indent=2),encoding="utf-8")
        else:
            r=self.last_result
            Path(path).write_text("SPAM MESSAGE & CALL DETECTOR\n\n"+f'Classification: {r["classification"]}\nSeverity: {r["severity"]}\nRisk: {r["risk_score"]}%\nML Probability: {r["ml_probability"]}%\n\nReasons:\n'+"\n".join(" - "+x for x in r["reasons"])+f'\n\nRecommendation:\n{r["recommendation"]}\n',encoding="utf-8")
        messagebox.showinfo("Export complete","Result exported successfully.")

    def _dashboard_ui(self):
        self.cards=tk.Frame(self.dashboard_tab,bg=BG); self.cards.pack(fill="x")
        self.card_labels={}
        for key,title in [("total","TOTAL SCANS"),("spam","SPAM"),("suspicious","SUSPICIOUS"),("normal","NORMAL")]:
            f=tk.Frame(self.cards,bg=PANEL); f.pack(side="left",fill="x",expand=True,padx=6,pady=6)
            tk.Label(f,text=title,bg=PANEL,fg=MUTED,font=("Segoe UI",9,"bold")).pack(anchor="w",padx=18,pady=(15,3))
            l=tk.Label(f,text="0",bg=PANEL,fg=WHITE,font=("Segoe UI",26,"bold")); l.pack(anchor="w",padx=18,pady=(0,15)); self.card_labels[key]=l
        box=tk.Frame(self.dashboard_tab,bg=PANEL); box.pack(fill="both",expand=True,pady=12)
        tk.Label(box,text="RISK DISTRIBUTION",bg=PANEL,fg=WHITE,font=("Segoe UI",13,"bold")).pack(anchor="w",padx=20,pady=18)
        self.chart=tk.Canvas(box,bg=PANEL,highlightthickness=0,height=300); self.chart.pack(fill="both",expand=True,padx=20,pady=10)

    def _refresh_dashboard(self):
        rows=history(500)
        counts={k:0 for k in ("spam","suspicious","normal")}
        for r in rows:
            k=r["classification"].lower()
            if k in counts: counts[k]+=1
        self.card_labels["total"].config(text=str(len(rows)))
        for k in counts:self.card_labels[k].config(text=str(counts[k]))
        if hasattr(self,"chart"):
            self.chart.delete("all"); w=max(self.chart.winfo_width(),700); h=300
            vals=[counts["normal"],counts["suspicious"],counts["spam"]]; labels=["NORMAL","SUSPICIOUS","SPAM"]
            maxv=max(vals+[1]); bw=120
            for i,(v,lab) in enumerate(zip(vals,labels)):
                x=90+i*210; bh=(v/maxv)*180
                self.chart.create_rectangle(x,h-55-bh,x+bw,h-55,fill=BLUE if i==0 else ORANGE if i==1 else RED,outline="")
                self.chart.create_text(x+bw/2,h-30,text=f"{v}",fill=WHITE,font=("Segoe UI",14,"bold"))
                self.chart.create_text(x+bw/2,h-10,text=lab,fill=MUTED,font=("Segoe UI",10,"bold"))

    def _history_ui(self):
        head=tk.Frame(self.history_tab,bg=BG); head.pack(fill="x")
        tk.Label(head,text="SCAN HISTORY",bg=BG,fg=WHITE,font=("Segoe UI",16,"bold")).pack(side="left")
        tk.Button(head,text="Refresh",command=self._refresh_history,bg=BLUE,fg=WHITE,relief="flat",padx=15,pady=7).pack(side="right")
        cols=("timestamp","sender","classification","risk","text")
        self.tree=ttk.Treeview(self.history_tab,columns=cols,show="headings")
        widths={"timestamp":160,"sender":160,"classification":120,"risk":80,"text":520}
        for c in cols:self.tree.heading(c,text=c.upper());self.tree.column(c,width=widths[c],anchor="w")
        self.tree.pack(fill="both",expand=True,pady=14)
        self._refresh_history()

    def _refresh_history(self):
        if not hasattr(self,"tree"):return
        for i in self.tree.get_children():self.tree.delete(i)
        for r in history(100):
            self.tree.insert("", "end", values=(r["timestamp"],r["sender"] or "—",r["classification"],f'{r["risk"]:.0f}%',r["text"][:80]))

    def _live_ui(self):
        top=tk.Frame(self.live_tab,bg=PANEL); top.pack(fill="x",pady=(0,10))
        tk.Label(top,text="LIVE CALL ANALYSIS",bg=PANEL,fg=WHITE,font=("Segoe UI",16,"bold")).pack(anchor="w",padx=22,pady=(18,4))
        tk.Label(top,text="Consent-based real-time speech-to-text and spam-risk analysis. No audio is saved by this app.",bg=PANEL,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w",padx=22,pady=(0,14))
        row=tk.Frame(top,bg=PANEL); row.pack(fill="x",padx=22,pady=(0,16))
        tk.Label(row,text="Audio source",bg=PANEL,fg=WHITE,font=("Segoe UI",10,"bold")).pack(side="left")
        self.live_mode=tk.StringVar(value="microphone")
        mode=ttk.Combobox(row,textvariable=self.live_mode,state="readonly",values=["microphone","system"],width=13)
        mode.pack(side="left",padx=8); mode.bind("<<ComboboxSelected>>",lambda e:self._refresh_live_devices())
        tk.Label(row,text="Device",bg=PANEL,fg=WHITE,font=("Segoe UI",10,"bold")).pack(side="left",padx=(16,4))
        self.live_device=tk.StringVar()
        self.live_devices=ttk.Combobox(row,textvariable=self.live_device,state="readonly",width=42); self.live_devices.pack(side="left",padx=5)
        tk.Button(row,text="Refresh",command=self._refresh_live_devices,bg="#334155",fg=WHITE,relief="flat",padx=12,pady=7).pack(side="left",padx=6)
        self.live_start=tk.Button(row,text="START LIVE ANALYSIS",command=self._start_live,bg=GREEN,fg=WHITE,relief="flat",font=("Segoe UI",10,"bold"),padx=15,pady=8); self.live_start.pack(side="left",padx=8)
        tk.Button(row,text="STOP",command=self._stop_live,bg=RED,fg=WHITE,relief="flat",font=("Segoe UI",10,"bold"),padx=15,pady=8).pack(side="left")
        self._refresh_live_devices()

        main=tk.Frame(self.live_tab,bg=BG); main.pack(fill="both",expand=True)
        left=tk.Frame(main,bg=PANEL); left.pack(side="left",fill="both",expand=True,padx=(0,8))
        right=tk.Frame(main,bg=PANEL,width=340); right.pack(side="right",fill="y",padx=(8,0)); right.pack_propagate(False)
        tk.Label(left,text="LIVE TRANSCRIPT",bg=PANEL,fg=WHITE,font=("Segoe UI",12,"bold")).pack(anchor="w",padx=18,pady=(18,6))
        self.live_transcript=tk.Text(left,bg="#0B1220",fg=WHITE,insertbackground=WHITE,relief="flat",font=("Segoe UI",11),wrap="word")
        self.live_transcript.pack(fill="both",expand=True,padx=18,pady=(0,12))
        self.live_status=tk.Label(left,text="Ready. Choose microphone or PC system audio, then start.",bg=PANEL,fg=MUTED,font=("Segoe UI",9),anchor="w")
        self.live_status.pack(fill="x",padx=18,pady=(0,16))
        tk.Label(right,text="REAL-TIME RISK",bg=PANEL,fg=WHITE,font=("Segoe UI",12,"bold")).pack(anchor="w",padx=18,pady=(18,10))
        self.live_badge=tk.Label(right,text="WAITING",bg="#334155",fg=WHITE,font=("Segoe UI",18,"bold"),padx=10,pady=10); self.live_badge.pack(fill="x",padx=18)
        self.live_risk=tk.Label(right,text="—",bg=PANEL,fg=WHITE,font=("Segoe UI",32,"bold")); self.live_risk.pack(anchor="w",padx=18,pady=(18,0))
        self.live_meta=tk.Label(right,text="No speech analyzed yet.",bg=PANEL,fg=MUTED,justify="left",wraplength=285,font=("Segoe UI",10)); self.live_meta.pack(anchor="w",padx=18,pady=8)
        tk.Label(right,text="DETECTED INDICATORS",bg=PANEL,fg=WHITE,font=("Segoe UI",10,"bold")).pack(anchor="w",padx=18,pady=(14,5))
        self.live_reasons=tk.Text(right,height=11,bg="#0B1220",fg=WHITE,relief="flat",font=("Segoe UI",9),wrap="word"); self.live_reasons.pack(fill="both",expand=True,padx=18,pady=(0,18))
        self.live_reasons.config(state="disabled")

    def _refresh_live_devices(self):
        try:
            if not LIVE_CALL_AVAILABLE or LiveCallEngine is None:
                names=[]
            else:
                names=LiveCallEngine.microphones() if self.live_mode.get()=="microphone" else LiveCallEngine.speakers()
            self.live_devices["values"]=names
            if names: self.live_device.set(names[0])
            else: self.live_device.set("No compatible audio device found")
        except Exception as e:
            self.live_devices["values"]=[]; self.live_device.set("Audio device error")
            self._live_status(str(e))

    def _start_live(self):
        if self.live_engine is None:
            messagebox.showwarning("Live Call unavailable", "Live Call components could not be initialized on this PC. Message analysis is still available.")
            return
        if self.live_device.get().startswith("No ") or not self.live_device.get():
            messagebox.showwarning("Audio device","Select a valid audio input first."); return
        self.live_start.config(state="disabled")
        self._live_status("Starting live analysis…")
        ok=self.live_engine.start(self.live_mode.get(),self.live_device.get(),4)
        if not ok:self.live_start.config(state="normal")

    def _stop_live(self):
        if self.live_engine:
            self.live_engine.stop()
        self.live_start.config(state="normal")

    def _live_transcript(self,text):
        self.after(0,lambda:self.live_transcript.insert("end",text+"\n\n"))
        self.after(0,lambda:self.live_transcript.see("end"))

    def _live_result(self,r):
        def update():
            c=RED if r["classification"]=="SPAM" else ORANGE if r["classification"]=="SUSPICIOUS" else GREEN
            self.live_badge.config(text=f'{r["classification"]} • {r["severity"]}',bg=c)
            self.live_risk.config(text=f'{r["risk_score"]:.0f}%')
            self.live_meta.config(text=f'ML probability: {r["ml_probability"]:.1f}%\nRule indicators: {r["rule_score"]:.0f}/100')
            self.live_reasons.config(state="normal"); self.live_reasons.delete("1.0","end")
            for x in r["reasons"]: self.live_reasons.insert("end","• "+x+"\n")
            self.live_reasons.config(state="disabled")
        self.after(0,update)

    def _live_status(self,msg):
        self.after(0,lambda:self.live_status.config(text=msg))

    def _close_app(self):
        try:self.live_engine.stop()
        except Exception:pass
        self.destroy()

    def _guide_ui(self):
        text="""SAFETY GUIDE

1. LINKS
Never open an unexpected link just because a message creates urgency. Verify the domain independently.

2. OTP / PASSWORDS
Never share OTPs, verification codes, passwords or recovery codes with callers or message senders.

3. MONEY
Do not send money, gift cards, crypto or bank transfers because of a threatening or urgent message.

4. UNKNOWN CALLERS
If a caller claims to be a bank, police, delivery company or service provider, hang up and call the official number yourself.

5. FALSE POSITIVES
A detection score is an advisory signal, not proof of fraud. Confirm important decisions using trusted channels.

CLASSIFICATION
NORMAL: low observed risk.
SUSPICIOUS: mixed or concerning indicators; verify before acting.
SPAM: strong spam/scam indicators; avoid interaction and verify independently.
"""
        tk.Label(self.guide_tab,text=text,bg=PANEL,fg=WHITE,justify="left",anchor="nw",font=("Segoe UI",12),padx=28,pady=28).pack(fill="both",expand=True)

if __name__=="__main__":
    App().mainloop()
