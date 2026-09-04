from pathlib import Path

path = Path("spam_detector_desktop.py")
s = path.read_text(encoding="utf-8")

old_ui = '''        tk.Label(right,text="SAFETY RECOMMENDATION",bg=PANEL,fg=WHITE,font=("Segoe UI",10,"bold")).pack(anchor="w",padx=22,pady=(14,4))
        self.rec=tk.Label(right,text="Analyze a message to receive guidance.",bg=PANEL,fg=MUTED,justify="left",anchor="nw",wraplength=350,font=("Segoe UI",10)); self.rec.pack(fill="x",anchor="w",padx=22,pady=(0,18))
'''
new_ui = '''        tk.Label(right,text="SAFETY RECOMMENDATION",bg=PANEL,fg=WHITE,font=("Segoe UI",10,"bold")).pack(anchor="w",padx=22,pady=(10,3))
        rec_frame=tk.Frame(right,bg="#0B1220"); rec_frame.pack(fill="x",padx=22,pady=(0,12))
        self.rec=tk.Text(rec_frame,height=3,bg="#0B1220",fg=MUTED,relief="flat",font=("Segoe UI",10),wrap="word",
                         padx=8,pady=6,highlightthickness=0,borderwidth=0)
        self.rec.pack(side="left",fill="both",expand=True)
        rec_scroll=ttk.Scrollbar(rec_frame,orient="vertical",command=self.rec.yview)
        rec_scroll.pack(side="right",fill="y")
        self.rec.configure(yscrollcommand=rec_scroll.set)
        self.rec.insert("1.0","Analyze a message to receive guidance.")
        self.rec.configure(state="disabled")
'''

old_analyze = '''        self.rec.config(text=r["recommendation"],fg=WHITE)
'''
new_analyze = '''        self.rec.config(state="normal",fg=WHITE)
        self.rec.delete("1.0","end")
        self.rec.insert("1.0",r["recommendation"])
        self.rec.config(state="disabled")
'''

old_clear = '''        self.meta.config(text="ML probability: —\\nRule indicators: —"); self.reasons.delete("1.0","end")
        self.rec.config(text="Analyze a message to receive guidance.",fg=MUTED); self.last_result=None
'''
new_clear = '''        self.meta.config(text="ML probability: —\\nRule indicators: —"); self.reasons.delete("1.0","end")
        self.rec.config(state="normal",fg=MUTED)
        self.rec.delete("1.0","end")
        self.rec.insert("1.0","Analyze a message to receive guidance.")
        self.rec.config(state="disabled")
        self.last_result=None
'''

for old, new in ((old_ui, new_ui), (old_analyze, new_analyze), (old_clear, new_clear)):
    if old not in s:
        raise SystemExit("Expected source block not found; refusing partial modification.")
    s = s.replace(old, new, 1)

path.write_text(s, encoding="utf-8")
print("UI safety recommendation fix applied")
