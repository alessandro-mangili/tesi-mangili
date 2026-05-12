# Docker - Avvio Rapido

Guida rapida per avviare l'ambiente Docker per l'analisi firmware.

---

## Setup Iniziale (Prima Volta)

```bash
# 1. Vai nella directory del progetto
cd tesi-mangili

# 2. Dai permessi alle directory di lavoro
chmod -R 777 retdec_klee/ angr/

# 3. Build dell'immagine Docker (10-15 minuti)
docker-compose build

# 4. Avvia il container
docker-compose up -d

# 5. Verifica che sia attivo
docker-compose ps
```

---

## Utilizzo Quotidiano

### Avvio Container

```bash
# Avvia
docker-compose up -d

# Verifica stato
docker-compose ps
```

### Accesso al Container

```bash
# Entra nel container
docker-compose exec analysis bash

# Ora sei dentro! Prompt:
[firmware] /workspace $
```

### Esegui Analisi

```bash
# Pipeline RetDec + KLEE
cd /workspace/retdec_klee
bash klee_pipeline.sh

# Script ANGR
cd /workspace/angr
python3 boot_main_exploration.py
```

### Uscita e Arresto

```bash
# Esci dal container
exit

# Ferma il container
docker-compose down
```

---

## Comandi Utili

```bash
# Restart container
docker-compose restart

# Visualizza log
docker-compose logs -f

# Rebuild (dopo modifiche al Dockerfile)
docker-compose build --no-cache
docker-compose up -d

# Entra come root (se servono permessi)
docker-compose exec -u root analysis bash
```

---

## Pulizia

```bash
# Ferma e rimuovi container
docker-compose down

# Pulisci cache Docker
docker builder prune -f

# Pulizia completa (rimuove tutto)
docker-compose down --rmi all
docker system prune -a -f
```

## 📋 Verifica Strumenti

```bash
# Dentro il container
retdec-decompiler --version  # RetDec
klee --version                # KLEE
llvm-as --version             # LLVM
python3 -c "import angr; print('ANGR OK')"  # ANGR
```

