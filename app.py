from flask import Flask, render_template_string, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from instagrapi import Client
from instagrapi.exceptions import LoginRequired, ChallengeRequired
import json
import random
import time
from datetime import datetime, timedelta
import os
import logging
from dotenv import load_dotenv

# بارگذاری تنظیمات محیطی
load_dotenv()

app = Flask(__name__)
app.secret_key = 'instagram-bot-secret-key-2024'

class AdvancedInstagramBot:
    def __init__(self):
        self.client = Client()
        self.is_logged_in = False
        self.followed_users = {}
        self.scheduler = BackgroundScheduler()
        self.setup_proxy()
        self.load_config()
        
    def setup_proxy(self):
        """تنظیم پروکسی برای ایران"""
        proxy_settings = {
            # پروکسی عمومی - اینها را با پروکسی واقعی جایگزین کنید
            "http": "http://proxy-server:port",
            "https": "https://proxy-server:port"
        }
        try:
            self.client.set_proxy(proxy_settings["https"])
            print("✅ پروکسی تنظیم شد")
        except:
            print("⚠️ استفاده بدون پروکسی")
    
    def load_config(self):
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except:
            self.config = {
                "instagram_credentials": {
                    "username": "",
                    "password": ""
                },
                "target_accounts": ["instagram", "natgeo", "nike", "adidas"],
                "daily_follow_limit": 50,
                "daily_unfollow_limit": 50,
                "daily_comment_limit": 30,
                "unfollow_after_days": 2,
                "comments": [
                    "👏 عالی بود!", "🔥 واقعا حرفه‌ای", "💫 فوق العاده است",
                    "❤️ عاشق این محتوایم", "👍 کارت درسته", "🌟 درخشیدی",
                    "😍 زیبا", "🎯 دقیق", "💯 درصد"
                ],
                "story_replies": [
                    "👌 عالی", "🔥🔥", "💯", "❤️❤️", "👍👍", "😍😍"
                ],
                "direct_message_responses": {
                    "سلام": "🙏 سلام! چطور می‌تونم کمک کنم؟",
                    "قیمت": "💵 لطفا به پیوی اصلی پیام بدید",
                    "همکاری": "🤝 برای همکاری در پیوی اصلی در ارتباط باشید",
                    "ممنون": "❤️ چشم، خوشحالم که راضی هستید"
                },
                "working_hours": {
                    "start": "09:00",
                    "end": "21:00"
                }
            }
            self.save_config()
    
    def save_config(self):
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)
    
    def login(self, username, password):
        try:
            print(f"🔐 تلاش برای ورود با کاربری: {username}")
            
            # ذخیره اطلاعات برای استفاده بعدی
            self.config["instagram_credentials"]["username"] = username
            self.config["instagram_credentials"]["password"] = password
            self.save_config()
            
            # ورود به اینستاگرام
            self.client.login(username, password)
            self.is_logged_in = True
            
            # شروع سرویس‌های زمان‌بندی شده
            self.start_scheduled_services()
            
            print("✅ ورود موفقیت‌آمیز بود")
            return True
            
        except ChallengeRequired:
            print("🔐 نیاز به تأیید هویت - لطفا از طریق اپ اینستاگرام تأیید کنید")
            return False
        except Exception as e:
            print(f"❌ خطا در ورود: {str(e)}")
            return False
    
    def start_scheduled_services(self):
        """شروع سرویس‌های زمان‌بندی شده"""
        if not self.scheduler.running:
            self.scheduler.start()
            
            # فالو روزانه - ساعت ۱۰ صبح
            self.scheduler.add_job(
                self.daily_follow_task,
                'cron',
                hour=10,
                minute=0
            )
            
            # آنفالو روزانه - ساعت ۱۸ عصر
            self.scheduler.add_job(
                self.daily_unfollow_task,
                'cron',
                hour=18,
                minute=0
            )
            
            # کامنت روزانه - ساعت ۱۴
            self.scheduler.add_job(
                self.daily_comment_task,
                'cron',
                hour=14,
                minute=0
            )
            
            # پاسخ به استوری‌ها - هر ۴ ساعت
            self.scheduler.add_job(
                self.reply_to_stories_task,
                'interval',
                hours=4
            )
            
            print("✅ سرویس‌های زمان‌بندی شده شروع شدند")
    
    def daily_follow_task(self):
        """کار فالو روزانه"""
        if not self.is_logged_in:
            return
        
        print("🔄 شروع فالو روزانه...")
        target_account = random.choice(self.config["target_accounts"])
        self.follow_users_from_target(target_account, 10)
    
    def daily_unfollow_task(self):
        """کار آنفالو روزانه"""
        if not self.is_logged_in:
            return
        
        print("🔄 شروع آنفالو روزانه...")
        self.check_and_unfollow()
    
    def daily_comment_task(self):
        """کار کامنت روزانه"""
        if not self.is_logged_in:
            return
        
        print("🔄 شروع کامنت روزانه...")
        target_account = random.choice(self.config["target_accounts"])
        self.comment_on_target_posts(target_account, 5)
    
    def reply_to_stories_task(self):
        """پاسخ به استوری‌ها"""
        if not self.is_logged_in:
            return
        
        print("📖 بررسی استوری‌ها برای پاسخ...")
        self.reply_to_followers_stories(3)
    
    def follow_users_from_target(self, target_username, count=10):
        """فالو کاربران از یک اکانت هدف"""
        if not self.is_logged_in:
            return {"status": "error", "message": "❌ لطفاً اول وارد حساب کاربری شوید"}
        
        try:
            user_id = self.client.user_id_from_username(target_username)
            followers = self.client.user_followers(user_id, amount=count)
            
            followed_count = 0
            for user in list(followers.values())[:count]:
                try:
                    self.client.user_follow(user.pk)
                    
                    self.followed_users[user.pk] = {
                        "username": user.username,
                        "follow_date": datetime.now().isoformat(),
                        "source_account": target_username,
                        "followed_back": False
                    }
                    followed_count += 1
                    
                    print(f"✅ فالو شد: {user.username}")
                    
                    # تاخیر تصادفی بین ۲۰-۴۰ ثانیه
                    time.sleep(random.uniform(20, 40))
                    
                except Exception as e:
                    print(f"⚠️ خطا در فالو {user.username}: {str(e)}")
                    continue
            
            self.save_followed_users()
            
            return {
                "status": "success", 
                "followed": followed_count,
                "message": f"✅ {followed_count} نفر از فالوورهای {target_username} فالو شدند"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"❌ خطا در فالو: {str(e)}"}
    
    def check_and_unfollow(self):
        """بررسی و آنفالو کاربرانی که فالو بک نکرده‌اند"""
        if not self.is_logged_in:
            return {"status": "error", "message": "❌ لطفاً اول وارد حساب کاربری شوید"}
        
        try:
            unfollow_count = 0
            current_time = datetime.now()
            
            for user_id, user_data in list(self.followed_users.items()):
                follow_date = datetime.fromisoformat(user_data["follow_date"])
                
                # اگر ۲ روز گذشته و هنوز فالو بک نکرده
                if (current_time - follow_date).days >= self.config["unfollow_after_days"]:
                    try:
                        friendship = self.client.user_friendship(user_id)
                        
                        if not friendship.followed_by and not user_data["followed_back"]:
                            self.client.user_unfollow(user_id)
                            del self.followed_users[user_id]
                            unfollow_count += 1
                            
                            print(f"❌ آنفالو شد: {user_data['username']}")
                            
                            # تاخیر بین آنفالوها
                            time.sleep(random.uniform(20, 40))
                            
                    except Exception as e:
                        print(f"⚠️ خطا در بررسی {user_id}: {str(e)}")
                        continue
            
            self.save_followed_users()
            
            return {
                "status": "success", 
                "message": f"❌ {unfollow_count} نفر آنفالو شدند"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"❌ خطا در آنفالو: {str(e)}"}
    
    def comment_on_target_posts(self, target_username, count=5):
        """ارسال کامنت روی پست‌های اکانت هدف"""
        if not self.is_logged_in:
            return {"status": "error", "message": "❌ لطفاً اول وارد حساب کاربری شوید"}
        
        try:
            user_id = self.client.user_id_from_username(target_username)
            medias = self.client.user_medias(user_id, amount=count)
            
            commented_count = 0
            for media in medias:
                try:
                    comment_text = random.choice(self.config["comments"])
                    self.client.media_comment(media.id, comment_text)
                    commented_count += 1
                    
                    print(f"💬 کامنت گذاشته شد روی پست {target_username}: {comment_text}")
                    
                    time.sleep(random.uniform(30, 60))
                    
                except Exception as e:
                    print(f"⚠️ خطا در کامنت: {str(e)}")
                    continue
            
            return {
                "status": "success", 
                "message": f"💬 {commented_count} کامنت روی پست‌های {target_username} گذاشته شد"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"❌ خطا در ارسال کامنت: {str(e)}"}
    
    def reply_to_followers_stories(self, count=5):
        """پاسخ به استوری‌های فالوورها"""
        if not self.is_logged_in:
            return {"status": "error", "message": "❌ لطفاً اول وارد حساب کاربری شوید"}
        
        try:
            # دریافت فالوورها
            user_info = self.client.account_info()
            followers = self.client.user_followers(user_info.pk, amount=count)
            
            replied_count = 0
            for user in list(followers.values())[:count]:
                try:
                    stories = self.client.user_stories(user.pk)
                    if stories:
                        story = stories[0]
                        reply_text = random.choice(self.config["story_replies"])
                        self.client.story_react(story.id, reply_text)
                        replied_count += 1
                        
                        print(f"📖 پاسخ به استوری {user.username}: {reply_text}")
                        
                        time.sleep(random.uniform(20, 40))
                        
                except Exception as e:
                    print(f"⚠️ خطا در پاسخ به استوری: {str(e)}")
                    continue
            
            return {
                "status": "success", 
                "message": f"📖 به {replied_count} استوری پاسخ داده شد"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"❌ خطا در پاسخ به استوری: {str(e)}"}
    
    def auto_reply_direct_messages(self):
        """پاسخ خودکار به پیام‌های مستقیم"""
        if not self.is_logged_in:
            return {"status": "error", "message": "❌ لطفاً اول وارد حساب کاربری شوید"}
        
        try:
            threads = self.client.direct_threads(amount=10)
            replied_count = 0
            
            for thread in threads:
                try:
                    last_message = thread.messages[0] if thread.messages else None
                    if last_message and last_message.user_id != self.client.user_id:
                        message_text = last_message.text.lower()
                        
                        # پیدا کردن پاسخ مناسب
                        response = None
                        for keyword, reply in self.config["direct_message_responses"].items():
                            if keyword in message_text:
                                response = reply
                                break
                        
                        if response:
                            self.client.direct_send(response, thread_ids=[thread.id])
                            replied_count += 1
                            print(f"💌 پاسخ به پیام: {response}")
                            
                            time.sleep(random.uniform(10, 20))
                            
                except Exception as e:
                    print(f"⚠️ خطا در پاسخ به پیام: {str(e)}")
                    continue
            
            return {
                "status": "success", 
                "message": f"💌 به {replied_count} پیام پاسخ داده شد"
            }
            
        except Exception as e:
            return {"status": "error", "message": f"❌ خطا در پاسخ به پیام: {str(e)}"}
    
    def save_followed_users(self):
        with open('followed_users.json', 'w', encoding='utf-8') as f:
            json.dump(self.followed_users, f, ensure_ascii=False, indent=4)
    
    def load_followed_users(self):
        try:
            with open('followed_users.json', 'r', encoding='utf-8') as f:
                self.followed_users = json.load(f)
        except:
            self.followed_users = {}
    
    def get_stats(self):
        following_count = 0
        follower_count = 0
        if self.is_logged_in:
            try:
                user_info = self.client.account_info()
                following_count = user_info.following_count
                follower_count = user_info.follower_count
                username = user_info.username
            except:
                username = "Unknown"
        
        return {
            "logged_in": self.is_logged_in,
            "username": username if self.is_logged_in else "Not logged in",
            "followed_count": len(self.followed_users),
            "actual_following": following_count,
            "follower_count": follower_count,
            "target_accounts_count": len(self.config["target_accounts"]),
            "comments_count": len(self.config["comments"]),
            "scheduler_running": self.scheduler.running if hasattr(self, 'scheduler') else False
        }

