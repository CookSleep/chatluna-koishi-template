#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parents[1]


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return resource_root()


ROOT = resource_root()
APP_ROOT = app_root()
TEMPLATE_KOISHI_YML = ROOT / "koishi" / "koishi.yml"
TEMPLATE_PACKAGE_JSON = ROOT / "koishi" / "package.json"
DEFAULT_NPM_REGISTRY = "https://registry.npmjs.org"
DEFAULT_STORAGE_SERVER_PATH = "http://127.0.0.1:5140"


def color(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)


def interpolate_color(c1: tuple[int, int, int], c2: tuple[int, int, int], factor: float) -> str:
    r = int(c1[0] + (c2[0] - c1[0]) * factor)
    g = int(c1[1] + (c2[1] - c1[1]) * factor)
    b = int(c1[2] + (c2[2] - c1[2]) * factor)
    return f"\033[38;2;{r};{g};{b}m"


COLOR_START = color("#2e2786")
COLOR_END = color("#664ba0")
RESET = "\033[0m"


def write_logo() -> None:
    logo = r"""
 ____     __                 __     __                                    
/\  _`\  /\ \               /\ \__ /\ \                                   
\ \ \/\_\\ \ \___       __  \ \ ,_\\ \ \       __  __    ___       __     
 \ \ \/_/_\ \  _ `\   /'__`\ \ \ \/ \ \ \  __ /\ \/\ \ /' _ `\   /'__`\   
  \ \ \L\ \\ \ \ \ \ /\ \L\.\_\ \ \_ \ \ \L\ \\ \ \_\ \/\ \/\ \ /\ \L\.\_ 
   \ \____/ \ \_\ \_\\ \__/.\_\\ \__\ \ \____/ \ \____/\ \_\ \_\\ \__/.\_\
    \/___/   \/_/\/_/ \/__/\/_/ \/__/  \/___/   \/___/  \/_/\/_/ \/__/\/_/
""".strip("\n").splitlines()
    print()
    for index, line in enumerate(logo):
        factor = index / (len(logo) - 1)
        prefix = interpolate_color(COLOR_START, COLOR_END, factor)
        print(f"{prefix}{line}{RESET}")
    print()


def title(text: str) -> None:
    print()
    print(f"=== {text} ===")


def ok(text: str) -> None:
    print(f"[OK] {text}")


def warn(text: str) -> None:
    print(f"[提示] {text}")


def ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return default if not value and default else value


def ask_yes_no(prompt: str, default_yes: bool = True) -> bool:
    suffix = "Y/n" if default_yes else "y/N"
    value = input(f"{prompt} ({suffix}): ").strip().lower()
    if not value:
        return default_yes
    return value in {"y", "yes", "是", "1"}


def select_npm_registry() -> str:
    registries = {
        "1": ("npm 官方源", DEFAULT_NPM_REGISTRY),
        "2": ("npmmirror 国内源", "https://registry.npmmirror.com"),
    }

    print("请选择 Koishi 插件依赖下载源：")
    for key, (label, url) in registries.items():
        print(f"  {key}. {label}：{url}")
    print("  M. 手动输入")

    choice = ask("请选择", "1").lower()
    if choice == "m":
        registry = ask("请输入 npm registry 地址", DEFAULT_NPM_REGISTRY)
    else:
        registry = registries.get(choice, registries["1"])[1]

    registry = registry.rstrip("/")
    ok(f"将使用 npm 源：{registry}")
    return registry


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def backup(path: Path) -> None:
    if path.exists():
        target = path.with_name(f"{path.name}.bak-{timestamp()}")
        shutil.copy2(path, target)
        ok(f"已备份：{target}")


def koishi_instance_root() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("找不到「APPDATA」环境变量。请确认正在 Windows 用户环境中运行。")
    return Path(appdata) / "Koishi" / "Desktop" / "data" / "instances"


def is_koishi_instance(path: Path) -> bool:
    return (path / "koishi.yml").exists() and (path / "package.json").exists()


def get_koishi_candidates() -> list[Path]:
    candidates: list[Path] = []
    root = koishi_instance_root()
    if root.exists():
        candidates.extend(path for path in root.iterdir() if path.is_dir() and is_koishi_instance(path))

    desktop = Path.home() / "Desktop"
    for name in ["koishi-app", "Koishi", "chatluna-koishi"]:
        path = desktop / name
        if path.exists() and is_koishi_instance(path):
            candidates.append(path)

    unique: dict[str, Path] = {}
    for path in candidates:
        unique[str(path.resolve()).lower()] = path.resolve()
    return sorted(unique.values(), key=lambda item: str(item).lower())


