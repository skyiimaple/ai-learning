export const SCORES: Record<string, number> = {
  Alice: 80,
  Bob: 95,
  Frank: 59,
  Grace: 88,
};

export function getScore(name: string) {
  if (!(name in SCORES)) {
    return { ok: false as const, error: "not found", name };
  }
  return { ok: true as const, name, score: SCORES[name] };
}

export function avgScore() {
  const vals = Object.values(SCORES);
  return {
    ok: true as const,
    count: vals.length,
    average:
      Math.round((vals.reduce((a, b) => a + b, 0) / vals.length) * 100) / 100,
  };
}
