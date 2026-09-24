"""
NEET AllRounder - Preparation Tracker
Single-file KivyMD app. Data local JSON me store hota hai.
"""
import os
import json
from datetime import date, datetime, timedelta
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.dialog import MDDialog
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.progressbar import MDProgressBar

# ---------------- SYLLABUS DATA ----------------
# (name, total_lectures) — approximate NCERT based, sum ~ 680
CHAPTERS = {
    "Physics": [
        ("Physical World & Units", 5), ("Motion in Straight Line", 8),
        ("Motion in Plane", 8), ("Laws of Motion", 10),
        ("Work, Energy & Power", 8), ("System of Particles & Rotational", 8),
        ("Gravitation", 6), ("Mechanical Properties of Solids", 5),
        ("Mechanical Properties of Fluids", 6), ("Thermal Properties", 6),
        ("Thermodynamics", 8), ("Kinetic Theory", 5),
        ("Oscillations", 8), ("Waves", 8),
        ("Electric Charges & Fields", 9), ("Electrostatic Potential", 8),
        ("Current Electricity", 10), ("Moving Charges & Magnetism", 10),
        ("Magnetism & Matter", 6), ("EMI", 10),
        ("AC", 8), ("EM Waves", 3),
        ("Ray Optics", 10), ("Wave Optics", 8),
        ("Dual Nature of Radiation", 6), ("Atoms", 5),
        ("Nuclei", 5), ("Semiconductors", 8),
        ("Experimental Skills", 9),
    ],
    "Chemistry": [
        ("Some Basic Concepts", 5), ("Structure of Atom", 8),
        ("Classification & Periodicity", 8), ("Chemical Bonding", 10),
        ("States of Matter", 6), ("Thermodynamics", 8),
        ("Equilibrium", 8), ("Redox Reactions", 5),
        ("Hydrogen", 4), ("s-Block Elements", 5),
        ("p-Block (13,14)", 6), ("Organic Basics (GOC)", 10),
        ("Hydrocarbons", 8), ("Environmental Chemistry", 3),
        ("Solid State", 6), ("Solutions", 7),
        ("Electrochemistry", 8), ("Chemical Kinetics", 7),
        ("Surface Chemistry", 5), ("Metallurgy", 6),
        ("p-Block (15,16,17,18)", 10), ("d & f Block", 8),
        ("Coordination Compounds", 8), ("Haloalkanes & Haloarenes", 8),
        ("Alcohols, Phenols, Ethers", 8), ("Aldehydes, Ketones, Acids", 10),
        ("Amines", 7), ("Biomolecules", 6),
        ("Polymers", 4), ("Chemistry in Everyday Life", 3),
    ],
    "Botany": [
        ("Living World", 3), ("Biological Classification", 6),
        ("Plant Kingdom", 6), ("Morphology of Plants", 5),
        ("Anatomy of Plants", 6), ("Cell: Unit of Life", 8),
        ("Cell Cycle & Division", 6), ("Biomolecules (Bio)", 6),
        ("Transport in Plants", 5), ("Mineral Nutrition", 5),
        ("Photosynthesis", 7), ("Respiration in Plants", 6),
        ("Plant Growth & Development", 6), ("Reproduction in Plants", 6),
        ("Sexual Reproduction in Flowering Plants", 8),
        ("Principles of Inheritance", 10), ("Molecular Basis of Inheritance", 10),
        ("Biotechnology - Principles", 8), ("Biotechnology - Applications", 6),
        ("Ecology & Ecosystem", 8),
    ],
    "Zoology": [
        ("Animal Kingdom", 8), ("Structural Organisation in Animals", 5),
        ("Digestion & Absorption", 6), ("Breathing & Exchange of Gases", 5),
        ("Body Fluids & Circulation", 7), ("Excretory Products", 6),
        ("Locomotion & Movement", 6), ("Neural Control", 7),
        ("Chemical Coordination", 8), ("Human Reproduction", 8),
        ("Reproductive Health", 5), ("Evolution", 8),
        ("Human Health & Disease", 7), ("Microbes in Human Welfare", 6),
        ("Ecosystem (Bio)", 5), ("Biodiversity & Conservation", 6),
        ("Environmental Issues", 5), ("Applied Biology", 7),
    ],
}

SUBJECT_COLORS = {
    "Physics": (0.2, 0.5, 0.9, 1),
    "Chemistry": (0.9, 0.5, 0.1, 1),
    "Botany": (0.1, 0.7, 0.3, 1),
    "Zoology": (0.8, 0.2, 0.4, 1),
}


