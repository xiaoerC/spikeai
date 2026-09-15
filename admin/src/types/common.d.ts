declare global {
  export interface PageQuery {
    page: number;
    size: number;
    filter: string;
    order: string;
  }

  export interface PageResult<T> {
    totalPages: number;
    total: number;
    number: number;
    size: number;
    list: T[];
    hasNext: boolean;
    hasPrevious: boolean;
    isFirst: boolean;
    isLast: boolean;
  }
}

export {};
