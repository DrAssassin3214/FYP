// Single source of truth. S.case is exactly the case JSON (docs/case_schema.md); nothing else is stored in it.

export const S = {
  case: null,            // the case JSON object
  result: null,          // last successful service result (register, rule flags, matrix), untouched
  resultKey: null,       // serialised case at the time of that result
  savedKey: null,        // serialised case at last New / Open / Load example / Save
  validation: { status: "idle", problems: [], warnings: [], key: null },
  meta: null, library: [], rules: [], health: null,
  evidence: new Map(),   // id -> record (curated records at start; others are added when a case cites them)
  evidenceList: [],
  ui: {
    screen: "case",
    fileName: null,
    open: new Set(),               // expanded risk cards, keys like "risk:3"
    autoAdded: new Set(),          // rule-flagged risk ids already auto-added to this case (never re-added after a delete)
    autoAddPending: false,         // set by a deliberate fact change; the next valid result may add flagged risks
    riskTab: "library",
    suggest: null, suggestBusy: false, suggestQuery: "",
    evQuery: "", evCitedOnly: false, evHits: null, evBusy: false,
  },
};

export const caseKey = () => JSON.stringify(S.case);
export const isDirty = () => S.case !== null && S.savedKey !== caseKey();
export const hasResult = () => !!S.result;
/** True while the inputs have problems, so the register/matrix shown are from the last valid state. */
export const isStale = () => !!S.result && S.resultKey !== caseKey();

export function riskIds() { return (S.case?.risks || []).map((r) => r.id).filter(Boolean); }
