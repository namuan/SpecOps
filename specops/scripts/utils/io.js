const fs = require("fs");
const path = require("path");

function parseArgs(argv) {
  const options = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) {
      continue;
    }
    const key = token.slice(2);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) {
      options[key] = true;
      continue;
    }
    options[key] = value;
    index += 1;
  }
  return options;
}

function resolvePath(inputPath) {
  return path.resolve(process.cwd(), inputPath);
}

function readJson(filePath) {
  const absolutePath = resolvePath(filePath);
  const content = fs.readFileSync(absolutePath, "utf8");
  return JSON.parse(content);
}

function readText(filePath) {
  const absolutePath = resolvePath(filePath);
  return fs.readFileSync(absolutePath, "utf8");
}

function ensureDirectoryFor(filePath) {
  const absolutePath = resolvePath(filePath);
  fs.mkdirSync(path.dirname(absolutePath), { recursive: true });
  return absolutePath;
}

function writeText(filePath, content) {
  const absolutePath = ensureDirectoryFor(filePath);
  fs.writeFileSync(absolutePath, content, "utf8");
  return absolutePath;
}

function applyTemplate(template, replacements) {
  return Object.entries(replacements).reduce(
    (acc, [key, value]) => acc.replace(new RegExp(`{{${key}}}`, "g"), String(value)),
    template,
  );
}

module.exports = {
  applyTemplate,
  parseArgs,
  readJson,
  readText,
  resolvePath,
  writeText,
};