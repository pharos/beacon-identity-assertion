#!/usr/bin/env bash
set -ex

# Allow the user to run docker commands without sudo
[[ -f "/var/run/docker.sock" ]] && sudo chown $(whoami) /var/run/docker.sock  || true

# If dotfiles have previously been installed, update them
[[ -d "${HOME}/dotfiles" ]] && cd ${HOME}/dotfiles && git pull && ./install.sh && cd ..  || true