"use client";

import { useState } from "react";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { X } from "lucide-react";

import type { ArxivCategory, TopicProfileCreate } from "@/lib/api/types";
import { RESEARCH_CATEGORIES } from "@/lib/api/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

const profileSchema = z.object({
  name: z.string().min(3, "Profile name should be at least 3 characters."),
  description: z.string().min(16, "Add a short description so future digests know what to optimize for."),
  categories: z.array(z.string()).min(1, "Select at least one arXiv category."),
  keywords: z.array(z.string()).min(2, "Add at least two keywords."),
});

type ProfileFormValues = z.infer<typeof profileSchema>;

type ProfileFormProps = {
  defaultValues?: TopicProfileCreate;
  submitLabel?: string;
  busy?: boolean;
  onSubmit: (value: TopicProfileCreate) => Promise<void> | void;
};

export function ProfileForm({
  defaultValues,
  submitLabel = "Save profile",
  busy = false,
  onSubmit,
}: ProfileFormProps) {
  const [keywordInput, setKeywordInput] = useState("");
  const {
    formState: { errors },
    handleSubmit,
    setValue,
    watch,
    register,
  } = useForm<ProfileFormValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      name: defaultValues?.name ?? "",
      description: defaultValues?.description ?? "",
      categories: defaultValues?.categories ?? ["cs.AI"],
      keywords: defaultValues?.keywords ?? [],
    },
  });
  const selectedCategories = watch("categories");
  const selectedKeywords = watch("keywords");

  function toggleCategory(category: ArxivCategory) {
    const next = selectedCategories.includes(category)
      ? selectedCategories.filter((item) => item !== category)
      : [...selectedCategories, category];

    setValue("categories", next, { shouldDirty: true, shouldValidate: true });
  }

  function pushKeyword() {
    const trimmed = keywordInput.trim().toLowerCase();

    if (!trimmed || selectedKeywords.includes(trimmed)) {
      setKeywordInput("");
      return;
    }

    setValue("keywords", [...selectedKeywords, trimmed], {
      shouldDirty: true,
      shouldValidate: true,
    });
    setKeywordInput("");
  }

  function removeKeyword(keyword: string) {
    setValue(
      "keywords",
      selectedKeywords.filter((item) => item !== keyword),
      { shouldDirty: true, shouldValidate: true }
    );
  }

  return (
    <form
      className="space-y-6"
      onSubmit={handleSubmit(async (value) => {
        await onSubmit({
          name: value.name.trim(),
          description: value.description.trim(),
          categories: value.categories as ArxivCategory[],
          keywords: value.keywords,
        });
      })}
    >
      <div className="space-y-2">
        <label htmlFor="profile-name" className="text-sm font-medium text-[var(--foreground)]">
          Profile name
        </label>
        <Input id="profile-name" placeholder="Scientific QA Systems" {...register("name")} />
        {errors.name ? <p className="text-sm text-rose-500">{errors.name.message}</p> : null}
      </div>

      <div className="space-y-2">
        <label htmlFor="profile-description" className="text-sm font-medium text-[var(--foreground)]">
          Description
        </label>
        <Textarea
          id="profile-description"
          placeholder="Describe what this profile should prioritize in daily paper triage."
          {...register("description")}
        />
        {errors.description ? (
          <p className="text-sm text-rose-500">{errors.description.message}</p>
        ) : null}
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-sm font-medium text-[var(--foreground)]">Tracked categories</p>
          <p className="mt-1 text-sm text-[var(--foreground-muted)]">
            Pick the arXiv lanes that should contribute to this profile.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {RESEARCH_CATEGORIES.map((category) => {
            const active = selectedCategories.includes(category);

            return (
              <button
                key={category}
                type="button"
                className={cn(
                  "min-h-11 rounded-full border px-4 text-sm font-medium transition-colors",
                  active
                    ? "border-[var(--primary)]/15 bg-[var(--primary-subtle)] text-[var(--primary)]"
                    : "border-[var(--border)] bg-[var(--surface)] text-[var(--foreground-muted)] hover:border-[var(--border-strong)]"
                )}
                onClick={() => toggleCategory(category)}
              >
                {category}
              </button>
            );
          })}
        </div>
        {errors.categories ? <p className="text-sm text-rose-500">{errors.categories.message}</p> : null}
      </div>

      <div className="space-y-3">
        <div>
          <p className="text-sm font-medium text-[var(--foreground)]">Keywords</p>
          <p className="mt-1 text-sm text-[var(--foreground-muted)]">
            Add task, method, or benchmark names that should strongly influence ranking.
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          <Input
            value={keywordInput}
            placeholder="retrieval, evidence grounding, benchmark"
            onChange={(event) => setKeywordInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" || event.key === ",") {
                event.preventDefault();
                pushKeyword();
              }
            }}
          />
          <Button type="button" variant="secondary" onClick={pushKeyword}>
            Add keyword
          </Button>
        </div>

        <div className="flex flex-wrap gap-2">
          {selectedKeywords.map((keyword) => (
            <span
              key={keyword}
              className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface-hover)] px-3 py-1.5 text-sm text-[var(--foreground)]"
            >
              {keyword}
              <button
                type="button"
                className="text-[var(--foreground-subtle)] hover:text-[var(--foreground)]"
                onClick={() => removeKeyword(keyword)}
                aria-label={`Remove ${keyword}`}
              >
                <X className="size-3.5" />
              </button>
            </span>
          ))}
        </div>
        {errors.keywords ? <p className="text-sm text-rose-500">{errors.keywords.message}</p> : null}
      </div>

      <div className="flex justify-end">
        <Button type="submit" disabled={busy}>
          {busy ? "Saving..." : submitLabel}
        </Button>
      </div>
    </form>
  );
}
