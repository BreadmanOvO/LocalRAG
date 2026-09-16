const storageKey = "betheboss.space-id.v1";
let fallback: string | undefined;

export function stableSpaceId() {
  try {
    const existing = window.localStorage.getItem(storageKey);
    if (existing) return existing;
    const identifier = `space-${crypto.randomUUID()}`;
    window.localStorage.setItem(storageKey, identifier);
    return identifier;
  } catch {
    fallback ??= `space-${crypto.randomUUID()}`;
    return fallback;
  }
}
