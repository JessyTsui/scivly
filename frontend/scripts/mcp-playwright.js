#!/usr/bin/env node
/**
 * MCP Server for Playwright - Screenshot functionality
 * This implements the Model Context Protocol for browser automation
 */

const { chromium } = require('playwright');
const readline = require('readline');

class PlaywrightMcpServer {
  constructor() {
    this.browser = null;
    this.context = null;
    this.page = null;
  }

  async initialize() {
    this.browser = await chromium.launch({ headless: true });
    this.context = await this.browser.newContext({
      viewport: { width: 1440, height: 900 },
      deviceScaleFactor: 2,
    });
  }

  async shutdown() {
    if (this.browser) {
      await this.browser.close();
    }
  }

  async handleRequest(request) {
    const { method, params, id } = request;

    try {
      switch (method) {
        case 'screenshot': {
          const { url, fullPage = true, waitForSelector } = params;

          if (!this.page) {
            this.page = await this.context.newPage();
          }

          await this.page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });

          if (waitForSelector) {
            await this.page.waitForSelector(waitForSelector, { timeout: 10000 });
          }

          // Wait for fonts and animations
          await this.page.waitForTimeout(1000);

          const screenshot = await this.page.screenshot({
            fullPage,
            type: 'png',
            encoding: 'base64'
          });

          return {
            jsonrpc: '2.0',
            id,
            result: {
              success: true,
              data: screenshot,
              format: 'png',
              encoding: 'base64'
            }
          };
        }

        case 'screenshot_element': {
          const { url, selector, waitForSelector } = params;

          if (!this.page) {
            this.page = await this.context.newPage();
          }

          await this.page.goto(url, { waitUntil: 'networkidle' });

          if (waitForSelector) {
            await this.page.waitForSelector(waitForSelector, { timeout: 10000 });
          }

          const element = await this.page.locator(selector).first();
          const screenshot = await element.screenshot({
            type: 'png',
            encoding: 'base64'
          });

          return {
            jsonrpc: '2.0',
            id,
            result: {
              success: true,
              data: screenshot,
              format: 'png',
              encoding: 'base64'
            }
          };
        }

        case 'capture_site': {
          const { baseUrl, pages } = params;
          const results = [];

          for (const { path, name } of pages) {
            const page = await this.context.newPage();
            const url = `${baseUrl}${path}`;

            try {
              await page.goto(url, { waitUntil: 'networkidle', timeout: 30000 });
              await page.waitForTimeout(1000);

              const screenshot = await page.screenshot({
                fullPage: true,
                type: 'png',
                encoding: 'base64'
              });

              results.push({ name, success: true, data: screenshot });
            } catch (error) {
              results.push({ name, success: false, error: error.message });
            } finally {
              await page.close();
            }
          }

          return {
            jsonrpc: '2.0',
            id,
            result: { success: true, pages: results }
          };
        }

        default:
          return {
            jsonrpc: '2.0',
            id,
            error: {
              code: -32601,
              message: `Method not found: ${method}`
            }
          };
      }
    } catch (error) {
      return {
        jsonrpc: '2.0',
        id,
        error: {
          code: -32000,
          message: error.message
        }
      };
    }
  }
}

// Main entry point
async function main() {
  const server = new PlaywrightMcpServer();
  await server.initialize();

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
  });

  console.log('Playwright MCP Server started');

  for await (const line of rl) {
    try {
      const request = JSON.parse(line);
      const response = await server.handleRequest(request);
      console.log(JSON.stringify(response));
    } catch (error) {
      console.log(JSON.stringify({
        jsonrpc: '2.0',
        id: null,
        error: {
          code: -32700,
          message: 'Parse error'
        }
      }));
    }
  }

  await server.shutdown();
}

main().catch(console.error);
