import type { ArxivCategory } from "@/lib/api/types";

import { Badge } from "@/components/ui/badge";

const categoryToneMap: Record<ArxivCategory, React.ComponentProps<typeof Badge>["variant"]> = {
  "cs.AI": "default",
  "cs.CL": "info",
  "cs.CV": "warning",
  "cs.IR": "outline",
  "cs.LG": "secondary",
  "cs.RO": "success",
  "stat.ML": "secondary",
};

export function CategoryTag({ category }: { category: ArxivCategory }) {
  return (
    <Badge variant={categoryToneMap[category]} className="font-medium">
      {category}
    </Badge>
  );
}
