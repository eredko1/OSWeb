#!/usr/bin/env bash
# Rebuilds vendor/tailwind.css from the classes used in index.html (replaces the runtime CDN script).
set -e; cd "$(dirname "$0")/.."
npx --yes tailwindcss@3.4.17 -c tools/tailwind.config.js -i tools/tailwind.in.css -o vendor/tailwind.css --minify
