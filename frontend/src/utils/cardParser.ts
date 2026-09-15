/**
 * SillyTavern V2/V3 角色卡与 PNG tEXt/iTXt 隐写数据解析工具。
 *
 * 遵循酒馆生态规范，支持：
 * 1. 客户端原生提取 PNG 中的 `chara` / `ccv3` 隐写元数据块；
 * 2. 原生解析 `.json` 角色卡；
 * 3. 智能检测普通图片 (如经过社交软件转码为 JPG、或未携带元数据的 PNG) 并返回立绘预览与精准诊断。
 *
 * @packageDocumentation
 *
 * @example
 * ```ts
 * import { parseCharacterCardFile } from "@/utils/cardParser";
 *
 * const result = await parseCharacterCardFile(file);
 * if (result.success && result.jsonData) {
 *   console.log("角色卡名称:", result.jsonData.name);
 * } else if (result.avatarDataUrl) {
 *   console.log("未检测到元数据，但可使用立绘:", result.avatarDataUrl);
 * }
 * ```
 */

export interface CardParseResult {
  /** 是否成功解析出角色卡结构化数据 */
  success: boolean;
  /** 文件类型识别结果 */
  fileType: "json" | "png" | "jpeg" | "webp" | "other_image" | "unknown";
  /** 文件中是否包含角色卡元数据 */
  hasMetadata: boolean;
  /** 解析出的 SillyTavern 角色卡 JSON 数据 */
  jsonData?: Record<string, any>;
  /** 提取或转换后的角色立绘图片 DataURL (如有) */
  avatarDataUrl?: string;
  /** 错误或诊断原因说明 (中文字符串) */
  errorMessage?: string;
}

/**
 * 将 Base64 编码的 UTF-8 字符串安全解码为原文字符串
 *
 * @param b64 - Base64 密文字符串
 * @returns UTF-8 明文字符串
 */
export function decodeBase64ToUtf8(b64: string): string {
  const cleanB64 = b64.replace(/[\r\n\s]/g, "");
  const binStr = atob(cleanB64);
  const bytes = new Uint8Array(binStr.length);
  for (let i = 0; i < binStr.length; i++) {
    bytes[i] = binStr.charCodeAt(i);
  }
  return new TextDecoder("utf-8").decode(bytes);
}

/**
 * 尝试解压 Deflate 字节流 (支持 iTXt 压缩块)
 *
 * @param compressedBytes - 经 Deflate 压缩的原始字节
 * @returns 解压后的字节
 */
async function decompressDeflate(compressedBytes: Uint8Array): Promise<Uint8Array> {
  if (typeof DecompressionStream === "undefined") {
    throw new Error("当前浏览器环境不支持 DecompressionStream，无法解压压缩格式的 iTXt 数据块");
  }
  const ds = new DecompressionStream("deflate");
  const writer = ds.writable.getWriter();
  await writer.write(compressedBytes as any);
  await writer.close();

  const reader = ds.readable.getReader();
  const chunks: Uint8Array[] = [];
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    if (value) chunks.push(value);
  }

  const totalLength = chunks.reduce((acc, c) => acc + c.length, 0);
  const merged = new Uint8Array(totalLength);
  let offset = 0;
  for (const chunk of chunks) {
    merged.set(chunk, offset);
    offset += chunk.length;
  }
  return merged;
}

/**
 * 从 PNG ArrayBuffer 字节流中扫描并提取 SillyTavern 'chara' 或 'ccv3' 元数据块
 *
 * @param buffer - PNG 图像的 ArrayBuffer
 * @returns 角色卡 JSON 字典对象或 null
 */
export async function extractCardFromPngBuffer(buffer: ArrayBuffer): Promise<Record<string, any> | null> {
  const view = new DataView(buffer);
  const uint8 = new Uint8Array(buffer);

  // 1. 校验 PNG 8 字节魔数: 89 50 4E 47 0D 0A 1A 0A
  if (buffer.byteLength < 8) return null;
  const isPng =
    uint8[0] === 0x89 &&
    uint8[1] === 0x50 &&
    uint8[2] === 0x4e &&
    uint8[3] === 0x47 &&
    uint8[4] === 0x0d &&
    uint8[5] === 0x0a &&
    uint8[6] === 0x1a &&
    uint8[7] === 0x0a;

  if (!isPng) return null;

  let offset = 8;
  const textDecoder = new TextDecoder("utf-8");

  while (offset < buffer.byteLength - 8) {
    const chunkLength = view.getUint32(offset, false);
    const chunkTypeBytes = uint8.slice(offset + 4, offset + 8);
    const chunkType = String.fromCharCode(...chunkTypeBytes);
    const chunkDataOffset = offset + 8;

    // 处理 tEXt 纯文本块
    if (chunkType === "tEXt") {
      const chunkData = uint8.slice(chunkDataOffset, chunkDataOffset + chunkLength);
      let nullIndex = -1;
      for (let i = 0; i < chunkData.length; i++) {
        if (chunkData[i] === 0) {
          nullIndex = i;
          break;
        }
      }

      if (nullIndex !== -1) {
        const keyword = String.fromCharCode(...chunkData.slice(0, nullIndex));
        if (keyword.toLowerCase() === "chara" || keyword.toLowerCase() === "ccv3") {
          const rawBase64Bytes = chunkData.slice(nullIndex + 1);
          const rawBase64 = textDecoder.decode(rawBase64Bytes);
          const jsonStr = decodeBase64ToUtf8(rawBase64);
          return JSON.parse(jsonStr);
        }
      }
    }

    // 处理 iTXt 国际化文本块
    if (chunkType === "iTXt") {
      const chunkData = uint8.slice(chunkDataOffset, chunkDataOffset + chunkLength);
      let nullIdx1 = -1;
      for (let i = 0; i < chunkData.length; i++) {
        if (chunkData[i] === 0) {
          nullIdx1 = i;
          break;
        }
      }

      if (nullIdx1 !== -1) {
        const keyword = textDecoder.decode(chunkData.slice(0, nullIdx1));
        if (keyword.toLowerCase() === "chara" || keyword.toLowerCase() === "ccv3") {
          const compressionFlag = chunkData[nullIdx1 + 1];
          // 查找语言标签 (null 结尾)
          let nullIdx2 = -1;
          for (let i = nullIdx1 + 3; i < chunkData.length; i++) {
            if (chunkData[i] === 0) {
              nullIdx2 = i;
              break;
            }
          }
          if (nullIdx2 !== -1) {
            // 查找翻译关键字 (null 结尾)
            let nullIdx3 = -1;
            for (let i = nullIdx2 + 1; i < chunkData.length; i++) {
              if (chunkData[i] === 0) {
                nullIdx3 = i;
                break;
              }
            }
            if (nullIdx3 !== -1) {
              const textBytes = chunkData.slice(nullIdx3 + 1);
              let rawBase64 = "";
              if (compressionFlag === 1) {
                try {
                  const decompressed = await decompressDeflate(textBytes);
                  rawBase64 = textDecoder.decode(decompressed);
                } catch {
                  rawBase64 = textDecoder.decode(textBytes);
                }
              } else {
                rawBase64 = textDecoder.decode(textBytes);
              }
              const jsonStr = decodeBase64ToUtf8(rawBase64);
              return JSON.parse(jsonStr);
            }
          }
        }
      }
    }

    if (chunkType === "IEND") {
      break;
    }

    offset += 12 + chunkLength;
  }

  return null;
}