def select_koishi_instance() -> Path:
    root = koishi_instance_root()
    candidates = get_koishi_candidates()

    if candidates:
        print("检测到以下 Koishi Desktop 实例：")
        for index, path in enumerate(candidates, 1):
            print(f"  {index}. {path}")
        print("  N. 创建新的 chatluna 实例")
        print("  M. 手动输入目录")
        choice = ask("请选择", "1")
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(candidates):
                return candidates[index]
        if choice.lower() == "m":
            return Path(ask("请输入 Koishi 实例目录")).expanduser().resolve()

    root.mkdir(parents=True, exist_ok=True)
    target = root / "chatluna"
    if target.exists():
        target = root / f"chatluna-{timestamp()}"
    target.mkdir(parents=True, exist_ok=True)
    return target


def koishi_instance_name(path: Path) -> str | None:
    root = koishi_instance_root().resolve()
    path = path.resolve()
    try:
        relative = path.relative_to(root)
    except ValueError:
        return None
    if len(relative.parts) == 1:
        return relative.parts[0]
    return None


def koishi_desktop_config_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("找不到 APPDATA 环境变量。请确认正在 Windows 用户环境中运行。")
    return Path(appdata) / "Koishi" / "Desktop" / "koi.yml"


def write_desktop_autostart(target_path: Path) -> None:
    instance_name = koishi_instance_name(target_path)
    if not instance_name:
        warn("当前项目不在 Koishi Desktop 默认实例目录下，无法自动设置 Desktop 启动实例。")
        return

    config_path = koishi_desktop_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if config_path.exists():
        backup(config_path)
        lines = config_path.read_text(encoding="utf-8").splitlines()
    else:
        lines = []

    start_block = ["start:", f"  - {instance_name}"]
    output: list[str] = []
    replaced = False
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.startswith((" ", "\t")) and line.split(":", 1)[0] == "start":
            if not replaced:
                output.extend(start_block)
                replaced = True
            index += 1
            while index < len(lines) and (not lines[index].strip() or lines[index].startswith((" ", "\t"))):
                index += 1
            continue
        output.append(line)
        index += 1

    if not replaced:
        if output and output[-1].strip():
            output.append("")
        output.extend(start_block)

    config_path.write_text("\n".join(output) + "\n", encoding="utf-8")
    written = config_path.read_text(encoding="utf-8")
    if f"  - {instance_name}" not in written:
        raise RuntimeError(f"Koishi Desktop 自动启动配置写入后校验失败：{config_path}")
    ok(f"已设置 Koishi Desktop 自动启动实例：{instance_name}")
    ok(f"已写入：{config_path}")


def find_koi_exe() -> Path | None:
    from_path = shutil.which("koi.exe") or shutil.which("koi")
    if from_path:
        return Path(from_path)

    roots = []
    for env_name in ["ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"]:
        value = os.environ.get(env_name)
        if value:
            roots.append(Path(value))
    appdata = os.environ.get("APPDATA")
    if appdata:
        roots.append(Path(appdata) / "Koishi" / "Desktop")

    for root in roots:
        candidate = root / "Koishi" / "Desktop" / "koi.exe"
        if candidate.exists():
            return candidate
    return None


def dependency_path(node_modules: Path, package_name: str) -> Path:
    if package_name.startswith("@"):
        scope, name = package_name.split("/", 1)
        return node_modules / scope / name
    return node_modules / package_name


def missing_installed_dependencies(target_path: Path) -> list[str]:
    node_modules = target_path / "node_modules"
    package_path = target_path / "package.json"
    if not package_path.exists():
        return ["package.json"]

    package_json = json.loads(package_path.read_text(encoding="utf-8"))
    dependencies = package_json.get("dependencies", {})
    if not isinstance(dependencies, dict):
        return ["package.json dependencies"]

    return [
        name
        for name in sorted(dependencies.keys())
        if not dependency_path(node_modules, name).exists()
    ]


def install_with_koishi_yarn(target_path: Path) -> bool:
    instance_name = koishi_instance_name(target_path)
    koi = find_koi_exe()
    if not instance_name or not koi:
        return False

    print(f"正在使用 Koishi Desktop 自带 Yarn 安装依赖：{instance_name}")
    subprocess.run(
        [str(koi), "--no-start", "yarn", "-n", instance_name, "install"],
        check=True,
    )
    return True


