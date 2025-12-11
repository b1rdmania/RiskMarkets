#!/usr/bin/env ts-node
import * as fs from 'fs';
import * as path from 'path';
import { sanityCheckJump, scaleToIndex, shouldPublishValue } from '../src/pipeline';

type Fixture = {
  raw: number;
  expected: number;
  expectPublish: boolean;
  expectSkipReason?: string;
  timestamp?: number;
};

const fixturePath =
  process.argv[2] ?? path.join(__dirname, '../test/fixtures/regression.json');

const indexScale = Number(process.env.INDEX_SCALE ?? 40);
const maxJumpFraction = Number(process.env.MAX_JUMP_FRACTION ?? 0.2);
const priceChangeEpsilon = Number(process.env.PRICE_EPSILON ?? 0.01);
const minPublishIntervalMs = Number(process.env.MIN_PUBLISH_INTERVAL_MS ?? 10000);

function main() {
  const content = fs.readFileSync(fixturePath, 'utf-8');
  const fixtures = JSON.parse(content) as Fixture[];

  let lastPublishedValue: number | null = null;
  let lastPublishTimestamp = 0;
  let previousIndex: number | null = null;
  const failures: string[] = [];

  fixtures.forEach((entry, idx) => {
    const now = entry.timestamp ?? idx * 3000;
    const scaled = scaleToIndex(entry.raw, indexScale);

    if (Math.abs(scaled - entry.expected) > 1e-6) {
      failures.push(`Fixture ${idx} expected ${entry.expected} got ${scaled}`);
    }

    const jumpCheck = sanityCheckJump(previousIndex, scaled, maxJumpFraction);
    const publishDecision = jumpCheck.ok
      ? shouldPublishValue(
          scaled,
          lastPublishedValue,
          lastPublishTimestamp,
          now,
          priceChangeEpsilon,
          minPublishIntervalMs
        )
      : { publish: false, reason: jumpCheck.reason };

    if (entry.expectPublish && (!jumpCheck.ok || !publishDecision.publish)) {
      failures.push(
        `Fixture ${idx} expected publish but was skipped: ${publishDecision.reason ?? jumpCheck.reason}`
      );
    }

    if (!entry.expectPublish && jumpCheck.ok && publishDecision.publish) {
      failures.push(`Fixture ${idx} expected skip but decided to publish`);
    }

    if (entry.expectSkipReason) {
      const reason = (jumpCheck.reason ?? publishDecision.reason ?? '').toLowerCase();
      if (!reason.includes(entry.expectSkipReason.toLowerCase())) {
        failures.push(
          `Fixture ${idx} expected skip reason containing "${entry.expectSkipReason}", got "${jumpCheck.reason ?? publishDecision.reason}"`
        );
      }
    }

    // Update state only when publish is allowed
    if (jumpCheck.ok && publishDecision.publish) {
      lastPublishedValue = scaled;
      lastPublishTimestamp = now;
    }
    if (jumpCheck.ok) {
      previousIndex = scaled;
    }
  });

  if (failures.length) {
    console.error(`❌ Regression failed (${failures.length} issues):`);
    failures.forEach((f) => console.error(` - ${f}`));
    process.exit(1);
  } else {
    console.log('✅ Regression fixtures passed');
  }
}

main();


