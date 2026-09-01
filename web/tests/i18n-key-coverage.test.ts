import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import ts from "typescript";

// Two ways a string escapes translation in this app, both found by play-testing
// the Korean UI: a `t("…")` call whose key no locale defines (i18next echoes the
// key, so the English source renders), and a hand-rolled `{zh, en}` pair that
// only those two locales can ever reach.

const WEB = process.cwd();
const SKIP = new Set(["node_modules", ".next", "dist", "tests", "scripts", "locales", "eslint"]);
const SOURCE_ROOTS = ["app", "components", "lib", "hooks", "context", "i18n"];

function listSources(dir: string): string[] {
  const out: string[] = [];
  if (!fs.existsSync(dir)) return out;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (SKIP.has(entry.name) || entry.name.startsWith(".")) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...listSources(full));
    else if (/\.tsx?$/.test(entry.name)) out.push(full);
  }
  return out;
}

const sources = SOURCE_ROOTS.flatMap((root) => listSources(path.join(WEB, root)));

const en = JSON.parse(
  fs.readFileSync(path.join(WEB, "locales/en/app.json"), "utf8"),
) as Record<string, string>;

test("every source directory we scan actually exists", () => {
  assert.ok(sources.length > 200, `only found ${sources.length} sources`);
});

test("every literal t() key is defined in the English locale", () => {
  // `t("…")`, but not `setDraft("")` — the lookbehind drops identifiers that
  // merely end in `t`.
  const call = /(?<![\w$])t\(\s*"((?:[^"\\]|\\.)+)"/g;
  const missing = new Set<string>();

  for (const file of sources) {
    const src = fs.readFileSync(file, "utf8");
    for (const match of src.matchAll(call)) {
      let key: string;
      try {
        key = JSON.parse(`"${match[1]}"`) as string;
      } catch {
        continue;
      }
      // i18next resolves a plural base key through its _one / _other forms.
      if (key in en || `${key}_one` in en || `${key}_other` in en) continue;
      missing.add(key);
    }
  }

  assert.deepEqual(
    [...missing].sort(),
    [],
    "these keys render as their English source in every translated locale",
  );
});

test("non-Chinese interface languages are not collapsed to English", () => {
  const collapsed = /startsWith\(["']zh["']\)\s*\?\s*["']zh["']\s*:\s*["']en["']/s;
  const offenders = sources
    .filter((file) => collapsed.test(fs.readFileSync(file, "utf8")))
    .map((file) => path.relative(WEB, file));

  assert.deepEqual(offenders, []);
});

test("hand-rolled locale objects include Korean", () => {
  // Older features used `{ zh, en }` or `{ cn, en }` objects instead of i18next.
  // If one remains, Korean silently falls through to English. Three-language
  // objects are allowed for feature-local dynamic copy that cannot be a key.
  const offenders = new Set<string>();

  for (const file of sources) {
    const source = fs.readFileSync(file, "utf8");
    const tree = ts.createSourceFile(
      file,
      source,
      ts.ScriptTarget.Latest,
      true,
      file.endsWith(".tsx") ? ts.ScriptKind.TSX : ts.ScriptKind.TS,
    );

    const visit = (node: ts.Node) => {
      if (ts.isObjectLiteralExpression(node)) {
        const names = new Set(
          node.properties.flatMap((property) => {
            if (!ts.isPropertyAssignment(property)) return [];
            const name = property.name;
            if (ts.isIdentifier(name) || ts.isStringLiteral(name)) {
              return [name.text];
            }
            return [];
          }),
        );
        if (
          (names.has("zh") || names.has("cn")) &&
          names.has("en") &&
          !names.has("ko")
        ) {
          offenders.add(path.relative(WEB, file));
        }
      }
      ts.forEachChild(node, visit);
    };

    visit(tree);
  }

  assert.deepEqual([...offenders].sort(), []);
});
