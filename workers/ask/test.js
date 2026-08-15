// Every control gets a red case.
//
// The half that matters most is the set of sentences that must NOT trip a guard. A guard
// that blocks its own correct refusal teaches the model to answer instead of decline, which
// is the exact outcome the rule exists to prevent, and it fails silently: the answer looks
// fine, it just stopped saying "the record doesn't say".
//
// Run: node workers/ask/test.js

import {
  checkCitations, checkNumerals, checkSentence, checkVerdict, checkVoice,
  normalise, numerals, plainly, splitSentences,
} from "./checks.js";

let fail = 0, pass = 0;
const ok = (label, cond, detail = "") => {
  if (cond) { pass++; return; }
  fail++;
  console.log(`  FAIL  ${label}${detail ? "  " + detail : ""}`);
};
const head = (t) => console.log("\n" + t);

// ---------------------------------------------------------------- numerals
head("A. numerals tokenise the way numeral_lint does");
ok("a thousands separator is inside the number, not a break in it",
  JSON.stringify(numerals("peak was 8,927 MW")) === JSON.stringify(["8927"]),
  JSON.stringify(numerals("peak was 8,927 MW")));
ok("a big one survives too",
  numerals("1,781,547.9 MWh")[0] === "1781547.9", numerals("1,781,547.9 MWh")[0]);
ok("a decimal survives", numerals("76.5 percent")[0] === "76.5");
ok("the zero in front of a decimal is kept",
  normalise("0.8469") === "0.8469", normalise("0.8469"));
ok("padding zeros still go", normalise("07") === "7");
ok("trailing zeros after a point still go", normalise("76.50") === "76.5");
ok("a padded date authorises the day a person writes",
  numerals("2026-07-09").includes("9"), JSON.stringify(numerals("2026-07-09")));

head("B. the numeral gate");
const allowed = new Set(["87648.5", "76.5", "58", "2026"]);
ok("an authorised figure passes",
  checkNumerals("Peak load reached 87648.5 MW.", allowed).ok);
ok("an invented figure is refused",
  !checkNumerals("Peak load reached 91234.6 MW.", allowed).ok);
ok("and the reason is named",
  checkNumerals("Peak load reached 91234.6 MW.", allowed).reason === "numeral");
ok("a citation's digits are not read as a figure",
  checkNumerals("See [[tx-2026-0001]] for the filing.", allowed).ok,
  JSON.stringify(checkNumerals("See [[tx-2026-0001]] for the filing.", allowed)));
ok("a model may write 8927 having been shown 8,927",
  checkNumerals("Peak was 8927 MW.", new Set(["8927"])).ok);

// ---------------------------------------------------------------- citations
head("C. the citation gate");
const slugs = new Set(["tx-2026-0001", "tx-2026-0002"]);
ok("a real decision passes", checkCitations("See [[tx-2026-0001]].", slugs).ok);
ok("an invented one is refused", !checkCitations("See [[tx-2026-9999]].", slugs).ok);
ok("and it says which",
  checkCitations("See [[tx-2026-9999]].", slugs).unknown[0] === "tx-2026-9999");
ok("prose with no citation passes", checkCitations("No filings are listed.", slugs).ok);

// ---------------------------------------------------------------- verdict
head("D. the verdict gate, which is the one that does not bend");
for (const s of [
  "The grid will hold through the summer.",
  "There is enough capacity to serve the forecast peak.",
  "ERCOT is safe this week.",
  "Expect rolling outages in August.",
  "There is no risk of a shortfall.",
  "Texans will be fine.",
  "A blackout is unlikely.",
  "The reservoirs will recover by spring.",
  "The rule will be approved.",
  "All clear on reserves.",
]) {
  ok(`refused: ${s}`, !checkVerdict(s).ok, JSON.stringify(checkVerdict(s)));
}

head("E. and it must NOT block its own correct refusal");
// The failure mode this half exists for. Each of these contains the words of the call it is
// declining to make, so a naive guard eats exactly the sentence the box should be writing.
for (const s of [
  "The record doesn't say whether there will be enough capacity.",
  "The record can't tell you whether the grid will hold.",
  "No one publishes a forecast of whether reserves are adequate.",
  "There is no public prediction of a shortfall.",
  "The docket doesn't state whether the rule will be approved.",
  "Per site large load metering is confidential, so the record doesn't answer that.",
  "Measured peak load was 87648.5 MW, and the record makes no call beyond that.",
]) {
  ok(`allowed: ${s}`, checkVerdict(s).ok, JSON.stringify(checkVerdict(s)));
}

