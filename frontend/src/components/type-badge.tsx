import { Badge } from "@/components/ui/badge";
import { t, type MessageKey } from "@/lib/i18n";

const TYPE_VARIANT: Record<string, "default" | "secondary" | "outline"> = {
  public: "secondary",
  private: "outline",
  applied_sciences: "default",
  art_music: "outline",
  church: "outline",
};

const TYPE_LABELS: Record<string, MessageKey> = {
  public: "university.type.public",
  private: "university.type.private",
  applied_sciences: "university.type.applied_sciences",
  art_music: "university.type.art_music",
  church: "university.type.church",
};

export function TypeBadge({ type }: { type: string | null | undefined }) {
  if (!type) return null;
  const labelKey = TYPE_LABELS[type];
  const label = labelKey ? t(labelKey) : type;
  return (
    <Badge variant={TYPE_VARIANT[type] ?? "secondary"} className="text-[10px] px-1.5 py-0">
      {label}
    </Badge>
  );
}
