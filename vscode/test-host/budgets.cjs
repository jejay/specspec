/* Aggregate test guards only; individual operation deadlines live in their tests. */
const PHASE_GUARD_MS = 160_000;
const HOST_GUARD_MS = 2 * PHASE_GUARD_MS + 40_000;
module.exports = { PHASE_GUARD_MS, HOST_GUARD_MS };
