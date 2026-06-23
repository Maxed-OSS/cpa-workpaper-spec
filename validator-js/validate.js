"use strict";
/**
 * CPA Workpaper Spec validator (JavaScript / Ajv).
 *
 * A parallel implementation of the Python validator so JavaScript and Node
 * teams can target the exact same JSON Schemas. It loads every schema in
 * `schema/v0.1/`, registers each under both its published `$id` and its bare
 * filename so cross-file `$ref`s resolve fully offline, and validates a
 * document against a named schema.
 *
 * This module is dependency-light: it only needs `ajv` and `ajv-formats`.
 */
const fs = require("fs");
const path = require("path");

const Ajv2020 = require("ajv/dist/2020");
const addFormats = require("ajv-formats");

const REPO_ROOT = path.resolve(__dirname, "..");
const SCHEMA_DIR = path.join(REPO_ROOT, "schema", "v0.1");
const EXAMPLE_DIR = path.join(REPO_ROOT, "examples", "v0.1");
const SCHEMA_SUFFIX = ".schema.json";

// Examples are paired with the schema they should validate against. Kept in
// sync with the Python validator's EXAMPLE_TO_SCHEMA map.
const EXAMPLE_TO_SCHEMA = {
  "engagement.example.json": "engagement",
  "close-checklist.example.json": "close-checklist",
  "tax-prep.example.json": "tax-prep",
  "engagement-letter.example.json": "engagement-letter",
  "request-list-item.example.json": "request-list-item",
  "workpaper.example.json": "workpaper",
};

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf-8"));
}

/** Load every schema file in the schema dir, keyed by schema name. */
function loadSchemas(schemaDir = SCHEMA_DIR) {
  const schemas = {};
  for (const file of fs.readdirSync(schemaDir).sort()) {
    if (!file.endsWith(SCHEMA_SUFFIX)) continue;
    const name = file.slice(0, -SCHEMA_SUFFIX.length);
    schemas[name] = readJson(path.join(schemaDir, file));
  }
  return schemas;
}

/**
 * Build an Ajv instance with every schema registered under both its `$id`
 * and its bare filename, so relative `$ref`s such as
 * `common.schema.json#/$defs/money` resolve fully offline.
 */
function buildAjv(schemas) {
  const ajv = new Ajv2020({
    strict: false, // the spec uses annotation keywords Ajv strict-mode warns on
    allErrors: true,
    allowUnionTypes: true,
  });
  addFormats(ajv);

  for (const [name, schema] of Object.entries(schemas)) {
    const filename = `${name}${SCHEMA_SUFFIX}`;
    // Register under the published $id (Ajv reads it from the schema content).
    // Relative cross-file $refs resolve against the referrer's $id base, so this
    // is what makes refs like common.schema.json#/$defs/money resolve when the
    // referrer's own $id is the full https URL.
    ajv.addSchema(schema);
    // Also alias under the bare filename so a $ref by plain filename resolves,
    // and so the CLI/validateDocument can look the schema up by name.
    if (!ajv.getSchema(filename)) {
      ajv.addSchema(schema, filename);
    }
  }
  return ajv;
}

function listSchemaNames(schemas) {
  return Object.keys(schemas).sort();
}

/**
 * Validate a document against a named schema.
 * Returns an array of human-readable error strings (empty == valid).
 */
function validateDocument(document, schemaName, schemas, ajv) {
  if (!Object.prototype.hasOwnProperty.call(schemas, schemaName)) {
    return [
      `unknown schema '${schemaName}'. known schemas: ${listSchemaNames(
        schemas
      ).join(", ")}`,
    ];
  }
  const filename = `${schemaName}${SCHEMA_SUFFIX}`;
  const validate = ajv.getSchema(filename) || ajv.compile(schemas[schemaName]);
  const ok = validate(document);
  if (ok) return [];
  const errors = (validate.errors || [])
    .slice()
    .sort((a, b) => a.instancePath.localeCompare(b.instancePath));
  return errors.map((err) => {
    const location = err.instancePath ? err.instancePath.replace(/^\//, "") : "<root>";
    return `  at ${location || "<root>"}: ${err.message}`;
  });
}

module.exports = {
  REPO_ROOT,
  SCHEMA_DIR,
  EXAMPLE_DIR,
  SCHEMA_SUFFIX,
  EXAMPLE_TO_SCHEMA,
  readJson,
  loadSchemas,
  buildAjv,
  listSchemaNames,
  validateDocument,
};
