# Keep-Alive Setup per Render Free Tier

Il bot include un sistema di keep-alive interno che si auto-pinga ogni 14 minuti per rimanere attivo.

## Come Funziona

1. **Sistema Interno**: Il bot si auto-pinga ogni 14 minuti tramite l'endpoint `/health`
2. **Endpoint Health**: Disponibile su `https://refloop-bot.onrender.com/health`
3. **Limite Render Free**: 750 ore/mese (circa 31 giorni se sempre attivo)

## Monitoraggio (Opzionale)

Se vuoi un monitoraggio esterno aggiuntivo, puoi usare questi servizi gratuiti:

### 1. UptimeRobot (Raccomandato)
- Vai su: https://uptimerobot.com
- Crea account gratuito
- Aggiungi nuovo monitor:
  - **Type**: HTTP(s)
  - **URL**: `https://refloop-bot.onrender.com/health`
  - **Monitoring Interval**: 5 minuti (piano gratuito)
  - **Monitor Type**: Keyword (cerca "ok" nella risposta)

### 2. Cron-Job.org
- Vai su: https://cron-job.org
- Crea account gratuito
- Crea nuovo cron job:
  - **URL**: `https://refloop-bot.onrender.com/health`
  - **Interval**: Ogni 10 minuti
  - **Method**: GET

### 3. Freshping
- Vai su: https://www.freshworks.com/website-monitoring/
- Piano gratuito: 50 checks
- Aggiungi check per `https://refloop-bot.onrender.com/health`

## Consumo Ore Render

Con keep-alive attivo 24/7:
- **Ore al giorno**: 24
- **Ore al mese**: ~720
- **Limite Render Free**: 750 ore/mese
- **Margine**: ~30 ore (1.25 giorni)

✅ Il bot dovrebbe rimanere attivo tutto il mese!

## Upgrade a Piano Paid (Raccomandato per Produzione)

Per un servizio professionale senza limiti:
- **Render Starter**: $7/mese
- **Vantaggi**: 
  - Nessun limite di ore
  - Sempre attivo
  - Più risorse (512MB RAM)
  - Nessun cold start

## Verifica Stato

Puoi verificare che il bot sia attivo visitando:
```
https://refloop-bot.onrender.com/health
```

Dovresti vedere:
```json
{"status":"ok","bot":"RefLoop","uptime":"running"}
```

## Logs

Per vedere i log del keep-alive su Render:
1. Vai su https://dashboard.render.com
2. Clicca sul servizio "refloop-bot"
3. Vai su "Logs"
4. Cerca: "Keep-alive ping successful"
