/**
 * Dev launcher — runs the Realtime Radar (WS) server + `next dev` together,
 * cross-platform, with clean shutdown on Ctrl+C.
 *
 *   node server/dev.js
 */

"use strict";

const { spawn } = require("child_process");

const children = [];

function run(command, args, name) {
  const child = spawn(command, args, {
    stdio: "inherit",
    shell: true,
    env: process.env,
  });
  child.on("exit", (code, signal) => {
    console.log(`[dev] ${name} exited (code=${code}, signal=${signal})`);
  });
  children.push(child);
  return child;
}

run("node", ["server/realtime.js"], "realtime");
run("npx", ["next", "dev"], "next");

function shutdown() {
  console.log("\n[dev] encerrando (realtime + next)…");
  for (const c of children) {
    try { c.kill("SIGTERM"); } catch (_) {}
  }
  setTimeout(() => process.exit(0), 500);
}

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);
