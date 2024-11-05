import os
import json
import time
import hashlib
import random
import requests
from datetime import datetime
from urllib.parse import unquote
from colorama import init, Fore, Style

# Inisialisasi colorama untuk output berwarna
init()

class Bums:
    def __init__(self):
        # Inisialisasi URL dan header untuk API
        self.base_url = 'https://api.bums.bot'
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://app.bums.bot",
            "Referer": "https://app.bums.bot/",
            "Sec-Ch-Ua": '"Not/A)Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36"
        }
        self.SECRET_KEY = '7be2a16a82054ee58398c5edb7ac4a5a'
        # Memuat konfigurasi dari file
        self.config = self.load_config()

    def load_config(self):
        """Memuat konfigurasi dari file config.json"""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.log(f"Error loading config: {str(e)}", 'error')
            # Konfigurasi default jika file tidak ditemukan
            return {
                "maxUpgradeCost": 1000000,
                "doTasks": True,
                "doUpgrades": True
            }

    def log(self, msg, type='info'):
        """Fungsi untuk menampilkan log dengan warna"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        if type == 'success':
            print(f"{Fore.GREEN}[{timestamp}] [✓] {msg}{Style.RESET_ALL}")
        elif type == 'custom':
            print(f"{Fore.MAGENTA}[{timestamp}] [*] {msg}{Style.RESET_ALL}")
        elif type == 'error':
            print(f"{Fore.RED}[{timestamp}] [✗] {msg}{Style.RESET_ALL}")
        elif type == 'warning':
            print(f"{Fore.YELLOW}[{timestamp}] [!] {msg}{Style.RESET_ALL}")
        else:
            print(f"{Fore.BLUE}[{timestamp}] [ℹ] {msg}{Style.RESET_ALL}")

    async def countdown(self, seconds):
        """Fungsi countdown dengan tampilan yang dinamis"""
        for i in range(seconds, 0, -1):
            timestamp = datetime.now().strftime('%H:%M:%S')
            print(f"\r{Fore.CYAN}[{timestamp}] [*] Menunggu {i} detik untuk melanjutkan...{Style.RESET_ALL}", end='')
            time.sleep(1)
        print("\r" + " " * 100 + "\r", end='')

    async def login(self, init_data, invitation_code):
        """Fungsi untuk login ke sistem"""
        url = f"{self.base_url}/miniapps/api/user/telegram_auth"
        data = {
            'invitationCode': invitation_code,
            'initData': init_data
        }
        
        try:
            response = requests.post(url, data=data, headers=self.headers)
            json_response = response.json()
            if response.status_code == 200 and json_response['code'] == 0:
                return {
                    'success': True,
                    'token': json_response['data']['token'],
                    'data': json_response['data']
                }
            else:
                return {'success': False, 'error': json_response.get('msg', 'Unknown error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def get_game_info(self, token):
        """Fungsi untuk mendapatkan informasi game"""
        url = f"{self.base_url}/miniapps/api/user_game_level/getGameInfo"
        headers = {**self.headers, "Authorization": f"Bearer {token}"}
        
        try:
            response = requests.get(url, headers=headers)
            json_response = response.json()
            if response.status_code == 200 and json_response['code'] == 0:
                return {
                    'success': True,
                    'coin': json_response['data']['gameInfo']['coin'],
                    'energySurplus': json_response['data']['gameInfo']['energySurplus'],
                    'data': json_response['data']
                }
            else:
                return {'success': False, 'error': json_response.get('msg', 'Unknown error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def generate_hash_code(self, collect_amount, collect_seq_no):
        """Fungsi untuk generate hash code"""
        data = f"{collect_amount}{collect_seq_no}{self.SECRET_KEY}"
        return hashlib.md5(data.encode()).hexdigest()

    def distribute_energy(self, total_energy):
        """Fungsi untuk mendistribusikan energi"""
        parts = 10
        remaining = int(total_energy)
        distributions = []
        
        for i in range(parts):
            is_last = i == parts - 1
            if is_last:
                distributions.append(remaining)
            else:
                max_amount = min(300, remaining // 2)
                amount = random.randint(1, max_amount)
                distributions.append(amount)
                remaining -= amount
        
        return distributions

    async def collect_coins(self, token, collect_seq_no, collect_amount):
        """Fungsi untuk mengumpulkan koin"""
        url = f"{self.base_url}/miniapps/api/user_game/collectCoin"
        headers = {**self.headers, "Authorization": f"Bearer {token}"}
        
        hash_code = self.generate_hash_code(collect_amount, collect_seq_no)
        data = {
            'hashCode': hash_code,
            'collectSeqNo': str(collect_seq_no),
            'collectAmount': str(collect_amount)
        }

        try:
            response = requests.post(url, data=data, headers=headers)
            json_response = response.json()
            if response.status_code == 200 and json_response['code'] == 0:
                return {
                    'success': True,
                    'newCollectSeqNo': json_response['data']['collectSeqNo'],
                    'data': json_response['data']
                }
            else:
                return {'success': False, 'error': json_response.get('msg', 'Unknown error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def process_energy_collection(self, token, energy, initial_collect_seq_no):
        """Fungsi untuk memproses pengumpulan energi"""
        energy_distributions = self.distribute_energy(energy)
        current_collect_seq_no = initial_collect_seq_no
        total_collected = 0

        for i, amount in enumerate(energy_distributions):
            self.log(f"Pengumpulan ke-{i + 1}/10: {amount} energi", 'custom')
            
            result = await self.collect_coins(token, current_collect_seq_no, amount)
            
            if result['success']:
                total_collected += amount
                current_collect_seq_no = result['newCollectSeqNo']
                self.log(f"Berhasil! Terkumpul: {total_collected}/{energy}", 'success')
            else:
                self.log(f"Error saat mengumpulkan: {result['error']}", 'error')
                break

            if i < len(energy_distributions) - 1:
                await self.countdown(5)

        return total_collected

    async def get_task_lists(self, token):
        """Fungsi untuk mendapatkan daftar tugas"""
        url = f"{self.base_url}/miniapps/api/task/lists"
        headers = {**self.headers, "Authorization": f"Bearer {token}"}
        params = {'_t': int(time.time() * 1000)}
        
        try:
            response = requests.get(url, headers=headers, params=params)
            json_response = response.json()
            if response.status_code == 200 and json_response['code'] == 0:
                return {
                    'success': True,
                    'tasks': [task for task in json_response['data']['lists'] if task['isFinish'] == 0]
                }
            else:
                return {'success': False, 'error': json_response.get('msg', 'Unknown error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def finish_task(self, token, task_id):
        """Fungsi untuk menyelesaikan tugas"""
        url = f"{self.base_url}/miniapps/api/task/finish_task"
        headers = {**self.headers, "Authorization": f"Bearer {token}"}
        data = {
            'id': str(task_id),
            '_t': str(int(time.time() * 1000))
        }

        try:
            response = requests.post(url, data=data, headers=headers)
            json_response = response.json()
            if response.status_code == 200 and json_response['code'] == 0:
                return {'success': True}
            else:
                return {'success': False, 'error': json_response.get('msg', 'Unknown error')}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    async def process_tasks(self, token):
        """Fungsi untuk memproses semua tugas"""
        self.log('Mengambil daftar tugas...', 'info')
        task_list = await self.get_task_lists(token)
        
        if not task_list['success']:
            self.log(f"Tidak dapat mengambil daftar tugas: {task_list['error']}", 'error')
            return

        if not task_list['tasks']:
            self.log('Tidak ada tugas baru!', 'warning')
            return

        for task in task_list['tasks']:
            self.log(f"Mengerjakan tugas: {task['name']}", 'info')
            result = await self.finish_task(token, task['id'])
            
            if result['success']:
                self.log(f"Tugas {task['name']} selesai | Hadiah: {task['rewardParty']}", 'success')
            else:
                self.log(f"Tidak dapat menyelesaikan tugas {task['name']}: {result.get('error', 'belum memenuhi syarat atau perlu dikerjakan manual')}", 'error')

            await self.countdown(5)

    async def main(self):
        """Fungsi utama program"""
        data_file = os.path.join(os.path.dirname(__file__), 'data.txt')
        if not os.path.exists(data_file):
            self.log('File data.txt tidak ditemukan!', 'error')
            return

        with open(data_file, 'r', encoding='utf-8') as f:
            data = [line.strip() for line in f.readlines() if line.strip()]

        if not data:
            self.log('File data.txt kosong!', 'error')
            return

        print(f"{Fore.GREEN}================================{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Tool dibagikan di channel telegram Dân Cày Airdrop.{Style.RESET_ALL}")
        print(f"{Fore.GREEN} Recode by @syns4033 search me on Github 👈 {Style.RESET_ALL}")
        print(f"{Fore.GREEN}================================{Style.RESET_ALL}")
        
        # Menggunakan konfigurasi dari file config.json
        do_tasks = self.config.get('doTasks', True)
        do_upgrades = self.config.get('doUpgrades', True)

        self.log(f"Mode tugas: {'Aktif' if do_tasks else 'Nonaktif'}", 'info')
        self.log(f"Mode upgrade: {'Aktif' if do_upgrades else 'Nonaktif'}", 'info')

        while True:
            for i, init_data in enumerate(data):
                try:
                    user_data = json.loads(unquote(init_data.split('user=')[1].split('&')[0]))
                    user_id = user_data['id']
                    first_name = user_data['first_name']

                    print(f"\n{Fore.GREEN}========== Akun {i + 1}/{len(data)} | {first_name} =========={Style.RESET_ALL}")
                    
                    self.log('Sedang login...', 'info')
                    login_result = await self.login(init_data, 'tjkzJBie')
                    
                    if not login_result['success']:
                        self.log(f"Login gagal: {login_result['error']}", 'error')
                        continue

                    self.log('Login berhasil!', 'success')
                    token = login_result['token']
                    
                    # Mendapatkan informasi game
                    game_info = await self.get_game_info(token)
                    if game_info['success']:
                        self.log(f"Koin: {game_info['coin']}", 'custom')
                        self.log(f"Energi: {game_info['energySurplus']}", 'custom')
                        
                        if int(game_info['energySurplus']) > 0:
                            self.log('Mulai mengumpulkan energi...', 'info')
                            collect_seq_no = game_info['data']['tapInfo']['collectInfo']['collectSeqNo']
                            await self.process_energy_collection(token, game_info['energySurplus'], collect_seq_no)
                        else:
                            self.log('Energi tidak cukup untuk dikumpulkan', 'warning')
                    else:
                        self.log(f"Tidak dapat mengambil info game: {game_info['error']}", 'error')

                    if do_tasks:
                        await self.process_tasks(token)

                    if i < len(data) - 1:
                        await self.countdown(5)

                except Exception as e:
                    self.log(f"Error memproses akun: {str(e)}", 'error')
                    continue

            await self.countdown(60 * 60)

if __name__ == "__main__":
    client = Bums()
    try:
        import asyncio
        asyncio.run(client.main())
    except KeyboardInterrupt:
        print("\nProgram dihentikan oleh pengguna")
    except Exception as err:
        client.log(str(err), 'error')
        exit(1)