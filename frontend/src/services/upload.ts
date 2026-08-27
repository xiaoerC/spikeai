/**
 * 资产与图片上传强类型服务模块。
 *
 * 支持将用户选择的头像、封面、背景图片上传至 MinIO 或后端静态存储，并返回公开访问直链。
 *
 * @packageDocumentation
 */

import api, { type ApiResponse } from "./api";

export interface UploadImageResult {
  url: string;
  filename: string;
}

export const uploadService = {
  /**
   * 上传单张图片至对象存储
   *
   * @param file - 待上传的 File 对象
   * @param folder - 归档目录类别
   * @returns 文件的可公开访问 URL
   *
   * @example
   * ```ts
   * const url = await uploadService.uploadImage(file, "avatars");
   * ```
   */
  async uploadImage(
    file: File,
    folder: "avatars" | "banners" | "chat" | "cards" = "avatars"
  ): Promise<string> {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("folder", folder);

    const res = await api.post<ApiResponse<UploadImageResult>>("/upload/image", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return res.data.data.url;
  },
};
