#!/bin/bash

# Глючная загрузка - киберпанк хак-экран
clear
tput civis  # скрыть курсор

glitch_lines=(
"Ξ Запуск кибердек ядра... [ну наконец-то]"
"Ξ Внедрение системных эксплойтов... [не спрашивай откуда они]"
"Ξ Рукопожатие с нейросетью... [надеемся, что она дружелюбная]"
"Ξ Подмена MAC-адреса... ok [теперь я - принтер HP]"
"Ξ Ректификация сплайнов... ok [никто не знает, что это]"
"Ξ Инициализация модуля анализа целей... [прицел калиброван]"
"Ξ Выпуск дронов SIGINT... [вышли через Wi-Fi соседа]"
"Ξ Подключение к интерфейсу кибервойны... [настраиваю лазерную указку]"
"Ξ ████████████▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░ [10%] загрузка кофеина"
"Ξ ███████████████▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░ [42%] теряется связь с реальностью"
"Ξ ███████████████████████▓▓▓▓▓▓░░░░░░░░ [76%] синхронизация с darknet"
"Ξ ████████████████████████████████████ [100%] ты больше не человек"
)

for line in "${glitch_lines[@]}"; do
  echo -ne "\e[1;32m$line\e[0m\n" | lolcat
  sleep 0.25
done

echo ""
echo -ne "\e[1;35m┌──────────────────────────────────────────────────────┐\e[0m\n"
echo -ne "\e[1;35m│ \e[0m\e[1;36m   HACK MODULE LOADED :: WELCOME, OPERATIVE.   \e[0m\e[1;35m      │\e[0m\n"
echo -ne "\e[1;35m└──────────────────────────────────────────────────────┘\e[0m\n"
sleep 1

# 💀 Маленький эффект глюка + появление ника
for i in {1..30}; do
    echo -ne "\e[32m$(head /dev/urandom | tr -dc 'A-Za-z0-9!@#$%^&*_?' | head -c $((RANDOM % 28 + 12)))\r\e[0m"
    sleep 0.05
done

sleep 0.3

# Плавное появление ника AKUMA из "шума"
nickname="AKUMA"
for ((i=0; i<${#nickname}; i++)); do
    echo -ne "\e[1;31m${nickname:$i:1}\e[0m"
    sleep 0.2
done

echo -e "\n"

# 💡 Финальная подпись с шуткой
echo -e "\n💀 Все системы онлайн. Если что — это не мы."
echo -e "🧠 Добро пожаловать в матрицу, \e[1;32m$nickname\e[0m... У нас тут sudo и печеньки 🍪."


tput cnorm  # вернуть курсор
echo -e "\n"

# Функция для логирования
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_DIR/log.log"
}

# === Автообновление инструментов ===
log "▶ Обновление инструментов..."
apt update && apt upgrade -y nmap
cd ~/WhatWeb && git pull
GO111MODULE=on go install github.com/jaeles-project/jaeles@latest
nuclei -update
cd ~
log "Обновление завершено."

# Проверка и установка необходимых инструментов
if ! command -v whatweb &> /dev/null; then
    log "Устанавливаю WhatWeb..."
    apt install -y whatweb
fi

# Инициализация конфигурации Jaeles
log "▶ Инициализация конфигурации Jaeles..."
echo "export PATH=\$PATH:\$HOME/go/bin" >> ~/.bashrc
source ~/.bashrc
jaeles config init >> "$LOG_DIR/log.log" 2>&1

# Обработка аргументов
while getopts "f:" opt; do
  case $opt in
    f) target_file="$OPTARG" ;;
    *) echo "Использование: $0 -f <файл с целями>"; exit 1 ;;
  esac
done

# Проверка наличия файла с целями
if [ -z "$target_file" ]; then
  log "Ошибка: Не указан файл с целями. Используйте -f <файл>"
  exit 1
fi

# Определение даты
DATE=$(date +%d-%m-%Y)
DATE2=$(date '+%c')
LOG_DIR="/root/web_scan/$DATE-vnu"
mkdir -p "$LOG_DIR"
cd "$LOG_DIR" || exit 1

# Начало логгирования
log "=== Начало выполнения скрипта ==="
log "Директория для результатов: $LOG_DIR"
log "Файл с целями: $target_file"

# Пинг-сканирование
log "▶ Выполняется пинг-сканирование (nmap)..."
nmap -sn -iL "$target_file" -oG ping_result.txt >> "$LOG_DIR/log.log" 2>&1
grep "Up" ping_result.txt | awk '{print $2}' > target_raw.txt

# Проверка на пустой список целей
if [ ! -s target.txt ]; then
    log "❌ Ошибка: После фильтрации IP-адресов список целей пуст. Завершаем работу."
    exit 1
fi

TARGETS=$(tr '\n' ' ' < target.txt)

