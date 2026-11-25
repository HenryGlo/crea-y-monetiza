#!/usr/bin/env bash
# Client landing deployment only; never restarts PerfectFlow or its workers.
set -euo pipefail
ADVENT_DIR=/opt/cym-advent-20261125
ADVENT_CONTAINER=cym-advent-20261125
cd "$ADVENT_DIR"
chmod 400 config.json
chown 1000:1000 config.json
chmod -R a+rX app content
docker network inspect repo_frontend >/dev/null
docker pull node:22-alpine
if ! docker inspect "$ADVENT_CONTAINER" >/dev/null 2>&1; then
  docker run -d --name "$ADVENT_CONTAINER" --restart unless-stopped --network repo_frontend \
    --user 1000:1000 --read-only --cap-drop ALL --security-opt no-new-privileges \
    --memory 160m --pids-limit 64 --log-opt max-size=5m --log-opt max-file=2 \
    --mount "type=bind,src=$ADVENT_DIR/app,dst=/srv,readonly" \
    --mount "type=bind,src=$ADVENT_DIR/content,dst=/content,readonly" \
    --mount "type=bind,src=$ADVENT_DIR/config.json,dst=/run/advent/config.json,readonly" \
    -e NODE_ENV=production --workdir /srv node:22-alpine node server.mjs
fi
# Validate the real workflow before changing any public route. The address is
# deliberately outside the student allowlist, so this probe cannot send mail.
docker exec "$ADVENT_CONTAINER" node --input-type=module -e '
  import fs from "node:fs";
  const c=JSON.parse(fs.readFileSync("/run/advent/config.json","utf8"));
  const r=await fetch(c.webhook,{method:"POST",headers:{"Content-Type":"application/json","X-Advent-Gateway":c.gatewayKey},body:JSON.stringify({action:"request",email:"henrylofiego+pf-unlisted-check@gmail.com",client_ip:"deployment-check"}),signal:AbortSignal.timeout(60000)});
  const result=await r.json();
  if(!r.ok || result.ok!==true)process.exit(1);
  console.log("Activepieces response verified; no mail requested.");
'
cd /app/repo
docker compose exec -T nginx wget -qO- "http://$ADVENT_CONTAINER:8080/calendario/health"
cp -p config/nginx.conf "$ADVENT_DIR/nginx.before.conf"
python3 - <<'PY'
from pathlib import Path
p=Path('/app/repo/config/nginx.conf')
s=p.read_bytes()
marker=b'    location /api/v1/automation { return 404; }'
block=b'''    # CYM_ADVENT_BEGIN - client landing, outside PerfectFlow
    location ^~ /calendario/ {
      proxy_pass http://cym-advent-20261125:8080;
      proxy_set_header Host $http_host;
      proxy_set_header X-Forwarded-Proto $scheme;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_read_timeout 65s;
      access_log off;
    }
    location ^~ /experiences/advent-students-2026 {
      return 303 https://creaymonetiza.perfectflow.cloud/calendario/alumnas/;
    }
    location = /experiences/advent-2026/events {
      proxy_pass http://cym-advent-20261125:8080/calendario/events;
      proxy_set_header Host $http_host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_read_timeout 65s;
      access_log off;
    }
    # CYM_ADVENT_END
'''
if b'# CYM_ADVENT_BEGIN' not in s:
 assert s.count(marker)==1, 'Unexpected nginx layout; no change'
 p.write_bytes(s.replace(marker,block+marker))
PY
if ! docker compose exec -T nginx nginx -t; then
  cp -p "$ADVENT_DIR/nginx.before.conf" config/nginx.conf
  exit 1
fi
docker compose exec -T nginx nginx -s reload
printf '\nClient landing service ready; CRM containers unchanged.\n'
