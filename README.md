# Enerji İzleme (Python + AI) Örneği

MQTT ile gelen ölçümleri FastAPI üzerinden kaydeden, basit agregasyon, alarm ve yapay zekâ (anomali + tahmin) örneği.

## Çalıştırma

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Örnek İstekler

- Sağlık kontrolü: `GET /health`
- Ölçüm ekleme: `POST /measurements` (isteğe bağlı `timestamp` alanı ile geçmiş zamanlı kayıt da yapılabilir)

```json
{
  "device_id": "plc-1",
  "phase": "A",
  "voltage": 230,
  "current": 10.5,
  "active_power": 2.1,
  "energy_kwh": 0.01,
  "power_factor": 0.93,
  "frequency": 50,
  "timestamp": "2024-07-01T10:00:00Z"
}
```

- Son ölçümler: `GET /measurements`
- 15 dakikalık özet: `GET /aggregates`
- Tahmin: `GET /ai/forecast?device_id=plc-1&horizon_minutes=60`
- Anomali skoru: `GET /ai/anomaly?score_value=2.4`
- Uyarılar: `GET /alerts`

## MQTT İneştirimi

`backend/app/mqtt_client.py` dosyasındaki `MQTTIngestor` sınıfı, bir topic dinleyip gelen JSON payload'ları `Measurement` tablosuna yazar. Başlatmak için:

```python
from app.db import init_db, get_session
from app.mqtt_client import MQTTIngestor

init_db()
ingestor = MQTTIngestor(
    broker_url="localhost", broker_port=1883, topic="plc/measurements", session_factory=get_session
)
ingestor.start()
```

## Notlar

- Demo SQLite kullanır; üretimde TimescaleDB/PostgreSQL tercih edin.
- Anomali modeli basit `IsolationForest` örneğidir; daha iyi sonuç için gerçek verinizle yeniden eğitin.
- Flutter istemci veya ek servisler için bu API uçlarını temel alabilirsiniz.

## Kodu GitHub'a Taşıma / Cursor'da Açma

1) **GitHub deposu oluştur**: GitHub'da boş bir repo açın (örn. `energy-monitor-ai`).
2) **Uzaktan ekle ve push et**:
   ```bash
   git remote add origin git@github.com:<kullanici_adiniz>/energy-monitor-ai.git
   git push -u origin main
   ```
   SSH yerine HTTPS kullanıyorsanız `git remote add origin https://github.com/<kullanici_adiniz>/energy-monitor-ai.git` yazabilirsiniz.
3) **Cursor veya VS Code'da aç**:
   - Cursor/VS Code açıp **File > Open Folder** ile bu depo klasörünü seçin.
   - Terminalden de açabilirsiniz: `cursor .` veya `code .`
4) **Çalıştırma**: Cursor/VS Code terminalinde `cd backend && source .venv/bin/activate` (veya `python -m venv .venv && pip install -r requirements.txt`) ardından `uvicorn app.main:app --reload` komutuyla API'yi başlatın.