# ایجاد نمونه ربات
bot = AdvancedInstagramBot()
bot.load_followed_users()

# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ربات پیشرفته اینستاگرام</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: Tahoma; }
        body { background: #f0f2f5; padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
        .header { text-align: center; margin-bottom: 20px; color: #405de6; }
        .section { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; border-right: 4px solid #405de6; }
        .form-group { margin-bottom: 10px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea, button, select { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #405de6; color: white; border: none; cursor: pointer; }
        button:hover { background: #304acd; }
        .btn-danger { background: #e1306c; }
        .btn-success { background: #00c851; }
        .alert { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin: 15px 0; }
        .stat-card { background: #405de6; color: white; padding: 15px; border-radius: 8px; text-align: center; }
        .tab { padding: 10px; background: #e9ecef; margin: 5px; border-radius: 5px; cursor: pointer; }
        .tab.active { background: #405de6; color: white; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 ربات پیشرفته اینستاگرام</h1>
            <p>مدیریت کامل اکانت اینستاگرام - نسخه حرفه‌ای</p>
        </div>

        <div class="stats-grid" id="stats">
            <!-- آمار اینجا نمایش داده می‌شود -->
        </div>

        <div style="display: flex; margin-bottom: 20px;">
            <div class="tab active" onclick="switchTab('login')">ورود</div>
            <div class="tab" onclick="switchTab('actions')">عملیات</div>
            <div class="tab" onclick="switchTab('settings')">تنظیمات</div>
            <div class="tab" onclick="switchTab('auto')">خودکار</div>
        </div>

        <!-- تب ورود -->
        <div id="login-tab" class="tab-content active">
            <div class="section">
                <h2>🔐 ورود به اینستاگرام</h2>
                <div class="form-group">
                    <label>نام کاربری:</label>
                    <input type="text" id="username" placeholder="username">
                </div>
                <div class="form-group">
                    <label>رمز عبور:</label>
                    <input type="password" id="password" placeholder="••••••••">
                </div>
                <button onclick="login()">ورود به اینستاگرام</button>
            </div>
        </div>

        <!-- تب عملیات -->
        <div id="actions-tab" class="tab-content">
            <div class="section">
                <h2>👥 فالو کاربران</h2>
                <div class="form-group">
                    <label>اکانت هدف:</label>
                    <select id="target-account">
                        <option value="random">تصادفی</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>تعداد:</label>
                    <input type="number" id="follow-count" value="10" min="1" max="50">
                </div>
                <button onclick="followUsers()">شروع فالو</button>
            </div>

            <div class="section">
                <h2>💬 ارسال کامنت</h2>
                <div class="form-group">
                    <label>اکانت هدف:</label>
                    <select id="comment-target">
                        <option value="random">تصادفی</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>تعداد کامنت:</label>
                    <input type="number" id="comment-count" value="5" min="1" max="20">
                </div>
                <button onclick="postComments()">ارسال کامنت</button>
            </div>

            <div class="section">
                <h2>📖 پاسخ به استوری</h2>
                <button onclick="replyToStories()">پاسخ به استوری فالوورها</button>
            </div>

            <div class="section">
                <h2>🔄 مدیریت فالوها</h2>
                <button class="btn-danger" onclick="checkUnfollow()">بررسی و آنفالو</button>
            </div>

            <div class="section">
                <h2>💌 پاسخ به پیام‌ها</h2>
                <button onclick="replyToMessages()">پاسخ خودکار به پیام‌ها</button>
            </div>
        </div>

        <!-- تب تنظیمات -->
        <div id="settings-tab" class="tab-content">
            <div class="section">
                <h2>⚙️ تنظیمات ربات</h2>
                <div class="form-group">
                    <label>اکانت‌های هدف (با کاما جدا کنید):</label>
                    <textarea id="target-accounts" placeholder="account1, account2, account3" rows="3"></textarea>
                </div>
                <div class="form-group">
                    <label>کامنت‌ها (هر خط یک کامنت):</label>
                    <textarea id="comments-list" rows="6" placeholder="کامنت‌ها..."></textarea>
                </div>
                <div class="form-group">
                    <label>پاسخ‌های استوری (با کاما جدا کنید):</label>
                    <input type="text" id="story-replies" placeholder="👌, 🔥, 💯">
                </div>
                <div class="form-group">
                    <label>محدودیت فالو روزانه:</label>
                    <input type="number" id="daily-follow-limit" value="50" min="1" max="150">
                </div>
                <button class="btn-success" onclick="updateSettings()">ذخیره تنظیمات</button>
            </div>
        </div>

        <!-- تب خودکار -->
        <div id="auto-tab" class="tab-content">
            <div class="section">
                <h2>🤖 عملیات خودکار</h2>
                <p>ربات به طور خودکار این کارها را انجام می‌دهد:</p>
                <ul>
                    <li>🕙 ۱۰:۰۰ - فالو کاربران از اکانت‌های هدف</li>
                    <li>🕑 ۱۴:۰۰ - ارسال کامنت روی پست‌ها</li>
                    <li>🕕 ۱۸:۰۰ - آنفالو کاربران بدون فالو بک</li>
                    <li>🔄 هر ۴ ساعت - پاسخ به استوری‌ها</li>
                </ul>
                <button class="btn-success" onclick="startAutoServices()">شروع سرویس خودکار</button>
                <button class="btn-danger" onclick="stopAutoServices()">توقف سرویس خودکار</button>
            </div>
        </div>

        <div id="results"></div>
    </div>

    <script>
        function switchTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.getElementById(tabName + '-tab').classList.add('active');
            event.target.classList.add('active');
        }

        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            const response = await fetch('/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            });
            
            const result = await response.json();
            showResult(result.message, result.status);
            loadStats();
            loadSettings();
        }

        async function followUsers() {
            const targetAccount = document.getElementById('target-account').value;
            const count = document.getElementById('follow-count').value;
            
            const response = await fetch('/follow', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({target_account: targetAccount, count: parseInt(count)})
            });
            
            const result = await response.json();
            showResult(result.message, result.status);
            loadStats();
        }

        async function postComments() {
            const targetAccount = document.getElementById('comment-target').value;
            const count = document.getElementById('comment-count').value;
            
            const response = await fetch('/comment', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({target_account: targetAccount, count: parseInt(count)})
            });
            
            const result = await response.json();
            showResult(result.message, result.status);
        }

        async function replyToStories() {
            const response = await fetch('/reply_stories', {method: 'POST'});
            const result = await response.json();
            showResult(result.message, result.status);
        }

        async function checkUnfollow() {
            const response = await fetch('/unfollow', {method: 'POST'});
            const result = await response.json();
            showResult(result.message, result.status);
            loadStats();
        }

        async function replyToMessages() {
            const response = await fetch('/reply_messages', {method: 'POST'});
            const result = await response.json();
            showResult(result.message, result.status);
        }

        async function startAutoServices() {
            const response = await fetch('/start_auto', {method: 'POST'});
            const result = await response.json();
            showResult(result.message, result.status);
        }

        async function stopAutoServices() {
            const response = await fetch('/stop_auto', {method: 'POST'});
            const result = await response.json();
            showResult(result.message, result.status);
        }

        async function updateSettings() {
            const targetAccounts = document.getElementById('target-accounts').value.split(',').map(a => a.trim()).filter(a => a);
            const comments = document.getElementById('comments-list').value.split('\\n').filter(c => c.trim());
            const storyReplies = document.getElementById('story-replies').value.split(',').map(r => r.trim()).filter(r => r);
            const dailyFollowLimit = parseInt(document.getElementById('daily-follow-limit').value);
            
            const response = await fetch('/update_settings', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    target_accounts: targetAccounts,
                    comments: comments,
                    story_replies: storyReplies,
                    daily_follow_limit: dailyFollowLimit
                })
            });
            
            const result = await response.json();
            showResult(result.message, result.status);
        }

        async function loadStats() {
            const response = await fetch('/stats');
            const stats = await response.json();
            
            document.getElementById('stats').innerHTML = `
                <div class="stat-card">
                    <div style="font-size: 24px;">${stats.logged_in ? '✅' : '❌'}</div>
                    <div>وضعیت ورود</div>
                </div>
                <div class="stat-card">
                    <div style="font-size: 24px;">${stats.username}</div>
                    <div>کاربر</div>
                </div>
                <div class="stat-card">
                    <div style="font-size: 24px;">${stats.followed_count}</div>
                    <div>فالو شده‌ها</div>
                </div>
                <div class="stat-card">
                    <div style="font-size: 24px;">${stats.follower_count || 0}</div>
                    <div>فالوورها</div>
                </div>
                <div class="stat-card">
                    <div style="font-size: 24px;">${stats.scheduler_running ? '✅' : '❌'}</div>
                    <div>سرویس خودکار</div>
                </div>
            `;
        }

        async function loadSettings() {
            const response = await fetch('/get_settings');
            const settings = await response.json();
            
            if (settings.target_accounts) {
                document.getElementById('target-accounts').value = settings.target_accounts.join(', ');
                document.getElementById('comments-list').value = settings.comments.join('\\n');
            }
        }

        function showResult(message, type) {
            const div = document.createElement('div');
            div.className = `alert ${type === 'success' ? 'success' : 'error'}`;
            div.textContent = message;
            document.getElementById('results').appendChild(div);
            
            setTimeout(() => div.remove(), 5000);
        }

        // بارگذاری اولیه
        loadStats();
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return HTML_TEMPLATE

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    if bot.login(username, password):
        return jsonify({"status": "success", "message": "✅ ورود موفقیت‌آمیز بود"})
    else:
        return jsonify({"status": "error", "message": "❌ خطا در ورود - اطلاعات را بررسی کنید"})

@app.route('/follow', methods=['POST'])
def follow():
    data = request.get_json()
    target_account = data.get('target_account', 'random')
    count = data.get('count', 10)
    
    if target_account == 'random':
        target_account = random.choice(bot.config["target_accounts"])
    
    result = bot.follow_users_from_target(target_account, count)
    return jsonify(result)

@app.route('/comment', methods=['POST'])
def comment():
    data = request.get_json()
    target_account = data.get('target_account', 'random')
    count = data.get('count', 5)
    
    if target_account == 'random':
        target_account = random.choice(bot.config["target_accounts"])
    
    result = bot.comment_on_target_posts(target_account, count)
    return jsonify(result)

@app.route('/reply_stories', methods=['POST'])
def reply_stories():
    result = bot.reply_to_followers_stories(3)
    return jsonify(result)

@app.route('/unfollow', methods=['POST'])
def unfollow():
    result = bot.check_and_unfollow()
    return jsonify(result)

@app.route('/reply_messages', methods=['POST'])
def reply_messages():
    result = bot.auto_reply_direct_messages()
    return jsonify(result)

@app.route('/start_auto', methods=['POST'])
def start_auto():
    if bot.is_logged_in:
        bot.start_scheduled_services()
        return jsonify({"status": "success", "message": "✅ سرویس خودکار شروع شد"})
    else:
        return jsonify({"status": "error", "message": "❌ اول وارد حساب کاربری شوید"})

@app.route('/stop_auto', methods=['POST'])
def stop_auto():
    if hasattr(bot, 'scheduler') and bot.scheduler.running:
        bot.scheduler.shutdown()
        return jsonify({"status": "success", "message": "✅ سرویس خودکار متوقف شد"})
    else:
        return jsonify({"status": "error", "message": "❌ سرویس خودکار در حال اجرا نیست"})

@app.route('/update_settings', methods=['POST'])
def update_settings():
    data = request.get_json()
    
    if 'target_accounts' in data:
        bot.config["target_accounts"] = data['target_accounts']
    
    if 'comments' in data:
        bot.config["comments"] = data['comments']
    
    if 'story_replies' in data:
        bot.config["story_replies"] = data['story_replies']
    
    if 'daily_follow_limit' in data:
        bot.config["daily_follow_limit"] = data['daily_follow_limit']
    
    bot.save_config()
    return jsonify({"status": "success", "message": "✅ تنظیمات به‌روز شد"})

@app.route('/get_settings', methods=['GET'])
def get_settings():
    return jsonify(bot.config)

@app.route('/stats', methods=['GET'])
def stats():
    stats = bot.get_stats()
    return jsonify(stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
