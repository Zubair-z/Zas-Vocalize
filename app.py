#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZAS Vocalize v4.0 — Ultra-Premium Edition
Redesigned with a high-end SaaS/DAW aesthetic.
"""

import sys, io, os, json, threading, asyncio, subprocess
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox
import tkinter as tk
import winsound

# ── Colors & Branding ─────────────────────────────────────────────────────────
BG_MAIN     = "#0B0E14"  # Very deep slate/black
BG_PANEL    = "#151921"  # Slightly lighter panel
BG_CARD     = "#1C222D"  # Card background
ACCENT_BLUE = "#3B82F6"  # Premium Blue
ACCENT_CYAN = "#06B6D4"  # Tech Cyan
TEXT_DIM    = "#94A3B8"  # Dimmed text
TEXT_BRIGHT = "#F8FAFC"  # High contrast text
BORDER_COLOR = "#2A3341" # Subtle border

# ── Fix Windows encoding ──────────────────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ctk.set_appearance_mode("dark")

# ── Voice Configuration ───────────────────────────────────────────────────────
CHARACTERS = {
    # YouTuber / Creator
    "youtuber":          {"color": "#F5A623", "pill_bg": "#2e2010", "desc": "Casual American YouTuber ⭐"},
    "youtuber_female":   {"color": "#FF9ED2", "pill_bg": "#2e1020", "desc": "Warm American vlogger ⭐"},
    # Narrator
    "narrator":          {"color": "#60A5FA", "pill_bg": "#1e293b", "desc": "British — Documentary"},
    "narrator_female":   {"color": "#93C5FD", "pill_bg": "#1e293b", "desc": "American — Audiobook"},
    "narrator_deep":     {"color": "#3B82F6", "pill_bg": "#0f172a", "desc": "Deep — Movie Trailer"},
    # Expert
    "expert":            {"color": "#10B981", "pill_bg": "#064e3b", "desc": "Podcast & Explainer"},
    "professor":         {"color": "#059669", "pill_bg": "#064e3b", "desc": "Academic & Lecture"},
    "expert_female":     {"color": "#34D399", "pill_bg": "#064e3b", "desc": "News & Corporate"},
    # Characters
    "hero":              {"color": "#22C55E", "pill_bg": "#052e16", "desc": "Bold Action Hero"},
    "villain":           {"color": "#EF4444", "pill_bg": "#450a0a", "desc": "Deep Menacing Villain"},
    "queen":             {"color": "#A855F7", "pill_bg": "#2e1065", "desc": "Regal Authority"},
    "child":             {"color": "#F97316", "pill_bg": "#431407", "desc": "Bright Young Child"},
    "old_man":           {"color": "#D97706", "pill_bg": "#451a03", "desc": "Wise Elder Mentor"},
    # Urdu / Hindi
    "urdu_male":         {"color": "#22C55E", "pill_bg": "#052e16", "desc": "Urdu Male (Asad) 🇵🇰"},
    "urdu_female":       {"color": "#10B981", "pill_bg": "#052e16", "desc": "Urdu Female (Uzma) 🇵🇰"},
    "hindi_male":        {"color": "#F97316", "pill_bg": "#431407", "desc": "Hindi Male (Madhur) 🇮🇳"},
    "hindi_female":      {"color": "#FB923C", "pill_bg": "#431407", "desc": "Hindi Female (Swara) 🇮🇳"},
    # Regional
    "british_male":      {"color": "#94A3B8", "pill_bg": "#334155", "desc": "Casual British"},
    "british_female":    {"color": "#CBD5E1", "pill_bg": "#334155", "desc": "Friendly British"},
    "australian_male":   {"color": "#4ADE80", "pill_bg": "#064e3b", "desc": "Relaxed Australian"},
    "indian_male":       {"color": "#FBBF24", "pill_bg": "#451a03", "desc": "Indian English"},
    # Moods
    "cheerful":          {"color": "#FACC15", "pill_bg": "#422006", "desc": "Upbeat Positive"},
    "serious":           {"color": "#64748B", "pill_bg": "#1e293b", "desc": "Formal Elegant"},
    "excited":           {"color": "#F87171", "pill_bg": "#450a0a", "desc": "Hype & Energy"},
}

# ══════════════════════════════════════════════════════════════════════════════
class SceneCard(ctk.CTkFrame):
    """Premium scene editor card."""

    def __init__(self, master, scene_id: int, on_delete, **kwargs):
        super().__init__(master, fg_color=BG_CARD, border_color=BORDER_COLOR, border_width=1, corner_radius=12, **kwargs)
        self.scene_id  = scene_id
        self.on_delete = on_delete
        self.output_path = None

        self.grid_columnconfigure(2, weight=1)

        # ── Left: Row ID ──────────────────────────────────────────────────────
        self.id_label = ctk.CTkLabel(
            self, text=f"{scene_id:02d}",
            font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
            text_color="#475569", width=40
        )
        self.id_label.grid(row=0, column=0, padx=(12, 4), pady=16)

        # ── Middle-Left: Character Select ─────────────────────────────────────
        self.char_var = ctk.StringVar(value="narrator")
        self.char_drop = ctk.CTkOptionMenu(
            self, values=list(CHARACTERS.keys()), variable=self.char_var,
            width=160, height=36, corner_radius=8,
            fg_color="#1F2937", button_color="#374151", button_hover_color="#4B5563",
            font=ctk.CTkFont(size=12, weight="normal"), dropdown_fg_color="#1F2937"
        )
        self.char_drop.grid(row=0, column=1, padx=8, pady=16)

        # ── Middle: Content Input ─────────────────────────────────────────────
        self.text_box = ctk.CTkTextbox(
            self, height=72, corner_radius=10,
            fg_color=BG_PANEL, border_color="#334155", border_width=1,
            text_color=TEXT_BRIGHT, font=ctk.CTkFont(size=13, family="Inter"),
            wrap="word", undo=True
        )
        self.text_box.grid(row=0, column=2, padx=8, pady=12, sticky="ew")

        # ── Right: Tool Actions ───────────────────────────────────────────────
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=0, column=3, padx=(8, 12), pady=16)

        self.play_btn = ctk.CTkButton(
            actions, text="▶", width=36, height=36, corner_radius=18,
            fg_color="#334155", hover_color=ACCENT_BLUE, text_color="white",
            state="disabled", font=ctk.CTkFont(size=16),
            command=self._play_audio
        )
        self.play_btn.pack(side="left", padx=4)

        self.del_btn = ctk.CTkButton(
            actions, text="✕", width=36, height=36, corner_radius=18,
            fg_color="transparent", hover_color="#EF4444", text_color="#94A3B8",
            font=ctk.CTkFont(size=14),
            command=lambda: on_delete(self)
        )
        self.del_btn.pack(side="left", padx=4)

        # Status Dot
        self.dot = tk.Canvas(actions, width=8, height=8, bg=BG_CARD, highlightthickness=0)
        self.dot.pack(side="left", padx=(8, 4))
        self.dot_circle = self.dot.create_oval(1, 1, 7, 7, fill="#334155", outline="")

    def _play_audio(self):
        if self.output_path and os.path.exists(self.output_path):
            try:
                winsound.PlaySound(self.output_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except:
                os.startfile(self.output_path)

    def get_data(self):
        return {
            "id": self.scene_id,
            "character": self.char_var.get(),
            "text": self.text_box.get("1.0", "end").strip(),
            "output_file": f"scene_{self.scene_id}.wav"
        }

    def set_status(self, status: str, path: str = None):
        colors = {"generating": ACCENT_CYAN, "done": "#22C55E", "failed": "#EF4444", "": "#334155"}
        self.dot.itemconfig(self.dot_circle, fill=colors.get(status, "#334155"))
        if status == "done" and path:
            # Ensure path uses backslashes for Windows winsound if needed
            self.output_path = str(Path(path).absolute())
            self.play_btn.configure(state="normal", fg_color="#22C55E")

# ══════════════════════════════════════════════════════════════════════════════
class PremiumVoiceApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("ZAS Vocalize — Studio Professional")
        self.geometry("1200x900")
        self.minsize(1050, 750)
        self.configure(fg_color=BG_MAIN)

        self.scene_rows: list[SceneCard] = []
        self.current_project = "untitled_project"
        self._build_ui()

    def _build_ui(self):
        # ── Header Bar ────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Logo/Title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(side="left", padx=32)

        ctk.CTkLabel(
            title_frame, text="ZAS",
            font=ctk.CTkFont(family="Inter", size=22, weight="bold"),
            text_color=ACCENT_BLUE
        ).pack(side="left")
        
        ctk.CTkLabel(
            title_frame, text="VOCALIZE 4.0",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            text_color=TEXT_DIM
        ).pack(side="left", padx=(10, 0), pady=(4, 0))

        # AI Generator Integrated
        ai_bar = ctk.CTkFrame(header, fg_color=BG_CARD, corner_radius=20, border_color=BORDER_COLOR, border_width=1)
        ai_bar.pack(side="right", padx=32, pady=14)

        ctk.CTkLabel(ai_bar, text="🪄", font=ctk.CTkFont(size=18)).pack(side="left", padx=(16, 4))
        
        self.ai_input = ctk.CTkEntry(
            ai_bar, placeholder_text="Enter topic for AI Script...",
            width=300, height=36, corner_radius=18,
            fg_color="transparent", border_width=0, font=ctk.CTkFont(size=13)
        )
        self.ai_input.pack(side="left", padx=4)

        self.ai_model = ctk.CTkOptionMenu(
            ai_bar, values=["llama3", "qwen3:4b"], width=100, height=30,
            fg_color=BG_PANEL, button_color="#374151", corner_radius=12
        )
        self.ai_model.pack(side="left", padx=8)

        self.ai_btn = ctk.CTkButton(
            ai_bar, text="Generate", width=90, height=30, corner_radius=15,
            fg_color=ACCENT_BLUE, hover_color="#2563EB", text_color="white",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._generate_ai_script
        )
        self.ai_btn.pack(side="left", padx=(4, 12))

        # ── Sidebar-less Layout (Modern Flow) ─────────────────────────────────
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=40, pady=24)
        main.grid_columnconfigure(0, weight=1)

        # ── Section 1: Voice Marketplace (Gallery) ───────────────────────────
        gallery_header = ctk.CTkFrame(main, fg_color="transparent")
        gallery_header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        
        ctk.CTkLabel(
            gallery_header, text="VOICE MARKETPLACE",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color=TEXT_DIM
        ).pack(side="left")

        self.voice_scroll = ctk.CTkScrollableFrame(
            main, height=110, fg_color=BG_PANEL, corner_radius=16,
            border_color=BORDER_COLOR, border_width=1, orientation="horizontal"
        )
        self.voice_scroll.grid(row=1, column=0, sticky="ew", pady=(0, 24))

        for name, cfg in CHARACTERS.items():
            self._add_gallery_item(name, cfg)

        # ── Section 2: Editor ────────────────────────────────────────────────
        editor_header = ctk.CTkFrame(main, fg_color="transparent")
        editor_header.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        
        ctk.CTkLabel(
            editor_header, text="SCRIPT EDITOR",
            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
            text_color=TEXT_DIM
        ).pack(side="left")

        ctk.CTkButton(
            editor_header, text="+ NEW SCENE", width=120, height=32, corner_radius=8,
            fg_color="#334155", hover_color="#475569", font=ctk.CTkFont(size=11, weight="bold"),
            command=self._add_scene
        ).pack(side="right")

        # Scene List
        self.scene_scroll = ctk.CTkScrollableFrame(
            main, fg_color="transparent", corner_radius=0
        )
        self.scene_scroll.grid(row=3, column=0, sticky="nsew", pady=(0, 24))
        main.grid_rowconfigure(3, weight=1)
        self.scene_scroll.grid_columnconfigure(0, weight=1)

        # Initial Scene
        self._add_scene()

        # ── Section 3: Footer Controls ───────────────────────────────────────
        footer = ctk.CTkFrame(main, fg_color=BG_PANEL, corner_radius=16, height=90, border_color=BORDER_COLOR, border_width=1)
        footer.grid(row=4, column=0, sticky="ew")
        footer.pack_propagate(False)

        # Project Info
        info_frame = ctk.CTkFrame(footer, fg_color="transparent")
        info_frame.pack(side="left", padx=24)
        
        ctk.CTkLabel(info_frame, text="PROJECT NAME", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_DIM).pack(anchor="w")
        self.proj_entry = ctk.CTkEntry(
            info_frame, width=200, height=36, corner_radius=8,
            fg_color=BG_CARD, border_width=1, border_color=BORDER_COLOR,
            font=ctk.CTkFont(size=13)
        )
        self.proj_entry.pack(anchor="w", pady=(4, 0))
        self.proj_entry.insert(0, "viral_promo_v1")

        # Action Buttons
        btn_frame = ctk.CTkFrame(footer, fg_color="transparent")
        btn_frame.pack(side="right", padx=24)

        self.folder_btn = ctk.CTkButton(
            btn_frame, text="📁", width=44, height=44, corner_radius=12,
            fg_color=BG_CARD, hover_color="#334155", font=ctk.CTkFont(size=18),
            command=self._open_output
        )
        self.folder_btn.pack(side="left", padx=8)

        self.gen_btn = ctk.CTkButton(
            btn_frame, text="RENDER MASTER AUDIO", width=260, height=50, corner_radius=12,
            fg_color=ACCENT_BLUE, hover_color="#2563EB",
            font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
            command=self._generate
        )
        self.gen_btn.pack(side="left", padx=8)

        # Progress / Status Bar
        self.status_bar = ctk.CTkFrame(self, fg_color=BG_PANEL, height=30, corner_radius=0)
        self.status_bar.pack(fill="x", side="bottom")

        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready", font=ctk.CTkFont(size=11), text_color=TEXT_DIM)
        self.status_label.pack(side="left", padx=20)

        self.progress_bar = ctk.CTkProgressBar(self.status_bar, width=300, height=6, fg_color=BG_CARD, progress_color=ACCENT_CYAN)
        self.progress_bar.pack(side="right", padx=20, pady=12)
        self.progress_bar.set(0)

    # ── Helper: Gallery Items ────────────────────────────────────────────────
    def _add_gallery_item(self, name, cfg):
        item = ctk.CTkFrame(self.voice_scroll, fg_color=BG_CARD, width=150, height=80, corner_radius=12, border_color=BORDER_COLOR, border_width=1)
        item.pack(side="left", padx=8, pady=10)
        item.pack_propagate(False)

        top = ctk.CTkFrame(item, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(10, 0))

        ctk.CTkLabel(
            top, text=name.split('_')[0].upper()[:10],
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=cfg["color"]
        ).pack(side="left")

        ctk.CTkButton(
            top, text="🔊", width=24, height=24, corner_radius=12,
            fg_color="transparent", hover_color="#334155", font=ctk.CTkFont(size=12),
            command=lambda n=name: self._test_voice(n)
        ).pack(side="right")

        # Description
        ctk.CTkLabel(
            item, text=cfg["desc"][:18] + "...",
            font=ctk.CTkFont(size=9), text_color=TEXT_DIM
        ).pack(padx=10, pady=(2, 0), anchor="w")

    # ── Logic: AI & Tests ────────────────────────────────────────────────────
    def _test_voice(self, char):
        self._set_status(f"Previewing '{char}' voice...")
        threading.Thread(target=self._run_voice_test, args=(char,), daemon=True).start()

    def _run_voice_test(self, char):
        try:
            from super_voice_tool import generate_preview
            path = Path("G:/Voice generation tool/temp_previews")
            path.mkdir(exist_ok=True)
            out_file = path / f"preview_{char}.wav"
            if generate_preview(char, str(out_file)):
                winsound.PlaySound(str(out_file), winsound.SND_FILENAME | winsound.SND_ASYNC)
        except Exception as e:
            print(f"Preview error: {e}")

    def _generate_ai_script(self):
        topic = self.ai_input.get().strip()
        if not topic: return
        self.ai_btn.configure(state="disabled", text="Working...")
        self._set_status(f"AI is drafting a masterpiece about '{topic}'...")
        threading.Thread(target=self._run_ollama, args=(topic,), daemon=True).start()

    def _run_ollama(self, topic):
        try:
            from super_voice_tool import generate_script_with_ollama
            data = generate_script_with_ollama(topic, self.ai_model.get())
            self.after(0, self._apply_ai_script, data)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("AI Error", str(e)))
            self.after(0, lambda: self.ai_btn.configure(state="normal", text="Generate"))

    def _apply_ai_script(self, data):
        for r in self.scene_rows: r.destroy()
        self.scene_rows.clear()
        
        scenes = data.get("scenes", [])
        for scene in scenes:
            row = self._add_scene()
            row.char_var.set(scene.get("character", "narrator"))
            row.text_box.insert("1.0", scene.get("text", ""))
        
        self.ai_btn.configure(state="normal", text="Generate")
        self._set_status(f"Script ready: {len(scenes)} scenes loaded.")

    # ── Logic: Scene Management ──────────────────────────────────────────────
    def _add_scene(self) -> SceneCard:
        scene_id = len(self.scene_rows) + 1
        card = SceneCard(self.scene_scroll, scene_id=scene_id, on_delete=self._delete_scene)
        card.grid(row=len(self.scene_rows), column=0, sticky="ew", padx=16, pady=8)
        self.scene_rows.append(card)
        return card

    def _delete_scene(self, card: SceneCard):
        if len(self.scene_rows) <= 1: return
        self.scene_rows.remove(card)
        card.destroy()
        for i, c in enumerate(self.scene_rows, 1):
            c.scene_id = i
            c.id_label.configure(text=f"{i:02d}")

    # ── Logic: Generation ────────────────────────────────────────────────────
    def _generate(self):
        scenes = [r.get_data() for r in self.scene_rows if r.get_data()["text"]]
        if not scenes: return

        project = self.proj_entry.get().strip().replace(" ", "_") or "untitled_project"
        self.current_project = project
        script_data = {"script_metadata": {"total_scenes": len(scenes), "project_name": project}, "scenes": scenes}

        base = Path("G:/Voice generation tool/scripts")
        base.mkdir(exist_ok=True)
        tmp_json = base / f"{project}.json"
        with open(tmp_json, "w", encoding="utf-8") as f:
            json.dump(script_data, f, indent=2, ensure_ascii=False)

        self.gen_btn.configure(state="disabled", text="RENDERING...")
        self.progress_bar.set(0)
        
        threading.Thread(target=self._run_render, args=(str(tmp_json),), daemon=True).start()

    def _run_render(self, json_path: str):
        try:
            from super_voice_tool import process_json_file
            
            def cb(curr, total, sid, char, status):
                self.after(0, lambda: self.progress_bar.set(curr/total))
                self.after(0, lambda: self._set_status(f"Rendering {char}... [{curr}/{total}]"))
                # Note: Card status update logic can be added here if needed
                if 0 <= sid-1 < len(self.scene_rows):
                    p = f"G:/Voice generation tool/audio_output/{self.current_project}/scene_{sid}.wav"
                    self.after(0, lambda: self.scene_rows[sid-1].set_status(status, p))

            summary = process_json_file(json_path, progress_callback=cb)
            self.after(0, self._on_render_done, summary)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Render Error", str(e)))
            self.after(0, lambda: self.gen_btn.configure(state="normal", text="RENDER MASTER AUDIO"))

    def _on_render_done(self, summary):
        self.gen_btn.configure(state="normal", text="RENDER MASTER AUDIO")
        self._set_status(f"Render Complete: {summary['success_count']} files exported.")
        messagebox.showinfo("ZAS Vocalize", "Project exported successfully!")

    def _set_status(self, msg: str):
        self.status_label.configure(text=msg)

    def _open_output(self):
        path = f"G:/Voice generation tool/audio_output/{self.proj_entry.get().strip()}"
        if os.path.exists(path): os.startfile(path)
        else: os.startfile("G:/Voice generation tool/audio_output")

if __name__ == "__main__":
    app = PremiumVoiceApp()
    app.mainloop()
