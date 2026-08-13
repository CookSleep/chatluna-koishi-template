<div align="center">

# ChatLuna Koishi 模板

[![License](https://img.shields.io/badge/license-GPL--3.0-10b981?style=flat-square)](https://github.com/CookSleep/chatluna-koishi-template/blob/main/LICENSE)
[![Koishi](https://img.shields.io/badge/Koishi-4.18-5546a3?style=flat-square)](https://koishi.chat/)
[![ChatLuna](https://img.shields.io/badge/ChatLuna-1.4-946ce6?style=flat-square)](https://chatluna.chat/)

**以 ChatLuna 为核心的 Koishi 一键部署模板**

预装并预配置 `adapter-onebot`、ChatLuna 系列插件、`sidebar-manager`、`logger-plus`、`without-assignee`、`change-auth-callme`、`ffmpeg-path`、`markdown` 等。<br>
支持 Docker 与 Windows Desktop 两种部署方式，开箱即用。

</div>

---

## ✨ 核心特性

- **开箱即用**：预装 ChatLuna 全家桶及常用辅助插件，免去手动逐一安装配置的繁琐流程。
- **多平台部署**：提供 Docker Compose 与 Windows Desktop 一键配置脚本，覆盖服务器和桌面场景。
- **灵活对接**：内置 OneBot 11 反向 WebSocket 适配器，兼容 LLBot、NapCat 等任意 OneBot 实现。
- **网络友好**：支持切换 npm 源（官方 / npmmirror），国内外网络均可顺畅部署。

---

## 🚀 部署与使用

提供 **Docker** 与 **Windows Desktop** 两类入口。

Docker 方式提供两种 Compose，二选一：

| 文件 | 说明 |
|------|------|
| `docker-compose.koishi.yml` | 仅启动 Koishi，用户自行对接 LLBot / NapCat 等 OneBot 实现 |
| `docker-compose.yml` | 同时启动 Koishi + LLBot（直连协议单容器），自动通过 OneBot 11 反向 WS 对接 |

<details>
<summary><strong>🐳 方式一：Docker 部署</strong></summary>

**方式 A：一次性安装器镜像（推荐）**

安装器只运行一次，自动落盘模板文件并拉起业务容器，完成后退出。

```bash
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /opt/chatluna-koishi-template:/opt/chatluna-koishi-template \
  -e TARGET_DIR=/opt/chatluna-koishi-template \
  -e KOISHI_AUTH_PASSWORD=change-me \
  -e BOT_QQ=123456789 \
  -e LLBOT_WEBUI_TOKEN=change-me \
  -e LLBOT_AUTH_TOKEN=从-auth.luckylillia.com-获取 \
  ghcr.io/cooksleep/chatluna-koishi-template-installer:latest
```

可选环境变量：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `TARGET_DIR` | 安装目录，需与 `-v` 挂载路径一致 | `/opt/chatluna-koishi-template` |
| `INSTALL_MODE` | `full`（Koishi + LLBot）或 `koishi`（仅 Koishi） | `full` |
| `NPM_REGISTRY` | npm 源 | `https://registry.npmjs.org` |
| `START_CONTAINERS` | 设为 `0` 时只落盘不启动容器 | `1` |

使用 LLBot 方式部署（`INSTALL_MODE=full`）时，还需提供以下变量：

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLBOT_AUTH_TOKEN` | **必填**。LLBot 直连协议登录 QQ 所需的 Auth Token，从 <https://auth.luckylillia.com> 获取。没有此 Token 将无法登录 QQ | `change-me` |
| `LLBOT_WEBUI_TOKEN` | LLBot WebUI 登录密码 | `change-me` |
| `LLBOT_WEBUI_PORT` | LLBot WebUI 端口 | `3080` |
| `LLBOT_TAG` | LLBot 镜像版本 | `latest` |

**方式 B：源码 Compose 部署**

1. 复制 `.env.example` 为 `.env`，修改 `BOT_QQ`、`KOISHI_AUTH_PASSWORD` 等字段。

2. 如使用 LLBot 方式，继续在 `.env` 中修改 `LLBOT_WEBUI_TOKEN`，并前往 <https://auth.luckylillia.com> 获取 `LLBOT_AUTH_TOKEN`。新版 LLBot 直连协议需要有效的 Auth Token 才能登录。

3. 按你的网络环境选择 npm 源，并修改 `.env` 中的 `NPM_REGISTRY`，见下方「🌐 网络环境」。

4. 启动：

   ```bash
   # 仅 Koishi
   docker compose -f docker-compose.koishi.yml up -d --build

   # Koishi + LLBot
   docker compose up -d --build
   ```

5. 打开 Koishi 控制台：`http://服务器地址:5140`。

6. 如使用 LLBot 方式，打开 LLBot WebUI：`http://服务器地址:3080`，完成 QQ 登录。

7. 参考下方「⚙️ 首次配置」，完成剩余配置。

</details>

<details>
<summary><strong>🖥️ 方式二：Windows Desktop</strong></summary>

Windows 用户建议使用 Koishi Desktop。本项目提供一键配置向导，自动生成适合本机环境的 Koishi 配置。

如果需要接入 QQ，可以额外安装并配置 LLBot Desktop。

**步骤**

1. 安装 Koishi Desktop：<https://k.ilharp.cc/win.msi>

2. （可选）如果需要接入 QQ，跟随 LLBot 文档完成 Windows 版下载、解压、启动和登录：  
   <https://luckylillia.com/guide/choice_install>

3. 下载 [`ChatLuna-Koishi-Windows-Desktop-Setup.exe`](https://github.com/CookSleep/chatluna-koishi-template/releases/latest/download/ChatLuna-Koishi-Windows-Desktop-Setup.exe)。

4. 运行脚本前，通过 **任务栏右键 Koishi 图标 → 高级 → 停止并退出** 退出 Koishi Desktop。

5. 双击运行 `ChatLuna-Koishi-Windows-Desktop-Setup.exe`。

6. 按提示选择 npm 源，并填写 Koishi 控制台用户名和密码、机器人 QQ、OneBot Token。

如果使用源码包而不是 exe，请下载并解压[最新源码](https://github.com/CookSleep/chatluna-koishi-template/archive/refs/heads/main.zip)，安装 Python 3 并勾选 **"Add python.exe to PATH"**，然后双击运行 `一键配置-Windows-Desktop.bat`。

**脚本会自动完成**

- 寻找 Koishi Desktop 实例目录或创建新实例
- 备份旧的 `koishi.yml` 和 `package.json`
- 写入适合 Windows Desktop 的 ChatLuna 模板配置
- 同步与 Docker 版一致的插件依赖清单
- 写入 `.yarnrc.yml`，让 Yarn 使用你在脚本中选择的 npm 源
- 使用 Koishi Desktop 自带的 Yarn 安装插件依赖
- 写入 Koishi 控制台用户名和密码
- 写入机器人 QQ 和 OneBot Token
- 可选配置 LLBot Desktop 的 OneBot 11 反向 WebSocket

**完成后**

脚本执行完成后，打开或重启 Koishi Desktop。

> 如果脚本提示依赖安装失败（找不到 `koi.exe`），请在 Koishi Desktop 侧栏的「依赖管理」中更新依赖。

**手动对接 OneBot**

如果之后需要接入 QQ，但没有使用脚本自动配置 LLBot，请在 LLBot Desktop 中启用 OneBot 11 反向 WebSocket，并填写：

```text
ws://127.0.0.1:5140/onebot
```

如果启用了 OneBot Token，需要和脚本中填写的 Token 保持一致。

</details>

---

## 🌐 网络环境

Koishi 插件依赖通过 npm registry 下载。本项目支持选择 npm 源：

- **Docker**：通过 `.env` 中的 `NPM_REGISTRY` 选择（安装器镜像通过 `-e NPM_REGISTRY=...` 传入）。
- **Windows Desktop**：运行脚本时交互选择，脚本会把结果写入 Koishi 实例的 `.yarnrc.yml`。

**国际网络**推荐使用官方源：

```env
NPM_REGISTRY=https://registry.npmjs.org
```

**国内网络**可选择国内镜像源：

```env
NPM_REGISTRY=https://registry.npmmirror.com
```

Docker 方式修改 `NPM_REGISTRY` 后，需要重新构建 Koishi 镜像才会生效：

```bash
# 仅 Koishi
docker compose -f docker-compose.koishi.yml up -d --build

# Koishi + LLBot
docker compose up -d --build
```

---

## ⚙️ 首次配置

部署完成后，还需要完成以下配置才能正常使用：

1. **赋权**  
   在 Koishi 插件配置中打开 `change-auth-callme`，遵循其指引为自己的 QQ 号赋予权限。否则部分指令无法使用。

2. **配置 ChatLuna 插件**  
   设置 LLM API、预设等。模型适配器默认全部关闭，请按需启用并填写 API Key。本项目默认未启用可选的、用于增加功能性的「扩展」插件，以及对新手上手难度较高的「高级」插件，你可以酌情根据官方文档进行配置。

详细的 ChatLuna 配置流程请参阅官方文档：

- [ChatLuna 快速上手](https://chatluna.chat/guide/getting-started.html)

---

## 🔧 后续维护

本模板仅用于初次部署。部署完成后，后续的插件更新、容器更新等操作请按照各项目官方文档进行：

- **Koishi 插件更新**：在 Koishi 控制台的「依赖管理」中操作。
- **LLBot / NapCat 等 OneBot 实现更新**：参阅对应项目的官方文档。

---

## 🤖 OneBot 对接说明

模板已预置 `adapter-onebot`，协议为 `ws-reverse`，监听路径为 `/onebot`。

你可以使用任何支持 OneBot 11 协议的实现（如 LLBot、NapCat 等）来对接。

- 如果使用 **LLBot 方式部署**，对接已自动完成，无需额外操作。
- 如果使用**纯 Koishi 方式部署**或其他 OneBot 实现，需要将反向 WS 地址指向 Koishi：

  ```text
  ws://Koishi可访问地址:5140/onebot
  ```

LLBot 的安装和配置请参阅官方文档：

- [LLBot 快速安装](https://luckylillia.com/guide/choice_install)

> `ONEBOT_TOKEN` 默认留空。如果启用 token，需要确保 Koishi 和 OneBot 实现使用相同的 token。  
> Docker 版中 Koishi 和 LLBot 会同时读取 `.env` 中的同一个环境变量。

---

## 📁 目录说明

```text
.
├── .env.example                  # 环境变量示例
├── docker-compose.yml            # Koishi + LLBot 启动文件
├── docker-compose.koishi.yml     # 纯 Koishi 启动文件
├── 一键配置-Windows-Desktop.bat   # Windows 一键入口
│
├── koishi/
│   ├── Dockerfile
│   ├── package.json              # 插件依赖
│   ├── koishi.yml                # Koishi 配置
│   ├── .yarnrc.yml
│   ├── data/                     # Koishi 运行数据（启动后生成）
│   └── locales/                  # Koishi 本地化文件（启动后生成）
│
└── llbot/
    └── data/                     # LLBot 配置、登录会话等持久化数据
```

---

## 🔒 安全说明

请不要将填写后的 `.env`、LLBot 登录数据、QQ 登录数据或 Koishi 数据库公开上传。

Docker 一次性安装器需要挂载 `/var/run/docker.sock`，这等同于授予安装器管理宿主机 Docker 的权限。请只运行你信任的镜像。

---

## 📄 许可证

本项目基于 [GPL-3.0](LICENSE) 协议发布。
