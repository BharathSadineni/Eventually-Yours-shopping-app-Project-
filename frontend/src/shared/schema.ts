import { z } from "zod";

export const insertShoppingQuerySchema = z.object({
  occasion: z.string().min(1, "Occasion is required"),
  brandsPreferred: z.string().optional(),
  shoppingInput: z.string().optional(),
});

export const insertUserProfileSchema = z.object({
  age: z.number().int().positive().optional(),
  gender: z.string().optional(),
  categories: z.array(z.string()).min(1, "Please select at least one category"),
  interests: z.string().optional(),
  location: z.string().optional(),
  budgetMin: z.number().optional(),
  budgetMax: z.number().optional(),
});
