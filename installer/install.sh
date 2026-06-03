#!/bin/sh
set -eu

TEMPLATE_DIR="/template"
TARGET_DIR="${TARGET_DIR:-/opt/chatluna-koishi-template}"
INSTALL_MODE="${INSTALL_MODE:-full}"
START_CONTAINERS="${START_CONTAINERS:-1}"
FORCE="${FORCE:-0}"

log() {
  printf '[ChatLuna Koishi] %s\n' "$1"
}

copy_file() {
  src="$1"
  dest="$2"
  mkdir -p "$(dirname "$dest")"
  if [ "$FORCE" = "1" ] || [ ! -e "$dest" ]; then
    cp "$src" "$dest"
    log "已写入：$dest"
  else
    log "已存在，跳过：$dest"
  fi
}

set_env_value() {
  key="$1"
  value="$2"
  file="$TARGET_DIR/.env"
  tmp="$(mktemp)"
  if grep -q "^${key}=" "$file"; then
    awk -v key="$key" -v value="$value" '
      $0 ~ "^" key "=" { print key "=" value; next }
      { print }
    ' "$file" > "$tmp"
  else
    cp "$file" "$tmp"
    printf '%s=%s\n' "$key" "$value" >> "$tmp"
  fi
  mv "$tmp" "$file"
}

apply_env_if_present() {
  key="$1"
  if printenv "$key" >/dev/null 2>&1; then
    set_env_value "$key" "$(printenv "$key")"
  fi
}

case "$INSTALL_MODE" in
  full)
    compose_file="docker-compose.yml"
    ;;
  koishi)
    compose_file="docker-compose.koishi.yml"
    ;;
  *)
    log "INSTALL_MODE 只能是 full 或 koishi，当前为：$INSTALL_MODE"
    exit 1
    ;;
esac

log "安装目录：$TARGET_DIR"
log "部署模式：$INSTALL_MODE"

mkdir -p \
  "$TARGET_DIR/koishi/data" \
  "$TARGET_DIR/koishi/locales" \
  "$TARGET_DIR/llbot/data" \
  "$TARGET_DIR/llbot/qq"

copy_file "$TEMPLATE_DIR/.env.example" "$TARGET_DIR/.env"
copy_file "$TEMPLATE_DIR/docker-compose.yml" "$TARGET_DIR/docker-compose.yml"
copy_file "$TEMPLATE_DIR/docker-compose.koishi.yml" "$TARGET_DIR/docker-compose.koishi.yml"
copy_file "$TEMPLATE_DIR/koishi/Dockerfile" "$TARGET_DIR/koishi/Dockerfile"
copy_file "$TEMPLATE_DIR/koishi/package.json" "$TARGET_DIR/koishi/package.json"
copy_file "$TEMPLATE_DIR/koishi/.yarnrc.yml" "$TARGET_DIR/koishi/.yarnrc.yml"
copy_file "$TEMPLATE_DIR/koishi/koishi.yml" "$TARGET_DIR/koishi/koishi.yml"

for key in \
  TZ \
  NPM_REGISTRY \
  KOISHI_AUTH_USERNAME \
  KOISHI_AUTH_PASSWORD \
  BOT_QQ \
  ONEBOT_TOKEN \
  LLBOT_WEBUI_TOKEN \
  LLBOT_TAG \
  PMHQ_TAG \
  LLBOT_WEBUI_PORT
do
  apply_env_if_present "$key"
done

if [ "$START_CONTAINERS" != "1" ]; then
  log "已写入模板文件，因 START_CONTAINERS=$START_CONTAINERS，跳过启动容器。"
  log "后续可执行：cd $TARGET_DIR && docker compose -f $compose_file up -d --build"
  exit 0
fi

if [ ! -S /var/run/docker.sock ]; then
  log "找不到 /var/run/docker.sock。请挂载宿主机 Docker socket：-v /var/run/docker.sock:/var/run/docker.sock"
  exit 1
fi

log "开始启动容器：docker compose -f $compose_file up -d --build"
cd "$TARGET_DIR"
docker compose -f "$compose_file" up -d --build

log "安装完成。安装器容器可以退出，业务容器会继续运行。"
log "Koishi 控制台：http://服务器地址:5140"
if [ "$INSTALL_MODE" = "full" ]; then
  log "LLBot WebUI：http://服务器地址:${LLBOT_WEBUI_PORT:-3080}"
fi
