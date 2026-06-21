"use strict";
/**
 * Tests for the JavaScript / Ajv validator. These mirror the Python pytest
 * suite so both validators are held to the same behaviour, plus they run the
 * shared conformance suite (conformance/suite) so the two implementations are
 * proven to agree.
 *
 * Run with:  node --test
 */
const test = require("node:test");
const assert = require("node:assert");
const fs = require("fs");
const path = require("path");

const {
  REPO_ROOT,
  EXAMPLE_DIR,
  EXAMPLE_TO_SCHEMA,
  readJson,
  loadSchemas,
  buildAjv,
  listSchemaNames,
  validateDocument,
} = require("../validate");

const SCHEMAS = loadSchemas();
const AJV = buildAjv(SCHEMAS);

function loadExample(name) {
  return readJson(path.join(EXAMPLE_DIR, name));
}

// ---------------------------------------------------------------------------
// Schema files are well-formed
// ---------------------------------------------------------------------------

test("all schemas declare draft 2020-12", () => {
  for (const [name, schema] of Object.entries(SCHEMAS)) {
    assert.strictEqual(
      schema.$schema,
      "https://json-schema.org/draft/2020-12/schema",
      name
    );
  }
});

test("all schemas have $id and title", () => {
  for (const [name, schema] of Object.entries(SCHEMAS)) {
    assert.ok(schema.$id, `${name} missing $id`);
    assert.ok(schema.title, `${name} missing title`);
  }
});

// ---------------------------------------------------------------------------
// Every bundled example validates against its schema
// ---------------------------------------------------------------------------

for (const [exampleName, schemaName] of Object.entries(EXAMPLE_TO_SCHEMA)) {
  test(`example ${exampleName} validates against '${schemaName}'`, () => {
    const errors = validateDocument(loadExample(exampleName), schemaName, SCHEMAS, AJV);
    assert.deepStrictEqual(errors, [], `${exampleName}:\n${errors.join("\n")}`);
  });
}

test("every entity schema has an example", () => {
  const entitySchemas = new Set(Object.keys(SCHEMAS).filter((n) => n !== "common"));
  const covered = new Set(Object.values(EXAMPLE_TO_SCHEMA));
  assert.deepStrictEqual([...entitySchemas].sort(), [...covered].sort());
});

// ---------------------------------------------------------------------------
// Negative cases: invalid documents are rejected
// ---------------------------------------------------------------------------

test("missing required field fails", () => {
  const doc = loadExample("engagement.example.json");
  delete doc.track;
  assert.ok(validateDocument(doc, "engagement", SCHEMAS, AJV).length);
});

test("unknown property fails under additionalProperties:false", () => {
  const doc = loadExample("engagement.example.json");
  doc.unexpectedField = "nope";
  assert.ok(validateDocument(doc, "engagement", SCHEMAS, AJV).length);
});

test("bad enum value fails", () => {
  const doc = loadExample("tax-prep.example.json");
  doc.currentStage = "totally_made_up_stage";
  assert.ok(validateDocument(doc, "tax-prep", SCHEMAS, AJV).length);
});

test("wrong specVersion fails", () => {
  const doc = loadExample("close-checklist.example.json");
  doc.specVersion = "9.9";
  assert.ok(validateDocument(doc, "close-checklist", SCHEMAS, AJV).length);
});

test("bad money amount format fails", () => {
  const doc = loadExample("engagement-letter.example.json");
  doc.fee.amount.amount = "not-a-number";
  assert.ok(validateDocument(doc, "engagement-letter", SCHEMAS, AJV).length);
});

test("bad currency pattern fails", () => {
  const doc = loadExample("engagement-letter.example.json");
  doc.fee.amount.currency = "dollars";
  assert.ok(validateDocument(doc, "engagement-letter", SCHEMAS, AJV).length);
});

test("unknown schema name reports error", () => {
  const errors = validateDocument(loadExample("engagement.example.json"), "does-not-exist", SCHEMAS, AJV);
  assert.ok(errors.length);
  assert.ok(errors[0].includes("unknown schema"));
});

test("nested open-item bad enum fails (cross-$def)", () => {
  const doc = loadExample("close-checklist.example.json");
  doc.openItems[0].status = "not_a_real_status";
  assert.ok(validateDocument(doc, "close-checklist", SCHEMAS, AJV).length);
});

test("personRef requires name (cross-file $ref to common)", () => {
  const doc = loadExample("engagement.example.json");
  doc.team[0] = { id: "usr_x" };
  assert.ok(validateDocument(doc, "engagement", SCHEMAS, AJV).length);
});

// ---------------------------------------------------------------------------
// Shared conformance suite: both validators must agree on these fixtures
// ---------------------------------------------------------------------------

const MANIFEST = readJson(path.join(REPO_ROOT, "conformance", "manifest.json"));

for (const c of MANIFEST.cases) {
  test(`conformance[valid]: ${c.file}`, { skip: c.expect !== "valid" }, () => {
    const doc = readJson(path.join(REPO_ROOT, "conformance", c.file));
    const errors = validateDocument(doc, c.schema, SCHEMAS, AJV);
    assert.deepStrictEqual(errors, [], `${c.file}:\n${errors.join("\n")}`);
  });
  test(`conformance[invalid]: ${c.file}`, { skip: c.expect !== "invalid" }, () => {
    const doc = readJson(path.join(REPO_ROOT, "conformance", c.file));
    const errors = validateDocument(doc, c.schema, SCHEMAS, AJV);
    assert.ok(errors.length, `${c.file} should have failed validation`);
  });
}

test("listSchemaNames is stable and includes common", () => {
  const names = listSchemaNames(SCHEMAS);
  assert.ok(names.includes("common"));
  assert.ok(names.includes("engagement"));
});
