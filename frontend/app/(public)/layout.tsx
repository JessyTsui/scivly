import type { ReactNode } from "react";

import { MarketingFooter } from "@/components/marketing-footer";
import { MarketingHeader } from "@/components/marketing-header";

export default function PublicLayout({ children }: { children: ReactNode }) {
  return (
    <div className="public-theme min-h-screen">
      <MarketingHeader />
      {children}
      <MarketingFooter />
    </div>
  );
}
