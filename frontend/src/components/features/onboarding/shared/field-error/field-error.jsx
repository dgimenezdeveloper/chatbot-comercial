/**
 * Muestra el mensaje de error correspondiente a un campo.
 *
 * Si no recibe ningún mensaje, no renderiza nada.
 */
export default function FieldError({ message }) {
  if (!message) return null;

  return (
    <p role="alert" className="mt-1 text-sm text-red-600">
      {message}
    </p>
  );
}