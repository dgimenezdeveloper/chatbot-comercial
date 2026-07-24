export function formatCurrency(amount) {
  return `$${amount.toLocaleString("es-AR")}`;
}

export function formatDuration(minutes) {
  return `${minutes} min`;
}
