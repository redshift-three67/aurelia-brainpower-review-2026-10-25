const { defineConfig } = require('@playwright/test');

const executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE || undefined;
const baseURL = process.env.PLAYWRIGHT_BASE_URL || 'http://127.0.0.1:8765';
const lowMemoryArgs = [
  '--disable-background-networking',
  '--disable-component-update',
  '--disable-extensions',
  '--disable-gpu',
  '--no-zygote',
  '--no-first-run',
];

module.exports = defineConfig({
  testDir: '.',
  timeout: 30000,
  retries: 0,
  workers: 1,
  reporter: 'line',
  use: {
    baseURL,
    headless: true,
    launchOptions: {executablePath, args: lowMemoryArgs},
  },
});
