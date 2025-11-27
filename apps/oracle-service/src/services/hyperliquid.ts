import { publishStats } from '../state';

export interface PublishResult {
  ok: boolean;
  skipped?: boolean;
}

let lastPublishedValue: number | null = null;

export async function publishToHyperliquid(value: number): Promise<PublishResult> {
  if (lastPublishedValue === value) {
    return { ok: true, skipped: true };
  }

  // Placeholder for Day 1
  console.log(`[HL] Would publish value=${value.toFixed(2)}`);
  lastPublishedValue = value;
  publishStats.lastPublish = Date.now();
  publishStats.totalPublishes += 1;

  return { ok: true };
}