/**
 * 从 File 对象中读取为 DataURL
 */
function readFileAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = (e) => reject(e);
    reader.readAsDataURL(file);
  });
}

/**
 * 从 File 对象中读取为 ArrayBuffer
 */
function readFileAsArrayBuffer(file: File): Promise<ArrayBuffer> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as ArrayBuffer);
    reader.onerror = (e) => reject(e);
    reader.readAsArrayBuffer(file);
  });
}

/**
 * 从 File 对象中读取为普通文本
 */
function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = (e) => reject(e);
    reader.readAsText(file);
  });
}

/**
 * 综合解析用户选择的任意角色卡文件 (支持 .json, .png, 以及普通图片诊断)
 *
 * @param file - 用户上传的 File 对象
 * @returns 角色卡诊断与解析结果
 */
export async function parseCharacterCardFile(file: File): Promise<CardParseResult> {
  const fileName = file.name.toLowerCase();

  // 1. JSON 文件处理
  if (fileName.endsWith(".json") || file.type === "application/json") {
    try {
      const text = await readFileAsText(file);
      const parsed = JSON.parse(text);
      return {
        success: true,
        fileType: "json",
        hasMetadata: true,
        jsonData: parsed,
      };
    } catch (err: any) {
      return {
        success: false,
        fileType: "json",
        hasMetadata: false,
        errorMessage: `JSON 文件解析失败: ${err.message || "文件格式错误"}`,
      };
    }
  }

  // 2. 图像文件处理 (PNG / JPG / WebP 等)
  const isJpg =
    fileName.endsWith(".jpg") ||
    fileName.endsWith(".jpeg") ||
    file.type === "image/jpeg";
  const isWebp = fileName.endsWith(".webp") || file.type === "image/webp";
  const isPng = fileName.endsWith(".png") || file.type === "image/png";

  let avatarDataUrl: string | undefined;
  try {
    avatarDataUrl = await readFileAsDataUrl(file);
  } catch {
    // 忽略立绘 DataURL 获取失败
  }

  // 如果是标准 PNG，尝试扫描 chara / ccv3 块
  if (isPng) {
    try {
      const arrayBuffer = await readFileAsArrayBuffer(file);
      const cardJson = await extractCardFromPngBuffer(arrayBuffer);

      if (cardJson) {
        return {
          success: true,
          fileType: "png",
          hasMetadata: true,
          jsonData: cardJson,
          avatarDataUrl,
        };
      }

      // 是 PNG 但未包含 chara 块
      return {
        success: false,
        fileType: "png",
        hasMetadata: false,
        avatarDataUrl,
        errorMessage:
          "该 PNG 图片未包含酒馆（SillyTavern）角色卡元数据。请确认是否为原作者发布的角色卡无损原图，或尝试导入 .json 格式文件。",
      };
    } catch (err: any) {
      return {
        success: false,
        fileType: "png",
        hasMetadata: false,
        avatarDataUrl,
        errorMessage: `解析 PNG 角色卡失败: ${err.message || "数据损坏"}`,
      };
    }
  }

  // 如果是 JPG 格式
  if (isJpg) {
    return {
      success: false,
      fileType: "jpeg",
      hasMetadata: false,
      avatarDataUrl,
      errorMessage:
        "该文件为 JPG 格式图片。酒馆角色卡依赖 PNG 无损隐写元数据，JPG 压缩已将角色人设数据彻底剥离（常见于社交软件自动转码或截图）。",
    };
  }

  // 如果是 WebP 格式
  if (isWebp) {
    return {
      success: false,
      fileType: "webp",
      hasMetadata: false,
      avatarDataUrl,
      errorMessage:
        "该文件为 WebP 格式缩略图。请从角色分享网站下载原版 PNG 角色卡或 JSON 配置文件。",
    };
  }

  // 其他未知格式
  return {
    success: false,
    fileType: "unknown",
    hasMetadata: false,
    avatarDataUrl,
    errorMessage: "不支持的文件格式。请上传无损 PNG 角色卡或 .json 配置文件。",
  };
}