# Детальное сканирование nmap
log "▶ Выполняется детальное сканирование (nmap)..."
nmap -p- -sV -Pn --script=http-title,ssl-cert \
     --min-rate 500 --max-rate 1000 \
     --min-parallelism 10 --max-parallelism 50 \
     --max-rtt-timeout 300ms --min-rtt-timeout 100ms \
     --max-retries 2 --open -oA "$LOG_DIR/nmap_result" \
     $TARGETS >> "$LOG_DIR/log.log" 2>&1

log "Сканирование завершено [$DATE2]"

# Проверка gnmap перед обработкой
if [ ! -s "$LOG_DIR/nmap_result.gnmap" ]; then
    log "❌ Ошибка: Файл nmap_result.gnmap отсутствует или пуст. Завершаем работу."
    exit 1
fi

# Копирование результатов nmap для Grafana
log "▶ Копирование результатов nmap для Grafana..."
cp "$LOG_DIR/nmap_result.xml" /root/nmap-did-what/data/ >> "$LOG_DIR/log.log" 2>&1

# Запуск Grafana
log "▶ Перезапуск Grafana..."
cd /root/nmap-did-what/grafana-docker
docker-compose up -d >> "$LOG_DIR/log.log" 2>&1
log "Grafana запущена."

# Создание БД для Grafana
log "▶ Создание базы данных для Grafana..."
cd /root/nmap-did-what/data/
python3 nmap-to-sqlite.py nmap_result.xml >> "$LOG_DIR/log.log" 2>&1

# Извлечение открытых портов
log "▶ Извлечение открытых портов..."
grep "Ports:" "$LOG_DIR/nmap_result.gnmap" | awk -F"[ /]" '{split($0, a, "Ports: "); split(a[2], ports, ", "); for (i in ports) { split(ports[i], p, "/"); print $2":"p[1]; }}' > "$LOG_DIR/open_ports.txt"
log "Открытые порты сохранены в open_ports.txt"

# Возврат в папку с результатами
cd $LOG_DIR/

# Поиск web-сервисов httpx
log "▶ Поиск web-сервисов (httpx)..."
httpx -l "open_ports.txt" -o "httpx_result.txt" >> "$LOG_DIR/log.log" 2>&1
log "Поиск web-сервисов завершен."

# Запуск WhatWeb
log "▶ Запуск WhatWeb..."
mkdir -p "whatweb_result"
while read -r url; do
    clean_url=$(echo "$url" | sed "s/^http[s]*:\/\///" | sed "s/:/_/g")
    whatweb "$url" > "whatweb_result/$clean_url.html"
done < "httpx_result.txt"
log "Сканирование WhatWeb завершено."

# Проверка на Bitrix24
log "▶ Проверка на Bitrix24..."
mkdir -p "bitrix_targets"
while read -r url; do
    if whatweb "$url" 2>/dev/null | grep -qi "Bitrix"; then
        echo "$url" >> bitrix_targets/bitrix_sites.txt
    fi
done < "httpx_result.txt"
log "Проверка на Bitrix24 завершена."

# Запуск Nuclei
log "▶ Запуск сканера Nuclei..."
nuclei -l "open_ports.txt" -o "nuclei_result.txt" -t /root/nuclei-templates >> "$LOG_DIR/log.log" 2>&1
log "Сканирование завершено, уязвимости сохранены."

# Запуск Nuclei для Bitrix24
echo "▶ Запуск Nuclei с шаблонами Bitrix..."
if [ -s "bitrix_targets/bitrix_sites.txt" ]; then
    nuclei -l "bitrix_targets/bitrix_sites.txt" -o "nuclei_bitrix_result.txt" -t /root/nuclei-templates-bitrix/
fi
echo "Сканирование Bitrix завершено."

# Запуск Jaeles
log "▶ Запуск Jaeles..."
jaeles scan -U "$LOG_DIR/httpx_result.txt" -S /root/.jaeles/base-signatures/ > "jaeles_result.txt" 2>> "$LOG_DIR/log.log"
log "Сканирование Jaeles завершено."

# Сортировка уязвимостей
log "▶ Сортировка уязвимостей по критичности..."
grep -iR 'critical' "nuclei_result.txt" > "critical.txt"
grep -iR 'high' "nuclei_result.txt" > "high.txt"
grep -iR 'medium' "nuclei_result.txt" > "medium.txt"
grep -iR 'critical' "jaeles_result.txt" >> "critical.txt"
grep -iR 'high' "jaeles_result.txt" >> "high.txt"
grep -iR 'medium' "jaeles_result.txt" >> "medium.txt"
log "Уязвимости отсортированы."

# Создание html отчета Jaeles.

jaeles report -o "$LOG_DIR/out" --title 'Verbose Report $DATE'

log "=== Все этапы успешно выполнены ==="
