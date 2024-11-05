# BUMS Bot Automation Script

Script ini adalah versi PYTHON dari bot automation BUMS yang original NODEJS dari Grup Telegram [Dân Cày Airdrop](https://t.me/dancayairdrop).

## 🚀 Fitur

- Auto collect energy
- Auto claim tasks
- Multi account support
- Customizable settings melalui config.json

## 📋 Requirements

```bash
pip install -r requirements.txt
```

## ⚙️ Konfigurasi

Edit file `config.json` untuk menyesuaikan pengaturan:

```json
{
    "maxUpgradeCost": 1000000,  // Batas maksimum biaya upgrade (default: 1000000)
    "doTasks": true,            // true = aktifkan auto tasks, false = nonaktifkan
    "doUpgrades": true          // true = aktifkan auto upgrade, false = nonaktifkan
}
```

## 🔧 Cara Penggunaan

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Sesuaikan pengaturan di `config.json`

3. Jalankan script:
```bash
python bot.py
```

## 💖 Support Development

Jika Anda merasa script ini berguna, Anda dapat memberikan dukungan melalui:

USDT (TRC20): `TA6RvgjTaJRy6birB78gyJ9abiEhcPurGL`

## 🙏 Credits

- Original Script: [Dân Cày Airdrop](https://t.me/dancayairdrop)
- Python Version: [@syns4033](https://github.com/syns4033)

## ⚠️ Disclaimer

Script ini dibuat untuk tujuan edukasi. Pengguna bertanggung jawab penuh atas penggunaan script ini. DYOR.

## 📝 License

[MIT License](LICENSE)
