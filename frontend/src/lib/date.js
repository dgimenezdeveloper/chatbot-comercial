const DAY_LABELS = [
  "Domingo",
  "Lunes",
  "Martes",
  "Miércoles",
  "Jueves",
  "Viernes",
  "Sábado",
];

const MONTH_LABELS = [
  "ene",
  "feb",
  "mar",
  "abr",
  "may",
  "jun",
  "jul",
  "ago",
  "sep",
  "oct",
  "nov",
  "dic",
];

export function toDateKey(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function addDays(date, days) {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

export function getWeekStart(date) {
  const result = new Date(date);
  const day = result.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  result.setDate(result.getDate() + diff);
  result.setHours(0, 0, 0, 0);
  return result;
}

export function getWeekDays(date, count = 6) {
  const weekStart = getWeekStart(date);
  return Array.from({ length: count }, (_, index) => addDays(weekStart, index));
}

export function formatDayLabel(date) {
  return DAY_LABELS[date.getDay()];
}

export function formatShortDate(date) {
  return `${date.getDate()} ${MONTH_LABELS[date.getMonth()]}`;
}

export function formatWeekRange(startDate, endDate) {
  const sameYear = startDate.getFullYear() === endDate.getFullYear();
  const start = `${startDate.getDate()} ${MONTH_LABELS[startDate.getMonth()]}`;
  const end = `${endDate.getDate()} ${MONTH_LABELS[endDate.getMonth()]}`;

  if (sameYear) {
    return `${start} - ${end} ${startDate.getFullYear()}`;
  }

  return `${start} ${startDate.getFullYear()} - ${end} ${endDate.getFullYear()}`;
}

export function parseTimeToMinutes(time) {
  const [hours, minutes] = time.split(":").map(Number);
  return hours * 60 + minutes;
}
