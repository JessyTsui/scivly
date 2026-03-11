"use client";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BellRing, Plus, Trash2, UserPlus } from "lucide-react";

import {
  addAuthorWatch,
  createProfile,
  getAuthorWatchlist,
  getNotificationChannels,
  getProfiles,
  removeAuthorWatch,
  updateNotificationChannel,
} from "@/lib/api/interests";
import { useScivlySession } from "@/lib/auth/scivly-session";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "@/components/ui/toast";
import { CategoryTag } from "@/components/workspace/CategoryTag";
import { ProfileForm } from "@/components/workspace/ProfileForm";

export default function WorkspaceInterestsPage() {
  const session = useScivlySession();
  const queryClient = useQueryClient();
  const queriesEnabled =
    session.isLoaded &&
    session.isSignedIn &&
    !session.isSyncing &&
    !session.error &&
    Boolean(session.workspace);
  const profilesQuery = useQuery({
    queryKey: ["profiles"],
    queryFn: getProfiles,
    enabled: queriesEnabled,
  });
  const authorsQuery = useQuery({
    queryKey: ["authors"],
    queryFn: getAuthorWatchlist,
    enabled: queriesEnabled,
  });
  const channelsQuery = useQuery({
    queryKey: ["channels"],
    queryFn: getNotificationChannels,
    enabled: queriesEnabled,
  });
  const [dialogOpen, setDialogOpen] = useState(false);
  const [authorName, setAuthorName] = useState("");
  const [authorNotes, setAuthorNotes] = useState("");
  const [channelDrafts, setChannelDrafts] = useState<Record<string, string>>({});
  const combinedError =
    profilesQuery.error ?? authorsQuery.error ?? channelsQuery.error ?? null;

  const createProfileMutation = useMutation({
    mutationFn: createProfile,
    onSuccess: (profile) => {
      queryClient.setQueryData(["profiles"], (previous: Awaited<ReturnType<typeof getProfiles>> | undefined) =>
        previous ? [profile, ...previous] : [profile]
      );
      toast("Profile saved", {
        description: `${profile.name} is ready to shape the next digest queue.`,
      });
      setDialogOpen(false);
    },
  });

  const addAuthorMutation = useMutation({
    mutationFn: addAuthorWatch,
    onSuccess: (author) => {
      queryClient.setQueryData(
        ["authors"],
        (previous: Awaited<ReturnType<typeof getAuthorWatchlist>> | undefined) =>
          previous ? [author, ...previous] : [author]
      );
      toast("Author added", {
        description: `${author.author_name} will now stay visible in the watchlist.`,
      });
      setAuthorName("");
      setAuthorNotes("");
    },
  });

  const removeAuthorMutation = useMutation({
    mutationFn: removeAuthorWatch,
    onSuccess: (_, id) => {
      queryClient.setQueryData(
        ["authors"],
        (previous: Awaited<ReturnType<typeof getAuthorWatchlist>> | undefined) =>
          previous?.filter((author) => author.id !== id) ?? []
      );
      toast("Author removed", {
        description: "The watchlist was updated for the next sync cycle.",
      });
    },
  });

  const updateChannelMutation = useMutation({
    mutationFn: updateNotificationChannel,
    onSuccess: (channel) => {
      setChannelDrafts((previous) => {
        const next = { ...previous };
        delete next[channel.id];
        return next;
      });
      queryClient.setQueryData(
        ["channels"],
        (previous: Awaited<ReturnType<typeof getNotificationChannels>> | undefined) =>
          previous?.map((item) => (item.id === channel.id ? channel : item)) ?? [channel]
      );
      toast("Channel updated", {
        description: `${channel.label} now reflects the latest delivery settings.`,
      });
    },
  });

  return (
    <div className="space-y-6">
      {!queriesEnabled ? (
        <Card>
          <CardContent className="pt-6 text-sm text-[var(--foreground-muted)]">
            Syncing authenticated workspace context with the backend...
          </CardContent>
        </Card>
      ) : null}

      {combinedError ? (
        <Card>
          <CardContent className="pt-6 text-sm text-rose-500">
            {combinedError instanceof Error
              ? combinedError.message
              : "Failed to load workspace interests from the backend API."}
          </CardContent>
        </Card>
      ) : null}

      <section className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="pt-6">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
              Profiles
            </p>
            <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
              {profilesQuery.data?.length ?? 0}
            </p>
            <p className="mt-2 text-sm text-[var(--foreground-muted)]">
              Saved themes that influence topical relevance and profile-fit scoring.
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
              Watched authors
            </p>
            <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
              {authorsQuery.data?.length ?? 0}
            </p>
            <p className="mt-2 text-sm text-[var(--foreground-muted)]">
              A lightweight prestige prior without turning prestige into a hard filter.
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--foreground-subtle)]">
              Active channels
            </p>
            <p className="mt-3 font-[family:var(--font-display)] text-3xl font-semibold">
              {channelsQuery.data?.filter((channel) => channel.is_active).length ?? 0}
            </p>
            <p className="mt-2 text-sm text-[var(--foreground-muted)]">
              Delivery routes ready to receive the next digest or high-priority alert.
            </p>
          </CardContent>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-[minmax(0,1.15fr)_minmax(360px,0.85fr)]">
        <Card>
          <CardHeader className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <CardTitle className="text-2xl">Topic profiles</CardTitle>
              <p className="mt-2 max-w-2xl text-sm leading-7 text-[var(--foreground-muted)]">
                Profiles define the themes, categories, and keywords that move papers through the
                metadata-first triage stack.
              </p>
            </div>

            <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
              <DialogTrigger asChild>
                <Button disabled={!queriesEnabled}>
                  <Plus />
                  Add profile
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create a new profile</DialogTitle>
                  <DialogDescription>
                    Keep the saved logic close to how you actually consume papers.
                  </DialogDescription>
                </DialogHeader>
                <ProfileForm
                  busy={createProfileMutation.isPending}
                  onSubmit={async (value) => {
                    await createProfileMutation.mutateAsync(value);
                  }}
                />
              </DialogContent>
            </Dialog>
          </CardHeader>
          <CardContent className="space-y-4">
            {profilesQuery.data?.map((profile) => (
              <div
                key={profile.id}
                className="rounded-[24px] border border-[var(--border)] bg-[var(--surface-hover)]/68 p-5"
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h3 className="font-[family:var(--font-display)] text-xl font-semibold">
                      {profile.name}
                    </h3>
                    <p className="mt-2 max-w-2xl text-sm leading-7 text-[var(--foreground-muted)]">
                      {profile.description}
                    </p>
                  </div>
                  <div className="shrink-0 rounded-full bg-[var(--primary-subtle)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-[var(--primary)]">
                    {profile.match_count_24h} matches / 24h
                  </div>
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  {profile.categories.map((category) => (
                    <CategoryTag key={category} category={category} />
                  ))}
                </div>

                <div className="mt-4 flex flex-wrap gap-2">
                  {profile.keywords.map((keyword) => (
                    <span
                      key={keyword}
                      className="rounded-full border border-[var(--border)] bg-[var(--surface)] px-3 py-1 text-sm text-[var(--foreground-muted)]"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">Author watchlist</CardTitle>
              <p className="text-sm leading-7 text-[var(--foreground-muted)]">
                Keep a soft shortlist of authors whose work should surface quickly during triage.
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-3">
                <Input
                  placeholder="Add an author name"
                  value={authorName}
                  onChange={(event) => setAuthorName(event.target.value)}
                />
                <Textarea
                  className="min-h-24"
                  placeholder="Optional note about why this author matters"
                  value={authorNotes}
                  onChange={(event) => setAuthorNotes(event.target.value)}
                />
                <Button
                  onClick={() => {
                    if (!authorName.trim()) {
                      return;
                    }

                    addAuthorMutation.mutate({
                      author_name: authorName.trim(),
                      notes: authorNotes.trim() || undefined,
                    });
                  }}
                  disabled={!queriesEnabled || addAuthorMutation.isPending || !authorName.trim()}
                >
                  <UserPlus />
                  Add author
                </Button>
              </div>

              <div className="space-y-3">
                {authorsQuery.data?.map((author) => (
                  <div
                    key={author.id}
                    className="rounded-[22px] border border-[var(--border)] bg-[var(--surface-hover)]/75 p-4"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="font-medium text-[var(--foreground)]">{author.author_name}</p>
                        <p className="mt-1 text-sm leading-6 text-[var(--foreground-muted)]">
                          {author.notes ?? "No note yet."}
                        </p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeAuthorMutation.mutate(author.id)}
                        disabled={!queriesEnabled || removeAuthorMutation.isPending}
                        aria-label={`Remove ${author.author_name}`}
                      >
                        <Trash2 className="size-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card id="settings">
            <CardHeader>
              <CardTitle className="text-2xl">Notification channels</CardTitle>
              <p className="text-sm leading-7 text-[var(--foreground-muted)]">
                Show the configuration UI now so delivery wiring later can stay thin and predictable.
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              {channelsQuery.data?.map((channel) => (
                <div
                  key={channel.id}
                  className="rounded-[24px] border border-[var(--border)] bg-[var(--surface-hover)]/75 p-4"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2">
                        <BellRing className="size-4 text-[var(--accent)]" />
                        <p className="font-medium text-[var(--foreground)]">{channel.label}</p>
                      </div>
                      <p className="mt-2 text-sm text-[var(--foreground-muted)]">
                        {channel.channel_type} delivery
                      </p>
                    </div>
                    <div
                      className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${
                        channel.is_active
                          ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-300"
                          : "bg-[var(--surface)] text-[var(--foreground-subtle)]"
                      }`}
                    >
                      {channel.is_active ? "Active" : "Paused"}
                    </div>
                  </div>

                  <div className="mt-4 grid gap-3">
                    <Input
                      value={channelDrafts[channel.id] ?? channel.config.target ?? ""}
                      onChange={(event) => {
                        setChannelDrafts((previous) => ({
                          ...previous,
                          [channel.id]: event.target.value,
                        }));
                      }}
                    />
                    <div className="flex flex-wrap gap-2">
                      <Button
                        variant="secondary"
                        disabled={!queriesEnabled || updateChannelMutation.isPending}
                        onClick={() =>
                          updateChannelMutation.mutate({
                            id: channel.id,
                            config: {
                              ...channel.config,
                              target: channelDrafts[channel.id] ?? channel.config.target ?? "",
                            },
                          })
                        }
                      >
                        Save target
                      </Button>
                      <Button
                        variant="outline"
                        disabled={!queriesEnabled || updateChannelMutation.isPending}
                        onClick={() =>
                          updateChannelMutation.mutate({
                            id: channel.id,
                            is_active: !channel.is_active,
                          })
                        }
                      >
                        {channel.is_active ? "Pause channel" : "Resume channel"}
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
