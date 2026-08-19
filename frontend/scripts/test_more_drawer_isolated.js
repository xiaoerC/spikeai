/**
 * 独立端口与独立数据目录 Chrome 自动化测试驱动脚本
 *
 * 通过独立启动 Chrome (Port: 9233, Isolated User Data Dir) + 纯原生 WebSocket CDP，
 * 彻底实现零冲突沙箱自测与真机截图。
 */

import { spawn } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import WebSocket from "ws";

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const DEBUG_PORT = 9233;
const ISOLATED_DATA_DIR = path.join(
  process.env.TEMP || "C:\\Temp",
  "chrome_isolated_drawer_test",
);
const TARGET_URL = "http://127.0.0.1:5173/";
const OUTPUT_IMAGE_PATH =
  "C:\\Users\\spike\\.gemini\\antigravity\\brain\\88125bf2-dcf4-461b-b349-ca579b7a8233\\more_drawer_isolated_test.png";

// 1. 清理并准备独立临时目录
if (fs.existsSync(ISOLATED_DATA_DIR)) {
  try {
    fs.rmSync(ISOLATED_DATA_DIR, { recursive: true, force: true });
  } catch (e) {}
}
fs.mkdirSync(ISOLATED_DATA_DIR, { recursive: true });

console.log(
  `[1/5] 启动独立 Chrome 实例 (Port: ${DEBUG_PORT}, DataDir: ${ISOLATED_DATA_DIR})...`,
);

const chromeProcess = spawn(
  CHROME_PATH,
  [
    `--remote-debugging-port=${DEBUG_PORT}`,
    `--user-data-dir=${ISOLATED_DATA_DIR}`,
    "--headless=new",
    "--window-size=440,956",
    "--hide-scrollbars",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    TARGET_URL,
  ],
  {
    detached: false,
    stdio: "ignore",
  },
);

// 等待 CDP 端口就绪
function waitForCdpReady(retries = 30) {
  return new Promise((resolve, reject) => {
    const check = (attempt) => {
      http
        .get(`http://127.0.0.1:${DEBUG_PORT}/json/list`, (res) => {
          let data = "";
          res.on("data", (chunk) => (data += chunk));
          res.on("end", () => {
            try {
              const list = JSON.parse(data);
              if (list && list.length > 0) {
                resolve(list[0].webSocketDebuggerUrl);
              } else {
                throw new Error("No tab found");
              }
            } catch (err) {
              if (attempt < retries) setTimeout(() => check(attempt + 1), 300);
              else reject(err);
            }
          });
        })
        .on("error", (err) => {
          if (attempt < retries) setTimeout(() => check(attempt + 1), 300);
          else reject(err);
        });
    };
    check(1);
  });
}

async function run() {
  try {
    const wsUrl = await waitForCdpReady();
    console.log(`[2/5] 成功连接独立 Chrome CDP: ${wsUrl}`);

    const ws = new WebSocket(wsUrl);
    let msgId = 1;
    const callbacks = new Map();

    ws.on("message", (raw) => {
      const resp = JSON.parse(raw);
      if (resp.id && callbacks.has(resp.id)) {
        const { resolve, reject } = callbacks.get(resp.id);
        callbacks.delete(resp.id);
        if (resp.error) reject(resp.error);
        else resolve(resp.result);
      }
    });

    const send = (method, params = {}) => {
      return new Promise((resolve, reject) => {
        const id = msgId++;
        callbacks.set(id, { resolve, reject });
        ws.send(JSON.stringify({ id, method, params }));
      });
    };

    await new Promise((res) => ws.on("open", res));

    console.log("[3/5] 导航并等待页面渲染...");
    await send("Page.enable");
    await send("Runtime.enable");
    await send("Emulation.setDeviceMetricsOverride", {
      width: 440,
      height: 956,
      deviceScaleFactor: 2,
      mobile: true,
    });

    await send("Page.navigate", { url: TARGET_URL });
    await new Promise((r) => setTimeout(r, 2500));

    console.log("[4/5] 模拟点击底部 TabBar 中的「更多」按钮...");
    const clickResult = await send("Runtime.evaluate", {
      expression: `(() => {
        const buttons = Array.from(document.querySelectorAll('nav button'));
        const moreBtn = buttons.find(b => b.innerText.includes('更多'));
        if (moreBtn) {
          moreBtn.click();
          return 'Clicked more button successfully';
        }
        return 'More button not found, total buttons: ' + buttons.length;
      })()`,
      returnByValue: true,
    });
    console.log(` -> 点击结果: ${JSON.stringify(clickResult.result.value)}`);

    // 等待抽屉展开动画
    await new Promise((r) => setTimeout(r, 1000));

    console.log("[5/5] 截取独立浏览器真机视口图...");
    const screenshot = await send("Page.captureScreenshot", {
      format: "png",
      captureBeyondViewport: false,
    });

    fs.writeFileSync(OUTPUT_IMAGE_PATH, Buffer.from(screenshot.data, "base64"));
    console.log(`✨ 截图已成功保存至: ${OUTPUT_IMAGE_PATH}`);

    ws.close();
    process.exit(0);
  } catch (err) {
    console.error("Test execution failed:", err);
    process.exit(1);
  } finally {
    try {
      chromeProcess.kill();
    } catch (e) {}
  }
}

run();
