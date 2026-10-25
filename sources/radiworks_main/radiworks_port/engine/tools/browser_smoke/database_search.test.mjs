import test from "node:test";
import assert from "node:assert/strict";
import { filterDatabaseNames } from "../../../webapp/js/views/database_search.js";

const names = ["ESSENCES_BACHFLOWERS_RATES", "HOMEOPATHY_Clarke", "CHEMISTRY_Elements"];
const groups = [["ESSENCES_", "Essenzen"], ["HOMEOPATHY_", "Homöopathie"]];

test("database search is local and searches names and displayed group labels", () => {
  assert.deepEqual(filterDatabaseNames(names, groups, ""), names);
  assert.deepEqual(filterDatabaseNames(names, groups, "clarke"), ["HOMEOPATHY_Clarke"]);
  assert.deepEqual(filterDatabaseNames(names, groups, "Essenzen"), ["ESSENCES_BACHFLOWERS_RATES"]);
  assert.deepEqual(filterDatabaseNames(names, groups, "unbekannt"), []);
});