def write_yarnrc(target_path: Path, npm_registry: str) -> None:
    yarnrc = target_path / ".yarnrc.yml"
    yarnrc.write_text(
        "enableTips: false\n"
        "nodeLinker: node-modules\n"
        f"npmRegistryServer: \"{npm_registry}\"\n",
        encoding="utf-8",
    )
    ok(f"已写入：{yarnrc}")


def install_koishi_dependencies(target_path: Path) -> None:
    title("安装 Koishi 插件依赖")

    missing = missing_installed_dependencies(target_path)
    if missing:
        warn("以下插件尚未安装到「node_modules」：" + "、".join(missing))
        try:
            if not install_with_koishi_yarn(target_path):
                warn("未找到「koi.exe」，无法自动调用 Koishi Desktop 安装依赖。")
                warn("请在 Koishi Desktop 侧栏的依赖管理中更新依赖。")
        except subprocess.CalledProcessError:
            warn("Koishi Desktop Yarn 安装失败，请检查网络或在 Koishi Desktop 依赖管理中更新依赖。")

    missing = missing_installed_dependencies(target_path)
    if missing:
        warn("仍有插件未安装：" + "、".join(missing))
        warn("请在 Koishi Desktop 侧栏的依赖管理中更新依赖，或执行「koi.exe yarn -n 实例名 install」。")
        return

    ok("依赖安装完成，插件已写入「node_modules」。")


def find_llbot_candidates() -> list[Path]:
    roots = [APP_ROOT, APP_ROOT.parent, Path.home() / "Desktop", Path.home() / "Downloads", Path("C:/LLBot"), Path("D:/LLBot")]
    candidates: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in [root, root / "LLBot", root / "llbot"]:
            if (path / "llbot.exe").exists() or (path / "data").exists():
                candidates.append(path.resolve())
    unique: dict[str, Path] = {}
    for path in candidates:
        unique[str(path).lower()] = path
    return sorted(unique.values(), key=lambda item: str(item).lower())


def select_llbot_path() -> Path | None:
    candidates = find_llbot_candidates()
    if candidates:
        print("检测到以下 LLBot 目录：")
        for index, path in enumerate(candidates, 1):
            print(f"  {index}. {path}")
        print("  S. 跳过 LLBot 自动配置")
        print("  M. 手动输入目录")
        choice = ask("请选择", "1")
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(candidates):
                return candidates[index]
        if choice.lower() == "s":
            return None

    if ask_yes_no("没有自动找到 LLBot，是否手动输入 LLBot 目录？", False):
        return Path(ask("请输入 LLBot 解压目录，例如 D:\\LLBot")).expanduser().resolve()
    return None


def default_llbot_config(onebot_token: str) -> dict:
    return {
        "webui": {"enable": True, "port": 3080},
        "milky": {
            "enable": False,
            "reportSelfMessage": False,
            "http": {"port": 3010, "prefix": "", "accessToken": ""},
            "webhook": {"urls": [], "accessToken": ""},
        },
        "satori": {"enable": False, "port": 5600, "token": ""},
        "ob11": {
            "enable": True,
            "connect": [
                {
                    "type": "ws",
                    "enable": False,
                    "port": 3001,
                    "heartInterval": 60000,
                    "token": "",
                    "reportSelfMessage": False,
                    "reportOfflineMessage": False,
                    "messageFormat": "array",
                    "debug": False,
                },
                {
                    "type": "ws-reverse",
                    "enable": True,
                    "url": "ws://127.0.0.1:5140/onebot",
                    "heartInterval": 60000,
                    "token": onebot_token,
                    "reportSelfMessage": True,
                    "reportOfflineMessage": True,
                    "messageFormat": "array",
                    "debug": False,
                },
                {
                    "type": "http",
                    "enable": False,
                    "port": 3000,
                    "token": "",
                    "reportSelfMessage": False,
                    "reportOfflineMessage": False,
                    "messageFormat": "array",
                    "debug": False,
                },
                {
                    "type": "http-post",
                    "enable": False,
                    "url": "",
                    "enableHeart": False,
                    "heartInterval": 60000,
                    "token": "",
                    "reportSelfMessage": False,
                    "reportOfflineMessage": False,
                    "messageFormat": "array",
                    "debug": False,
                },
            ],
        },
        "log": True,
        "autoDeleteFile": False,
        "autoDeleteFileSecond": 60,
        "musicSignUrl": "",
        "msgCacheExpire": 120,
        "onlyLocalhost": True,
        "ffmpeg": "",
    }


