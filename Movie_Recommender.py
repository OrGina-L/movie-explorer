# -*- coding: utf-8 -*-
"""
🎬 سینماسنج حرفه‌ای - اتصال مستقیم به TMDB API
برای جشنواره خوارزمی
توسعه‌دهنده: محمد جواد منصوری
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import random
from datetime import datetime
import time
import threading

# ==================== تنظیمات API ==================== #
TMDB_API_KEY = "d835c41276aafa3785266afd3b0a2f2c"

# ==================== مدیر TMDB ==================== #
class TMDBManager:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.image_url = "https://image.tmdb.org/t/p/w500"
        self.session = requests.Session()
        
        self.session.headers.update({
            'User-Agent': 'CinemaSensePro/3.0'
        })
        
        # ژانرهای فارسی ثابت
        self.genres_cache = {
            28: {'id': 28, 'name': 'اکشن', 'color': '#e63946'},
            12: {'id': 12, 'name': 'ماجراجویی', 'color': '#2a9d8f'},
            16: {'id': 16, 'name': 'انیمیشن', 'color': '#ff9e00'},
            35: {'id': 35, 'name': 'کمدی', 'color': '#ffd166'},
            80: {'id': 80, 'name': 'جنایی', 'color': '#6a040f'},
            18: {'id': 18, 'name': 'درام', 'color': '#7209b7'},
            10751: {'id': 10751, 'name': 'خانوادگی', 'color': '#06d6a0'},
            14: {'id': 14, 'name': 'فانتزی', 'color': '#8338ec'},
            27: {'id': 27, 'name': 'ترسناک', 'color': '#1a1a2e'},
            878: {'id': 878, 'name': 'علمی تخیلی', 'color': '#4cc9f0'},
            53: {'id': 53, 'name': 'هیجانی', 'color': '#3a0ca3'},
            10749: {'id': 10749, 'name': 'عاشقانه', 'color': '#ef476f'},
            9648: {'id': 9648, 'name': 'معمایی', 'color': '#3a86ff'},
            10752: {'id': 10752, 'name': 'جنگی', 'color': '#588157'},
            37: {'id': 37, 'name': 'وسترن', 'color': '#bc6c25'},
            99: {'id': 99, 'name': 'مستند', 'color': '#415a77'},
            10402: {'id': 10402, 'name': 'موزیکال', 'color': '#ffafcc'},
            36: {'id': 36, 'name': 'تاریخی', 'color': '#7b2cbf'},
            10770: {'id': 10770, 'name': 'فیلم TV', 'color': '#3a86ff'},
        }
        
        self.movies_cache = {}
        self.last_request_time = 0
        self.request_delay = 0.5
        
        # تلاش برای بارگذاری ژانرها از API
        try:
            self.load_genres()
        except Exception as e:
            print(f"⚠️  استفاده از ژانرهای پیش‌فرض: {e}")
    
    def make_request(self, url, params, timeout=15, max_retries=2):
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        
        for attempt in range(max_retries):
            try:
                params['api_key'] = self.api_key
                print(f"📡 درخواست به TMDB (تلاش {attempt+1}): {url}")
                
                response = self.session.get(url, params=params, timeout=timeout)
                self.last_request_time = time.time()
                
                if response.status_code == 429:
                    print("⚠️  محدودیت نرخ، منتظر می‌مانیم...")
                    time.sleep(2)
                    continue
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.Timeout:
                print(f"⏱️  تایم‌اوت در تلاش {attempt+1}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)
                
            except requests.exceptions.ConnectionError:
                print(f"🔌 خطای اتصال در تلاش {attempt+1}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ خطا در تلاش {attempt+1}: {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)
        
        raise Exception("همه تلاش‌ها شکست خورد")
    
    def load_genres(self):
        try:
            url = f"{self.base_url}/genre/movie/list"
            params = {'language': 'en-US'}
            
            print(f"🔍 درخواست ژانرها از: {url}")
            response = self.make_request(url, params)
            data = response.json()
            
            print(f"📊 پاسخ ژانرها: {data}")
            
            if 'genres' in data:
                print(f"✅ دریافت {len(data['genres'])} ژانر از API")
                for genre in data['genres']:
                    genre_id = genre.get('id')
                    genre_name_en = genre.get('name', '')
                    
                    if genre_id is not None:
                        # ترجمه انگلیسی به فارسی
                        en_to_fa = {
                            'Action': 'اکشن',
                            'Adventure': 'ماجراجویی',
                            'Animation': 'انیمیشن',
                            'Comedy': 'کمدی',
                            'Crime': 'جنایی',
                            'Documentary': 'مستند',
                            'Drama': 'درام',
                            'Family': 'خانوادگی',
                            'Fantasy': 'فانتزی',
                            'History': 'تاریخی',
                            'Horror': 'ترسناک',
                            'Music': 'موزیک',
                            'Mystery': 'معمایی',
                            'Romance': 'عاشقانه',
                            'Science Fiction': 'علمی تخیلی',
                            'TV Movie': 'فیلم TV',
                            'Thriller': 'هیجانی',
                            'War': 'جنگی',
                            'Western': 'وسترن'
                        }
                        
                        genre_name_fa = en_to_fa.get(genre_name_en, genre_name_en)
                        
                        # رنگ‌های ثابت برای هر ژانر
                        genre_colors = {
                            28: '#e63946', 12: '#2a9d8f', 16: '#ff9e00',
                            35: '#ffd166', 80: '#6a040f', 18: '#7209b7',
                            10751: '#06d6a0', 14: '#8338ec', 27: '#1a1a2e',
                            878: '#4cc9f0', 53: '#3a0ca3', 10749: '#ef476f',
                            9648: '#3a86ff', 10752: '#588157', 37: '#bc6c25',
                            99: '#415a77', 10402: '#ffafcc', 36: '#7b2cbf',
                            10770: '#3a86ff'
                        }
                        
                        self.genres_cache[genre_id] = {
                            'id': genre_id,
                            'name': genre_name_fa,
                            'name_en': genre_name_en,
                            'color': genre_colors.get(genre_id, '#415a77')
                        }
                        print(f"   → ID: {genre_id}, EN: {genre_name_en}, FA: {genre_name_fa}")
            
            print(f"✅ {len(self.genres_cache)} ژانر بارگذاری شد")
            return True
            
        except Exception as e:
            print(f"⚠️  خطا در بارگذاری ژانرها: {e}")
            return False
    
    def get_available_genres(self):
        """دریافت لیست ژانرهای موجود با مرتب‌سازی امن"""
        genres = []
        for genre_id, genre_data in self.genres_cache.items():
            # بررسی مقادیر None
            name = genre_data.get('name')
            if name is None:
                name = genre_data.get('name_en', 'نامشخص')
            
            color = genre_data.get('color')
            if color is None:
                color = '#415a77'
            
            genres.append({
                'id': genre_id,
                'name': name,
                'color': color
            })
        
        # مرتب‌سازی امن با استفاده از نام
        try:
            genres.sort(key=lambda x: x['name'])
        except:
            # اگر خطا داد، بر اساس ID مرتب کن
            genres.sort(key=lambda x: x['id'])
        
        return genres
    
    def search_movies(self, genre_ids=None, year_from=2010, min_rating=6.0, page=1):
        try:
            url = f"{self.base_url}/discover/movie"
            
            params = {
                'language': 'en-US',
                'sort_by': 'popularity.desc',
                'vote_count.gte': 50,
                'primary_release_date.gte': f'{year_from}-01-01',
                'vote_average.gte': min_rating,
                'page': page,
                'with_runtime.gte': 60
            }
            
            if genre_ids and len(genre_ids) > 0:
                params['with_genres'] = ','.join(str(gid) for gid in genre_ids)
                print(f"🔍 جستجو با ژانرها: {genre_ids}")
            
            print(f"📡 جستجوی فیلم با پارامترها: {params}")
            response = self.make_request(url, params, timeout=20)
            data = response.json()
            
            print(f"📊 تعداد نتایج: {data.get('total_results', 0)}")
            
            movies = []
            if 'results' in data:
                for movie in data['results']:
                    print(f"🎬 پردازش فیلم: {movie.get('title', 'بدون عنوان')}")
                    processed_movie = self.process_movie_data(movie)
                    if processed_movie and processed_movie['title'] and processed_movie['year'] > 0:
                        movies.append(processed_movie)
                        print(f"   ✅ اضافه شد: {processed_movie['title']}")
            
            # مرتب‌سازی امن
            for movie in movies:
                if movie.get('rating') is None:
                    movie['rating'] = 0
                if movie.get('popularity') is None:
                    movie['popularity'] = 0
            
            movies.sort(key=lambda x: (x.get('rating', 0), x.get('popularity', 0)), reverse=True)
            print(f"✅ {len(movies)} فیلم پردازش شد")
            return movies[:12]
            
        except Exception as e:
            print(f"⚠️  خطا در جستجوی فیلم‌ها: {e}")
            return []
    
    def process_movie_data(self, movie_data):
        if not movie_data:
            return None
        
        movie_id = movie_data.get('id')
        if movie_id is None:
            return None
        
        if movie_id in self.movies_cache:
            return self.movies_cache[movie_id]
        
        title = str(movie_data.get('title', 'نامشخص')).strip()
        if not title or title == 'نامشخص':
            title = str(movie_data.get('original_title', 'نامشخص')).strip()
        
        release_date = movie_data.get('release_date', '')
        year = 0
        if release_date and len(release_date) >= 4:
            try:
                year = int(release_date[:4])
            except:
                year = 0
        
        rating = 0.0
        try:
            rating = float(movie_data.get('vote_average', 0))
            rating = round(rating, 1)
        except:
            rating = 0.0
        
        overview = str(movie_data.get('overview', 'No description available.')).strip()
        if not overview or overview == 'No description available.':
            overview = 'این فیلم توضیح خاصی ندارد.'
        
        movie_genres = []
        genre_ids = movie_data.get('genre_ids', []) or []
        for genre_id in genre_ids[:2]:
            if genre_id in self.genres_cache:
                genre_name = self.genres_cache[genre_id].get('name', 'نامشخص')
                movie_genres.append(genre_name)
        
        poster_color = "#415a77"
        if genre_ids and genre_ids[0] in self.genres_cache:
            poster_color = self.genres_cache[genre_ids[0]].get('color', '#415a77')
        
        poster_path = movie_data.get('poster_path', '')
        poster_url = f"{self.image_url}{poster_path}" if poster_path else None
        
        movie = {
            'id': movie_id,
            'title': title,
            'year': year,
            'rating': rating,
            'description': overview,
            'genres': movie_genres,
            'poster_url': poster_url,
            'poster_color': poster_color,
            'popularity': float(movie_data.get('popularity', 0)) or 0,
            'vote_count': int(movie_data.get('vote_count', 0)) or 0
        }
        
        self.movies_cache[movie_id] = movie
        return movie
    
    def get_movie_details(self, movie_id):
        try:
            if movie_id in self.movies_cache and 'director' in self.movies_cache[movie_id]:
                return self.movies_cache[movie_id]
            
            url = f"{self.base_url}/movie/{movie_id}"
            params = {
                'language': 'en-US',
                'append_to_response': 'credits'
            }
            
            print(f"📡 دریافت جزئیات فیلم: {movie_id}")
            response = self.make_request(url, params)
            movie_data = response.json()
            
            processed_movie = self.process_movie_data(movie_data)
            if not processed_movie:
                return None
            
            director = "نامشخص"
            crew = movie_data.get('credits', {}).get('crew', [])
            for person in crew:
                if person.get('job') == 'Director':
                    director = person.get('name', 'نامشخص')
                    break
            
            actors = []
            cast = movie_data.get('credits', {}).get('cast', [])[:3]
            for actor in cast:
                actor_name = actor.get('name', 'نامشخص')
                if actor_name:
                    actors.append(actor_name)
            
            if not actors:
                actors = ['نامشخص']
            
            runtime = movie_data.get('runtime', 0)
            duration = f"{runtime} دقیقه" if runtime and runtime > 0 else "نامشخص"
            
            country = "نامشخص"
            countries = movie_data.get('production_countries', [])
            if countries and len(countries) > 0:
                country = countries[0].get('name', 'نامشخص')
            
            processed_movie.update({
                'director': director,
                'actors': actors,
                'duration': duration,
                'country': country,
                'budget': movie_data.get('budget', 0) or 0,
                'revenue': movie_data.get('revenue', 0) or 0
            })
            
            self.movies_cache[movie_id] = processed_movie
            return processed_movie
            
        except Exception as e:
            print(f"⚠️  خطا در دریافت جزئیات فیلم: {e}")
            return None

# ==================== برنامه اصلی ==================== #
class CinemaSensePro:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.show_loading_screen()
        self.root.after(1000, self.initialize_app)
    
    def setup_window(self):
        self.root.title("🎬 سینماسنج حرفه‌ای")
        self.root.geometry("1200x700")
        
        self.colors = {
            'primary': '#0d1b2a',
            'secondary': '#1b263b',
            'accent': '#e63946',
            'light': '#f1faee',
            'highlight': '#a8dadc',
            'gold': '#ffd166',
            'button_active': '#2a9d8f',
            'button_inactive': '#415a77',
            'info': '#7209b7',
            'creator': '#ff6b6b'
        }
        
        self.root.configure(bg=self.colors['primary'])
        self.center_window()
        
        self.status_text = tk.StringVar(value="آماده")
        self.watchlist = []
        self.genre_buttons = {}
        self.selected_genres = []
        self.api_connected = False
        self.api_manager = None
        self.current_page = 1
    
    def center_window(self):
        self.root.update_idletasks()
        width = 1200
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_loading_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.loading_frame = tk.Frame(self.root, bg=self.colors['primary'])
        self.loading_frame.pack(expand=True, fill='both')
        
        # نمایش لوگو
        logo_frame = tk.Frame(self.loading_frame, bg=self.colors['primary'])
        logo_frame.pack(pady=(80, 20))
        
        tk.Label(
            logo_frame,
            text="🎬",
            font=("Arial", 72),
            fg=self.colors['gold'],
            bg=self.colors['primary']
        ).pack()
        
        # نمایش نام برنامه
        tk.Label(
            self.loading_frame,
            text="سینماسنج حرفه‌ای",
            font=("Tahoma", 28, 'bold'),
            fg=self.colors['gold'],
            bg=self.colors['primary']
        ).pack()
        
        # نمایش زیرنویس
        tk.Label(
            self.loading_frame,
            text="برای جشنواره خوارزمی | توسعه: محمد جواد منصوری",
            font=("Tahoma", 14),
            fg=self.colors['highlight'],
            bg=self.colors['primary']
        ).pack(pady=10)
        
        # نمایش وضعیت بارگذاری
        self.loading_status = tk.StringVar(value="در حال راه‌اندازی...")
        tk.Label(
            self.loading_frame,
            textvariable=self.loading_status,
            font=("Tahoma", 11),
            fg=self.colors['light'],
            bg=self.colors['primary']
        ).pack(pady=30)
        
        # نوار پیشرفت
        self.progress = ttk.Progressbar(
            self.loading_frame,
            length=300,
            mode='indeterminate'
        )
        self.progress.pack(pady=20)
        self.progress.start(10)
        
        # نمایش نسخه
        tk.Label(
            self.loading_frame,
            text="نسخه ۳.۰",
            font=("Tahoma", 10),
            fg=self.colors['creator'],
            bg=self.colors['primary']
        ).pack(pady=10)
    
    def initialize_app(self):
        try:
            self.loading_status.set("برقراری اتصال به TMDB...")
            
            # تست ساده اتصال
            try:
                test_url = "https://api.themoviedb.org/3/movie/550"
                params = {'api_key': TMDB_API_KEY}
                response = requests.get(test_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    print("✅ اتصال به TMDB برقرار شد")
                    self.api_manager = TMDBManager(TMDB_API_KEY)
                    self.api_connected = True
                    self.loading_status.set("✅ اتصال موفق - آماده به کار")
                else:
                    print(f"❌ خطا در اتصال: کد {response.status_code}")
                    self.api_connected = False
                    self.loading_status.set("❌ خطا در اتصال به TMDB")
                    
            except Exception as e:
                print(f"❌ خطا در تست اتصال: {e}")
                self.api_connected = False
                self.loading_status.set("❌ خطا در اتصال اینترنت")
            
            time.sleep(1.5)
            self.progress.stop()
            self.loading_frame.destroy()
            
            if self.api_connected:
                self.setup_ui()
                self.apply_initial_filters()
            else:
                self.show_offline_interface()
                
        except Exception as e:
            print(f"❌ خطای اصلی در بارگذاری: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_screen(str(e))
    
    def show_error_screen(self, error_msg):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        error_frame = tk.Frame(self.root, bg=self.colors['primary'])
        error_frame.pack(expand=True, fill='both', padx=50, pady=50)
        
        tk.Label(
            error_frame,
            text="❌ خطا در اجرای برنامه",
            font=("Tahoma", 24, 'bold'),
            fg=self.colors['accent'],
            bg=self.colors['primary']
        ).pack(pady=20)
        
        tk.Label(
            error_frame,
            text=f"خطا:\n{error_msg[:200]}",
            font=("Tahoma", 12),
            fg=self.colors['light'],
            bg=self.colors['primary'],
            justify='left',
            wraplength=500
        ).pack(pady=20)
        
        button_frame = tk.Frame(error_frame, bg=self.colors['primary'])
        button_frame.pack(pady=30)
        
        tk.Button(
            button_frame,
            text="🔄 تلاش مجدد",
            command=self.retry_connection,
            font=("Tahoma", 12, 'bold'),
            bg=self.colors['button_active'],
            fg='white',
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame,
            text="🎬 حالت آفلاین",
            command=self.load_sample_data,
            font=("Tahoma", 12, 'bold'),
            bg=self.colors['gold'],
            fg='black',
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(side='left', padx=10)
        
        tk.Button(
            button_frame,
            text="🚪 خروج",
            command=self.root.quit,
            font=("Tahoma", 12, 'bold'),
            bg=self.colors['accent'],
            fg='white',
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(side='left', padx=10)
    
    def show_offline_interface(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        header = tk.Frame(self.root, bg=self.colors['secondary'], height=100)
        header.pack(fill='x')
        
        tk.Label(
            header,
            text="🎬 سینماسنج حرفه‌ای",
            font=("Tahoma", 28, 'bold'),
            fg=self.colors['gold'],
            bg=self.colors['secondary']
        ).pack(pady=20)
        
        main_frame = tk.Frame(self.root, bg=self.colors['primary'])
        main_frame.pack(expand=True, fill='both', padx=50, pady=30)
        
        tk.Label(
            main_frame,
            text="🔌 حالت آفلاین",
            font=("Tahoma", 24, 'bold'),
            fg=self.colors['accent'],
            bg=self.colors['primary']
        ).pack(pady=20)
        
        tk.Label(
            main_frame,
            text="برنامه نمی‌تواند به TMDB API متصل شود.\n\n"
                 "می‌توانید از داده‌های نمونه استفاده کنید:",
            font=("Tahoma", 14),
            fg=self.colors['light'],
            bg=self.colors['primary'],
            justify='left'
        ).pack(pady=20)
        
        button_frame = tk.Frame(main_frame, bg=self.colors['primary'])
        button_frame.pack(pady=30)
        
        tk.Button(
            button_frame,
            text="🔄 تلاش مجدد برای اتصال",
            command=self.retry_connection,
            font=("Tahoma", 12, 'bold'),
            bg=self.colors['button_active'],
            fg='white',
            padx=30,
            pady=12,
            cursor='hand2'
        ).pack(pady=10)
        
        tk.Button(
            button_frame,
            text="🎬 نمایش داده‌های نمونه",
            command=self.load_sample_data,
            font=("Tahoma", 12, 'bold'),
            bg=self.colors['gold'],
            fg='black',
            padx=30,
            pady=12,
            cursor='hand2'
        ).pack(pady=10)
        
        self.status_text.set("حالت آفلاین")
        status_bar = tk.Frame(self.root, bg=self.colors['secondary'], height=35)
        status_bar.pack(side='bottom', fill='x')
        
        tk.Label(
            status_bar,
            textvariable=self.status_text,
            font=("Tahoma", 10),
            fg=self.colors['light'],
            bg=self.colors['secondary'],
            anchor='w'
        ).pack(side='left', padx=15, fill='x', expand=True)
        
        tk.Label(
            status_bar,
            text="نسخه ۳.۰ | محمد جواد منصوری",
            font=("Tahoma", 10),
            fg=self.colors['creator'],
            bg=self.colors['secondary']
        ).pack(side='right', padx=15)
    
    def retry_connection(self):
        self.show_loading_screen()
        self.root.after(1500, self.initialize_app)
    
    def load_sample_data(self):
        class SampleManager:
            def get_available_genres(self):
                return [
                    {'id': 28, 'name': 'اکشن', 'color': '#e63946'},
                    {'id': 18, 'name': 'درام', 'color': '#7209b7'},
                    {'id': 35, 'name': 'کمدی', 'color': '#ffd166'},
                    {'id': 878, 'name': 'علمی تخیلی', 'color': '#4cc9f0'},
                    {'id': 16, 'name': 'انیمیشن', 'color': '#ff9e00'},
                    {'id': 10749, 'name': 'عاشقانه', 'color': '#ef476f'},
                    {'id': 53, 'name': 'هیجانی', 'color': '#3a0ca3'},
                    {'id': 27, 'name': 'ترسناک', 'color': '#1a1a2e'}
                ]
            
            def search_movies(self, **kwargs):
                return self.get_sample_movies()
            
            def get_sample_movies(self):
                return [
                    {
                        'id': 1,
                        'title': 'شوالیه تاریکی',
                        'year': 2008,
                        'rating': 9.0,
                        'description': 'باتمن باید با جوکر، یک تروریست روان‌پریش مقابله کند که می‌خواهد شهر گاتهام را نابود کند.',
                        'genres': ['اکشن', 'درام'],
                        'poster_color': '#e63946',
                        'popularity': 85.5
                    },
                    {
                        'id': 2,
                        'title': 'پاراسایت',
                        'year': 2019,
                        'rating': 8.6,
                        'description': 'یک خانواده فقیر کره‌ای با فریب دادن یک خانواده ثروتمند، به زندگی آن‌ها نفوذ می‌کنند.',
                        'genres': ['درام', 'هیجانی'],
                        'poster_color': '#7209b7',
                        'popularity': 78.2
                    },
                    {
                        'id': 3,
                        'title': 'درون و بیرون',
                        'year': 2015,
                        'rating': 8.1,
                        'description': 'داستان احساسات یک دختر نوجوان و چگونگی کنترل آن‌ها در ذهن او.',
                        'genres': ['انیمیشن', 'کمدی'],
                        'poster_color': '#ff9e00',
                        'popularity': 72.8
                    },
                    {
                        'id': 4,
                        'title': 'آواتار',
                        'year': 2009,
                        'rating': 7.8,
                        'description': 'یک سرباز معلول در مأموریتی به سیاره پاندورا می‌رود و با موجودات آنجا ارتباط برقرار می‌کند.',
                        'genres': ['اکشن', 'ماجراجویی'],
                        'poster_color': '#4cc9f0',
                        'popularity': 68.4
                    },
                    {
                        'id': 5,
                        'title': 'پلنگ سیاه',
                        'year': 2018,
                        'rating': 7.3,
                        'description': 'تیت‌چالا، پادشاه جدید وکندا، باید از کشورش در برابر دشمنان قدیمی دفاع کند.',
                        'genres': ['اکشن', 'ماجراجویی'],
                        'poster_color': '#3a0ca3',
                        'popularity': 65.1
                    }
                ]
            
            def get_movie_details(self, movie_id):
                movies = self.get_sample_movies()
                for movie in movies:
                    if movie['id'] == movie_id:
                        movie.update({
                            'director': 'کارگردان نمونه',
                            'actors': ['بازیگر ۱', 'بازیگر ۲', 'بازیگر ۳'],
                            'duration': '120 دقیقه',
                            'country': 'آمریکا'
                        })
                        return movie
                return None
        
        self.api_manager = SampleManager()
        self.api_connected = False
        self.setup_ui()
        self.show_sample_results()
    
    def show_sample_results(self):
        self.results_title.config(text="🎬 فیلم‌های نمونه (حالت آفلاین)")
        self.results_counter.config(text="تعداد: ۵")
        self.status_text.set("نمایش داده‌های نمونه")
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        movies = self.api_manager.get_sample_movies()
        for i, movie in enumerate(movies, 1):
            card = self.create_movie_card(movie, i)
            card.pack(fill='x', pady=8, padx=5)
    
    def setup_ui(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.create_header()
        
        main_frame = tk.Frame(self.root, bg=self.colors['primary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.create_left_panel(main_frame)
        self.create_right_panel(main_frame)
        self.create_status_bar()
    
    def create_header(self):
        header = tk.Frame(self.root, bg=self.colors['secondary'], height=120)
        header.pack(fill='x')
        
        title_frame = tk.Frame(header, bg=self.colors['secondary'])
        title_frame.pack(expand=True, fill='both', pady=15)
        
        # عنوان اصلی
        tk.Label(
            title_frame,
            text="🎬 سینماسنج حرفه‌ای",
            font=("Tahoma", 28, 'bold'),
            fg=self.colors['gold'],
            bg=self.colors['secondary']
        ).pack()
        
        # زیرنویس با اطلاعات
        subtitle = "اتصال به TMDB API" if self.api_connected else "حالت آفلاین"
        tk.Label(
            title_frame,
            text=f"{subtitle} | جشنواره خوارزمی | نسخه ۳.۰",
            font=('Tahoma', 11),
            fg=self.colors['highlight'],
            bg=self.colors['secondary']
        ).pack(pady=5)
    
    def create_left_panel(self, parent):
        panel = tk.Frame(parent, bg=self.colors['secondary'], width=280)
        panel.pack(side='left', fill='y', padx=(0, 15))
        
        tk.Label(
            panel,
            text="⚙️ فیلترهای جستجو",
            font=("Tahoma", 16, 'bold'),
            fg=self.colors['highlight'],
            bg=self.colors['secondary'],
            pady=20
        ).pack()
        
        self.create_genre_section(panel)
        self.create_year_section(panel)
        self.create_rating_section(panel)
        self.create_control_buttons(panel)
    
    def create_genre_section(self, panel):
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
        
        genres = self.api_manager.get_available_genres()
        print(f"🎭 تعداد ژانرهای موجود: {len(genres)}")
        
        self.genre_buttons = {}
        self.selected_genres = []
        
        # فقط 10 ژانر اول را نمایش می‌دهیم
        for i, genre in enumerate(genres[:10]):
            row = i // 2
            col = i % 2
            
            btn = tk.Button(
                genre_frame,
                text=genre['name'],
                font=("Tahoma", 10),
                width=13,
                height=2,
                relief='sunken',
                cursor='hand2',
                command=lambda g=genre: self.toggle_genre(g['id'])
            )
            
            btn.config(
                bg=genre['color'],
                fg='white',
                activebackground=self.colors['accent'],
                activeforeground='white'
            )
            
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
            self.genre_buttons[genre['id']] = {
                'button': btn,
                'selected': True,
                'color': genre['color']
            }
            self.selected_genres.append(genre['id'])
            print(f"   ✅ ژانر: {genre['name']} (ID: {genre['id']})")
        
        control_frame = tk.Frame(genre_frame, bg=self.colors['secondary'])
        rows_needed = ((min(10, len(genres)) + 1) // 2)
        control_frame.grid(row=rows_needed, column=0, columnspan=2, pady=(15, 0), sticky='ew')
        
        tk.Button(
            control_frame,
            text="✅ انتخاب همه",
            command=self.select_all_genres,
            font=("Tahoma", 10),
            bg=self.colors['highlight'],
            fg='white',
            cursor='hand2',
            padx=10,
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
            padx=10,
            pady=5
        ).pack(side='left', padx=5)
    
    def toggle_genre(self, genre_id):
        if genre_id not in self.genre_buttons:
            return
            
        genre_data = self.genre_buttons[genre_id]
        genre_data['selected'] = not genre_data['selected']
        
        if genre_data['selected']:
            genre_data['button'].config(relief='sunken', bg=genre_data['color'])
            if genre_id not in self.selected_genres:
                self.selected_genres.append(genre_id)
        else:
            genre_data['button'].config(relief='raised', bg=self.colors['button_inactive'])
            if genre_id in self.selected_genres:
                self.selected_genres.remove(genre_id)
        
        print(f"🎭 ژانر {genre_id} {'انتخاب شد' if genre_data['selected'] else 'لغو شد'}")
        self.apply_filters()
    
    def select_all_genres(self):
        for genre_id, genre_data in self.genre_buttons.items():
            genre_data['selected'] = True
            genre_data['button'].config(relief='sunken', bg=genre_data['color'])
            if genre_id not in self.selected_genres:
                self.selected_genres.append(genre_id)
        print("✅ همه ژانرها انتخاب شدند")
        self.apply_filters()
    
    def deselect_all_genres(self):
        for genre_id, genre_data in self.genre_buttons.items():
            genre_data['selected'] = False
            genre_data['button'].config(relief='raised', bg=self.colors['button_inactive'])
            if genre_id in self.selected_genres:
                self.selected_genres.remove(genre_id)
        print("❌ همه ژانرها لغو شدند")
        self.apply_filters()
    
    def create_year_section(self, panel):
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
            from_=1990,
            to=2024,
            variable=self.year_var,
            orient='horizontal',
            length=240,
            bg=self.colors['secondary'],
            fg=self.colors['light'],
            troughcolor=self.colors['primary'],
            highlightthickness=0,
            command=lambda x: self.on_slider_change()
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
    
    def create_rating_section(self, panel):
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
            length=240,
            bg=self.colors['secondary'],
            fg=self.colors['light'],
            troughcolor=self.colors['primary'],
            highlightthickness=0,
            command=lambda x: self.on_slider_change()
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
    
    def on_slider_change(self):
        self.year_label.config(text=f"سال: {self.year_var.get()}")
        self.rating_label.config(text=f"امتیاز: {self.rating_var.get()}/10")
        if hasattr(self, '_slider_timeout'):
            self.root.after_cancel(self._slider_timeout)
        self._slider_timeout = self.root.after(500, self.apply_filters)
    
    def create_control_buttons(self, panel):
        buttons_frame = tk.Frame(panel, bg=self.colors['secondary'], pady=20)
        buttons_frame.pack(fill='x', padx=10)
        
        buttons = [
            ("🎲 شگفت‌زده شو", self.random_suggestion, "#7209b7"),
            ("⭐ لیست منتخب‌ها", self.show_watchlist, "#ff9e00"),
            ("🔄 بازنشانی فیلترها", self.reset_filters, "#ef476f"),
            ("📊 آمار و اطلاعات", self.show_statistics, "#06d6a0"),
            ("💾 ذخیره نتایج", self.save_results, "#2a9d8f"),
            ("ℹ️ اطلاعات برنامه", self.show_program_info, "#7209b7", True)  # دکمه جدید با ایکون ویژه
        ]
        
        for button_info in buttons:
            if len(button_info) == 4:  # اگر دکمه ویژه باشد
                text, command, color, is_special = button_info
                special_style = True
            else:
                text, command, color = button_info
                special_style = False
            
            btn = tk.Button(
                buttons_frame,
                text=text,
                command=command,
                font=("Tahoma", 11, 'bold' if special_style else 'normal'),
                bg=color,
                fg='white',
                height=1,
                cursor='hand2',
                bd=0,
                padx=15,
                pady=12,
                relief='raised' if special_style else 'flat'
            )
            
            if special_style:
                # برای دکمه اطلاعات برنامه، استایل ویژه
                btn.config(
                    font=("Tahoma", 12, 'bold'),
                    bg='#8a2be2',  # ✅ رنگ بنفش زیبا
                    fg='white',
                    activebackground='#6a0dad',
                    activeforeground='white',
                    borderwidth=3,
                    relief='groove',
                    cursor='hand2',
                    padx=20,
                    pady=12 
                )
            
            btn.pack(fill='x', pady=8)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=b.cget('bg') + '80'))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
    
    def show_program_info(self):
        """نمایش اطلاعات برنامه"""
        info_window = tk.Toplevel(self.root)
        info_window.title("ℹ️ اطلاعات برنامه")
        info_window.geometry("500x450")
        info_window.configure(bg=self.colors['primary'])
        info_window.resizable(False, False)
        
        # هدر پنجره
        header_frame = tk.Frame(info_window, bg=self.colors['info'], height=100)
        header_frame.pack(fill='x')
        
        tk.Label(
            header_frame,
            text="🎬 سینماسنج حرفه‌ای",
            font=("Tahoma", 24, 'bold'),
            fg='white',
            bg=self.colors['info'],
            pady=20
        ).pack()
        
        # محتوای اصلی
        content_frame = tk.Frame(info_window, bg=self.colors['primary'])
        content_frame.pack(fill='both', expand=True, padx=30, pady=20)
        
        # اطلاعات برنامه
        info_text = """
        ═══════════════════════════════════════
        📱 اطلاعات برنامه
        
        🎬 نام برنامه: سینماسنج حرفه‌ای
        📅 نسخه: ۳.۰
        🔧 وضعیت: پروژه جشنواره خوارزمی
        
        ═══════════════════════════════════════
        👨‍💻 توسعه‌دهنده
        
        ✨ نام: محمد جواد منصوری
        🎓 دانش‌آموز: متوسطه دوم
        🏆 پروژه: برای جشنواره خوارزمی
        
        ═══════════════════════════════════════
        🌐 ویژگی‌های برنامه
        
        ✅ اتصال مستقیم به TMDB API
        ✅ جستجوی پیشرفته فیلم‌ها
        ✅ فیلتر بر اساس ژانر، سال و امتیاز
        ✅ لیست فیلم‌های منتخب
        ✅ نمایش جزئیات کامل فیلم‌ها
        ✅ حالت آفلاین با داده‌های نمونه
        ✅ رابط کاربری فارسی و زیبا
        
        ═══════════════════════════════════════
        🚀 فناوری‌های استفاده شده
        
        🐍 زبان برنامه‌نویسی: Python
        🎨 کتابخانه رابط کاربری: Tkinter
        🌐 API استفاده شده: The Movie Database
        🎯 هدف: یادگیری و توسعه مهارت‌های برنامه‌نویسی
        
        ═══════════════════════════════════════
        📞 ارتباط
        
        💡 این پروژه به عنوان یک پروژه آموزشی
        و برای شرکت در جشنواره خوارزمی توسعه یافته است.
        """
        
        # ایجاد قاب برای متن با اسکرول
        text_frame = tk.Frame(content_frame, bg=self.colors['primary'])
        text_frame.pack(fill='both', expand=True)
        
        text_widget = tk.Text(
            text_frame,
            height=20,
            width=50,
            font=("Tahoma", 10),
            bg=self.colors['secondary'],
            fg=self.colors['light'],
            wrap='word',
            relief='flat',
            padx=15,
            pady=15
        )
        
        scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # درج متن اطلاعات
        text_widget.insert('1.0', info_text)
        text_widget.config(state='disabled')
        
        # دکمه بستن
        close_frame = tk.Frame(info_window, bg=self.colors['primary'])
        close_frame.pack(fill='x', pady=10)
        
        close_btn = tk.Button(
            close_frame,
            text="بستن",
            command=info_window.destroy,
            font=("Tahoma", 12, 'bold'),
            bg=self.colors['creator'],
            fg='white',
            padx=30,
            pady=10,
            cursor='hand2',
            relief='raised',
            bd=3
        )
        close_btn.pack()
        
        # انیمیشن برای دکمه
        def on_enter(e):
            close_btn.config(bg='#ff8a8a')
        def on_leave(e):
            close_btn.config(bg=self.colors['creator'])
        
        close_btn.bind("<Enter>", on_enter)
        close_btn.bind("<Leave>", on_leave)
        
        self.center_toplevel(info_window)
        info_window.transient(self.root)
        info_window.grab_set()
    
    def create_right_panel(self, parent):
        panel = tk.Frame(parent, bg=self.colors['primary'])
        panel.pack(side='right', fill='both', expand=True)
        
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
        
        # اضافه کردن دکمه‌های صفحه‌بندی
        pagination_frame = tk.Frame(results_header, bg=self.colors['secondary'])
        pagination_frame.pack(side='right', padx=(0, 20))
        
        self.page_buttons = []
        
        self.prev_btn = tk.Button(
            pagination_frame,
            text="◀ قبلی",
            command=self.prev_page,
            font=("Tahoma", 10),
            bg=self.colors['button_inactive'],
            fg='white',
            state='disabled',
            cursor='hand2',
            padx=10,
            pady=5
        )
        self.prev_btn.pack(side='left', padx=2)
        self.page_buttons.append(self.prev_btn)
        
        self.page_label = tk.Label(
            pagination_frame,
            text="صفحه 1",
            font=("Tahoma", 10),
            fg=self.colors['highlight'],
            bg=self.colors['secondary']
        )
        self.page_label.pack(side='left', padx=10)
        
        self.next_btn = tk.Button(
            pagination_frame,
            text="بعدی ▶",
            command=self.next_page,
            font=("Tahoma", 10),
            bg=self.colors['button_active'],
            fg='white',
            cursor='hand2',
            padx=10,
            pady=5
        )
        self.next_btn.pack(side='left', padx=2)
        self.page_buttons.append(self.next_btn)
        
        self.create_results_display(panel)
    
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.update_pagination_buttons()
            self.apply_filters()
    
    def next_page(self):
        self.current_page += 1
        self.update_pagination_buttons()
        self.apply_filters()
    
    def update_pagination_buttons(self):
        self.page_label.config(text=f"صفحه {self.current_page}")
        
        # غیرفعال کردن دکمه قبلی اگر در صفحه اول هستیم
        if self.current_page == 1:
            self.prev_btn.config(state='disabled', bg=self.colors['button_inactive'])
        else:
            self.prev_btn.config(state='normal', bg=self.colors['button_active'])
        
        # همیشه دکمه بعدی فعال باشد
        self.next_btn.config(state='normal', bg=self.colors['button_active'])
    
    def create_results_display(self, panel):
        display_frame = tk.Frame(panel, bg=self.colors['primary'])
        display_frame.pack(fill='both', expand=True)
        
        self.results_canvas = tk.Canvas(
            display_frame,
            bg=self.colors['primary'],
            highlightthickness=0
        )
        
        scrollbar = ttk.Scrollbar(
            display_frame,
            orient='vertical',
            command=self.results_canvas.yview
        )
        
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
        
        # Bind mouse wheel for scrolling
        self.results_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.results_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.results_canvas.bind_all("<Button-5>", self._on_mousewheel)
    
    def create_status_bar(self):
        self.status_bar = tk.Frame(
            self.root,
            bg=self.colors['secondary'],
            height=40
        )
        self.status_bar.pack(side='bottom', fill='x')
        
        # وضعیت برنامه
        self.status_label = tk.Label(
            self.status_bar,
            textvariable=self.status_text,
            font=("Tahoma", 10),
            fg=self.colors['light'],
            bg=self.colors['secondary'],
            anchor='w'
        )
        self.status_label.pack(side='left', padx=15, fill='x', expand=True)
        
        # اطلاعات سازنده و نسخه
        creator_frame = tk.Frame(self.status_bar, bg=self.colors['secondary'])
        creator_frame.pack(side='right', padx=15)
        
        tk.Label(
            creator_frame,
            text="🎬",
            font=("Arial", 12),
            fg=self.colors['gold'],
            bg=self.colors['secondary']
        ).pack(side='left', padx=(0, 5))
        
        tk.Label(
            creator_frame,
            text="نسخه ۳.۰ | محمد جواد منصوری",
            font=("Tahoma", 10, 'bold'),
            fg=self.colors['creator'],
            bg=self.colors['secondary']
        ).pack(side='left')
        
        # زمان
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
        if event.num == 4 or event.delta > 0:
            self.results_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.results_canvas.yview_scroll(1, "units")
    
    def update_time(self):
        current_time = datetime.now().strftime("%Y/%m/%d - %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
    
    def apply_initial_filters(self):
        print("🎯 اعمال فیلترهای اولیه...")
        self.current_page = 1
        self.update_pagination_buttons()
        self.apply_filters()
    
    def apply_filters(self, event=None):
        print("🎯 شروع جستجو با فیلترها...")
        print(f"   🎭 ژانرهای انتخاب شده: {self.selected_genres}")
        print(f"   📅 سال از: {self.year_var.get()}")
        print(f"   ⭐ حداقل امتیاز: {self.rating_var.get()}")
        print(f"   📄 صفحه فعلی: {self.current_page}")
        
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        loading_frame = tk.Frame(self.scrollable_frame, bg=self.colors['primary'])
        loading_frame.pack(expand=True, pady=50)
        
        tk.Label(
            loading_frame,
            text="⏳ در حال جستجو...",
            font=("Tahoma", 14, 'bold'),
            fg=self.colors['light'],
            bg=self.colors['primary']
        ).pack()
        
        tk.Label(
            loading_frame,
            text="لطفاً چند ثانیه صبر کنید",
            font=("Tahoma", 11),
            fg=self.colors['highlight'],
            bg=self.colors['primary']
        ).pack(pady=10)
        
        if self.api_connected:
            self.results_title.config(text=f"🔍 در حال جستجو در TMDB (صفحه {self.current_page})...")
            self.status_text.set("در حال دریافت داده‌ها از TMDB...")
            threading.Thread(target=self._perform_search, daemon=True).start()
        else:
            self.results_title.config(text="🔍 در حال بارگذاری نمونه‌ها...")
            self.status_text.set("در حال بارگذاری داده‌های نمونه...")
            self.root.after(1500, self.show_sample_results)
    
    def _perform_search(self):
        try:
            print("🔍 شروع جستجو در TMDB...")
            movies = self.api_manager.search_movies(
                genre_ids=self.selected_genres if self.selected_genres else None,
                year_from=self.year_var.get(),
                min_rating=self.rating_var.get(),
                page=self.current_page
            )
            
            print(f"✅ {len(movies)} فیلم یافت شد")
            self.root.after(0, self._display_results, movies)
            
        except Exception as e:
            error_msg = str(e)[:100]
            print(f"❌ خطا در جستجو: {error_msg}")
            self.root.after(0, self._show_search_error, error_msg)
    
    def _display_results(self, movies):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        if not movies:
            print("⚠️ هیچ فیلمی یافت نشد")
            no_results_frame = tk.Frame(self.scrollable_frame, bg=self.colors['primary'])
            no_results_frame.pack(expand=True, pady=50)
            
            tk.Label(
                no_results_frame,
                text="🎬 هیچ فیلمی یافت نشد!",
                font=("Tahoma", 14, 'bold'),
                fg=self.colors['light'],
                bg=self.colors['primary']
            ).pack()
            
            tk.Label(
                no_results_frame,
                text="لطفاً فیلترهای خود را تغییر دهید یا صفحه بعدی را امتحان کنید.",
                font=("Tahoma", 11),
                fg=self.colors['highlight'],
                bg=self.colors['primary']
            ).pack(pady=10)
            
            # دکمه برگشت به صفحه قبلی
            if self.current_page > 1:
                tk.Button(
                    no_results_frame,
                    text="◀ بازگشت به صفحه قبلی",
                    command=self.prev_page,
                    font=("Tahoma", 11),
                    bg=self.colors['button_active'],
                    fg='white',
                    padx=20,
                    pady=8,
                    cursor='hand2'
                ).pack(pady=10)
            
            self.results_title.config(text="🎬 هیچ فیلمی یافت نشد")
            self.results_counter.config(text="تعداد: ۰")
            self.status_text.set("⚠️ هیچ فیلمی با فیلترهای انتخابی یافت نشد")
            return
        
        valid_count = 0
        for i, movie in enumerate(movies, 1):
            if movie and movie.get('title'):
                try:
                    card = self.create_movie_card(movie, i)
                    card.pack(fill='x', pady=8, padx=5)
                    valid_count += 1
                    print(f"   ✅ کارت {i}: {movie['title']}")
                except Exception as e:
                    print(f"   ❌ خطا در ایجاد کارت فیلم {i}: {e}")
                    continue
        
        self.results_title.config(text=f"🎬 {valid_count} فیلم برتر (صفحه {self.current_page})")
        self.results_counter.config(text=f"تعداد: {valid_count}")
        self.status_text.set(f"✅ {valid_count} فیلم از TMDB دریافت شد")
        print(f"✅ نمایش {valid_count} فیلم")
    
    def _show_search_error(self, error_msg):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        error_frame = tk.Frame(self.scrollable_frame, bg=self.colors['primary'])
        error_frame.pack(expand=True, pady=50)
        
        tk.Label(
            error_frame,
            text="❌ خطا در دریافت داده‌ها",
            font=("Tahoma", 14, 'bold'),
            fg=self.colors['accent'],
            bg=self.colors['primary']
        ).pack()
        
        tk.Label(
            error_frame,
            text=f"خطا: {error_msg}",
            font=("Tahoma", 10),
            fg=self.colors['light'],
            bg=self.colors['primary']
        ).pack(pady=10)
        
        tk.Button(
            error_frame,
            text="🔄 تلاش مجدد",
            command=self.apply_filters,
            font=("Tahoma", 11),
            bg=self.colors['button_active'],
            fg='white',
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(pady=15)
        
        self.results_title.config(text="❌ خطا در اتصال")
        self.status_text.set("خطا در دریافت داده‌ها از TMDB")
    
    def create_movie_card(self, movie, index):
        card_color = movie.get('poster_color', self.colors['secondary'])
        title = movie.get('title', 'نامشخص')
        year = movie.get('year', 0)
        rating = movie.get('rating', 0)
        
        card = tk.Frame(
            self.scrollable_frame,
            bg=card_color,
            relief='raised',
            bd=2
        )
        
        # شماره فیلم
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
            text=title[:40] + ('...' if len(title) > 40 else ''),
            font=("Tahoma", 13, 'bold'),
            fg='white',
            bg=card_color,
            anchor='w'
        ).pack(side='left')
        
        if year:
            tk.Label(
                title_frame,
                text=f"({year})",
                font=("Tahoma", 11),
                fg=self.colors['gold'],
                bg=card_color
            ).pack(side='left', padx=(10, 0))
        
        # امتیاز
        if rating > 0:
            rating_frame = tk.Frame(info_frame, bg=card_color)
            rating_frame.pack(fill='x', pady=6)
            
            stars_count = min(5, int(rating // 2))
            stars = "★" * stars_count
            empty_stars = "☆" * (5 - stars_count)
            
            tk.Label(
                rating_frame,
                text=f"⭐ {rating}/10  {stars}{empty_stars}",
                font=('Arial', 11),
                fg=self.colors['gold'],
                bg=card_color
            ).pack(side='left')
        
        # ژانرها
        genres = movie.get('genres', [])
        if genres:
            genres_frame = tk.Frame(info_frame, bg=card_color)
            genres_frame.pack(fill='x', pady=4)
            
            genres_text = " • ".join(genres[:2])
            tk.Label(
                genres_frame,
                text=f"🎭 {genres_text}",
                font=("Tahoma", 10),
                fg='white',
                bg=card_color
            ).pack(side='left')
        
        # دکمه‌ها
        buttons_frame = tk.Frame(card, bg=card_color)
        buttons_frame.pack(side='right', padx=10)
        
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
        
        return card
    
    def show_movie_details(self, movie):
        if not movie:
            messagebox.showwarning("هشدار", "اطلاعات فیلم نامعتبر است.")
            return
        
        if self.api_connected and movie.get('id'):
            threading.Thread(
                target=self._load_and_show_details,
                args=(movie['id'],),
                daemon=True
            ).start()
        else:
            self._display_movie_details(movie)
    
    def _load_and_show_details(self, movie_id):
        try:
            movie = self.api_manager.get_movie_details(movie_id)
            
            if not movie:
                self.root.after(0, lambda: messagebox.showerror(
                    "خطا", "خطا در دریافت جزئیات فیلم"
                ))
                return
            
            self.root.after(0, lambda: self._display_movie_details(movie))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "خطا", f"خطا در دریافت اطلاعات:\n{str(e)[:100]}"
            ))
    
    def _display_movie_details(self, movie):
        if not movie:
            messagebox.showerror("خطا", "اطلاعات فیلم نامعتبر است")
            return
        
        details_window = tk.Toplevel(self.root)
        details_window.title(f"جزئیات فیلم: {movie.get('title', 'نامشخص')}")
        details_window.geometry("600x550")
        details_window.configure(bg=movie.get('poster_color', self.colors['secondary']))
        details_window.resizable(False, False)
        
        # محتوای اصلی
        main_frame = tk.Frame(details_window, bg=movie.get('poster_color', self.colors['secondary']))
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Canvas برای اسکرول
        canvas = tk.Canvas(main_frame, bg=movie.get('poster_color', self.colors['secondary']), highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=movie.get('poster_color', self.colors['secondary']))
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # محتوای قابل اسکرول
        content_frame = tk.Frame(scrollable_frame, bg=movie.get('poster_color', self.colors['secondary']))
        content_frame.pack(fill='both', expand=True)
        
        # عنوان
        tk.Label(
            content_frame,
            text=movie.get('title', 'نامشخص'),
            font=("Tahoma", 20, 'bold'),
            fg='white',
            bg=movie.get('poster_color', self.colors['secondary'])
        ).pack()
        
        # سال
        year = movie.get('year', 0)
        if year:
            tk.Label(
                content_frame,
                text=f"({year})",
                font=("Tahoma", 16),
                fg=self.colors['highlight'],
                bg=movie.get('poster_color', self.colors['secondary'])
            ).pack(pady=(0, 20))
        
        # کارت اطلاعات
        info_card = tk.Frame(
            content_frame,
            bg=self.colors['secondary'],
            relief='raised',
            bd=2
        )
        info_card.pack(fill='x', pady=10)
        
        # اطلاعات فیلم
        director = movie.get('director', 'نامشخص')
        rating = movie.get('rating', 0)
        duration = movie.get('duration', 'نامشخص')
        country = movie.get('country', 'نامشخص')
        genres = movie.get('genres', [])
        actors = movie.get('actors', [])
        
        # تبدیل actors به لیست اگر نیست
        if not actors:
            actors = ['نامشخص']
        elif not isinstance(actors, list):
            actors = [str(actors)]
        
        # آیتم‌های اطلاعات
        info_items = [
            ("🎬 کارگردان:", director),
            ("⭐ امتیاز:", f"{rating}/10"),
            ("📅 سال تولید:", str(year) if year else "نامشخص"),
            ("⏱️ مدت زمان:", duration),
            ("🌍 کشور:", country),
            ("🎭 ژانر:", " • ".join(genres) if genres else "نامشخص"),
            ("👥 بازیگران:", ", ".join(actors[:3]) if actors else "نامشخص")
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
                text=str(value),
                font=("Tahoma", 12),
                fg='white',
                bg=self.colors['secondary'],
                anchor='w'
            ).pack(side='left', padx=(10, 0), fill='x', expand=True)
        
        # خلاصه داستان
        summary_frame = tk.Frame(content_frame, bg=movie.get('poster_color', self.colors['secondary']))
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
        
        text_scrollbar = tk.Scrollbar(text_frame, command=summary_text.yview)
        summary_text.config(yscrollcommand=text_scrollbar.set)
        
        summary_text.pack(side='left', fill='x', expand=True)
        text_scrollbar.pack(side='right', fill='y')
        
        description = movie.get('description', 'توضیحی موجود نیست.')
        summary_text.insert('1.0', description)
        summary_text.config(state='disabled')
        
        # دکمه‌ها
        button_frame = tk.Frame(content_frame, bg=movie.get('poster_color', self.colors['secondary']))
        button_frame.pack(fill='x', pady=20)
        
        in_watchlist = any(w.get('id') == movie.get('id') for w in self.watchlist)
        
        if not in_watchlist:
            tk.Button(
                button_frame,
                text="➕ افزودن به لیست منتخب",
                command=lambda m=movie: self.add_to_watchlist_from_details(m, details_window),
                bg=self.colors['highlight'],
                fg='white',
                font=("Tahoma", 11),
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
            font=("Tahoma", 11),
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack(side='right', padx=5)
        
        # مرکز کردن پنجره
        self.center_toplevel(details_window)
        
        # جلوگیری از تعامل با پنجره اصلی
        details_window.transient(self.root)
        details_window.grab_set()
    
    def add_to_watchlist_from_details(self, movie, window):
        self.add_to_watchlist(movie)
        window.destroy()
        self._display_movie_details(movie)
    
    def add_to_watchlist(self, movie):
        if not movie:
            return
            
        movie_id = movie.get('id')
        for w in self.watchlist:
            if w.get('id') == movie_id:
                messagebox.showinfo("توجه", "این فیلم قبلاً در لیست منتخب‌های شما وجود دارد.")
                return
        
        self.watchlist.append(movie)
        title = movie.get('title', 'فیلم')
        self.status_text.set(f"✅ '{title}' به لیست منتخب‌ها اضافه شد")
        messagebox.showinfo("موفقیت", f"فیلم '{title}' به لیست منتخب‌های شما اضافه شد.")
    
    def show_watchlist(self):
        if not self.watchlist:
            messagebox.showinfo("لیست منتخب‌ها", "لیست منتخب‌های شما خالی است.")
            return
        
        watchlist_window = tk.Toplevel(self.root)
        watchlist_window.title("⭐ لیست فیلم‌های منتخب من")
        watchlist_window.geometry("600x500")
        watchlist_window.configure(bg=self.colors['primary'])
        watchlist_window.resizable(False, False)
        
        tk.Label(
            watchlist_window,
            text="🎬 فیلم‌های منتخب من",
            font=("Tahoma", 18, 'bold'),
            fg=self.colors['gold'],
            bg=self.colors['primary'],
            pady=20
        ).pack()
        
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
            
            title = movie.get('title', 'نامشخص')
            year = movie.get('year', '')
            rating = movie.get('rating', 0)
            
            # فریم برای اطلاعات
            info_frame = tk.Frame(movie_frame, bg=self.colors['secondary'])
            info_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
            
            tk.Label(
                info_frame,
                text=f"{i}. {title} ({year}) - ⭐ {rating}/10",
                font=("Tahoma", 12),
                fg=self.colors['light'],
                bg=self.colors['secondary'],
                anchor='w'
            ).pack(fill='x')
            
            # دکمه‌ها
            buttons_frame = tk.Frame(movie_frame, bg=self.colors['secondary'])
            buttons_frame.pack(side='right', padx=10)
            
            # دکمه مشاهده جزئیات
            tk.Button(
                buttons_frame,
                text="ℹ️ جزئیات",
                command=lambda m=movie: self.show_movie_details(m),
                font=("Tahoma", 10),
                bg=self.colors['highlight'],
                fg='white',
                bd=0,
                padx=10,
                pady=5,
                cursor='hand2'
            ).pack(side='left', padx=2)
            
            # دکمه حذف
            tk.Button(
                buttons_frame,
                text="🗑️ حذف",
                command=lambda m=movie: self.remove_from_watchlist(m, watchlist_window),
                font=("Tahoma", 10),
                bg=self.colors['accent'],
                fg='white',
                bd=0,
                padx=10,
                pady=5,
                cursor='hand2'
            ).pack(side='left', padx=2)
        
        # دکمه بستن
        button_frame = tk.Frame(watchlist_window, bg=self.colors['primary'])
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="بستن",
            command=watchlist_window.destroy,
            bg=self.colors['accent'],
            fg='white',
            font=("Tahoma", 12),
            padx=30,
            pady=10,
            cursor='hand2'
        ).pack()
        
        self.center_toplevel(watchlist_window)
    
    def remove_from_watchlist(self, movie, window):
        if movie in self.watchlist:
            self.watchlist.remove(movie)
            title = movie.get('title', 'فیلم')
            self.status_text.set(f"🗑️ '{title}' از لیست منتخب‌ها حذف شد")
            window.destroy()
            self.show_watchlist()
    
    def random_suggestion(self):
        if not self.selected_genres and self.api_connected:
            messagebox.showwarning("هشدار", "لطفاً حداقل یک ژانر انتخاب کنید!")
            return
        
        try:
            if self.api_connected:
                movies = self.api_manager.search_movies(
                    genre_ids=self.selected_genres,
                    year_from=self.year_var.get(),
                    min_rating=self.rating_var.get(),
                    page=random.randint(1, 3)
                )
            else:
                movies = self.api_manager.get_sample_movies()
            
            if not movies:
                messagebox.showwarning("هشدار", "هیچ فیلمی با فیلترهای فعلی وجود ندارد!")
                return
            
            movie = random.choice(movies[:min(10, len(movies))])
            
            response = messagebox.askyesno(
                "پیشنهاد شانس",
                f"🎲 فیلم پیشنهادی:\n\n"
                f"🎬 {movie.get('title', 'نامشخص')} ({movie.get('year', '')})\n"
                f"⭐ امتیاز: {movie.get('rating', 0)}/10\n"
                f"🎭 ژانر: {' • '.join(movie.get('genres', ['نامشخص'])[:2])}\n\n"
                f"آیا می‌خواهید جزئیات این فیلم را مشاهده کنید؟"
            )
            
            if response:
                self.show_movie_details(movie)
            
            title = movie.get('title', 'فیلم')
            self.status_text.set(f"🎲 فیلم تصادفی: {title}")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در دریافت فیلم تصادفی:\n{str(e)[:100]}")
    
    def reset_filters(self):
        self.select_all_genres()
        self.year_var.set(2010)
        self.year_slider.set(2010)
        self.rating_var.set(6.0)
        self.rating_slider.set(6.0)
        self.current_page = 1
        self.update_pagination_buttons()
        self.apply_filters()
        self.status_text.set("🔄 تمام فیلترها بازنشانی شدند")
    
    def show_statistics(self):
        stats_text = f"""
        📊 آمار و اطلاعات برنامه
        
        • وضعیت: {'آنلاین' if self.api_connected else 'آفلاین'}
        • تعداد ژانرها: {len(self.genre_buttons)}
        • ژانرهای انتخاب شده: {len(self.selected_genres)}
        
        📈 آمار کاربری:
        • تعداد فیلم‌های منتخب: {len(self.watchlist)}
        • سال انتخابی: {self.year_var.get()}
        • حداقل امتیاز: {self.rating_var.get()}/10
        • صفحه فعلی: {self.current_page}
        
        🎬 سینماسنج حرفه‌ای
        نسخه ۳.۰ - برای جشنواره خوارزمی
        """
        
        messagebox.showinfo("📊 آمار و اطلاعات", stats_text)
        self.status_text.set("📊 آمار برنامه نمایش داده شد")
    
    def save_results(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"نتایج_سینماسنج_{timestamp}.txt"
            
            content = "=" * 50 + "\n"
            content += "نتایج جستجوی سینماسنج\n"
            content += f"تاریخ: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}\n"
            content += f"وضعیت: {'آنلاین' if self.api_connected else 'آفلاین'}\n"
            content += f"ژانرها: {len(self.selected_genres)} ژانر\n"
            content += f"سال از: {self.year_var.get()}\n"
            content += f"حداقل امتیاز: {self.rating_var.get()}\n"
            content += f"صفحه: {self.current_page}\n"
            content += "=" * 50 + "\n\n"
            
            content += "🎬 فیلم‌های ذخیره شده:\n\n"
            
            if self.watchlist:
                for i, movie in enumerate(self.watchlist, 1):
                    content += f"{i}. {movie.get('title', 'نامشخص')} ({movie.get('year', 'نامشخص')})\n"
                    content += f"   امتیاز: {movie.get('rating', 0)}/10\n"
                    content += f"   ژانر: {' • '.join(movie.get('genres', ['نامشخص']))}\n"
                    content += "-" * 40 + "\n"
            else:
                content += "لیست منتخب‌های شما خالی است.\n"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            messagebox.showinfo("موفقیت", f"نتایج در '{filename}' ذخیره شد.")
            self.status_text.set(f"💾 نتایج در {filename} ذخیره شد")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در ذخیره فایل: {str(e)}")
    
    def center_toplevel(self, toplevel):
        toplevel.update_idletasks()
        width = toplevel.winfo_width()
        height = toplevel.winfo_height()
        x = (toplevel.winfo_screenwidth() // 2) - (width // 2)
        y = (toplevel.winfo_screenheight() // 2) - (height // 2)
        toplevel.geometry(f'{width}x{height}+{x}+{y}')

# ==================== اجرای برنامه ==================== #
def main():
    try:
        print("=" * 50)
        print("🚀 شروع برنامه سینماسنج حرفه‌ای")
        print("🎬 نسخه ۳.۰")
        print("👨‍💻 توسعه‌دهنده: محمد جواد منصوری")
        print("🏆 برای جشنواره خوارزمی")
        print("=" * 50)
        
        root = tk.Tk()
        app = CinemaSensePro(root)
        root.mainloop()
        
    except Exception as e:
        print(f"❌ خطای بحرانی: {e}")
        import traceback
        traceback.print_exc()
        
        error_root = tk.Tk()
        error_root.withdraw()
        messagebox.showerror("خطای بحرانی", 
            f"خطا در اجرای برنامه:\n\n{str(e)[:200]}\n\n"
            "لطفاً اتصال اینترنت خود را بررسی کنید.")
        error_root.destroy()

if __name__ == "__main__":
    main()