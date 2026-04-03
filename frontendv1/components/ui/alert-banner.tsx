import { AlertTriangle, CheckCircle2, Info } from "lucide-react";

import { cn } from "@/lib/utils";

const toneMap = {
  info: {
    icon: Info,
    classes: "border-forest/20 bg-mist text-forest"
  },
  success: {
    icon: CheckCircle2,
    classes: "border-forest/20 bg-[#e6f2ec] text-forest"
  },
  warning: {
    icon: AlertTriangle,
    classes: "border-ember/20 bg-[#fff0e8] text-[#7a3d21]"
  },
  error: {
    icon: AlertTriangle,
    classes: "border-[#c65353]/20 bg-[#faeaea] text-[#7c2020]"
  }
};

export function AlertBanner({
  detail,
  title,
  tone = "info"
}: {
  title: string;
  detail?: string;
  tone?: keyof typeof toneMap;
}) {
  const toneConfig = toneMap[tone];
  const Icon = toneConfig.icon;

  return (
    <div className={cn("rounded-[22px] border p-4", toneConfig.classes)}>
      <div className="flex items-start gap-3">
        <Icon className="mt-0.5 h-5 w-5 shrink-0" />
        <div>
          <p className="font-semibold">{title}</p>
          {detail ? <p className="mt-1 text-sm leading-6 opacity-85">{detail}</p> : null}
        </div>
      </div>
    </div>
  );
}