# ---------------- DATA MANAGER ----------------
class DataManager:
    def __init__(self, path):
        self.path = path
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = self._default()
        else:
            self.data = self._default()
        self._ensure_keys()
        self.save()

    def _default(self):
        syllabus = {}
        for subj, chs in CHAPTERS.items():
            syllabus[subj] = [{"name": n, "total": t, "done": 0} for n, t in chs]
        return {
            "syllabus": syllabus,
            "daily": {},
            "mocks": [],
            "streak": 0,
            "last_active": "",
            "start_date": date.today().isoformat(),
        }

    def _ensure_keys(self):
        for k, v in self._default().items():
            if k not in self.data:
                self.data[k] = v
        # add any new chapters added later in CHAPTERS
        for subj, chs in CHAPTERS.items():
            if subj not in self.data["syllabus"]:
                self.data["syllabus"][subj] = [
                    {"name": n, "total": t, "done": 0} for n, t in chs
                ]

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print("Save error:", e)

    # --- Stats ---
    def total_lectures(self):
        return sum(ch["total"] for subj in self.data["syllabus"].values() for ch in subj)

    def done_lectures(self):
        return sum(ch["done"] for subj in self.data["syllabus"].values() for ch in subj)

    def overall_percent(self):
        t = self.total_lectures()
        return 0 if t == 0 else round(self.done_lectures() / t * 100, 1)

    def subject_stats(self, subj):
        chs = self.data["syllabus"][subj]
        total = sum(c["total"] for c in chs)
        done = sum(c["done"] for c in chs)
        return done, total, (0 if total == 0 else round(done / total * 100, 1))

    def remaining_in_subject(self, subj):
        return sum(c["total"] - c["done"] for c in self.data["syllabus"][subj])

    # --- Daily Task Generation ---
    def generate_daily_tasks(self, dstr=None):
        if dstr is None:
            dstr = date.today().isoformat()
        if dstr in self.data["daily"]:
            return self.data["daily"][dstr]

        is_sunday = date.fromisoformat(dstr).weekday() == 6
        tasks = []

        if is_sunday:
            tasks.append({"id": f"{dstr}-mock", "text": "Full Mock Test (NEET pattern, 200Q, 3h 20m)",
                          "type": "mock", "done": False, "subject": None, "chapter": None})
            tasks.append({"id": f"{dstr}-analysis", "text": "Mock Analysis - 2 ghante, error notebook update",
                          "type": "revision", "done": False, "subject": None, "chapter": None})
            for subj in CHAPTERS.keys():
                tasks.append({"id": f"{dstr}-rev-{subj}", "text": f"{subj} - 30 din purane chapters revise",
                              "type": "revision", "done": False, "subject": subj, "chapter": None})
        else:
            # distribute 5 lectures among subjects by remaining ratio
            remaining = {s: self.remaining_in_subject(s) for s in CHAPTERS.keys()}
            total_rem = sum(remaining.values()) or 1
            plan = {}
            raw = {s: (remaining[s] / total_rem) * 5 for s in remaining}
            floors = {s: int(raw[s]) for s in raw}
            left = 5 - sum(floors.values())
            # sort by decimal part
            for s in sorted(raw.keys(), key=lambda x: raw[x] - int(raw[x]), reverse=True)[:left]:
                floors[s] += 1
            for s, n in floors.items():
                plan[s] = n

            # Build lecture tasks with next pending chapter
            for subj, n in plan.items():
                picked = 0
                for ch in self.data["syllabus"][subj]:
                    if picked >= n:
                        break
                    if ch["done"] < ch["total"]:
                        take = min(n - picked, ch["total"] - ch["done"])
                        for i in range(take):
                            tasks.append({
                                "id": f"{dstr}-lec-{subj}-{ch['name']}-{i}",
                                "text": f"{subj} - {ch['name']} (Lecture {ch['done'] + i + 1}/{ch['total']})",
                                "type": "lecture", "done": False,
                                "subject": subj, "chapter": ch["name"]
                            })
                        picked += take

            # practice + revision
            tasks.append({"id": f"{dstr}-module", "text": "Aaj ke chapters ke 100+ MCQs (PW module)",
                          "type": "practice", "done": False, "subject": None, "chapter": None})
            tasks.append({"id": f"{dstr}-pyq", "text": "Aaj ke chapters ke PYQ last 10 years",
                          "type": "practice", "done": False, "subject": None, "chapter": None})
            tasks.append({"id": f"{dstr}-rev", "text": "7 din purane chapters ka revision",
                          "type": "revision", "done": False, "subject": None, "chapter": None})

        self.data["daily"][dstr] = tasks
        self.save()
        return tasks

    def tick_task(self, dstr, task_id):
        for t in self.data["daily"].get(dstr, []):
            if t["id"] == task_id:
                t["done"] = not t["done"]
                # update syllabus if lecture
                if t["type"] == "lecture" and t["done"]:
                    for ch in self.data["syllabus"][t["subject"]]:
                        if ch["name"] == t["chapter"]:
                            if ch["done"] < ch["total"]:
                                ch["done"] += 1
                            break
                elif t["type"] == "lecture" and not t["done"]:
                    for ch in self.data["syllabus"][t["subject"]]:
                        if ch["name"] == t["chapter"]:
                            if ch["done"] > 0:
                                ch["done"] -= 1
                            break
                self.save()
                return t["done"]
        return None

    def today_summary(self, dstr=None):
        if dstr is None:
            dstr = date.today().isoformat()
        tasks = self.data["daily"].get(dstr, [])
        total = len(tasks)
        done = sum(1 for t in tasks if t["done"])
        return done, total

    def update_streak(self):
        today = date.today().isoformat()
        last = self.data.get("last_active", "")
        if last == today:
            return
        if last:
            last_d = date.fromisoformat(last)
            if (date.today() - last_d).days == 1:
                self.data["streak"] += 1
            else:
                self.data["streak"] = 1
        else:
            self.data["streak"] = 1
        self.data["last_active"] = today
        self.save()

    def add_mock(self, subj, chapter, marks, total, mtype):
        self.data["mocks"].append({
            "date": date.today().isoformat(),
            "subject": subj, "chapter": chapter,
            "marks": marks, "total": total, "type": mtype
        })
        self.save()

    def mock_stats(self):
        mocks = self.data["mocks"]
        if not mocks:
            return 0, 0, 0
        last10 = mocks[-10:]
        avg_pct = sum(m["marks"] / m["total"] * 100 for m in last10) / len(last10)
        best_pct = max(m["marks"] / m["total"] * 100 for m in mocks)
        return round(avg_pct, 1), round(best_pct, 1), len(mocks)