// ---------------------------------------------------------------- voice
head("F. first person, banned in published copy");
for (const s of ["I think the filing is open.", "We track 58 decisions.",
                 "Let me pull that up.", "That is our record."]) {
  ok(`refused: ${s}`, !checkVoice(s).ok, JSON.stringify(checkVoice(s)));
}
head("G. and it must not fire inside an ordinary word");
// This record is mostly about the weather, so "we" inside a word is not hypothetical.
for (const s of [
  "The weather station recorded a maximum of 104 degrees.",
  "However, the comment window has closed.",
  "Power and the grid is the topic.",
  "The lower reservoir is at 44.77 percent.",
  "Owners were notified.",
  "Somewhere between the two filings.",
  // The three that a lazy apostrophe would have eaten.
  "The comment period was well attended.",
  "They wed the two dockets into one project.",
  "Filings were accepted through August 11th, 2026.",
  // And the country, which is not the first person plural.
  "The US Army Corps of Engineers is the decider.",
]) {
  ok(`allowed: ${s}`, checkVoice(s).ok, JSON.stringify(checkVoice(s)));
}
ok("a quoted source may say we",
  checkVoice('The filing says "we are aligned with the thought".').ok,
  JSON.stringify(checkVoice('The filing says "we are aligned with the thought".')));

// ---------------------------------------------------------------- punctuation
head("H. punctuation is repaired, never refused");
ok("a colon becomes a comma",
  plainly("The status is this: pending.") === "The status is this, pending.",
  plainly("The status is this: pending."));
ok("a clock time keeps its colon",
  plainly("The meeting is at 9:15 tomorrow.").includes("9:15"),
  plainly("The meeting is at 9:15 tomorrow."));
ok("a semicolon becomes a full stop and a capital",
  plainly("It filed; the window closed.") === "It filed. The window closed.",
  plainly("It filed; the window closed."));
ok("an em dash becomes a comma",
  !plainly("The rule — filed in July — is pending.").includes("—"));
ok("a dash between numbers stays a range, both numbers intact",
  plainly("The 2024–2025 window").includes("2024-2025"),
  plainly("The 2024–2025 window"));
ok("cannot becomes can't", plainly("The record cannot say.") === "The record can't say.",
  plainly("The record cannot say."));
ok("curly quotes are straightened", !plainly("the “filing”").includes("“"));
ok("throat clearing is dropped and the sentence keeps its capital",
  plainly("Great question! The window closed.") === "The window closed.",
  plainly("Great question! The window closed."));
ok("a sentence may not open with And",
  plainly("And the window closed.") === "The window closed.",
  plainly("And the window closed."));
ok("a sentence may not open with But",
  plainly("But the window closed.") === "The window closed.",
  plainly("But the window closed."));

head("I. nothing in the repair may touch a figure");
// The one rule that goes near digits is the range. Everything else must leave numbers alone,
// because this file's entire job is that a published figure is the one the record holds.
for (const s of ["Peak load reached 87,648.5 MW at hour ending 17.",
                 "Storage was 24,142,425 acre feet, 76.5 percent full.",
                 "The load factor was 0.8469."]) {
  const before = numerals(s).join(",");
  const after = numerals(plainly(s)).join(",");
  ok(`figures survive the repair: ${s.slice(0, 40)}`, before === after,
    `${before} -> ${after}`);
}

// ---------------------------------------------------------------- composite
head("J. the composite, in the order a failure should be reported");
const ctx = { allowed: new Set(["87648.5", "58", "2026", "1"]), slugs };
ok("a clean sentence passes",
  checkSentence("Peak load reached 87648.5 MW, per [[tx-2026-0001]].", ctx).ok,
  JSON.stringify(checkSentence("Peak load reached 87648.5 MW, per [[tx-2026-0001]].", ctx)));
ok("a bad citation is reported as citation, not as numeral",
  checkSentence("See [[tx-2026-9999]] for 87648.5 MW.", ctx).reason === "citation");
ok("a bad figure is reported as numeral",
  checkSentence("Peak load reached 99999.1 MW.", ctx).reason === "numeral");
ok("first person is reported as voice",
  checkSentence("We track 58 decisions.", ctx).reason === "voice");
ok("a verdict is reported as verdict",
  checkSentence("The grid will hold.", ctx).reason === "verdict");

head("K. streaming splits on sentences and holds the remainder");
const s1 = splitSentences("The window closed. Peak was 87648.5 MW. Want the");
ok("complete sentences come out", s1.sentences.length === 2, JSON.stringify(s1.sentences));
ok("the partial one is held back", s1.remainder === "Want the", JSON.stringify(s1.remainder));
ok("repair happens before the split, so what is checked is what is sent",
  splitSentences("It filed; the window closed. Next").sentences[0] === "It filed.",
  JSON.stringify(splitSentences("It filed; the window closed. Next")));

console.log("");
console.log(fail === 0 ? `checks clean, ${pass} assertions`
                       : `checks FAILED, ${fail} of ${pass + fail}`);
process.exit(fail ? 1 : 0);
