import { priceState } from '../state';

export interface PythPriceResult {
  value: number;
  timestamp: number;
}

export async function fetchPythPrice(feedId: string): Promise<PythPriceResult> {
  // Placeholder implementation for Day 1
  // TODO: Replace with real Pyth testnet client
  const mockValue = 1800 + Math.random() * 10;
  const now = Date.now();

  priceState.value = mockValue;
  priceState.timestamp = now;
  priceState.stale = false;

  return { value: mockValue, timestamp: now };
}
