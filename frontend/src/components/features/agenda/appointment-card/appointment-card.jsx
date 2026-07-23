import { APPOINTMENT_STATUS } from "@/lib/data/mock-appointments";
import { cn } from "@/lib/utils";

const toneStyles = {
  green: "border-green-200 bg-green-50 text-green-900",
  purple: "border-purple-200 bg-purple-50 text-purple-900",
  yellow: "border-yellow-200 bg-yellow-50 text-yellow-900",
  gray: "border-slate-200 bg-slate-100 text-slate-600",
};

const statusDotStyles = {
  [APPOINTMENT_STATUS.CONFIRMED]: "bg-green-500",
  [APPOINTMENT_STATUS.CANCELLED]: "bg-slate-400",
  [APPOINTMENT_STATUS.BLOCKED]: "bg-yellow-500",
};

export default function AppointmentCard({ appointment, style, onClick }) {
  const tone = appointment.tone ?? "green";

  return (
    <button
      type="button"
      onClick={() => onClick?.(appointment.id)}
      style={style}
      className={cn(
        "absolute right-1 left-1 overflow-hidden rounded-md border px-2 py-1.5 text-left text-xs shadow-sm transition-opacity hover:opacity-90",
        toneStyles[tone],
      )}
    >
      <div className="flex items-start gap-1.5">
        <span
          className={cn(
            "mt-1 size-2 shrink-0 rounded-full",
            statusDotStyles[appointment.status],
          )}
        />
        <span className="line-clamp-2 leading-snug font-medium">
          {appointment.clientName} - {appointment.serviceName}
        </span>
      </div>
    </button>
  );
}
