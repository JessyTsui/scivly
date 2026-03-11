"use client";

import { Bell, ChevronRight, Globe, Key, Palette, Shield, User } from "lucide-react";
import Link from "next/link";

const settingsSections = [
  {
    icon: User,
    title: "Account",
    description: "Manage your profile and preferences",
    href: "#",
  },
  {
    icon: Bell,
    title: "Notifications",
    description: "Configure email and push notifications",
    href: "#",
  },
  {
    icon: Globe,
    title: "Language & Region",
    description: "Set your language and timezone",
    href: "#",
  },
  {
    icon: Key,
    title: "API Keys",
    description: "Manage API access tokens",
    href: "#",
  },
  {
    icon: Shield,
    title: "Security",
    description: "Password and authentication settings",
    href: "#",
  },
  {
    icon: Palette,
    title: "Appearance",
    description: "Theme and display preferences",
    href: "#",
  },
];

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="font-[family:var(--font-display)] text-2xl font-semibold">
          Settings
        </h2>
        <p className="text-sm text-[var(--foreground-muted)]">
          Manage your account and preferences
        </p>
      </div>

      {/* Settings Sections */}
      <div className="space-y-3">
        {settingsSections.map((section) => {
          const Icon = section.icon;
          return (
            <Link
              key={section.title}
              href={section.href}
              className="flex items-center justify-between rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4 hover:bg-[var(--surface-hover)]"
            >
              <div className="flex items-center gap-4">
                <div className="rounded-lg bg-[var(--primary-subtle)] p-2">
                  <Icon className="h-5 w-5 text-[var(--primary)]" />
                </div>
                <div>
                  <p className="font-medium">{section.title}</p>
                  <p className="text-sm text-[var(--foreground-muted)]">
                    {section.description}
                  </p>
                </div>
              </div>
              <ChevronRight className="h-5 w-5 text-[var(--foreground-subtle)]" />
            </Link>
          );
        })}
      </div>

      {/* Quick Settings */}
      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-5">
        <h3 className="font-medium mb-4">Quick Settings</h3>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Email Notifications</p>
              <p className="text-xs text-[var(--foreground-muted)]">
                Receive daily digest emails
              </p>
            </div>
            <label className="relative inline-flex cursor-pointer items-center">
              <input type="checkbox" className="peer sr-only" defaultChecked />
              <div className="h-6 w-11 rounded-full bg-[var(--border)] peer-checked:bg-[var(--primary)] peer-focus:ring-2 peer-focus:ring-[var(--primary)]/30" />
              <div className="absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white transition-transform peer-checked:translate-x-5" />
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Auto-translate</p>
              <p className="text-xs text-[var(--foreground-muted)]">
                Automatically translate papers to English
              </p>
            </div>
            <label className="relative inline-flex cursor-pointer items-center">
              <input type="checkbox" className="peer sr-only" defaultChecked />
              <div className="h-6 w-11 rounded-full bg-[var(--border)] peer-checked:bg-[var(--primary)] peer-focus:ring-2 peer-focus:ring-[var(--primary)]/30" />
              <div className="absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white transition-transform peer-checked:translate-x-5" />
            </label>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Public Profile</p>
              <p className="text-xs text-[var(--foreground-muted)]">
                Make your research profile public
              </p>
            </div>
            <label className="relative inline-flex cursor-pointer items-center">
              <input type="checkbox" className="peer sr-only" />
              <div className="h-6 w-11 rounded-full bg-[var(--border)] peer-checked:bg-[var(--primary)] peer-focus:ring-2 peer-focus:ring-[var(--primary)]/30" />
              <div className="absolute left-0.5 top-0.5 h-5 w-5 rounded-full bg-white transition-transform peer-checked:translate-x-5" />
            </label>
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-5">
        <h3 className="font-medium text-red-500 mb-4">Danger Zone</h3>

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Clear All Data</p>
              <p className="text-xs text-[var(--foreground-muted)]">
                Delete all papers and digests
              </p>
            </div>
            <button className="rounded-lg border border-red-500/50 px-4 py-2 text-sm text-red-500 hover:bg-red-500/10">
              Clear Data
            </button>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Delete Account</p>
              <p className="text-xs text-[var(--foreground-muted)]">
                Permanently delete your account
              </p>
            </div>
            <button className="rounded-lg border border-red-500/50 px-4 py-2 text-sm text-red-500 hover:bg-red-500/10">
              Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
