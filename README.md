# 🌙 ChatLuna Koishi 模板

以 ChatLuna 为核心的 Koishi 部署模板。

预装并预配置：`adapter-onebot`、ChatLuna 系列插件、`sidebar-manager`、`logger-plus`、`without-assignee`、`change-auth-callme`、`ffmpeg-path`、`markdown`。

---

## 🚀 部署方式

提供 **Docker** 与 **Windows Desktop** 两类入口。

Docker 方式提供两种 Compose，二选一：

| 文件 | 说明 |
|------|------|
| `docker-compose.koishi.yml` | 仅启动 Koishi，用户自行对接 LLBot / NapCat 等 OneBot 实现 |
| `docker-compose.yml` | 同时启动 Koishi + LLBot + PMHQ，自动通过 OneBot 11 反向 WS 对接 |

---

## 🧩 使用方式

### 🐳 Docker

1. 复制 `.env.example` 为 `.env`，修改 `BOT_QQ`、`KOISHI_AUTH_PASSWORD` 等字段。

2. 如使用 LLBot 方式，继续在 `.env` 中修改 `LLBOT_WEBUI_TOKEN`。

3. 按你的网络环境选择 npm 源，见下方「🌐 网络环境」。

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

---

### 🖥️ Windows Desktop

Windows 用户建议使用 Koishi Desktop。本项目提供一键配置向导，自动生成与 Docker 版一致的 Koishi 配置。

如果需要接入 QQ，可以额外安装并配置 LLBot Desktop。

#### 步骤

1. 安装 Koishi Desktop：<https://k.ilharp.cc/win.msi>

2. （可选）如果需要接入 QQ，跟随 LLBot 文档完成 Windows 版下载、解压、启动和登录：  
   <https://luckylillia.com/guide/choice_install>

3. 下载并解压[最新版本源码](https://github.com/CookSleep/chatluna-koishi-template/archive/refs/tags/v1.0.0.zip)。

4. 安装 Python 3：<https://www.python.org/ftp/python/3.14.5/python-3.14.5-amd64.exe>  
   安装时勾选 **"Add python.exe to PATH"**。

5. 运行脚本前，通过 **任务栏右键 Koishi 图标 → 高级 → 停止并退出** 退出 Koishi Desktop。

6. 双击运行 `一键配置-Windows-Desktop.bat`。

7. 按提示填写 Koishi 控制台用户名和密码、机器人 QQ、OneBot Token。

#### 脚本会自动完成

- 寻找 Koishi Desktop 实例目录或创建新实例
- 备份旧的 `koishi.yml` 和 `package.json`
- 写入与 Docker 版一致的 ChatLuna 模板配置
- 同步与 Docker 版一致的插件依赖清单
- 写入 `.yarnrc.yml`，让 Yarn 使用官方 npm registry
- 使用 Koishi Desktop 自带的 Yarn 安装插件依赖
- 写入 Koishi 控制台用户名和密码
- 写入机器人 QQ 和 OneBot Token
- 可选配置 LLBot Desktop 的 OneBot 11 反向 WebSocket

#### 完成后

脚本执行完成后，打开或重启 Koishi Desktop。

> 如果脚本提示依赖安装失败（找不到 `koi.exe`），请在 Koishi Desktop 侧栏的「依赖管理」中更新依赖。

#### 手动对接 OneBot

如果之后需要接入 QQ，但没有使用脚本自动配置 LLBot，请在 LLBot Desktop 中启用 OneBot 11 反向 WebSocket，并填写：

```text
ws://127.0.0.1:5140/onebot
```

如果启用了 OneBot Token，需要和脚本中填写的 Token 保持一致。

---

## 🌐 网络环境

Koishi 镜像构建时会安装插件依赖，Docker 方式通过 `.env` 中的 `NPM_REGISTRY` 选择 npm 源。

Windows Desktop 方式使用 Koishi Desktop 自身环境，不需要用户单独处理 npm。

> Koishi 自带的 `market` 的 `registry.endpoint` 似乎无效。

**国际网络**推荐使用官方源：

```env
NPM_REGISTRY=https://registry.npmjs.org
```

**国内网络**可改为国内镜像源：

```env
NPM_REGISTRY=https://registry.npmmirror.com
```

修改 `NPM_REGISTRY` 后，需要重新构建 Koishi 镜像才会生效：

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
   设置 LLM API、预设等。本项目默认未启用可选的、用于增加功能性的「扩展」插件，以及对新手上手难度较高的「高级」插件，你可以酌情根据官方文档进行配置。

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
├── scripts/
│   └── setup_windows_desktop.py  # Windows Desktop 一键配置向导
│
└── llbot/
    ├── data/                     # LLBot 配置数据（启动后生成）
    └── qq/                       # QQ 登录数据（启动后生成）
```

---

## 🔒 安全说明

请不要将填写后的 `.env`、LLBot 登录数据、QQ 登录数据或 Koishi 数据库公开上传。

---

## 📜 许可证

本项目基于 [GPL-3.0](LICENSE) 协议发布。
