#!/bin/bash

# Debugging: Sprawdź, czy `playerctl` jest dostępny
command -v playerctl >/dev/null 2>&1 || { echo "playerctl not found"; exit 1; }

# Sprawdź, czy jest aktywny odtwarzacz
player=$(playerctl -l)
if [ -z "$player" ]; then
    echo "No media playing"
    exit 1
fi

# Pobierz aktualny utwór i minutę
title=$(playerctl metadata title)
artist=$(playerctl metadata artist)
if [ -z "$title" ]; then
    echo "No media playing"
    exit 1
fi

# Pobierz czas odtwarzania
position=$(playerctl position | awk -F. '{print $1}')  # Czas w sekundach, tylko cała liczba

# Zamień czas na minutę:sekundę
minutes=$((position / 60))
seconds=$((position % 60))
time="$minutes:$seconds"

# Debugging: Zapisz wynik do pliku
echo "$title - $artist ($time)" > /tmp/current_audio_debug_output.log

# Zwróć tytuł utworu, artystę i czas
echo "$title - $artist ($time)"
