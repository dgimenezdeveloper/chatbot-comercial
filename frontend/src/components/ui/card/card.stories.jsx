import { Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardAction,
  CardDescription,
  CardContent, } from "./card";

export default {
  title: "UI/Card",
  component: Card,
};

export const Default = () => (
  <Card>
    <CardContent>Contenido de la tarjeta</CardContent>
  </Card>
);