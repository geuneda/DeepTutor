import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";

const INIT = path.resolve(process.cwd(), "i18n/init.ts");
const APPEARANCE = path.resolve(
  process.cwd(),
  "app/(utility)/settings/appearance/page.tsx",
);
const TOOLS = path.resolve(process.cwd(), "app/(utility)/settings/tools/page.tsx");
const QUIZ_JUDGE = path.resolve(process.cwd(), "lib/quiz-judge.ts");
const QUIZ_VIEWER = path.resolve(process.cwd(), "components/quiz/QuizViewer.tsx");

// Read the bundles instead of importing them: an import would make tsc emit a
// copy of locales/ under dist/node-tests, which the sibling suites mistake for
// the web root when they walk up from __dirname.
function locale(name: string): Record<string, string> {
  return JSON.parse(
    fs.readFileSync(
      path.resolve(process.cwd(), "locales", name, "app.json"),
      "utf8",
    ),
  ) as Record<string, string>;
}

test("the Korean bundle covers every English key", () => {
  const en = locale("en");
  const ko = locale("ko");

  const missing = Object.keys(en).filter((key) => !(key in ko));
  assert.deepEqual(missing, []);
  assert.equal(Object.keys(ko).length, Object.keys(en).length);
});

test("Korean copy is actually translated, not copied from English", () => {
  const en = locale("en");
  const ko = locale("ko");

  // Brand names, code identifiers and pure-placeholder strings legitimately
  // stay identical; anything more than a handful means a chunk went untouched.
  const identical = Object.keys(en).filter((key) => en[key] === ko[key]);
  assert.ok(
    identical.length < 60,
    `Too many Korean values match English verbatim: ${identical.length}`,
  );

  assert.equal(ko["Settings"], "설정");
  assert.equal(ko["language.korean"], "한국어");
});

test("i18next loads the Korean bundle on demand", () => {
  const source = fs.readFileSync(INIT, "utf8");

  assert.match(source, /AppLanguage = "en" \| "zh" \| "ko"/);
  assert.match(source, /s === "ko" \|\| s === "kr" \|\| s === "korean"/);
  assert.match(source, /import\("@\/locales\/ko\/app\.json"\)/);
  assert.match(source, /addResourceBundle\("ko", "app"/);
});

test("the appearance page offers Korean as an interface language", () => {
  const source = fs.readFileSync(APPEARANCE, "utf8");

  assert.match(source, /\["en", "zh", "ko"\] as const\)\.map\(\(v\)/);
  assert.match(source, /t\("language\.korean"\)/);
});

test("tool hints are read per interface locale, not collapsed onto English", () => {
  const source = fs.readFileSync(TOOLS, "utf8");

  // The backend ships a hint bundle for every interface locale now, so the
  // page must index by the active language instead of branching on Chinese.
  assert.match(source, /hints: Record<AppLanguage, ToolHints>/);
  assert.match(source, /tool\.hints\[language\] \?\? tool\.hints\.en/);
  assert.doesNotMatch(source, /language === "zh" \? tool\.hints\.zh/);
});

test("the quiz judge is asked for the reader's own locale", () => {
  const judge = fs.readFileSync(QUIZ_JUDGE, "utf8");
  const viewer = fs.readFileSync(QUIZ_VIEWER, "utf8");

  assert.match(judge, /language: "zh" \| "en" \| "ko"/);
  // The prop is a free-form string, so it has to be normalized rather than
  // narrowed to English for everything that is not Chinese.
  assert.match(viewer, /language: normalizeLanguage\(language\)/);
  assert.doesNotMatch(viewer, /judgeLanguage/);
});
