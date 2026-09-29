#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Render Free services have no Dashboard Shell. On the first Blueprint deploy,
# Render prompts for these sync:false values. The command creates the custom
# SRMCEM application admin once; future deploys leave an existing admin alone.
if [[ -n "${INITIAL_ADMIN_USERNAME:-}" && -n "${INITIAL_ADMIN_EMAIL:-}" && -n "${INITIAL_ADMIN_PASSWORD:-}" ]]; then
  python manage.py create_app_admin \
    --username "$INITIAL_ADMIN_USERNAME" \
    --email "$INITIAL_ADMIN_EMAIL" \
    --password "$INITIAL_ADMIN_PASSWORD"
fi
