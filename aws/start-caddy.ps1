caddy.exe run --config .\caddy.json

caddy adapt --config /path/to/Caddyfile

curl.exe localhost:2019/load `
-H "Content-Type: application/json" `
-d "@caddy.json"


http://localhost:2019/config/


caddy reverse-proxy --from :2080 --to :9000
