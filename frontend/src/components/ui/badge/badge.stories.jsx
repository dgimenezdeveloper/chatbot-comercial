import { Badge, badgeVariants } from "@/components/ui/badge/badge";

export default  {
    title: "Components/UI/Badge",
}

export const Default = () => <Badge>Default Badge</Badge>;
export const Variant = () => <Badge className={badgeVariants({ variant: "secondary" })}>Secondary</Badge>;