# ---------------- HELPERS ----------------
def section_card(title, subtitle=""):
    card = MDCard(orientation="vertical", padding=dp(12), spacing=dp(6),
                  size_hint_y=None, height=dp(70), radius=[12],
                  md_bg_color=(0.13, 0.13, 0.18, 1))
    card.add_widget(MDLabel(text=title, bold=True, font_style="H6",
                            theme_text_color="Custom", text_color=(1, 1, 1, 1)))
    if subtitle:
        card.add_widget(MDLabel(text=subtitle, font_style="Caption",
                                theme_text_color="Custom", text_color=(0.8, 0.8, 0.9, 1)))
    return card


def stat_card(label, value, color=(0.2, 0.6, 0.9, 1)):
    card = MDCard(orientation="vertical", padding=dp(12), spacing=dp(2),
                  size_hint=(1, None), height=dp(90), radius=[12],
                  md_bg_color=(0.13, 0.13, 0.18, 1))
    card.add_widget(MDLabel(text=label, font_style="Caption",
                            theme_text_color="Custom", text_color=(0.75, 0.75, 0.85, 1)))
    card.add_widget(MDLabel(text=str(value), bold=True, font_style="H4",
                            theme_text_color="Custom", text_color=color))
    return card


def progress_row(label, percent, done, total, color):
    box = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(60),
                      spacing=dp(4), padding=[0, dp(4)])
    top = MDBoxLayout(size_hint_y=None, height=dp(24))
    top.add_widget(MDLabel(text=f"{label}", font_style="Subtitle2"))
    top.add_widget(MDLabel(text=f"{done}/{total} ({percent}%)", halign="right",
                           font_style="Caption"))
    box.add_widget(top)
    pb = MDProgressBar(value=percent, max=100, color=color)
    box.add_widget(pb)
    return box


