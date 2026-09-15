/**
 * 叙梦 Naro 客户端原生标准 IndexedDB 离线秒开加速持久化服务 (chatStorage)
 *
 * 核心设计:
 * 1. 使用原生标准 IndexedDB (零外部重型依赖，完全隔离，性能最高)；
 * 2. 建立 sessions, messages, controlPanels, narrativeStates 四大持久化存储区；
 * 3. 采用 Stale-While-Revalidate (SWR) 模式：
 *    - 页面加载时 0ms 瞬间从本地 IndexedDB 取出历史消息呈现，消除白屏与网络等待；
 *    - 后台异步与服务端对齐增量消息，静默更新本地持久化缓存。
 *
 * @packageDocumentation
 */

import type { ControlPanelDTO, NarrativeStateDTO, StoryBranchDetail } from "@/services/chat";
import type { ChatMessage } from "@/views/chat/constants/mockChatData";

const DB_NAME = "NaroChatStorageDB";
const DB_VERSION = 1;

const STORES = {
  SESSIONS: "sessions",
  MESSAGES: "messages",
  BRANCHES: "branches",
  CONTROL_PANELS: "controlPanels",
  NARRATIVE_STATES: "narrativeStates",
} as const;

class ChatStorageService {
  private dbPromise: Promise<IDBDatabase> | null = null;

