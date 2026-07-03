import { Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardAction,
  CardDescription,
  CardContent, } from "./card";

const CardStories = {
  title: "Component/UI/Card",
  component: Card,
};

export default CardStories;

export const Default = () => (
  <Card>
    <CardHeader>
      <CardTitle>Producto 1</CardTitle>
      <CardDescription>Resumen breve del producto o servicio.</CardDescription>
      <CardAction>
        <button className="rounded-md bg-primary px-3 py-1 text-white">Ver más</button>
      </CardAction>
    </CardHeader>
    <CardContent>
      <p>Este es el contenido principal de la tarjeta.</p>
    </CardContent>
    <CardFooter>
      <span className="text-sm text-muted-foreground">Actualizado hace 2 horas</span>
    </CardFooter>
  </Card>
);