def update_llbot_reverse_ws(config: dict, onebot_token: str) -> dict:
    config.setdefault("webui", {})
    config["webui"].update({"enable": True, "port": 3080})
    config.setdefault("ob11", {})
    config["ob11"]["enable"] = True
    connect = config["ob11"].setdefault("connect", [])

    reverse = None
    for item in connect:
        if isinstance(item, dict) and item.get("type") == "ws-reverse":
            reverse = item
            break
    if reverse is None:
        reverse = {"type": "ws-reverse"}
        connect.append(reverse)

    reverse.update(
        {
            "enable": True,
            "url": "ws://127.0.0.1:5140/onebot",
            "heartInterval": 60000,
            "token": onebot_token,
            "reportSelfMessage": True,
            "reportOfflineMessage": True,
            "messageFormat": "array",
            "debug": False,
        }
    )
    config.setdefault("onlyLocalhost", True)
    return config


def update_llbot_config_file(path: Path, onebot_token: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup(path)
        try:
            config = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(config, dict):
                raise ValueError("LLBot config root is not an object")
            config = update_llbot_reverse_ws(config, onebot_token)
        except Exception:
            warn("现有 LLBot 配置解析失败，将写入新的默认配置。原文件已备份。")
            config = default_llbot_config(onebot_token)
    else:
        config = default_llbot_config(onebot_token)
    path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ok(f"已写入：{path}")


def sync_package_json(target_path: Path) -> None:
    template_package = json.loads(TEMPLATE_PACKAGE_JSON.read_text(encoding="utf-8"))
    target_package_path = target_path / "package.json"

    if target_package_path.exists():
        target_package = json.loads(target_package_path.read_text(encoding="utf-8-sig"))
    else:
        target_package = {"name": "chatluna-koishi-desktop", "version": "1.0.0", "private": True}

    target_package.setdefault("scripts", {})["start"] = "koishi start"
    target_package["packageManager"] = template_package.get("packageManager", "yarn@4.12.0")
    target_package.setdefault("dependencies", {}).update(template_package.get("dependencies", {}))
    target_package_path.write_text(json.dumps(target_package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ok(f"已写入：{target_package_path}")


def write_koishi_config(target_path: Path, username: str, password: str, bot_qq: str, onebot_token: str) -> None:
    content = TEMPLATE_KOISHI_YML.read_text(encoding="utf-8")
    replacements = {
        "${{ env.KOISHI_AUTH_USERNAME }}": username,
        "${{ env.KOISHI_AUTH_PASSWORD }}": password,
        "${{ env.BOT_QQ }}": bot_qq,
        "${{ env.ONEBOT_TOKEN }}": onebot_token,
    }
    for source, value in replacements.items():
        content = content.replace(source, value.replace('"', '\\"'))
    content = content.replace("serverPath: http://koishi:5140", f"serverPath: {DEFAULT_STORAGE_SERVER_PATH}")
    target = target_path / "koishi.yml"
    target.write_text(content, encoding="utf-8")
    ok(f"已写入：{target}")


def main() -> None:
    write_logo()
    title("ChatLuna Koishi Windows Desktop 一键配置")
    print("请先安装 Koishi Desktop。接入 QQ 需要一个 OneBot 11 实现（如 LLBot、NapCat 等）。")
    print("请先通过「任务栏右键 Koishi 图标 - 高级 - 停止并退出」退出 Koishi Desktop，再运行脚本。脚本会自动备份旧配置。")
    print("如果没有任务栏图标，可先跳过；脚本安装依赖时会使用 --no-start，避免启动 Desktop 后台服务。")

    if not TEMPLATE_KOISHI_YML.exists():
        raise FileNotFoundError(f"找不到模板配置：{TEMPLATE_KOISHI_YML}")
    if not TEMPLATE_PACKAGE_JSON.exists():
        raise FileNotFoundError(f"找不到模板依赖清单：{TEMPLATE_PACKAGE_JSON}")

    title("选择依赖下载源")
    npm_registry = select_npm_registry()

    title("填写 Koishi 控制台凭据")
    print("以下用户名和密码用于登录 Koishi 控制台网页界面（http://127.0.0.1:5140）。")
    print("这是你自己设定的管理凭据，不是 QQ 账号密码。")
    username = ask("Koishi 控制台用户名", "admin")
    password = ask("Koishi 控制台密码", "change-me")

    title("选择 Koishi Desktop 实例")
    target_path = select_koishi_instance()
    target_path.mkdir(parents=True, exist_ok=True)
    ok(f"将配置 Koishi 实例：{target_path}")

    backup(target_path / "koishi.yml")
    backup(target_path / "package.json")

    title("配置 OneBot 实现（接入 QQ）")
    print("如需接入 QQ，需要一个 OneBot 11 实现（如 LLBot、NapCat 等）。")
    print("脚本目前可以自动配置 LLBot；其他实现请手动将「反向 WS」地址指向「ws://127.0.0.1:5140/onebot」。")
    bot_qq = ""
    onebot_token = ""
    llbot_configured = False
    if ask_yes_no("是否需要接入 QQ？", True):
        print("以下 QQ 号是你希望机器人使用的 QQ 账号，不是你自己的 QQ。")
        bot_qq = ask("机器人 QQ 号，可以先留空，之后再运行脚本补上")
        print("OneBot Token 用于 Koishi 与 OneBot 实现之间的鉴权，双方需保持一致。")
        print("如果 Koishi 和 OneBot 实现运行在同一台电脑上，通常可以留空。")
        onebot_token = ask("OneBot Token，普通本机部署可留空")

        if ask_yes_no("是否使用 LLBot 并让脚本自动配置？", True):
            llbot_path = select_llbot_path()
            if llbot_path:
                data_path = llbot_path / "data"
                data_path.mkdir(parents=True, exist_ok=True)
                update_llbot_config_file(llbot_path / "default_config.json", onebot_token)
                if bot_qq:
                    update_llbot_config_file(data_path / f"config_{bot_qq}.json", onebot_token)
                else:
                    warn("未填写机器人 QQ 号，只写入 default_config.json。")
                    warn("LLBot 登录 QQ 后会自动生成专属配置并继承默认设置。如未生效，可重新运行脚本并填写 QQ 号。")
                llbot_configured = True
            else:
                warn("已跳过 LLBot 自动配置。")
        else:
            print("请在你选择的 OneBot 实现中，手动配置 OneBot 11「反向 WS」：")
            ok("地址：ws://127.0.0.1:5140/onebot")
            if onebot_token:
                ok(f"Token：{onebot_token}")

    title("写入 Koishi 配置")
    write_koishi_config(target_path, username, password, bot_qq, onebot_token)

    title("同步插件依赖")
    sync_package_json(target_path)
    write_yarnrc(target_path, npm_registry)

    install_koishi_dependencies(target_path)

    title("设置 Koishi Desktop 自动启动实例")
    write_desktop_autostart(target_path)

    title("完成")
    print()
    print("【启动】")
    ok("下一步：打开 Koishi Desktop。")
    ok("Koishi 控制台地址：http://127.0.0.1:5140")

    print()
    print("【首次启动未弹出界面时】")
    warn("请先按正常流程关闭 Koishi，然后重新启动。")
    print("  1. 查看任务栏右下角托盘区，右键 Koishi 图标，选择「高级」-「停止并退出」。")
    print("  2. 仅关闭 Koishi 窗口通常不会结束后台进程，请务必通过托盘菜单执行「停止并退出」。")
    print("  3. 如果找不到 Koishi 托盘图标，请打开任务管理器，结束 Koishi 相关进程。")
    print("  4. 重新启动 Koishi，通常即可正常显示控制台界面。")

    print()
    print("【ChatLuna 文档】")
    warn("在开始使用前，请务必查看 ChatLuna 使用文档：")
    print("  https://chatluna.chat/guide/getting-started.html")

    print()
    print("【接入 QQ】")
    if llbot_configured:
        ok("LLBot「反向 WS」地址：ws://127.0.0.1:5140/onebot")
    elif not llbot_configured:
        warn("如需接入 QQ，请确保 OneBot 11 实现的「反向 WS」地址指向「ws://127.0.0.1:5140/onebot」。")

    print()
    print("【后续检查】")
    warn("如果未能自动安装依赖，请在 Koishi Desktop 侧栏的依赖管理中更新依赖，或执行「koi.exe yarn -n 实例名 install」。")
    warn("模型适配器默认全部关闭。请在 Koishi 控制台按需启用并填写 API Key。")
    warn("首次启动后，请在 Koishi 控制台启用「change-auth-callme」，并按提示给自己的 QQ 赋权。")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已取消。")
    except Exception as error:
        print(f"\n[错误] {error}")
    input("按回车键退出...")