  /**
   * 打开并初始化本地 IndexedDB 数据库
   */
  private async getDB(): Promise<IDBDatabase> {
    if (this.dbPromise) {
      return this.dbPromise;
    }

    this.dbPromise = new Promise<IDBDatabase>((resolve, reject) => {
      if (typeof indexedDB === "undefined") {
        reject(new Error("IndexedDB is not supported in this environment"));
        return;
      }

      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // 1. 会话表 (以 sessionId 为主键)
        if (!db.objectStoreNames.contains(STORES.SESSIONS)) {
          db.createObjectStore(STORES.SESSIONS, { keyPath: "sessionId" });
        }

        // 2. 消息表 (以 sessionId 为主键，存入整个消息数组或单独建索引)
        if (!db.objectStoreNames.contains(STORES.MESSAGES)) {
          db.createObjectStore(STORES.MESSAGES, { keyPath: "sessionId" });
        }

        // 3. 分支表 (以 sessionId 为主键)
        if (!db.objectStoreNames.contains(STORES.BRANCHES)) {
          db.createObjectStore(STORES.BRANCHES, { keyPath: "sessionId" });
        }

        // 4. 控制面板表 (以 sessionId 为主键)
        if (!db.objectStoreNames.contains(STORES.CONTROL_PANELS)) {
          db.createObjectStore(STORES.CONTROL_PANELS, { keyPath: "sessionId" });
        }

        // 5. 剧情状态机表 (以 sessionId 为主键)
        if (!db.objectStoreNames.contains(STORES.NARRATIVE_STATES)) {
          db.createObjectStore(STORES.NARRATIVE_STATES, { keyPath: "sessionId" });
        }
      };

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        console.error("Failed to open IndexedDB:", request.error);
        reject(request.error);
      };
    });

    return this.dbPromise;
  }

  // ================= 消息存取 (Messages) =================

  /**
   * 获取指定会话在本地缓存的所有历史消息 (0ms 秒开)
   */
  async getCachedMessages(sessionId: string): Promise<ChatMessage[] | null> {
    try {
      const db = await this.getDB();
      return new Promise<ChatMessage[] | null>((resolve) => {
        const tx = db.transaction(STORES.MESSAGES, "readonly");
        const store = tx.objectStore(STORES.MESSAGES);
        const req = store.get(sessionId);

        req.onsuccess = () => {
          if (req.result && Array.isArray(req.result.messages)) {
            resolve(req.result.messages);
          } else {
            resolve(null);
          }
        };

        req.onerror = () => {
          resolve(null);
        };
      });
    } catch (err) {
      console.warn("Failed to get cached messages from IndexedDB:", err);
      return null;
    }
  }

  /**
   * 全量持久化保存指定会话的消息列表
   */
  async saveMessages(sessionId: string, messages: ChatMessage[]): Promise<void> {
    if (!sessionId) return;
    try {
      const db = await this.getDB();
      return new Promise<void>((resolve, reject) => {
        const tx = db.transaction(STORES.MESSAGES, "readwrite");
        const store = tx.objectStore(STORES.MESSAGES);
        // 保存克隆纯对象，消除 Proxy 反应式包装
        const plainMessages = JSON.parse(JSON.stringify(messages));
        const req = store.put({
          sessionId,
          messages: plainMessages,
          updatedAt: Date.now(),
        });

        req.onsuccess = () => resolve();
        req.onerror = () => reject(req.error);
      });
    } catch (err) {
      console.warn("Failed to save messages to IndexedDB:", err);
    }
  }

  /**
   * 追加单条消息至指定会话
   */
  async appendMessage(sessionId: string, message: ChatMessage): Promise<void> {
    if (!sessionId) return;
    const current = (await this.getCachedMessages(sessionId)) || [];
    const idx = current.findIndex((m) => m.id === message.id);
    if (idx !== -1) {
      current[idx] = message;
    } else {
      current.push(message);
    }
    await this.saveMessages(sessionId, current);
  }

  // ================= 分支数据存取 (Branches) =================

  async getCachedBranches(sessionId: string): Promise<StoryBranchDetail[] | null> {
    try {
      const db = await this.getDB();
      return new Promise<StoryBranchDetail[] | null>((resolve) => {
        const tx = db.transaction(STORES.BRANCHES, "readonly");
        const store = tx.objectStore(STORES.BRANCHES);
        const req = store.get(sessionId);
        req.onsuccess = () => {
          resolve(req.result ? req.result.branches : null);
        };
        req.onerror = () => resolve(null);
      });
    } catch (_) {
      return null;
    }
  }

  async saveBranches(sessionId: string, branches: StoryBranchDetail[]): Promise<void> {
    if (!sessionId) return;
    try {
      const db = await this.getDB();
      const tx = db.transaction(STORES.BRANCHES, "readwrite");
      const store = tx.objectStore(STORES.BRANCHES);
      store.put({
        sessionId,
        branches: JSON.parse(JSON.stringify(branches)),
        updatedAt: Date.now(),
      });
    } catch (err) {
      console.warn("Failed to save branches to IndexedDB:", err);
    }
  }

  // ================= 控制面板与状态机存取 =================

  async getCachedControlPanel(sessionId: string): Promise<ControlPanelDTO | null> {
    try {
      const db = await this.getDB();
      return new Promise<ControlPanelDTO | null>((resolve) => {
        const tx = db.transaction(STORES.CONTROL_PANELS, "readonly");
        const store = tx.objectStore(STORES.CONTROL_PANELS);
        const req = store.get(sessionId);
        req.onsuccess = () => resolve(req.result ? req.result.data : null);
        req.onerror = () => resolve(null);
      });
    } catch (_) {
      return null;
    }
  }

  async saveControlPanel(sessionId: string, data: ControlPanelDTO): Promise<void> {
    if (!sessionId) return;
    try {
      const db = await this.getDB();
      const tx = db.transaction(STORES.CONTROL_PANELS, "readwrite");
      const store = tx.objectStore(STORES.CONTROL_PANELS);
      store.put({
        sessionId,
        data: JSON.parse(JSON.stringify(data)),
        updatedAt: Date.now(),
      });
    } catch (err) {
      console.warn("Failed to save control panel to IndexedDB:", err);
    }
  }

  async getCachedNarrativeState(sessionId: string): Promise<NarrativeStateDTO | null> {
    try {
      const db = await this.getDB();
      return new Promise<NarrativeStateDTO | null>((resolve) => {
        const tx = db.transaction(STORES.NARRATIVE_STATES, "readonly");
        const store = tx.objectStore(STORES.NARRATIVE_STATES);
        const req = store.get(sessionId);
        req.onsuccess = () => resolve(req.result ? req.result.data : null);
        req.onerror = () => resolve(null);
      });
    } catch (_) {
      return null;
    }
  }

  async saveNarrativeState(sessionId: string, data: NarrativeStateDTO): Promise<void> {
    if (!sessionId) return;
    try {
      const db = await this.getDB();
      const tx = db.transaction(STORES.NARRATIVE_STATES, "readwrite");
      const store = tx.objectStore(STORES.NARRATIVE_STATES);
      store.put({
        sessionId,
        data: JSON.parse(JSON.stringify(data)),
        updatedAt: Date.now(),
      });
    } catch (err) {
      console.warn("Failed to save narrative state to IndexedDB:", err);
    }
  }

  /**
   * 清除特定会话的所有离线缓存
   */
  async clearSessionCache(sessionId: string): Promise<void> {
    if (!sessionId) return;
    try {
      const db = await this.getDB();
      const tx = db.transaction(
        [STORES.MESSAGES, STORES.BRANCHES, STORES.CONTROL_PANELS, STORES.NARRATIVE_STATES],
        "readwrite",
      );
      tx.objectStore(STORES.MESSAGES).delete(sessionId);
      tx.objectStore(STORES.BRANCHES).delete(sessionId);
      tx.objectStore(STORES.CONTROL_PANELS).delete(sessionId);
      tx.objectStore(STORES.NARRATIVE_STATES).delete(sessionId);
    } catch (err) {
      console.warn("Failed to clear session cache from IndexedDB:", err);
    }
  }
}

export const chatStorage = new ChatStorageService();
