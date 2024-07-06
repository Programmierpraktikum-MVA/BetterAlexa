const { execSync, spawn } = require("node:child_process");
const argv = process.argv.slice(2);
if (argv.length < 1) {
  console.log("Usage: node start.js <script>");
  process.exit(1);
}
function spawnProcess(command, args) {
  return spawn(command, args, { stdio: "inherit" }).on(
    "exit",
    function (exitCode, signal) {
      if (typeof exitCode === "number") {
        process.exit(exitCode);
      } else {
        process.kill(process.pid, signal);
      }
    },
  );
}
try {
  execSync("python3 -V");
  spawnProcess("python3", argv);
} catch {
  spawnProcess("python", argv);
}
