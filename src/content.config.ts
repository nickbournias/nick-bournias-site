import { defineCollection } from "astro:content";
import { glob } from "astro/loaders";
import { z } from "astro/zod";

const insights = defineCollection({
    loader: glob({
        pattern: "**/*.md",
        base: "./src/content/insights",
    }),

    schema: z.object({
        title: z.string(),
        description: z.string(),
        date: z.coerce.date(),
        category: z.string().optional(),
    }),
});

export const collections = {
    insights,
};