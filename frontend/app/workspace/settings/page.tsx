"use client";

import { CreditCard, KeyRound, Webhook } from "lucide-react";

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ApiKeySettingsPanel } from "@/components/workspace/ApiKeySettingsPanel";
import { BillingSettingsPanel } from "@/components/workspace/billing-settings-panel";
import { WebhookSettingsPanel } from "@/components/workspace/WebhookSettingsPanel";

export default function WorkspaceSettingsPage() {
  return (
    <div className="space-y-6">
      <section className="rounded-[28px] border border-[var(--border)] bg-[var(--surface)]/86 p-6">
        <p className="text-sm font-semibold uppercase tracking-[0.22em] text-[var(--foreground-subtle)]">
          Workspace settings
        </p>
        <h1 className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
          Secure the APIs your workspace exposes.
        </h1>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-[var(--foreground-muted)]">
          Manage human-issued API keys and outbound webhooks in one place. Both surfaces are
          scoped to the current workspace and follow the same delivery, audit, and auth
          conventions.
        </p>
      </section>

      <Tabs defaultValue="api-keys">
        <TabsList className="w-full justify-start overflow-x-auto rounded-[20px] border border-[var(--border)] bg-[var(--surface)]/84 p-1">
          <TabsTrigger value="api-keys" className="gap-2">
            <KeyRound className="size-4" />
            API Keys
          </TabsTrigger>
          <TabsTrigger value="webhooks" className="gap-2">
            <Webhook className="size-4" />
            Webhooks
          </TabsTrigger>
          <TabsTrigger value="billing" className="gap-2">
            <CreditCard className="size-4" />
            Billing
          </TabsTrigger>
        </TabsList>

        <TabsContent value="api-keys">
          <ApiKeySettingsPanel />
        </TabsContent>

        <TabsContent value="webhooks">
          <WebhookSettingsPanel />
        </TabsContent>

        <TabsContent value="billing">
          <BillingSettingsPanel />
        </TabsContent>
      </Tabs>
    </div>
  );
}
