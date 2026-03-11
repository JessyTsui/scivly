import { test, expect } from "@playwright/test";

test.describe("Public pages smoke tests", () => {
  test("landing page loads", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/Scivly/i);
    await expect(page.locator("body")).toBeVisible();
  });

  test("pricing page loads", async ({ page }) => {
    await page.goto("/pricing");
    await expect(page.locator("body")).toBeVisible();
    // Should have pricing-related content
    await expect(page.getByText(/free|pro|pricing/i).first()).toBeVisible();
  });

  test("public papers page loads", async ({ page }) => {
    await page.goto("/papers");
    await expect(page.locator("body")).toBeVisible();
    // Should have paper library heading or search
    await expect(page.getByText(/paper|library|search/i).first()).toBeVisible();
  });

  test("docs page loads", async ({ page }) => {
    await page.goto("/docs");
    await expect(page.locator("body")).toBeVisible();
  });
});

test.describe("Navigation smoke tests", () => {
  test("landing page has nav links", async ({ page }) => {
    await page.goto("/");
    // Check for common navigation elements
    const nav = page.locator("nav, header");
    await expect(nav.first()).toBeVisible();
  });

  test("pricing page has plan cards", async ({ page }) => {
    await page.goto("/pricing");
    // Should have at least one plan/card element
    const cards = page.locator('[class*="card"], [class*="plan"], [class*="pricing"]');
    await expect(cards.first()).toBeVisible();
  });
});
