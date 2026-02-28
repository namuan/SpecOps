#!/usr/bin/env node

const path = require("path");
const {
  applyTemplate,
  parseArgs,
  readJson,
  readText,
  writeText,
} = require("../utils/io");

function usage() {
  process.stderr.write(
    "Usage: node generate_jest.js --spec <compiled-spec.json> --out <output.test.js> [--template <template-path>]\n",
  );
}

function sanitizeTestTitle(value) {
  return String(value).replace(/"/g, "'");
}

function indent(text, count = 2) {
  const prefix = " ".repeat(count);
  return text
    .split("\n")
    .map((line) => `${prefix}${line}`)
    .join("\n");
}

function scenarioToTestBlock(scenario) {
  const title = sanitizeTestTitle(`${scenario.id} ${scenario.description}`);
  const serializedScenario = JSON.stringify(
    {
      given: scenario.given,
      when: scenario.when,
      then: scenario.then,
    },
    null,
    2,
  );

  return [
    `test("${title}", async () => {`,
    indent(`const scenario = ${serializedScenario};`, 2),
    indent(
      `throw new Error("SpecOps generated failing test for ${scenario.id}: implement behavior to satisfy compiled spec.");`,
      2,
    ),
    "});",
  ].join("\n");
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const specPath = args.spec;
  const outPath = args.out;
  const templatePath =
    args.template ||
    path.resolve(__dirname, "../../templates/jest.test.template");

  if (!specPath || !outPath) {
    usage();
    process.exit(1);
  }

  const spec = readJson(specPath);

  if (!Array.isArray(spec.scenarios) || spec.scenarios.length === 0) {
    throw new Error("Compiled spec must include a non-empty scenarios array.");
  }

  const testCases = spec.scenarios.map(scenarioToTestBlock).map((block) => indent(block)).join("\n\n");
  const template = readText(templatePath);
  const rendered = applyTemplate(template, {
    FEATURE_NAME: spec.featureName,
    GENERATED_AT: new Date().toISOString(),
    TEST_CASES: testCases,
  });

  const outputFile = writeText(outPath, rendered);
  process.stdout.write(`Generated Jest tests: ${outputFile}\n`);
}

main();