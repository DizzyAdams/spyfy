#!/usr/bin/env sh
# Gera o Caddyfile com basic auth (a partir de env) e sobe o Caddy.
# Usado pelo servico `caddy` no docker-compose.yml para proteger o tunel publico.
set -e

USER="${BASIC_AUTH_USER:-spyfy}"
PASS="${BASIC_AUTH_PASSWORD:-change-me-please}"
HASH="$(caddy hash-password "$PASS")"

cat > /etc/caddy/Caddyfile <<EOF
{
    admin off
}
:8080 {
    basicauth {
        ${USER} ${HASH}
    }
    reverse_proxy web:3000
}
EOF

echo "Caddyfile gerado (basic auth para usuario '${USER}')."
exec caddy run --config /etc/caddy/Caddyfile
