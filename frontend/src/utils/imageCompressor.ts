/**
 * 客户端图片压缩与 DataURL 转换工具。
 *
 * 针对酒馆超大隐写 PNG（常包含未压缩的巨型原画与多余 chunk），
 * 在保留高画质的前提下，将 10MB+ 的立绘快速压缩至 < 300KB 的 WebP/JPEG，
 * 极大加快上传速度并彻底杜绝请求超时与内存崩溃。
 *
 * @packageDocumentation
 */

export interface CompressImageOptions {
  maxWidth?: number;
  maxHeight?: number;
  quality?: number;
  outputFormat?: "image/webp" | "image/jpeg" | "image/png";
}

/**
 * 将 DataURL 或图片数据压缩至轻量化 DataURL
 *
 * @param src - 图片原始 DataURL
 * @param options - 压缩参数
 * @returns 压缩后的 DataURL
 *
 * @example
 * `	s
 * const compressed = await compressImageDataUrl(rawBase64, { maxWidth: 1024, quality: 0.85 });
 * `
 */
export async function compressImageDataUrl(
  src: string,
  options: CompressImageOptions = {},
): Promise<string> {
  const {
    maxWidth = 1024,
    maxHeight = 1024,
    quality = 0.85,
    outputFormat = "image/webp",
  } = options;

  return new Promise((resolve) => {
    // 非 base64 或本身小于 50KB 则不额外处理
    if (!src || !src.startsWith("data:image/") || src.length < 50000) {
      resolve(src);
      return;
    }

    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      try {
        let { width, height } = img;
        if (width > maxWidth || height > maxHeight) {
          if (width / height > maxWidth / maxHeight) {
            height = Math.round((height * maxWidth) / width);
            width = maxWidth;
          } else {
            width = Math.round((width * maxHeight) / height);
            height = maxHeight;
          }
        }

        const canvas = document.createElement("canvas");
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext("2d");
        if (!ctx) {
          resolve(src);
          return;
        }

        ctx.drawImage(img, 0, 0, width, height);
        const compressedDataUrl = canvas.toDataURL(outputFormat, quality);
        resolve(compressedDataUrl);
      } catch (err) {
        console.warn("Canvas 压缩图片失败，回退原图:", err);
        resolve(src);
      }
    };
    img.onerror = (err) => {
      console.warn("加载图片进行压缩失败，回退原图:", err);
      resolve(src);
    };
    img.src = src;
  });
}

/**
 * 将 DataURL 转换为 File 对象，用于通过 multipart/form-data 上传
 *
 * @param dataUrl - Base64 DataURL
 * @param filename - 目标文件名
 * @returns File 对象
 */
export function dataUrlToFile(dataUrl: string, filename = "avatar.webp"): File {
  const arr = dataUrl.split(",");
  const mime = arr[0]?.match(/:(.*?);/)?.[1] || "image/webp";
  const bstr = atob(arr[1] || "");
  let n = bstr.length;
  const u8arr = new Uint8Array(n);
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n);
  }
  return new File([u8arr], filename, { type: mime });
}
