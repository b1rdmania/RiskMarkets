export interface PriceSnapshot {
  value: number;
  timestamp: number;
  stale: boolean;
  lastError?: string;
}

export interface PublishStats {
  lastPublish?: number;
  totalPublishes: number;
}

export const priceState: PriceSnapshot = {
  value: 0,
  timestamp: 0,
  stale: true,
  lastError: undefined,
};

export const publishStats: PublishStats = {
  totalPublishes: 0,
};
