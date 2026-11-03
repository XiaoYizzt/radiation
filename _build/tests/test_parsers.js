// Offline parser checks for the CSV/TXT code added to spviewer.js.
// Run with: node _build/test_parsers.js
const fs = require("fs");
const vm = require("vm");

const js = fs.readFileSync("tool/WESViewer/wesviewer/spviewer.js", "utf8");
const start = js.indexOf("function spviewer_strip_bom");
const end = js.indexOf("function find_ev2ch_in_spectrum");
if (start < 0 || end < 0) throw new Error("parser block not found");
const block = js.slice(start, end);

const context = {
  console,
  parse_error_message: "",
  alert: (msg) => console.log("ALERT:", msg),
  $: { each: (obj, fn) => { Object.keys(obj).forEach((k, i) => fn(i, obj[k])); } },
  format_time: (second) => String(second),
  split_line: (data) => {
    const lines = String(data).replace(/\r?\n|\r/g, "\n").split("\n");
    if (lines.length && lines[lines.length - 1] === "") lines.pop();
    return lines;
  },
  format_int: (num, len) => String(num).padStart(len, "0"),
  find_min_count: (data) => {
    let min = 0;
    for (const pair of data) {
      const v = pair[1];
      if ((min === 0 || min > v) && v > 0) min = v;
    }
    return min;
  },
  convert_count2cps: (time, data) => data.map((pair) => [pair[0], pair[1] / time]),
  sp_info_gps: () => [],
};
vm.createContext(context);
vm.runInContext(block, context);

function check(name, cond, detail = "") {
  console.log((cond ? "PASS " : "FAIL ") + name + (detail ? " :: " + detail : ""));
  if (!cond) process.exitCode = 1;
}

const files = [
  ["Ra-226.csv", "CSV", 2500, 13061843],
  ["Am241.txt", "TXT", 4096, 1506411],
];
for (const [file, kind, expected, expectedTotal] of files) {
  const raw = fs.readFileSync("tool/WESViewer/wesviewer/" + file);
  const text = raw.toString("utf8");
  const fn = kind === "CSV" ? context.draw_graph_csv_spectrum : context.draw_graph_txt_spectrum;
  const spectrum = fn(file, "test", text);
  check(file + " parsed", !!spectrum, context.parse_error_message);
  if (!spectrum) continue;
  const ch = spectrum.spectrum_data_ch;
  const ev = spectrum.spectrum_data_ev;
  check(file + " channel count", ch.length === expected, ch.length + " vs " + expected);
  check(file + " energy count", ev.length === expected, ev.length + " vs " + expected);
  check(file + " has_energy", spectrum.has_energy === true, String(spectrum.has_energy));
  check(file + " time", spectrum.time > 0, String(spectrum.time));
  const total = ch.reduce((sum, pair) => sum + pair[1] * spectrum.time, 0);
  check(file + " total counts", Math.abs(total - expectedTotal) < 1, total.toFixed(3) + " vs " + expectedTotal);
  console.log("  first ch/ev/cps:", ch[0], ev[0]);
  console.log("  last  ch/ev/cps:", ch[ch.length - 1], ev[ev.length - 1]);
  console.log("  info rows:", spectrum.sp_info.length);
}

// A counts-only CSV without an energy column must remain channel-only.
const countsOnly = "Counts\n10\n20\n30\n";
const only = context.draw_graph_csv_spectrum("counts.csv", "", countsOnly);
check("counts-only CSV parsed", !!only, context.parse_error_message);
if (only) {
  check("counts-only has no energy", only.has_energy === false, String(only.has_energy));
  check("counts-only channel count", only.spectrum_data_ch.length === 3);
  check("counts-only ev array empty", only.spectrum_data_ev.length === 0);
}

// Headerless one-column counts file.
const headerless = context.draw_graph_csv_spectrum("counts.txt", "", "10\n20\n30\n");
check("headerless counts parsed", !!headerless, context.parse_error_message);
if (headerless) {
  check("headerless counts channel count", headerless.spectrum_data_ch.length === 3);
  check("headerless counts has no energy", headerless.has_energy === false);
}

// Malformed CSV must produce a useful error rather than a spectrum.
context.parse_error_message = "";
const bad = context.draw_graph_csv_spectrum("bad.csv", "", "Channel,Energy,Counts\n0,0,abc\n1,1,2\n");
check("malformed CSV rejected", bad === false, context.parse_error_message);
