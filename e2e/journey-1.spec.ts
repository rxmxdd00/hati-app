import { randomUUID } from "node:crypto";
import { expect, test } from "@playwright/test";

test("adds a shared expense and shows each person’s share", async ({
  page,
}) => {
  const runId = randomUUID();
  const payer = `Alex ${runId}`;
  const secondPerson = `Bea ${runId}`;
  const thirdPerson = `Cam ${runId}`;
  const description = `Groceries ${runId}`;

  await page.goto("/");
  const descriptionInput = page.getByLabel("Description");
  const amountInput = page.getByLabel("Amount (PHP)");
  const addExpenseButton = page.getByRole("button", { name: "Add expense" });

  await addExpenseButton.click();
  expect(
    await descriptionInput.evaluate(
      (input) => (input as HTMLInputElement).validity.valueMissing,
    ),
  ).toBe(true);

  await descriptionInput.fill(description);
  await page.getByLabel("Who paid?").fill(payer);
  await page
    .getByLabel("Who shares it?")
    .fill(`${payer}, ${secondPerson}, ${thirdPerson}`);
  await amountInput.fill("0.00");
  await addExpenseButton.click();
  expect(
    await amountInput.evaluate(
      (input) => (input as HTMLInputElement).validity.rangeUnderflow,
    ),
  ).toBe(true);

  await amountInput.fill("100.00");
  await addExpenseButton.click();
  for (const person of [secondPerson, thirdPerson]) {
    const settlement = page.getByRole("listitem").filter({
      hasText: `${person} owes ${payer} ₱33.33`,
    });
    await expect(settlement).toHaveCount(1);
  }

  const expense = page.getByRole("listitem").filter({ hasText: description });
  await expect(expense).toHaveCount(1);
  await expect(expense).toContainText(`₱100.00 — paid by ${payer}`);
  await expect(expense).toContainText(
    `shared by ${payer}, ${secondPerson}, ${thirdPerson}`,
  );
});
