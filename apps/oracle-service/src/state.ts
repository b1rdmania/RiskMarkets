export interface PriceSnapshot {
  value: number;
  timestamp: number;
  stale: boolean;
}

export interface PublishStats {
  lastPublish?: number;
  totalPublishes: number;
}

export const priceState: PriceSnapshot = {
  value: 0,
  timestamp: 0,
  stale: true,
};

export const publishStats: PublishStats = {
  totalPublishes: 0,
};
