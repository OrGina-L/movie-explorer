# -*- coding: utf-8 -*-


import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime

# ==================== کلاس Tooltip ==================== #
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind('<Enter>', self.show_tooltip)
        self.widget.bind('<Leave>', self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        if self.tip_window:
            return
        
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + 25
        
        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self.tip_window,
            text=self.text,
            background="#2a9d8f",
            foreground="white",
            relief="solid",
            borderwidth=1,
            font=("Tahoma", 9),
            padx=5,
            pady=2
        )
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# ==================== برنامه اصلی ==================== #
class MovieRecommender:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.load_movies_data()
        self.setup_ui()
        self.apply_filters()
        
    def setup_window(self):
        """تنظیمات پنجره"""
        self.root.title("🎬 کاوشگر فیلم ")
        self.root.geometry("1200x750")
        
        # فقط تم تاریک
        self.colors = {
            'primary': '#0d1b2a',      # آبی تیره عمیق
            'secondary': '#1b263b',    # آبی تیره
            'accent': '#e63946',       # قرمز جذاب
            'light': '#f1faee',        # سفید کرمی
            'highlight': '#a8dadc',    # فیروزه‌ای
            'gold': '#ffd166',         # طلایی
            'button_active': '#2a9d8f',# سبز آبی
            'button_inactive': '#415a77'# آبی خاکستری
        }
        
        self.root.configure(bg=self.colors['primary'])
        
        
        self.center_window()
        
        # متغیرهای وضعیت
        self.status_text = tk.StringVar(value="سینماسنج آماده است!")
        self.watchlist = []
    
    def center_window(self):
        """مرکز کردن پنجره"""
        self.root.update_idletasks()
        width = 1200
        height = 750
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_movies_data(self):
        """بارگذاری داده‌های فیلم‌ها"""
        self.movies_db = {
            "اکشن": [
                {
                    "id": 1, "title": "جان ویک ۴", "year": 2023, "rating": 7.8,
                    "director": "چاد استاهلزکی", "duration": "169 دقیقه",
                    "description": "ماجراجویی جدید جان ویک در برابر دشمنان قدرتمند",
                    "poster_color": "#1a1a2e", "country": "آمریکا",
                    "actors": ["کیانو ریوز", "دانیل برنهارت"]
                },
                {
                    "id": 2, "title": "تاپ گان: ماوریک", "year": 2022, "rating": 8.2,
                    "director": "جوزف کوشینسکی", "duration": "130 دقیقه",
                    "description": "بازگشت ماوریک به مدرسه خلبانی",
                    "poster_color": "#15616d", "country": "آمریکا",
                    "actors": ["تام کروز", "مایلز تلر"]
                },
                {
                    "id": 3, "title": "مأموریت غیرممکن ۷", "year": 2023, "rating": 7.5,
                    "director": "کریستوفر مک‌کوری", "duration": "163 دقیقه",
                    "description": "ماجراهای جدید ایگان هانت در برابر یک دشمن قدرتمند",
                    "poster_color": "#2a9d8f", "country": "آمریکا",
                    "actors": ["تام کروز", "هیلی اتمول"]
                }
            ],
            "درام": [
                {
                    "id": 4, "title": "اپنهایمر", "year": 2023, "rating": 8.3,
                    "director": "کریستوفر نولان", "duration": "180 دقیقه",
                    "description": "داستان زندگی فیزیکدان مشهور، رابرت اوپنهایمر",
                    "poster_color": "#3a0ca3", "country": "آمریکا",
                    "actors": ["کیلین مورفی", "امیلی بلانت"]
                },
                {
                    "id": 5, "title": "زندگی در چارچوب", "year": 2022, "rating": 7.9,
                    "director": "تاد فیلد", "duration": "158 دقیقه",
                    "description": "داستانی عمیق درباره زندگی و مرگ یک موسیقیدان مشهور",
                    "poster_color": "#7209b7", "country": "آمریکا",
                    "actors": ["تاد فیلد", "کیت بلانشت"]
                }
            ],
            "کمدی": [
                {
                    "id": 6, "title": "چیزهای عجیب", "year": 2022, "rating": 7.2,
                    "director": "الیزابت بنکس", "duration": "112 دقیقه",
                    "description": "کمدی ماجراجویانه با حال و هوای دهه ۸۰",
                    "poster_color": "#ff9e00", "country": "آمریکا",
                    "actors": ["نیکلاس کیج", "پدرو پاسکال"]
                },
                {
                    "id": 7, "title": "برتری", "year": 2022, "rating": 6.5,
                    "director": "نیکلاس استولر", "duration": "103 دقیقه",
                    "description": "کمدی درباره گروهی از بازیگران که در قرنطینه فیلم می‌سازند",
                    "poster_color": "#ffafcc", "country": "آمریکا",
                    "actors": ["کارن گیلان", "ایسا رای"]
                }
            ],
            "علمی تخیلی": [
                {
                    "id": 8, "title": "آواتار: راه آب", "year": 2022, "rating": 7.6,
                    "director": "جیمز کامرون", "duration": "192 دقیقه",
                    "description": "ادامه ماجراجویی در سیاره پاندورا و اقیانوس‌های شگفت‌انگیز آن",
                    "poster_color": "#06d6a0", "country": "آمریکا",
                    "actors": ["سام ورثینگتون", "زو سالدانیا"]
                },
                {
                    "id": 9, "title": "چندجهانی دیوانگی", "year": 2022, "rating": 7.8,
                    "director": "دن کوان", "duration": "139 دقیقه",
                    "description": "کمدی علمی تخیلی چندجهانی درباره یک زن چینی-آمریکایی",
                    "poster_color": "#4cc9f0", "country": "آمریکا",
                    "actors": ["میشل یئو", "کی هوی کوان"]
                }
            ],
            "انیمیشن": [
                {
                    "id": 10, "title": "اسپایدرمن: درون دنیای عنکبوتی", "year": 2023, "rating": 8.7,
                    "director": "خواکیم دوس سانتوس", "duration": "140 دقیقه",
                    "description": "ماجراجویی چندجهانی مرد عنکبوتی در دنیاهای موازی",
                    "poster_color": "#ef476f", "country": "آمریکا",
                    "actors": ["شامیک مور", "هایلی استاینفلد"]
                }
            ]
        }
        
        self.genres = list(self.movies_db.keys())
        self.genre_states = {genre: True for genre in self.genres}
    
    def setup_ui(self):
        """ایجاد رابط کاربری"""
        # هدر
        self.create_header()
        
        # بدنه اصلی
        main_frame = tk.Frame(self.root, bg=self.colors['primary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # پنل سمت چپ
        self.create_left_panel(main_frame)
        
        # پنل سمت راست
        self.create_right_panel(main_frame)
        
        # نوار اتفاقات
        self.create_status_bar()
    
    def create_header(self):
        """ایجاد هدر"""
        header = tk.Frame(self.root, bg=self.colors['secondary'], height=100)
        header.pack(fill='x')
        
        # عنوان فارسی
        tk.Label(
            header,
            text="🎬 سینماسنج",
            font=("Tahoma", 28, 'bold'),
            fg=self.colors['gold'],
            bg=self.colors['secondary']
        ).pack(pady=20)
        
        # عنوان انگلیسی
        tk.Label(
            header,
            text="CinemaSense AI - Movie Recommender System",
            font=('Arial', 12, 'italic'),
            fg=self.colors['highlight'],
            bg=self.colors['secondary']
        ).pack()
    
    def create_left_panel(self, parent):
        """ساخت پنل فیلترها"""
        panel = tk.Frame(parent, bg=self.colors['secondary'], width=320)
        panel.pack(side='left', fill='y', padx=(0, 15))
        
        # نام پنل
        tk.Label(
            panel,
            text="⚙️ فیلترهای پیشرفته",
            font=("Tahoma", 16, 'bold'),
            fg=self.colors['highlight'],
            bg=self.colors['secondary'],
            pady=20
        ).pack()
        
        # بخش ژانرها
        self.create_genre_section(panel)
        
        # بخش سال
        self.create_year_section(panel)
        
        # بخش امتیاز
        self.create_rating_section(panel)
        
        # دکمه‌های کنترلی
        self.create_control_buttons(panel)
    
    def create_genre_section(self, panel):
        """ایجاد بخش ژانرها"""
        genre_frame = tk.LabelFrame(
            panel,
            text="🎭 انتخاب ژانر",
            font=("Tahoma", 12, 'bold'),
            fg=self.colors['light'],
            bg=self.colors['secondary'],
            padx=15,
            pady=15
        )
        genre_frame.pack(fill='x', padx=10, pady=10)
        
        self.genre_buttons = {}
        
        # ایجاد دکمه‌های toggle برای ژانرها
        for i, genre in enumerate(self.genres):
            row = i // 3
            col = i % 3
            
            btn = tk.Button(
                genre_frame,
                text=genre,
                font=("Tahoma", 10),
                width=12,
                height=2,
                relief='sunken',
                cursor='hand2',
                command=lambda g=genre: self.toggle_genre(g)
            )
            
            # همه ژانرها در ابتدا انتخاب شده‌اند
            btn.config(
                bg=self.colors['button_active'],
                fg='white',
                activebackground=self.colors['accent']
            )
            
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            self.genre_buttons[genre] = btn
            
            ToolTip(btn, f"کلیک برای انتخاب/عدم انتخاب ژانر {genre}")
        
        # دکمه‌های کنترل
        control_frame = tk.Frame(genre_frame, bg=self.colors['secondary'])
        control_frame.grid(row=((len(self.genres) + 2) // 3), column=0, columnspan=3, pady=(15, 0))
        
        tk.Button(
            control_frame,
            text="✅ انتخاب همه",
            command=self.select_all_genres,
            font=("Tahoma", 10),
            bg=self.colors['highlight'],
            fg='white',
            cursor='hand2',
            padx=15,
            pady=5
        ).pack(side='left', padx=5)
        
        tk.Button(
            control_frame,
            text="❌ حذف همه",
            command=self.deselect_all_genres,
            font=("Tahoma", 10),
            bg=self.colors['accent'],
            fg='white',
            cursor='hand2',
            padx=15,
            pady=5
        ).pack(side='left', padx=5)
    
    def toggle_genre(self, genre):
        """تغییر وضعیت ژانر"""
        self.genre_states[genre] = not self.genre_states[genre]
        btn = self.genre_buttons[genre]
        
        if self.genre_states[genre]:
            btn.config(
                relief='sunken',
                bg=self.colors['button_active'],
                fg='white'
            )
        else:
            btn.config(
                relief='raised',
                bg=self.colors['button_inactive'],
                fg=self.colors['light']
            )
        
        self.apply_filters()
    
    def select_all_genres(self):
        """انتخاب همه ژانرها"""
        for genre in self.genres:
            self.genre_states[genre] = True
            btn = self.genre_buttons[genre]
            btn.config(
                relief='sunken',
                bg=self.colors['button_active'],
                fg='white'
            )
        self.apply_filters()
    
    def deselect_all_genres(self):
        """انتخاب نکردن همه ژانرها"""
        for genre in self.genres:
            self.genre_states[genre] = False
            btn = self.genre_buttons[genre]
            btn.config(
                relief='raised',
                bg=self.colors['button_inactive'],
                fg=self.colors['light']
            )
        self.apply_filters()
    
    def create_year_section(self, panel):
        """ایجاد بخش فیلتر سال"""
        year_frame = tk.LabelFrame(
            panel,
            text="📅 حداقل سال تولید",
            font=("Tahoma", 12, 'bold'),
            fg=self.colors['light'],
            bg=self.colors['secondary'],
            padx=15,
            pady=15
        )
        year_frame.pack(fill='x', padx=10, pady=10)
        
        self.year_var = tk.IntVar(value=2010)
        self.year_slider = tk.Scale(
            year_frame,
            from_=2000,
            to=2024,
            variable=self.year_var,
            orient='horizontal',
            length=250,
            bg=self.colors['secondary'],
            fg=self.colors['light'],
            troughcolor=self.colors['primary'],
            highlightthickness=0,
            sliderrelief='raised',
            command=lambda x: self.apply_filters()
        )
        self.year_slider.pack(fill='x', pady=10)
        
        self.year_label = tk.Label(
            year_frame,
            text=f"سال: {self.year_var.get()}",
            font=("Tahoma", 10),
            fg=self.colors['highlight'],
            bg=self.colors['secondary']
        )
        self.year_label.pack()
        
        ToolTip(self.year_slider, "انتخاب حداقل سال تولید فیلم")
    
    def create_rating_section(self, panel):
        """ساخت بخش فیلتر امتیاز"""
        rating_frame = tk.LabelFrame(
            panel,
            text="⭐ حداقل امتیاز",
            font=("Tahoma", 12, 'bold'),
            fg=self.colors['light'],
            bg=self.colors['secondary'],
            padx=15,
            pady=15
        )
        rating_frame.pack(fill='x', padx=10, pady=10)
        
        self.rating_var = tk.DoubleVar(value=6.0)
        self.rating_slider = tk.Scale(
            rating_frame,
            from_=0,
            to=10,
            resolution=0.5,
            variable=self.rating_var,
            orient='horizontal',
            length=250,
            bg=self.colors['secondary'],
            fg=self.colors['light'],
            troughcolor=self.colors['primary'],
            highlightthickness=0,
            sliderrelief='raised',
            command=lambda x: self.apply_filters()
        )
        self.rating_slider.pack(fill='x', pady=10)
        
        self.rating_label = tk.Label(
            rating_frame,
            text=f"امتیاز: {self.rating_var.get()}/10",
            font=("Tahoma", 10),
            fg=self.colors['highlight'],
            bg=self.colors['secondary']
        )
        self.rating_label.pack()
        
        ToolTip(self.rating_slider, "تنظیم حداقل امتیاز IMDb")
    
    def create_control_buttons(self, panel):
        """ایجاد دکمه‌های کنترلی"""
        buttons_frame = tk.Frame(panel, bg=self.colors['secondary'], pady=20)
        buttons_frame.pack(fill='x', padx=10)
        
        buttons = [
            ("🎲 شگفت‌زده شو", self.random_suggestion, "#7209b7"),
            ("⭐ لیست منتخب‌ها", self.show_watchlist, "#ff9e00"),
            ("🔄 بازنشانی فیلترها", self.reset_filters, "#ef476f"),
            ("📊 آمار و اطلاعات", self.show_statistics, "#06d6a0"),
            ("💾 ذخیره نتایج", self.save_results, "#2a9d8f")
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(
                buttons_frame,
                text=text,
                command=command,
                font=("Tahoma", 11, 'bold'),
                bg=color,
                fg='white',
                height=1,
                cursor='hand2',
                bd=0,
                padx=10,
                pady=10
            )
            btn.pack(fill='x', pady=6)
            ToolTip(btn, command.__doc__ if command.__doc__ else text)
    
    def create_right_panel(self, parent):
        """ایجاد پنل نتایج"""
        panel = tk.Frame(parent, bg=self.colors['primary'])
        panel.pack(side='right', fill='both', expand=True)
        
        # هدر نتایج
        results_header = tk.Frame(panel, bg=self.colors['secondary'], height=60)
        results_header.pack(fill='x', pady=(0, 10))
        
        self.results_title = tk.Label(
            results_header,
            text="🎬 فیلم‌های پیشنهادی",
            font=("Tahoma", 16, 'bold'),
            fg=self.colors['gold'],
            bg=self.colors['secondary']
        )
        self.results_title.pack(side='left', padx=20, pady=20)
        
        self.results_counter = tk.Label(
            results_header,
            text="تعداد: ۰",
            font=("Tahoma", 12, 'bold'),
            fg=self.colors['highlight'],
            bg=self.colors['secondary']
        )
        self.results_counter.pack(side='right', padx=20, pady=20)
        
        # نمایش نتایج
        self.create_results_display(panel)
    
    def create_results_display(self, parent):
        """ایجاد نمایش‌دهنده نتایج"""
        display_frame = tk.Frame(parent, bg=self.colors['primary'])
        display_frame.pack(fill='both', expand=True)
        
        # Canvas برای اسکرول
        self.results_canvas = tk.Canvas(
            display_frame,
            bg=self.colors['primary'],
            highlightthickness=0
        )
        
        # اسکرول بار
        scrollbar = ttk.Scrollbar(
            display_frame,
            orient='vertical',
            command=self.results_canvas.yview
        )
        
        # فریم قابل اسکرول
        self.scrollable_frame = tk.Frame(
            self.results_canvas,
            bg=self.colors['primary']
        )
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.results_canvas.configure(
                scrollregion=self.results_canvas.bbox("all")
            )
        )
        
        self.results_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.results_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.results_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # اسکرول با موس
        self.results_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def create_status_bar(self):
        """ایجاد نوار وضعیت"""
        self.status_bar = tk.Frame(
            self.root,
            bg=self.colors['secondary'],
            height=35
        )
        self.status_bar.pack(side='bottom', fill='x')
        
        self.status_label = tk.Label(
            self.status_bar,
            textvariable=self.status_text,
            font=("Tahoma", 10),
            fg=self.colors['light'],
            bg=self.colors['secondary'],
            anchor='w'
        )
        self.status_label.pack(side='left', padx=15, fill='x', expand=True)
        
        # نمایش زمان
        self.time_label = tk.Label(
            self.status_bar,
            text="",
            font=("Tahoma", 10),
            fg=self.colors['highlight'],
            bg=self.colors['secondary']
        )
        self.time_label.pack(side='right', padx=15)
        
        self.update_time()
    
    def _on_mousewheel(self, event):
        """کنترل اسکرول با موس"""
        self.results_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def update_time(self):
        """به‌روزرسانی زمان"""
        current_time = datetime.now().strftime("%Y/%m/%d - %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def apply_filters(self):
        """اعمال فیلترها و نمایش نتایج"""
        # به‌روزرسانی برچسب‌ها
        self.year_label.config(text=f"سال: {self.year_var.get()}")
        self.rating_label.config(text=f"امتیاز: {self.rating_var.get()}/10")
        
        # پاک کردن نتایج قبلی
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # جمع‌آوری ژانرهای انتخاب شده
        selected_genres = [
            genre for genre, state in self.genre_states.items() 
            if state
        ]
        
        if not selected_genres:
            selected_genres = self.genres
        
        # فیلتر کردن فیلم‌ها
        filtered_movies = []
        for genre in selected_genres:
            if genre in self.movies_db:
                for movie in self.movies_db[genre]:
                    if (movie['year'] >= self.year_var.get() and 
                        movie['rating'] >= self.rating_var.get()):
                        filtered_movies.append(movie)
        
        # مرتب‌سازی
        filtered_movies.sort(key=lambda x: x['rating'], reverse=True)
        filtered_movies = filtered_movies[:20]
        
        # نمایش کارت‌ها
        for i, movie in enumerate(filtered_movies, 1):
            card = self.create_movie_card(movie, i)
            card.pack(fill='x', pady=6, padx=5)
        
        # به‌روزرسانی اطلاعات
        self.results_title.config(
            text=f"🎬 {len(filtered_movies)} فیلم برتر"
        )
        self.results_counter.config(text=f"تعداد: {len(filtered_movies)}")
        self.status_text.set(f"✅ {len(filtered_movies)} فیلم یافت شد")
    
    def create_movie_card(self, movie, index):
        """ایجاد کارت فیلم"""
        card_color = movie.get('poster_color', self.colors['secondary'])
        
        card = tk.Frame(
            self.scrollable_frame,
            bg=card_color,
            relief='raised',
            bd=2
        )
        
        # شماره
        number_frame = tk.Frame(card, bg='#000000', width=45)
        number_frame.pack_propagate(False)
        number_frame.pack(side='left', fill='y', padx=(0, 15))
        
        tk.Label(
            number_frame,
            text=str(index),
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#000000'
        ).pack(expand=True)
        
        # اطلاعات فیلم
        info_frame = tk.Frame(card, bg=card_color)
        info_frame.pack(side='left', fill='both', expand=True, padx=10, pady=12)
        
        # عنوان
        title_frame = tk.Frame(info_frame, bg=card_color)
        title_frame.pack(fill='x')
        
        tk.Label(
            title_frame,
            text=movie['title'],
            font=("Tahoma", 13, 'bold'),
            fg='white',
            bg=card_color,
            anchor='w'
        ).pack(side='left')
        
        tk.Label(
            title_frame,
            text=f"({movie['year']})",
            font=("Tahoma", 11),
            fg=self.colors['gold'],
            bg=card_color
        ).pack(side='left', padx=(10, 0))
        
        # امتیاز
        rating_frame = tk.Frame(info_frame, bg=card_color)
        rating_frame.pack(fill='x', pady=6)
        
        stars = "★" * int(movie['rating'] // 2)
        empty_stars = "☆" * (5 - int(movie['rating'] // 2))
        
        tk.Label(
            rating_frame,
            text=f"⭐ {movie['rating']}/10  {stars}{empty_stars}",
            font=('Arial', 11),
            fg=self.colors['gold'],
            bg=card_color
        ).pack(side='left')
        
        # جزئیات
        details_frame = tk.Frame(info_frame, bg=card_color)
        details_frame.pack(fill='x')
        
        tk.Label(
            details_frame,
            text=f"🎬 {movie['director']}",
            font=("Tahoma", 11),
            fg='white',
            bg=card_color
        ).pack(side='left')
        
        tk.Label(
            details_frame,
            text=f"⏱️ {movie.get('duration', 'نامشخص')}",
            font=("Tahoma", 11),
            fg='white',
            bg=card_color
        ).pack(side='left', padx=(15, 0))
        
        # دکمه‌های اطراف
        buttons_frame = tk.Frame(card, bg=card_color)
        buttons_frame.pack(side='right', padx=10)
        
        # دکمه جزئیات
        info_btn = tk.Button(
            buttons_frame,
            text="ℹ️ جزئیات",
            command=lambda m=movie: self.show_movie_details(m),
            font=("Tahoma", 10),
            bg=self.colors['highlight'],
            fg='white',
            bd=0,
            padx=12,
            pady=5,
            cursor='hand2'
        )
        info_btn.pack(pady=3)
        ToolTip(info_btn, "مشاهده جزئیات کامل این فیلم")
        
        # دکمه سیو
        save_btn = tk.Button(
            buttons_frame,
            text="➕ ذخیره",
            command=lambda m=movie: self.add_to_watchlist(m),
            font=("Tahoma", 10),
            bg=self.colors['accent'],
            fg='white',
            bd=0,
            padx=12,
            pady=5,
            cursor='hand2'
        )
        save_btn.pack(pady=3)
        ToolTip(save_btn, "افزودن به لیست فیلم‌های منتخب")
        
        return card
    
    def show_movie_details(self, movie):
        """نمایش جزئیات کامل فیلم"""
        details_window = tk.Toplevel(self.root)
        details_window.title(f"جزئیات فیلم: {movie['title']}")
        details_window.geometry("600x500")
        details_window.configure(bg=movie.get('poster_color', self.colors['secondary']))
        details_window.resizable(False, False)
        
        # فریم اصلی
        main_frame = tk.Frame(details_window, bg=movie.get('poster_color', self.colors['secondary']))
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # عنوان
        tk.Label(
            main_frame,
            text=movie['title'],
            font=("Tahoma", 22, 'bold'),
            fg='white',
            bg=movie.get('poster_color', self.colors['secondary'])
        ).pack()
        
        tk.Label(
            main_frame,
            text=f"({movie['year']})",
            font=("Tahoma", 16),
            fg=self.colors['highlight'],
            bg=movie.get('poster_color', self.colors['secondary'])
        ).pack(pady=(0, 20))
        
        # کارت اطلاعات
        info_card = tk.Frame(
            main_frame,
            bg=self.colors['secondary'],
            relief='raised',
            bd=2
        )
        info_card.pack(fill='x', pady=10)
        
        info_items = [
            ("🎬 کارگردان:", movie['director']),
            ("⭐ امتیاز:", f"{movie['rating']}/10"),
            ("📅 سال تولید:", str(movie['year'])),
            ("⏱️ مدت زمان:", movie.get('duration', 'نامشخص')),
            ("🌍 کشور:", movie.get('country', 'نامشخص'))
        ]
        
        for label, value in info_items:
            item_frame = tk.Frame(info_card, bg=self.colors['secondary'])
            item_frame.pack(fill='x', padx=15, pady=8)
            
            tk.Label(
                item_frame,
                text=label,
                font=("Tahoma", 12, 'bold'),
                fg=self.colors['light'],
                bg=self.colors['secondary'],
                width=12,
                anchor='w'
            ).pack(side='left')
            
            tk.Label(
                item_frame,
                text=value,
                font=("Tahoma", 12),
                fg='white',
                bg=self.colors['secondary'],
                anchor='w'
            ).pack(side='left', padx=(10, 0))
        
        # خلاصه داستان
        summary_frame = tk.Frame(main_frame, bg=movie.get('poster_color', self.colors['secondary']))
        summary_frame.pack(fill='x', pady=15)
        
        tk.Label(
            summary_frame,
            text="📖 خلاصه داستان:",
            font=("Tahoma", 12, 'bold'),
            fg=self.colors['light'],
            bg=movie.get('poster_color', self.colors['secondary'])
        ).pack(anchor='w')
        
        text_frame = tk.Frame(summary_frame, bg=movie.get('poster_color', self.colors['secondary']))
        text_frame.pack(fill='x')
        
        summary_text = tk.Text(
            text_frame,
            height=6,
            wrap='word',
            font=("Tahoma", 11),
            bg=self.colors['secondary'],
            fg='white',
            relief='flat',
            padx=10,
            pady=10
        )
        
        scrollbar = tk.Scrollbar(text_frame, command=summary_text.yview)
        summary_text.config(yscrollcommand=scrollbar.set)
        
        summary_text.pack(side='left', fill='x', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        summary_text.insert('1.0', movie.get('description', 'توضیحی موجود نیست.'))
        summary_text.config(state='disabled')
        
        # دکمه‌ها
        button_frame = tk.Frame(main_frame, bg=movie.get('poster_color', self.colors['secondary']))
        button_frame.pack(fill='x', pady=20)
        
        if movie not in self.watchlist:
            tk.Button(
                button_frame,
                text="➕ افزودن به لیست منتخب",
                command=lambda: self.add_to_watchlist_from_details(movie, details_window),
                bg=self.colors['highlight'],
                fg='white',
                font=("Tahoma", 11, 'bold'),
                padx=20,
                pady=10,
                cursor='hand2'
            ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="بستن",
            command=details_window.destroy,
            bg=self.colors['accent'],
            fg='white',
            font=("Tahoma", 11, 'bold'),
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(side='right', padx=5)
        
        # مرکز کردن پنجره
        self.center_toplevel(details_window)
    
    def add_to_watchlist_from_details(self, movie, window):
        """افزودن فیلم به لیست از پنجره جزئیات"""
        self.add_to_watchlist(movie)
        window.destroy()
        self.show_movie_details(movie)
    
    def add_to_watchlist(self, movie):
        """افزودن فیلم به لیست منتخب‌ها"""
        if movie not in self.watchlist:
            self.watchlist.append(movie)
            self.status_text.set(f"✅ '{movie['title']}' به لیست منتخب‌ها اضافه شد")
            messagebox.showinfo("موفقیت", f"فیلم '{movie['title']}' به لیست منتخب‌های شما اضافه شد.")
        else:
            messagebox.showinfo("توجه", "این فیلم قبلاً در لیست منتخب‌های شما وجود دارد.")
    
    def show_watchlist(self):
        """نمایش لیست فیلم‌های منتخب"""
        if not self.watchlist:
            messagebox.showinfo("لیست منتخب‌ها", "لیست منتخب‌های شما خالی است.")
            return
        
        watchlist_window = tk.Toplevel(self.root)
        watchlist_window.title("⭐ لیست فیلم‌های منتخب من")
        watchlist_window.geometry("600x500")
        watchlist_window.configure(bg=self.colors['primary'])
        watchlist_window.resizable(False, False)
        
        # عنوان
        tk.Label(
            watchlist_window,
            text="🎬 فیلم‌های منتخب من",
            font=("Tahoma", 18, 'bold'),
            fg=self.colors['gold'],
            bg=self.colors['primary'],
            pady=20
        ).pack()
        
        # فریم لیست
        list_frame = tk.Frame(watchlist_window, bg=self.colors['primary'])
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Canvas برای اسکرول
        canvas = tk.Canvas(list_frame, bg=self.colors['primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=canvas.yview)
        scrollable_list = tk.Frame(canvas, bg=self.colors['primary'])
        
        scrollable_list.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_list, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # نمایش فیلم‌ها
        for i, movie in enumerate(self.watchlist, 1):
            movie_frame = tk.Frame(
                scrollable_list,
                bg=self.colors['secondary'],
                relief='raised',
                bd=1
            )
            movie_frame.pack(fill='x', pady=5, padx=5)
            
            tk.Label(
                movie_frame,
                text=f"{i}. {movie['title']} ({movie['year']}) - ⭐ {movie['rating']}/10",
                font=("Tahoma", 12),
                fg=self.colors['light'],
                bg=self.colors['secondary'],
                anchor='w',
                padx=10,
                pady=10
            ).pack(side='left', fill='x', expand=True)
            
            # دکمه حذف
            tk.Button(
                movie_frame,
                text="🗑️ حذف",
                command=lambda m=movie: self.remove_from_watchlist(m, watchlist_window),
                font=("Tahoma", 10),
                bg=self.colors['accent'],
                fg='white',
                bd=0,
                padx=10,
                pady=5,
                cursor='hand2'
            ).pack(side='right', padx=5)
        
        # دکمه بستن
        tk.Button(
            watchlist_window,
            text="بستن",
            command=watchlist_window.destroy,
            bg=self.colors['accent'],
            fg='white',
            font=("Tahoma", 12, 'bold'),
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(pady=20)
        
        self.center_toplevel(watchlist_window)
    
    def remove_from_watchlist(self, movie, window):
        """حذف فیلم از لیست"""
        if movie in self.watchlist:
            self.watchlist.remove(movie)
            self.status_text.set(f"🗑️ '{movie['title']}' از لیست منتخب‌ها حذف شد")
            window.destroy()
            self.show_watchlist()
    
    def random_suggestion(self):
        """پیشنهاد یک فیلم تصادفی"""
        all_movies = []
        selected_genres = [genre for genre, state in self.genre_states.items() if state]
        
        for genre in selected_genres:
            if genre in self.movies_db:
                for movie in self.movies_db[genre]:
                    if (movie['year'] >= self.year_var.get() and 
                        movie['rating'] >= self.rating_var.get()):
                        all_movies.append(movie)
        
        if not all_movies:
            messagebox.showwarning("هشدار", "هیچ فیلمی با فیلترهای فعلی وجود ندارد!")
            return
        
        movie = random.choice(all_movies)
        response = messagebox.askyesno(
            "پیشنهاد شانس",
            f"🎲 فیلم پیشنهادی:\n\n"
            f"🎬 {movie['title']} ({movie['year']})\n"
            f"⭐ امتیاز: {movie['rating']}/10\n"
            f"🎬 کارگردان: {movie['director']}\n\n"
            f"آیا می‌خواهید جزئیات این فیلم را مشاهده کنید؟"
        )
        
        if response:
            self.show_movie_details(movie)
        
        self.status_text.set(f"🎲 فیلم تصادفی: {movie['title']}")
    
    def reset_filters(self):
        """بازنشانی تمام فیلترها"""
        self.select_all_genres()
        self.year_var.set(2010)
        self.year_slider.set(2010)
        self.rating_var.set(6.0)
        self.rating_slider.set(6.0)
        self.apply_filters()
        self.status_text.set("🔄 تمام فیلترها بازنشانی شدند")
    
    def show_statistics(self):
        """نمایش آمار و اطلاعات برنامه"""
        total_movies = sum(len(movies) for movies in self.movies_db.values())
        avg_rating = sum(
            movie['rating'] 
            for movies in self.movies_db.values() 
            for movie in movies
        ) / total_movies if total_movies > 0 else 0
        
        stats_text = f"""
        📊 آمار و اطلاعات برنامه
        
        • تعداد کل فیلم‌ها در پایگاه داده: {total_movies}
        • تعداد ژانرهای موجود: {len(self.genres)}
        • میانگین امتیاز کل فیلم‌ها: {avg_rating:.2f}/10
        • بازه زمانی فیلم‌ها: ۲۰۰۰ تا ۲۰۲۴
        
        📈 آمار کاربری:
        • تعداد فیلم‌های منتخب شما: {len(self.watchlist)}
        • تعداد ژانرهای انتخاب شده: {sum(1 for state in self.genre_states.values() if state)}
        
        🎬 سینماسنج 
         توسعه‌دهنده: [محمد جواد منصوری]
        """
        
        messagebox.showinfo("📊 آمار و اطلاعات", stats_text)
        self.status_text.set("📊 آمار برنامه نمایش داده شد")
    
    def save_results(self):
        """ذخیره نتایج فعلی در فایل"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"نتایج_سینماسنج_{timestamp}.txt"
            
            content = "=" * 50 + "\n"
            content += "نتایج جستجوی سینماسنج\n"
            content += f"تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}\n"
            content += "=" * 50 + "\n\n"
            
            # جمع‌آوری فیلم‌های فعلی
            selected_genres = [genre for genre, state in self.genre_states.items() if state]
            filtered_movies = []
            
            for genre in selected_genres:
                if genre in self.movies_db:
                    for movie in self.movies_db[genre]:
                        if (movie['year'] >= self.year_var.get() and 
                            movie['rating'] >= self.rating_var.get()):
                            filtered_movies.append(movie)
            
            filtered_movies.sort(key=lambda x: x['rating'], reverse=True)
            filtered_movies = filtered_movies[:20]
            
            for i, movie in enumerate(filtered_movies, 1):
                content += f"{i}. {movie['title']} ({movie['year']})\n"
                content += f"   امتیاز: {movie['rating']}/10\n"
                content += f"   کارگردان: {movie['director']}\n"
                content += f"   مدت زمان: {movie.get('duration', 'نامشخص')}\n"
                content += "-" * 40 + "\n"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            messagebox.showinfo("موفقیت", f"نتایج با موفقیت در فایل '{filename}' ذخیره شد.")
            self.status_text.set(f"💾 نتایج ذخیره شد: {filename}")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره فایل: {str(e)}")
    
    def center_toplevel(self, toplevel):
        """مرکز کردن پنجره فرعی"""
        toplevel.update_idletasks()
        width = toplevel.winfo_width()
        height = toplevel.winfo_height()
        x = (toplevel.winfo_screenwidth() // 2) - (width // 2)
        y = (toplevel.winfo_screenheight() // 2) - (height // 2)
        toplevel.geometry(f'{width}x{height}+{x}+{y}')

# ==================== اجرای برنامه ==================== #
def main():
    root = tk.Tk()
    app = MovieRecommender(root)
    root.mainloop()

if __name__ == "__main__":

    main()

