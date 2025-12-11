export interface PublishDecision {
  publish: boolean;
  reason?: string;
}

export function scaleToIndex(rawPrice: number, indexScale: number): number {
  if (indexScale <= 0) {
    throw new Error('indexScale must be > 0');
  }
  return rawPrice / indexScale;
}

export function sanityCheckJump(
  previous: number | null,
  next: number,
  maxJumpFraction: number
): { ok: boolean; reason?: string } {
  if (previous === null) {
    return { ok: true };
  }

  if (maxJumpFraction <= 0) {
    return { ok: true };
  }

  const jumpFraction = Math.abs(next - previous) / Math.max(Math.abs(previous), 1e-9);
  if (jumpFraction > maxJumpFraction) {
    return {
      ok: false,
      reason: `Jump too large: ${(jumpFraction * 100).toFixed(2)}% > ${(maxJumpFraction * 100).toFixed(2)}%`,
    };
  }

  return { ok: true };
}

export function shouldPublishValue(
  nextValue: number,
  lastPublishedValue: number | null,
  lastPublishTimestamp: number,
  now: number,
  priceChangeEpsilon: number,
  minPublishIntervalMs: number
): PublishDecision {
  if (lastPublishedValue === null) {
    return { publish: true };
  }

  const diff = Math.abs(nextValue - lastPublishedValue);
  if (diff >= priceChangeEpsilon) {
    return { publish: true };
  }

  if (now - lastPublishTimestamp >= minPublishIntervalMs) {
    return { publish: true };
  }

  return { publish: false, reason: 'No material change' };
}