# ---------------- SCREENS ----------------
class DashboardScreen(MDScrollView):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.container = MDBoxLayout(orientation="vertical", padding=dp(12),
                                     spacing=dp(12), size_hint_y=None)
        self.container.bind(minimum_height=self.container.setter("height"))
        self.add_widget(self.container)
        Clock.schedule_once(lambda *_: self.refresh(), 0.2)

    def refresh(self):
        self.container.clear_widgets()
        dm = self.app.dm
        # Header
        self.container.add_widget(section_card(
            f"🔥 NEET AllRounder", f"Streak: {dm.data['streak']} din | Goal: 650+"))
        # Stats grid
        overall = dm.overall_percent()
        done, total = dm.done_lectures(), dm.total_lectures()
        avg, best, count = dm.mock_stats()
        td, tt = dm.today_summary()

        row1 = MDBoxLayout(size_hint_y=None, height=dp(90), spacing=dp(8))
        row1.add_widget(stat_card("Syllabus %", f"{overall}%", (0.2, 0.8, 0.4, 1)))
        row1.add_widget(stat_card("Lectures", f"{done}/{total}", (0.4, 0.6, 1, 1)))
        self.container.add_widget(row1)

        row2 = MDBoxLayout(size_hint_y=None, height=dp(90), spacing=dp(8))
        row2.add_widget(stat_card("Aaj ke Tasks", f"{td}/{tt}", (1, 0.7, 0.2, 1)))
        row2.add_widget(stat_card("Mock Avg %", f"{avg}", (0.9, 0.4, 0.6, 1)))
        self.container.add_widget(row2)

        # Subject progress
        self.container.add_widget(section_card("📚 Subject-wise Progress", ""))
        for subj in CHAPTERS.keys():
            d, t, p = dm.subject_stats(subj)
            self.container.add_widget(progress_row(subj, p, d, t, SUBJECT_COLORS[subj]))

        # Mock summary
        self.container.add_widget(section_card("📝 Mock Summary",
            f"Total: {count} | Best: {best}% | Avg (last 10): {avg}%"))


class DailyScreen(MDScrollView):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.container = MDBoxLayout(orientation="vertical", padding=dp(12),
                                     spacing=dp(8), size_hint_y=None)
        self.container.bind(minimum_height=self.container.setter("height"))
        self.add_widget(self.container)
        Clock.schedule_once(lambda *_: self.refresh(), 0.2)

    def refresh(self):
        self.container.clear_widgets()
        dm = self.app.dm
        dstr = date.today().isoformat()
        tasks = dm.generate_daily_tasks(dstr)
        done = sum(1 for t in tasks if t["done"])
        total = len(tasks)
        pct = 0 if total == 0 else round(done / total * 100)

        self.container.add_widget(section_card(
            f"📅 Aaj ka Plan ({dstr})",
            f"{done}/{total} complete ({pct}%)"))

        for t in tasks:
            card = MDCard(orientation="horizontal", padding=dp(8), spacing=dp(6),
                          size_hint_y=None, height=dp(60), radius=[10],
                          md_bg_color=(0.15, 0.15, 0.2, 1) if t["done"]
                          else (0.10, 0.10, 0.15, 1))
            cb = MDCheckbox(active=t["done"], size_hint=(None, None),
                            size=(dp(40), dp(40)))
            cb.bind(active=lambda inst, val, tid=t["id"]: self.on_tick(tid, val))
            card.add_widget(cb)
            lbl = MDLabel(text=t["text"], valign="middle", font_style="Body2")
            card.add_widget(lbl)
            self.container.add_widget(card)

    def on_tick(self, tid, val):
        dm = self.app.dm
        dstr = date.today().isoformat()
        current = next((t for t in dm.data["daily"].get(dstr, []) if t["id"] == tid), None)
        if current is None:
            return
        if current["done"] != val:
            dm.tick_task(dstr, tid)
        # refresh dashboard too
        self.app.dashboard.refresh()


class SyllabusScreen(MDScrollView):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.container = MDBoxLayout(orientation="vertical", padding=dp(12),
                                     spacing=dp(8), size_hint_y=None)
        self.container.bind(minimum_height=self.container.setter("height"))
        self.add_widget(self.container)
        Clock.schedule_once(lambda *_: self.refresh(), 0.2)

    def refresh(self):
        self.container.clear_widgets()
        dm = self.app.dm
        for subj in CHAPTERS.keys():
            d, t, p = dm.subject_stats(subj)
            self.container.add_widget(section_card(
                f"{subj}", f"{d}/{t} lectures done — {p}%"))
            for ch in dm.data["syllabus"][subj]:
                row = MDBoxLayout(orientation="horizontal", size_hint_y=None,
                                  height=dp(40), spacing=dp(6))
                row.add_widget(MDLabel(text=ch["name"], font_style="Body2",
                                       valign="middle"))
                row.add_widget(MDLabel(text=f"{ch['done']}/{ch['total']}",
                                       halign="right", valign="middle",
                                       size_hint_x=0.3, font_style="Caption"))
                self.container.add_widget(row)


