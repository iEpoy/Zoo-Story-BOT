import json
import time
import hashlib
import urllib.parse
from datetime import datetime, timezone
import requests
import asyncio
import sys
import os
from colorama import init, Fore
from datetime import datetime, timedelta

# Initialize colorama for cross-platform colored output
init()

class ZooAPIClient:
    def __init__(self):
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
            "Content-Type": "application/json",
            "Origin": "https://game.zoo.team",
            "Referer": "https://game.zoo.team/",
            "Sec-Ch-Ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Is-Beta-Server": "null"
        }
        self.cached_data = None

    def log(self, msg, type='info'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        if type == 'success':
            print(f"[{timestamp}] [✓] {Fore.GREEN}{msg}{Fore.RESET}")
        elif type == 'custom':
            print(f"[{timestamp}] [*] {Fore.MAGENTA}{msg}{Fore.RESET}")
        elif type == 'error':
            print(f"[{timestamp}] [✗] {Fore.RED}{msg}{Fore.RESET}")
        elif type == 'warning':
            print(f"[{timestamp}] [!] {Fore.YELLOW}{msg}{Fore.RESET}")
        else:
            print(f"[{timestamp}] [ℹ] {Fore.BLUE}{msg}{Fore.RESET}")

    async def create_api_hash(self, timestamp, data):
        combined_data = f"{timestamp}_{data}"
        encoded_data = urllib.parse.quote(combined_data)
        return hashlib.md5(encoded_data.encode()).hexdigest()

    async def get_user_data(self, init_data):
        try:
            hash_value = init_data.split('hash=')[1].split('&')[0]
            if not hash_value:
                raise ValueError('Tidak dapat mengekstrak hash dari initData')

            current_time = int(time.time())
            data_payload = json.dumps({"data": {}})
            api_hash = await self.create_api_hash(current_time, data_payload)
            
            headers = {
                **self.headers,
                "api-hash": api_hash,
                "Api-Key": hash_value,
                "Api-Time": str(current_time)
            }

            response = requests.post(
                "https://api.zoo.team/user/data/all",
                json={"data": {}},
                headers=headers
            )

            if response.status_code == 200 and response.json()['success']:
                self.cached_data = response.json()['data']
                return {'success': True, 'data': response.json()['data']}
            return {'success': False, 'error': response.json().get('message', 'Gagal mendapatkan data pengguna')}

        except Exception as error:
            return {'success': False, 'error': str(error)}

    async def get_user_data_after(self, init_data):
        try:
            hash_value = init_data.split('hash=')[1].split('&')[0]
            if not hash_value:
                raise ValueError('Tidak dapat mengekstrak hash dari initData')

            current_time = int(time.time())
            data_payload = json.dumps({"data": {}})
            api_hash = await self.create_api_hash(current_time, data_payload)
            
            headers = {
                **self.headers,
                "api-hash": api_hash,
                "Api-Key": hash_value,
                "Api-Time": str(current_time)
            }

            response = requests.post(
                "https://api.zoo.team/user/data/after",
                json={"data": {}},
                headers=headers
            )

            if response.status_code == 200 and response.json()['success']:
                return {'success': True, 'data': response.json()['data']}
            return {'success': False, 'error': response.json().get('message', 'Gagal mendapatkan data after')}

        except Exception as error:
            return {'success': False, 'error': str(error)}

    async def login(self, init_data):
        if not init_data:
            return {'success': False, 'error': 'initData diperlukan'}

        try:
            hash_value = init_data.split('hash=')[1].split('&')[0]
            if not hash_value:
                raise ValueError('Tidak dapat mengekstrak hash dari initData')

            current_time = int(time.time())
            user_data_part = init_data.split('user=')[1].split('&')[0]
            user_data = json.loads(urllib.parse.unquote(user_data_part))
            
            start_param = ''
            if 'start_param=' in init_data:
                start_param = init_data.split('start_param=')[1].split('&')[0]
            
            chat_instance = ''
            if 'chat_instance=' in init_data:
                chat_instance = init_data.split('chat_instance=')[1].split('&')[0]

            payload = {
                "data": {
                    "initData": init_data,
                    "startParam": "code_reff",
                    "photoUrl": user_data.get('photo_url', ""),
                    "platform": "android",
                    "chatId": "",
                    "chatType": "channel",
                    "chatInstance": chat_instance
                }
            }

            api_hash = await self.create_api_hash(current_time, json.dumps(payload))
            headers = {
                **self.headers,
                "api-hash": api_hash,
                "Api-Key": hash_value,
                "Api-Time": str(current_time)
            }

            response = requests.post(
                "https://api.zoo.team/telegram/auth",
                json=payload,
                headers=headers
            )

            if response.status_code == 200 and response.json()['success']:
                return {'success': True, 'data': response.json()['data']}
            return {'success': False, 'error': response.json().get('message', 'Login gagal')}

        except Exception as error:
            return {'success': False, 'error': str(error)}

    async def finish_onboarding(self, init_data):
        try:
            hash_value = init_data.split('hash=')[1].split('&')[0]
            if not hash_value:
                raise ValueError('Tidak dapat mengekstrak hash dari initData')

            current_time = int(time.time())
            payload = {"data": 1}
            api_hash = await self.create_api_hash(current_time, json.dumps(payload))
            
            headers = {
                **self.headers,
                "api-hash": api_hash,
                "Api-Key": hash_value,
                "Api-Time": str(current_time)
            }

            response = requests.post(
                "https://api.zoo.team/hero/onboarding/finish",
                json=payload,
                headers=headers
            )

            if response.status_code == 200 and response.json()['success']:
                return {'success': True, 'data': response.json()['data']}
            return {'success': False, 'error': response.json().get('message', 'Onboarding gagal')}

        except Exception as error:
            return {'success': False, 'error': str(error)}

    async def claim_daily_reward(self, init_data, reward_index):
        try:
            hash_value = init_data.split('hash=')[1].split('&')[0]
            if not hash_value:
                raise ValueError('Tidak dapat mengekstrak hash dari initData')

            current_time = int(time.time())
            payload = {"data": reward_index}
            api_hash = await self.create_api_hash(current_time, json.dumps(payload))
            
            headers = {
                **self.headers,
                "api-hash": api_hash,
                "Api-Key": hash_value,
                "Api-Time": str(current_time)
            }

            response = requests.post(
                "https://api.zoo.team/quests/daily/claim",
                json=payload,
                headers=headers
            )

            if response.status_code == 200 and response.json()['success']:
                return {'success': True, 'data': response.json()['data']}
            return {'success': False, 'error': response.json().get('message', 'Gagal mengklaim hadiah')}

        except Exception as error:
            return {'success': False, 'error': str(error)}

    async def handle_auto_feed(self, init_data):
        try:
            hash_value = init_data.split('hash=')[1].split('&')[0]
            if not hash_value:
                raise ValueError('Tidak dapat mengekstrak hash dari initData')

            user_data_result = await self.get_user_data(init_data)
            if not user_data_result['success']:
                raise ValueError(f"Gagal mendapatkan data pengguna: {user_data_result['error']}")

            hero = user_data_result['data']['hero']
            feed = user_data_result['data']['feed']

            if feed['isNeedFeed']:
                if "20" not in hero['onboarding']:
                    current_time = int(time.time())
                    payload = {"data": 20}
                    api_hash = await self.create_api_hash(current_time, json.dumps(payload))
                    
                    headers = {
                        **self.headers,
                        "api-hash": api_hash,
                        "Api-Key": hash_value,
                        "Api-Time": str(current_time)
                    }

                    onboarding_response = requests.post(
                        "https://api.zoo.team/hero/onboarding/finish",
                        json=payload,
                        headers=headers
                    )

                    if not onboarding_response.json()['success']:
                        raise ValueError('Gagal menyelesaikan langkah onboarding 20')

                current_time = int(time.time())
                feed_payload = {"data": "instant"}
                api_hash = await self.create_api_hash(current_time, json.dumps(feed_payload))
                
                headers = {
                    **self.headers,
                    "api-hash": api_hash,
                    "Api-Key": hash_value,
                    "Api-Time": str(current_time)
                }

                feed_response = requests.post(
                    "https://api.zoo.team/autofeed/buy",
                    json=feed_payload,
                    headers=headers
                )

                if feed_response.json()['success']:
                    self.log('Berhasil memberi makan hewan', 'success')
                    return {'success': True, 'data': feed_response.json()}

            return {'success': True}

        except Exception as error:
            return {'success': False, 'error': str(error)}

    async def buy_or_upgrade_animals(self, init_data):
        try:
            hash_value = init_data.split('hash=')[1].split('&')[0]
            if not hash_value:
                raise ValueError('Tidak dapat mengekstrak hash dari initData')

            user_data_result = await self.get_user_data(init_data)
            if not user_data_result['success']:
                raise ValueError(f"Gagal mendapatkan data pengguna: {user_data_result['error']}")

            animals = user_data_result['data']['animals']
            hero = user_data_result['data']['hero']
            db_data = user_data_result['data']['dbData']

            existing_keys = set(animal['key'] for animal in animals)
            used_positions = set(animal['position'] for animal in animals)
            
            # Buy new animals
            for db_animal in db_data['dbAnimals']:
                if db_animal['key'] not in existing_keys:
                    level1_price = db_animal['levels'][0]['price']
                    
                    if hero['coins'] >= level1_price:
                        position = 1
                        while position in used_positions:
                            position += 1

                        current_time = int(time.time())
                        payload = {"data": {"position": position, "animalKey": db_animal['key']}}
                        api_hash = await self.create_api_hash(current_time, json.dumps(payload))
                        
                        headers = {
                            **self.headers,
                            "api-hash": api_hash,
                            "Api-Key": hash_value,
                            "Api-Time": str(current_time)
                        }

                        response = requests.post(
                            "https://api.zoo.team/animal/buy",
                            json=payload,
                            headers=headers
                        )

                        if response.status_code == 200 and response.json()['success']:
                            self.log(f"Berhasil membeli {db_animal['title']}", 'success')
                            used_positions.add(position)
                            existing_keys.add(db_animal['key'])

            # Upgrade existing animals
            for animal in animals:
                db_animal = next((dba for dba in db_data['dbAnimals'] if dba['key'] == animal['key']), None)
                if db_animal:
                    next_level = animal['level'] + 1
                    next_level_data = next((l for l in db_animal['levels'] if l['level'] == next_level), None)
                    
                    if next_level_data and hero['coins'] >= next_level_data['price']:
                        current_time = int(time.time())
                        payload = {"data": {"position": animal['position'], "animalKey": animal['key']}}
                        api_hash = await self.create_api_hash(current_time, json.dumps(payload))
                        
                        headers = {
                            **self.headers,
                            "api-hash": api_hash,
                            "Api-Key": hash_value,
                            "Api-Time": str(current_time)
                        }

                        try:
                            response = requests.post(
                                "https://api.zoo.team/animal/buy",
                                json=payload,
                                headers=headers
                            )

                            if response.status_code == 200 and response.json()['success']:
                                self.log(f"Berhasil meningkatkan level {db_animal['title']} ke level {next_level}", 'success')
                        except Exception as error:
                            if getattr(error, 'response', None) and error.response.status_code == 500:
                                self.log(f"Tidak dapat meningkatkan level {db_animal['title']}: {str(error)}", 'error')

            return {'success': True}

        except Exception as error:
            return {'success': False, 'error': str(error)}

    def calculate_wait_time_in_seconds(self, next_feed_time):
        try:
            feed_time = datetime.strptime(next_feed_time, "%Y-%m-%d %H:%M:%S")
            feed_time = feed_time.replace(tzinfo=timezone.utc).astimezone()
            now = datetime.now().astimezone()
            diff_seconds = max(0, int((feed_time - now).total_seconds()))
            return diff_seconds
        except Exception:
            return 24 * 60 * 60  # Return 24 hours in seconds as default

    async def countdown(self, seconds):
        end_time = datetime.now() + timedelta(seconds=seconds)
        
        for i in range(seconds, 0, -1):
            current_time = datetime.now().strftime("%H:%M:%S")
            remaining_time = end_time - datetime.now()
            remaining_minutes = int(remaining_time.total_seconds() // 60)
            remaining_seconds = int(remaining_time.total_seconds() % 60)
            
            print(f"\r[{current_time}] [*] Menunggu {remaining_minutes} menit {remaining_seconds} detik untuk melanjutkan...", end='')
            await asyncio.sleep(1)
        
        print("\r" + " " * 100 + "\r", end='')  # Clear the countdown line

    async def main(self):
        try:
            if not os.path.exists('data.txt'):
                self.log('File data.txt tidak ditemukan!', 'error')
                return

            with open('data.txt', 'r', encoding='utf-8') as file:
                data = [line.strip() for line in file if line.strip()]

            if not data:
                self.log('Tidak ada data ditemukan di data.txt', 'error')
                return

            next_cycle_wait_time = 24 * 60 * 60  # Default 24 jam dalam detik
            
            while True:
                first_account_feed_time = None

                for i, init_data in enumerate(data):
                    try:
                        # Extract user data from init_data
                        user_data_str = init_data.split('user=')[1].split('&')[0]
                        user_data_str = urllib.parse.unquote(user_data_str)
                        user_data = json.loads(user_data_str)
                        username = user_data.get('username', 'Unknown')

                        print(f"\n{'='*10} Akun {i + 1} | {username} {'='*10}")
                        
                        self.log("Sedang login...", 'info')
                        login_result = await self.login(init_data)
                        
                        if login_result['success']:
                            self.log('Login berhasil!', 'success')
                            
                            user_data_result = await self.get_user_data(init_data)
                            if user_data_result['success']:
                                hero = user_data_result['data']['hero']
                                feed = user_data_result['data']['feed']

                                if i == 0 and not feed['isNeedFeed'] and feed.get('nextFeedTime'):
                                    first_account_feed_time = feed['nextFeedTime']
                                    feed_time_local = datetime.strptime(feed['nextFeedTime'], "%Y-%m-%d %H:%M:%S")
                                    feed_time_local = feed_time_local.replace(tzinfo=timezone.utc).astimezone()
                                    self.log(f"Waktu pemberian makan berikutnya: {feed_time_local.strftime('%Y-%m-%d %H:%M:%S')}", 'info')

                                # Handle onboarding if needed
                                if isinstance(hero.get('onboarding'), list) and len(hero['onboarding']) == 0:
                                    self.log('Menyelesaikan onboarding...', 'info')
                                    onboarding_result = await self.finish_onboarding(init_data)
                                    if onboarding_result['success']:
                                        self.log('Onboarding selesai!', 'success')

                                # Auto feed
                                await self.handle_auto_feed(init_data)

                                # Buy or upgrade animals
                                await self.buy_or_upgrade_animals(init_data)

                                # Check daily rewards
                                data_after_result = await self.get_user_data_after(init_data)
                                if data_after_result['success']:
                                    daily_rewards = data_after_result['data'].get('dailyRewards', {})
                                    for day in range(1, 17):
                                        if daily_rewards.get(str(day)) == 'canTake':
                                            self.log(f"Mengambil hadiah hari ke-{day}...", 'info')
                                            claim_result = await self.claim_daily_reward(init_data, day)
                                            if claim_result['success']:
                                                self.log('Berhasil mengambil hadiah harian!', 'success')
                                            break

                                # Show final status
                                final_data = await self.get_user_data(init_data)
                                if final_data['success']:
                                    self.log(f"Token: {final_data['data']['hero']['tokens']}", 'custom')
                                    self.log(f"Coins: {final_data['data']['hero']['coins']}", 'custom')

                        await asyncio.sleep(2)  # Delay antar akun

                    except Exception as error:
                        self.log(f"Error memproses akun {i + 1}: {str(error)}", 'error')
                        continue

                if first_account_feed_time:
                    next_cycle_wait_time = self.calculate_wait_time_in_seconds(first_account_feed_time)
                    wait_minutes = next_cycle_wait_time // 60
                    wait_seconds = next_cycle_wait_time % 60
                    self.log(f"Menunggu {wait_minutes} menit {wait_seconds} detik sampai pemberian makan berikutnya", 'info')
                else:
                    self.log("Menggunakan waktu tunggu default 24 jam", 'info')

                await self.countdown(next_cycle_wait_time)

        except Exception as error:
            self.log(f"Error pada proses utama: {str(error)}", 'error')
            return

if __name__ == "__main__":
    client = ZooAPIClient()
    asyncio.run(client.main())