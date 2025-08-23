import { test, expect } from "@playwright/test";

test("bankruptcies chip+table", async ({ page }) => {
  await page.goto("/chat");
  await page.fill('[data-testid="chat-input"]', "recent bankruptcies in the IT sector (last 3 months)");
  await page.click('[data-testid="chat-send"]');
  await expect(page.getByText("type: bankruptcy")).toBeVisible();
  await expect(page.getByRole("table")).toBeVisible();
});
