#!/usr/bin/env node
"use strict";
/**
 * CLI for the JavaScript / Ajv validator. Mirrors the Python CLI:
 *
 *   cpa-workpaper-validate <document.json> --schema <schema-name>
 *   cpa-workpaper-validate --all                 # validate every bundled example
 *   cpa-workpaper-validate --list-schemas
 *
 * Exit code is 0 when every requested validation passes, 1 otherwise.
 */
const fs = require("fs");
const path = require("path");

const {
  EXAMPLE_DIR,
  EXAMPLE_TO_SCHEMA,
  readJson,
  loadSchemas,
  buildAjv,
  listSchemaNames,
  validateDocument,
} = require("./validate");

function printResult(label, errors) {
  if (errors.length) {
    console.log(`FAIL  ${label}`);
    for (const line of errors) console.log(line);
  } else {
    console.log(`OK    ${label}`);
  }
}

function parseArgs(argv) {
  const args = { document: null, schema: null, all: false, listSchemas: false };
  for (let i = 0; i < argv.length; i += 1) {
    const a = argv[i];
    if (a === "--all") args.all = true;
    else if (a === "--list-schemas") args.listSchemas = true;
    else if (a === "--schema") {
      args.schema = argv[i + 1];
      i += 1;
    } else if (!a.startsWith("-") && args.document === null) {
      args.document = a;
    }
  }
  return args;
}

function main(argv) {
  const args = parseArgs(argv);
  const schemas = loadSchemas();
  const ajv = buildAjv(schemas);

  if (args.listSchemas) {
    for (const name of listSchemaNames(schemas)) console.log(name);
    return 0;
  }

  if (args.all) {
    let rc = 0;
    for (const [exampleName, schemaName] of Object.entries(EXAMPLE_TO_SCHEMA)) {
      const p = path.join(EXAMPLE_DIR, exampleName);
      if (!fs.existsSync(p)) {
        console.log(`FAIL  ${exampleName} (missing example file)`);
        rc = 1;
        continue;
      }
      const errors = validateDocument(readJson(p), schemaName, schemas, ajv);
      printResult(`${exampleName} against '${schemaName}'`, errors);
      if (errors.length) rc = 1;
    }
    return rc;
  }

  if (!args.document || !args.schema) {
    process.stderr.write(
      "error: provide a document and --schema, or use --all / --list-schemas\n"
    );
    return 2;
  }

  if (!fs.existsSync(args.document)) {
    process.stderr.write(`error: document not found: ${args.document}\n`);
    return 1;
  }
  const errors = validateDocument(readJson(args.document), args.schema, schemas, ajv);
  printResult(`${path.basename(args.document)} against '${args.schema}'`, errors);
  return errors.length ? 1 : 0;
}

if (require.main === module) {
  process.exit(main(process.argv.slice(2)));
}

module.exports = { main };
