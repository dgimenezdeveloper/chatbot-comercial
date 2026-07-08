import {
    Table,
    TableHeader,
    TableBody,
    TableFooter,
    TableHead,
    TableRow,
    TableCell,
    TableCaption,
} from "@/components/ui/table/table";

export default {
    title: "Components/UI/Table",
};

export const Default = () => (
    <Table>
        <TableCaption>Tabla de ejemplo</TableCaption>
        <TableHeader>
            <TableRow>
                <TableHead>Nombre</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Estado</TableHead>
            </TableRow>
        </TableHeader>
        <TableBody>
            <TableRow>
                <TableCell>Juan</TableCell>
                <TableCell>juan@example.com</TableCell>
                <TableCell>Activo</TableCell>
            </TableRow>
            <TableRow>
                <TableCell>María</TableCell>
                <TableCell>maria@example.com</TableCell>
                <TableCell>Activo</TableCell>
            </TableRow>
        </TableBody>
        <TableFooter>
            <TableRow>
                <TableCell>Total</TableCell>
                <TableCell colSpan="2">2 registros</TableCell>
            </TableRow>
        </TableFooter>

    </Table>
)