class MocksScreen(MDScrollView):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.container = MDBoxLayout(orientation="vertical", padding=dp(12),
                                     spacing=dp(8), size_hint_y=None)
        self.container.bind(minimum_height=self.container.setter("height"))
        self.add_widget(self.container)
        Clock.schedule_once(lambda *_: self.refresh(), 0.2)

    def refresh(self):
        self.container.clear_widgets()
        dm = self.app.dm
        avg, best, count = dm.mock_stats()

        self.container.add_widget(section_card(
            "📊 Mock Performance",
            f"Total: {count} | Best: {best}% | Avg(last10): {avg}%"))

        # Add mock button
        btn = MDRaisedButton(text="+ Add Mock Result", size_hint=(1, None),
                             height=dp(50), md_bg_color=(0.2, 0.6, 0.9, 1))
        btn.bind(on_release=lambda *_: self.app.open_add_mock_dialog())
        self.container.add_widget(btn)

        self.container.add_widget(section_card("📋 History", "Latest 20"))

        for m in reversed(dm.data["mocks"][-20:]):
            pct = round(m["marks"] / m["total"] * 100, 1)
            color = (0.2, 0.8, 0.3, 1) if pct >= 70 else (
                (1, 0.8, 0.2, 1) if pct >= 50 else (1, 0.3, 0.3, 1))
            card = MDCard(orientation="vertical", padding=dp(10), spacing=dp(2),
                          size_hint_y=None, height=dp(75), radius=[10],
                          md_bg_color=(0.13, 0.13, 0.18, 1))
            top = MDBoxLayout(size_hint_y=None, height=dp(24))
            top.add_widget(MDLabel(text=f"{m['type']} — {m['subject']}", bold=True))
            top.add_widget(MDLabel(text=f"{pct}%", halign="right",
                                   theme_text_color="Custom", text_color=color,
                                   bold=True))
            card.add_widget(top)
            sub = m["chapter"] if m["chapter"] else "Full length"
            card.add_widget(MDLabel(text=f"{sub} | {m['marks']}/{m['total']} | {m['date']}",
                                    font_style="Caption"))
            self.container.add_widget(card)


# ---------------- APP ----------------
class NEETApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "BlueGray"
        data_path = os.path.join(self.user_data_dir, "neet_data.json")
        self.dm = DataManager(data_path)
        self.dm.update_streak()
        self.dm.generate_daily_tasks()

        self.dashboard = DashboardScreen(self)
        self.daily = DailyScreen(self)
        self.syllabus = SyllabusScreen(self)
        self.mocks = MocksScreen(self)

        bn = MDBottomNavigation()
        items = [
            ("Dashboard", "view-dashboard", self.dashboard),
            ("Daily", "check-circle-outline", self.daily),
            ("Syllabus", "book-open-variant", self.syllabus),
            ("Mocks", "chart-line", self.mocks),
        ]
        for label, icon, widget in items:
            item = MDBottomNavigationItem(name=label, text=label, icon=icon)
            item.add_widget(widget)
            bn.add_widget(item)

        self.bn = bn
        return bn

    def on_start(self):
        # refresh daily at midnight (rough)
        Clock.schedule_interval(self._midnight_check, 60 * 30)

    def _midnight_check(self, *args):
        self.dm.generate_daily_tasks()
        self.daily.refresh()

    # ---- Add Mock Dialog ----
    def open_add_mock_dialog(self):
        content = MDBoxLayout(orientation="vertical", spacing=dp(10),
                              size_hint_y=None, height=dp(360))
        self.dlg_subject = MDTextField(hint_text="Subject (Physics/Chemistry/Botany/Zoology)")
        self.dlg_chapter = MDTextField(hint_text="Chapter (blank = full length)")
        self.dlg_type = MDTextField(hint_text="Type (chapter / full)")
        self.dlg_marks = MDTextField(hint_text="Marks obtained", input_filter="float")
        self.dlg_total = MDTextField(hint_text="Total marks", input_filter="float")
        for w in [self.dlg_subject, self.dlg_chapter, self.dlg_type,
                  self.dlg_marks, self.dlg_total]:
            content.add_widget(w)

        self.dialog = MDDialog(
            title="Add Mock Result",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda *_: self.dialog.dismiss()),
                MDRaisedButton(text="SAVE", on_release=self._save_mock),
            ],
        )
        self.dialog.open()

    def _save_mock(self, *args):
        try:
            subj = self.dlg_subject.text.strip() or "Mixed"
            chap = self.dlg_chapter.text.strip()
            mtype = self.dlg_type.text.strip() or ("Full" if not chap else "Chapter")
            marks = float(self.dlg_marks.text or 0)
            total = float(self.dlg_total.text or 1)
            if total <= 0:
                total = 1
            self.dm.add_mock(subj, chap, marks, total, mtype)
        except Exception as e:
            print("Mock save error:", e)
        self.dialog.dismiss()
        self.mocks.refresh()
        self.dashboard.refresh()


if __name__ == "__main__":
    NEETApp().run()
