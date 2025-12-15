#!/bin/sh
if [ ! -S "$SSH_AUTH_SOCK" ]; then
  echo "SSH agent socket not found. Starting ssh-agent..."
  eval "$(ssh-agent -s)"
else
  echo "SSH agent socket found at $SSH_AUTH_SOCK"
fi
